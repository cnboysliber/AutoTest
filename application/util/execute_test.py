import json
import timeit
import time
import sys
import traceback
import re
import html
import requests
import os
from urllib.parse import quote
import urllib3
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta
from requests.exceptions import ConnectionError, ConnectTimeout

from application import app
from application.util import encryption as Encryption
from application.util import parameter as ParameterUtil
from application.api import run_log as RunLogAPI
from application.api import interface as InterfaceAPI
from application.api import parameter as ParameterAPI
from application.api import batch as BatchAPI
from application.api import use_case as UseCaseAPI
from application.api import encryption as EncryptionAPI
from application.api import environment as EnvironmentAPI
from application.api import email as EmailAPI
from application.util.exception import try_except
from application.util import g_DNS
from application.util import email_send as m
from application.util.custom_http import CustomAdapter

if not app.config['DEBUG']:
    from application.util import logger as LOGGER
else:
    from application.util import LocalLogger as LOGGER

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# 多进程执行器
executor = ThreadPoolExecutor(max_workers=8)
host_name = app.config['HOST_NAME']


@try_except
def interface_log_insert(interface_log_dict):
    """
    记录接口请求日志
    :param interface_log_dict:      接口请求信息
    """
    interface_end_time = datetime.utcnow()
    interface_stop = interface_log_dict['interface_stop'] if 'interface_stop' in interface_log_dict \
        else timeit.default_timer()

    RunLogAPI.add_interface_run_log(**{
        'use_case_run_log_id': interface_log_dict['use_case_run_log_id'],
        'interface_id': interface_log_dict['interface_id'],
        'is_pass': interface_log_dict['is_pass'],
        'cost_time':
            interface_stop - interface_log_dict['interface_start'] if 'interface_start' in interface_log_dict else 0,
        'start_time': interface_log_dict['interface_start_time'],
        'end_time': interface_end_time,
        'error_message': interface_log_dict['error_message'] if 'error_message' in interface_log_dict else '',
        's_header': interface_log_dict['s_header'] if 's_header' in interface_log_dict else '',
        's_payload': interface_log_dict['s_payload'] if 's_payload' in interface_log_dict else '',
        'r_code': interface_log_dict['r_code'] if 'r_code' in interface_log_dict else '',
        'r_header': interface_log_dict['r_header'] if 'r_header' in interface_log_dict else '',
        'r_payload': interface_log_dict['r_payload'] if 'r_payload' in interface_log_dict else ''
    })


@try_except
def use_case_exception_log_update(use_case_log_id, use_case_start):
    """
    用例执行过程中抛出异常时
    更新用例的运行日志
    :param use_case_log_id:
    :param use_case_start:
    :return:
    """
    use_case_stop = timeit.default_timer()
    end_time = datetime.utcnow()
    return RunLogAPI.modify_use_case_run_log(**{
        'id': use_case_log_id,
        'is_pass': False,
        'end_time': end_time,
        'cost_time': use_case_stop - use_case_start
    })


@app.context_processor
def run_use_case(use_case_id, batch_log_id=None, environment_id=None, relation_id=None,
                 use_case_count=None, batch_start_timer=None, auto_run=False, alarm_monitor=False):
    # if async:
    #     engine.dispose()
    exec_result_list = []
    interface_count = 1

    # 信息初始化
    start_time = datetime.utcnow()
    use_case_start = timeit.default_timer()
    run_pass = True
    use_case_log_info = {
        'use_case_id': use_case_id,
        'start_time': start_time,
        'auto_run': auto_run
    }
    if batch_log_id:
        use_case_log_info['batch_run_log_id'] = batch_log_id
    try:
        use_case_log_id = RunLogAPI.add_use_case_run_log(**use_case_log_info)

    except Exception as e:
        error = '{0}: {1}'.format(str(e.__class__.__name__), str(e))
        return except_result(interface_count, exec_result_list, error, batch_log_id, use_case_count, batch_start_timer)

    # 获取用例信息以及用例下接口信息
    try:
        use_case_info = UseCaseAPI.get_use_case(id=use_case_id)[0]
        if relation_id:
            interface_list = UseCaseAPI.get_relation(id=relation_id)
        else:
            interface_list = UseCaseAPI.get_relation(use_case_id=use_case_id)
    except Exception as e:
        use_case_exception_log_update(use_case_log_id, use_case_start)
        error = '{0}: {1}'.format(str(e.__class__.__name__), str(e))
        return except_result(interface_count, exec_result_list, error, batch_log_id, use_case_count, batch_start_timer)

    try:
        use_case_info['interface_list'] = []
        # 对用例中使用预定义参数的做参数替换
        for interface_relation in interface_list:
            eval_string = interface_relation['eval_string']
            interface_id = interface_relation['interface_id']
            interface_info = InterfaceAPI.get_interface(id=interface_id)[0]
            interface_info['interface_delay'] = interface_relation['interface_delay']
            interface_info['eval_string'] = eval_string

            interface_info['param_define_list'] = get_param_define_list(interface_relation['id'])
            use_case_info['interface_list'].append(interface_info)
        interface_list = use_case_info['interface_list']
    except Exception as e:
        # 用例运行日志记录
        use_case_exception_log_update(use_case_log_id, use_case_start)

        error = '{0}: {1}'.format(str(e.__class__.__name__), str(e))
        return except_result(interface_count, exec_result_list, error, batch_log_id, use_case_count, batch_start_timer)

    function_id = use_case_info['function_id']
    email_addrs = EmailAPI.query_email_by_function_id(function_id)
    addr_dicts = {email['email_address'].split('@')[0]: email['email_address'] for email in email_addrs}

    # 由于线上环境配置有host，所以监控模式下，也要配置环境信息
    if batch_log_id:
        environment_id = environment_id
    else:
        environment_id = environment_id or use_case_info['environment_id']
    environment_info = EnvironmentAPI.get_environment_line_info(environment_id=environment_id)
    url_map_ip = dict()
    for element in environment_info:
        url = element['url'].strip()
        ip_address = element['map_ip'].strip()
        url_map_ip[url] = ip_address
    encryption_dict = EncryptionAPI.get_encryption_id_to_name()

    with requests.Session() as session:
        for interface in interface_list:
            # 添加延时运行接口
            interface_delay = int(interface.get('interface_delay'))
            if interface_delay > 0:
                time.sleep(interface_delay)
            interface_name = interface.get('interface_name')
            interface_log_dict = {
                'interface_start_time': datetime.utcnow(),
                'use_case_run_log_id': use_case_log_id,
                'interface_id': interface['id']
            }
            try:
                # 将接口未替换的参数全部替换
                request_method = interface['interface_method']

                result_list = get_item_to_rephrase(interface, exec_result_list, data_type=interface['body_type'])
                url, header, json_payload = result_list
            except Exception as e:
                # 数据处理以及日志记录
                interface_log_dict['is_pass'] = False
                interface_log_dict['error_message'] = '参数替换: {0}: {1}'.format(str(e.__class__.__name__), str(e))
                interface_log_insert(interface_log_dict)
                # 用例运行日志记录
                use_case_exception_log_update(use_case_log_id, use_case_start)
                error = '{0}: {1}'.format(str(e.__class__.__name__), str(e))
                return except_result(interface_count, exec_result_list, error, batch_log_id, use_case_count,
                                     batch_start_timer)

            try:
                # 加密
                if interface['body_type'] == 0 and json_payload:
                    requested_interface = get_remote_interface_name(json.loads(json_payload), interface, url)
                else:
                    requested_interface = get_remote_interface_name('', interface, url)
                if header:
                    header = json.loads(header)
                if json_payload:
                    if interface['interface_encryption'] != 0:
                        encryption_method = encryption_dict[interface['interface_encryption']]
                        method = getattr(Encryption, encryption_method)
                        if interface['interface_encryption'] in [1, 4]:
                            header = method(json_payload, header)
                        elif interface['interface_encryption'] == 5:
                            url, json_payload = method(url, json_payload)
                        else:
                            json_payload = method(json_payload)
            except Exception as e:
                # 数据处理以及日志记录
                print(e)
                interface_log_dict['is_pass'] = False
                interface_log_dict['error_message'] = 'json处理或加密: {0}: {1}'.format(str(e.__class__.__name__), str(e))

                interface_log_dict['s_header'] = str(header)
                interface_log_dict['s_payload'] = str(json_payload)
                interface_log_dict['interface_start'] = timeit.default_timer()

                interface_log_insert(interface_log_dict)
                # 用例运行日志记录
                use_case_exception_log_update(use_case_log_id, use_case_start)

                error = '{0}: {1}'.format(str(e.__class__.__name__), str(e))
                return except_result(interface_count, exec_result_list, error, batch_log_id, use_case_count,
                                     batch_start_timer)

            # 请求接口参数准备
            request_kwargs = {
                'timeout': 30
            }
            if header:
                request_kwargs['headers'] = header
            else:
                request_kwargs['headers'] = dict()
            if json_payload:
                request_kwargs.update({'json': json_payload}) if interface['body_type'] == 0 \
                    else request_kwargs.update({"data": json_payload})

            # 获取域名对应的服务名
            server_name = get_server_name(url)

            # 获取方法ID, 接口名

            # 日志内容
            interface_log_dict['s_header'] = json.dumps(header, ensure_ascii=False) if header else ''
            if interface['body_type'] == 0:
                interface_log_dict['s_payload'] = json.dumps(json_payload, ensure_ascii=False) if json_payload else ''
            else:
                interface_log_dict['s_payload'] = json_payload
            interface_log_dict['interface_start'] = timeit.default_timer()

            request_exception = False
            log_report_code = 0
            error_string = ''
            json_response = result = dict()
            request_method = request_method.upper()
            request_kwargs['headers']['Connection'] = 'close'

            try:
                url_netloc = url.rsplit('/')
                prefix = '//'.join([url_netloc[0], url_netloc[2]])
                host_name = url_netloc[2]
                if environment_id:
                    source_address = url_map_ip.get(host_name, None)
                    session.mount(prefix, CustomAdapter(source_address=source_address))

                r = session.request(request_method, url, **request_kwargs)
                time.sleep(0.01)
                r.encoding = 'utf-8'
                try:
                    json_response = r.json()
                    json_flag = True
                except Exception as e:
                    json_flag = False
                    r_type = r.headers['Content-Type']
                    if 'application/json' != r_type:
                        json_response = r.content.decode()
                    else:
                        json_response = {}
                interface_log_dict['interface_stop'] = timeit.default_timer()
                result = {
                    'r_request': request_kwargs,
                    'status_code': r.status_code,
                    'header': dict(r.headers),
                    'json_response': json_response,
                    'interface_name': interface_name
                }
                interface_log_dict['r_code'] = r.status_code
                interface_log_dict['r_header'] = json.dumps(result['header'], ensure_ascii=False)
                if json_flag:
                    interface_log_dict['r_payload'] = json.dumps(result['json_response'], ensure_ascii=False)
                elif interface['interface_encryption'] == 6:
                    interface_log_dict['r_payload'] = json.dumps(json_response, ensure_ascii=False)
                else:
                    r.encoding = 'utf-8'
                    interface_log_dict['r_payload'] = r.text
                    result['json_response'] = '<iframe srcdoc="{}" style="width:100%;height:60vh" ' \
                                              'frameborder="0"></iframe>'.format(html.escape(r.text))
            except ConnectTimeout as e:
                request_exception = True
                error_string = '{0}: {1} ，{2}'.format('请求服务连接超时', str(e.__class__.__name__), str(e))
                log_report_code = '9991'
            except ConnectionError as e:
                if os.getpid() in g_DNS.get_dns():
                    dns_info = g_DNS.get_dns()[os.getpid()]
                    LOGGER.info_log('连接失败，环境映射信息：{}, 当前url:{}'.format(dns_info, url))
                request_exception = True
                error_string = '{0}，{1}: {2}'.format('请求服务连接失败', str(e.__class__.__name__), str(e))
                log_report_code = '9992'
            except KeyError as e:
                request_exception = True
                error_string = '错误代码行{0}: {1}'.format(sys._getframe().f_lineno, str(e))
                log_report_code = '9993'
            except Exception as e:
                request_exception = True
                error_string = '{0}: {1}，{2}'.format(sys._getframe().f_lineno, str(e.__class__.__name__), str(e))
                log_report_code = '9994'
            finally:
                if request_exception:
                    if alarm_monitor and not app.config['DEBUG']:
                        cost_time = timeit.default_timer() - interface_log_dict['interface_start']
                        LOGGER.request_log(server_name, server_name, requested_interface, log_report_code,
                                           str(cost_time))
                        message = get_email_body(use_case_info['use_case_name'],
                                                 interface_name, error_string, use_case_log_id)
                        executor.submit(execute_fail_email, addr_dicts, message)

                    # 数据处理以及日志记录
                    interface_log_dict['is_pass'] = False
                    interface_log_dict['error_message'] = '{0}'.format(error_string)
                    interface_log_insert(interface_log_dict)
                    # 用例运行日志记录
                    use_case_exception_log_update(use_case_log_id, use_case_start)
                    return except_result(interface_count, exec_result_list, error_string, batch_log_id, use_case_count,
                                         batch_start_timer)
            try:
                # 验证接口返回
                eval_success = eval_interface_result(result, interface['eval_string'], exec_result_list)
                result['success'] = eval_success
                run_pass = run_pass and eval_success
                exec_result_list.append(result)
                # 数据处理以及日志记录
                interface_log_dict['is_pass'] = result['success']
                executor.submit(interface_log_insert, interface_log_dict)

                if alarm_monitor and not app.config['DEBUG']:
                    executor.submit(monitor_request, interface_log_dict, json_response,
                                    eval_success, server_name, requested_interface)
                    if not result['success']:
                        message = get_email_body(use_case_info['use_case_name'],
                                                 interface_name, '返回结果验证失败', use_case_log_id)
                        executor.submit(execute_fail_email, addr_dicts, message)

                if not result['success']:
                    break
            except Exception as e:
                result['success'] = False
                exec_result_list.append(result)
                # 数据处理以及日志记录
                interface_log_dict['is_pass'] = result['success']
                exc_type, exc_obj, exc_tb = sys.exc_info()
                error = '{0}: {1}'.format(str(e.__class__.__name__), str(e))
                interface_log_dict['error_message'] = '验证: {0}: {1},异常信息：{2}'. \
                    format(str(e.__class__.__name__), str(e), str(traceback.extract_tb(exc_tb)))

                if alarm_monitor and not app.config['DEBUG']:
                    message = get_email_body(use_case_info['use_case_name'],
                                             interface_name, interface_log_dict['error_message'], use_case_log_id)

                    executor.submit(execute_fail_email, addr_dicts, message)

                interface_log_insert(interface_log_dict)
                # 用例运行日志记录
                use_case_exception_log_update(use_case_log_id, use_case_start)

                return except_result(interface_count, exec_result_list, error,
                                     batch_log_id, use_case_count, batch_start_timer)

            interface_count += 1

    # 用例运行日志记录
    use_case_stop = timeit.default_timer()
    end_time = datetime.utcnow()
    RunLogAPI.modify_use_case_run_log(**{
        'id': use_case_log_id,
        'is_pass': run_pass,
        'end_time': end_time,
        'cost_time': use_case_stop - use_case_start
    })
    response = {'pass': run_pass,
                'res': exec_result_list,
                'batch_log_id': batch_log_id,
                'use_case_count': use_case_count,
                'batch_start_timer': batch_start_timer}
    return response


def run_use_case_callback(obj):
    """
    用例异步运行的回调函数
    :param obj:
    :return:
    """

    result = obj.result()
    batch_log_id = result['batch_log_id']
    success_count = 0
    try:
        batch_log = RunLogAPI.get_batch_run_log_info(id=batch_log_id)
        if not batch_log:
            return
        if batch_log[0]['pass_rate'] != -1:
            return
        use_case_count = result['use_case_count']
        use_case_run_logs = RunLogAPI.get_use_case_run_log(batch_run_log_id=batch_log_id)
        finished_use_case = 0
        for use_case_log in use_case_run_logs:
            if use_case_log['cost_time'] != 0.0:
                finished_use_case += 1
        if finished_use_case == use_case_count:
            batch_start_timer = result['batch_start_timer']
            batch_end_timer = timeit.default_timer()

            for run_log in use_case_run_logs:
                if run_log['is_pass']:
                    success_count += 1
            pass_rate = int(success_count / use_case_count * 100)
            RunLogAPI.modify_batch_run_log(**{
                'id': batch_log_id,
                'pass_rate': pass_rate,
                'end_time': datetime.utcnow(),
                'cost_time': batch_end_timer - batch_start_timer
            })
    except Exception as e:
        LOGGER.info_log(str(e))
        RunLogAPI.modify_batch_run_log(**{
            'id': batch_log_id,
            'pass_rate': int(success_count / result['use_case_count'] * 100),
            'end_time': datetime.utcnow(),
            'cost_time': timeit.default_timer() - result['batch_start_timer']
        })


@try_except
def run_use_case_async(use_case_id, batch_log_id=None, environment_id=None, use_case_count=None,
                       batch_start_timer=None, auto_run=False, alarm_monitor=False):
    """
    用例异步运行接口
    :param use_case_id:
    :param batch_log_id:
    :param environment_id:
    :param use_case_count:
    :param batch_start_timer:
    :param auto_run:
    :param alarm_monitor:
    :return:
    """
    if batch_log_id:
        executor.submit(run_use_case, use_case_id, batch_log_id, environment_id, None, use_case_count,
                        batch_start_timer, auto_run, alarm_monitor). \
            add_done_callback(run_use_case_callback)
    else:
        executor.submit(run_use_case, use_case_id, batch_log_id, environment_id, None, use_case_count,
                        batch_start_timer, auto_run, alarm_monitor)


@try_except
def run_batch(batch_id, environment_id=0, auto_run=False, alarm_monitor=False):
    """
    批次运行接口
    :param batch_id:
    :param environment_id:
    :param auto_run:
    :param alarm_monitor:
    :return:
    """
    start_timer = timeit.default_timer()
    relation_list = BatchAPI.get_batch_use_case_relation(batch_id=batch_id)
    use_case_count = len(relation_list)
    start_time = datetime.utcnow()
    batch_log_id = RunLogAPI.add_batch_run_log(**{
        'batch_id': batch_id,
        'use_case_count': use_case_count,
        'start_time': start_time
    })

    counter = 0
    for relation in relation_list:
        counter += 1
        use_case = UseCaseAPI.get_use_case(id=relation['use_case_id'])[0]
        run_use_case_async(use_case['id'], batch_log_id, environment_id=environment_id, use_case_count=use_case_count,
                           batch_start_timer=start_timer, auto_run=auto_run, alarm_monitor=alarm_monitor)


def get_param_define_list(relation_id=None):
    """
    正则解析用例全局参数的实际值返回相关值列表
    :param relation_id:
    :return:
    """
    param_define_list = UseCaseAPI.get_case_parameter_relation(relation_id=relation_id)
    param_list = []
    for param in param_define_list:
        pattern = re.compile(r'\${param\|[^${}]*}|^random\(.*\)|\${timestamps}|\$md5\(.*\)')
        match_result = pattern.findall(param['parameter_value'])
        if match_result:
            if 'random' in match_result[0]:
                param_value = ParameterUtil.random_length_seq(match_result[0])
            elif '${timestamps}' in match_result:
                temp_string = str(int(time.time()))
                param_value = param['parameter_value'].replace('${timestamps}', temp_string)
                a = []
                exec_string = 'a.append({0})'.format(param_value)
                exec(exec_string, globals(), locals())
                param_value = str(a[0])
            elif '$md5(' in match_result[0]:
                param_value = ParameterUtil.param_2_md5(match_result[0])
            else:
                param_name = match_result[0].split('|')[1].replace('}', '')
                param_value = ParameterAPI.get_parameter(parameter_name=param_name)[0]['value']
            param['parameter_value'] = param_value
        param_list.append(param)
    return param_list


def eval_interface_result(result, eval_string, exec_result_list):
    """
    验证接口返回
    :param result:
    :param eval_string:
    :param exec_result_list: 前置接口运行的结果列表对象
    :return:
    """
    LOGGER.info_log(result)
    if eval_string:
        eval_string = eval_string.replace('${status_code}', 'result["status_code"]') \
            .replace('${header}', 'result["header"]') \
            .replace('${json_payload}', 'result["json_response"]')
        value_to_rephrase = ParameterUtil.search_parameter(eval_string)
        if value_to_rephrase:
            for value_info in value_to_rephrase:
                order, name = value_info.split('|')
                name = 'json_response' if name == 'json_payload' else name

                temp_string = 'exec_result_list[{0}]["{1}"]'.format(str(int(order) - 1), name)
                eval_string = eval_string.replace('${{{0}}}'.format(value_info), temp_string)
        a = []
        exec_string = 'a.append({0})'.format(eval_string)
        exec(exec_string, locals(), locals())
        return bool(a[0])
    else:
        return True


def get_server_name(url):
    """
     获取域名对应的服务名
    :param url:
    :return:
    """
    get_server_name_dict = {
        "_head": {
            "_version": "0.01",
            "_msgType": "request",
            "_timestamps": "",
            "_invokeId": "",
            "_callerServiceId": "",
            "_groupNo": "",
            "_interface": "get_server_name",
            "_remark": ""
        },
        "_params": {
            "strUrl": url
        }
    }
    try:
        response = requests.post('http://123.207.51.243:8000/base_server', json=get_server_name_dict, timeout=5)
        server_name = response.json()['_data']['retInfo']['serverName']
    except Exception as e:
        server_name = '获取服务名失败:'.format(str(e))
    return server_name


def get_remote_interface_name(json_payload, interface, url):
    """
    获取方法ID, 接口名
    :param json_payload:
    :param interface:
    :param url:
    :return:
    """
    requested_interface = ''
    if json_payload:
        if 'head' in json_payload:
            if 'interface' in json_payload['head']:
                requested_interface = json_payload['head']['interface']
        elif '_head' in json_payload:
            if '_interface' in json_payload['_head']:
                requested_interface = json_payload['_head']['_interface']
    if not requested_interface:
        try:
            requested_interface = url.split('//')[1].split('/')[0]
        except Exception as e:
            LOGGER.info_log('接口名称获取异常：{}'.format(str(e)))
            requested_interface = interface['interface_url'].split('//')[1].split('/')[0]
    return requested_interface


def except_result(interface_count, exec_result_list, error, batch_log_id, use_case_count, batch_start_timer):
    """
    用例运行异常返回结果
    :param interface_count:
    :param exec_result_list:
    :param error:
    :param batch_log_id:
    :param use_case_count:
    :param batch_start_timer:
    :return:
    """
    return {'success': False,
            'error_str': '接口{0} json处理或加密'.format(interface_count),
            'res': exec_result_list,
            'error': error,
            'batch_log_id': batch_log_id,
            'use_case_count': use_case_count,
            'batch_start_timer': batch_start_timer
            }


def monitor_request(interface_log_dict, json_response, eval_success, server_name, requested_interface):
    """
    监控用例运行结果函数，把用例运行结果记录到日志中
    :param interface_log_dict:
    :param json_response:
    :param eval_success:
    :param server_name:
    :param requested_interface:
    :return:
    """
    cost_time = interface_log_dict['interface_stop'] - interface_log_dict['interface_start']
    ret_code = '' if eval_success else '1'
    if not ret_code:
        if 'body' in json_response:
            if 'ret' in json_response['body']:
                ret_code = json_response['body']['ret']
        elif '_data' in json_response:
            if '_ret' in json_response['_data']:
                ret_code = json_response['_data']['_ret']
        else:
            ret_code = '0'
    LOGGER.request_log(server_name, server_name, requested_interface, ret_code, str(cost_time))


def get_item_to_rephrase(interface, exec_result_list, data_type=0):
    """
    替换用例中关联接口的参数
    :param interface: 接口信息
    :param exec_result_list: 前置接口运行的结果列表对象
    :param data_type: 数据类型
    :return:
    """
    i_url = 0
    to_rephrase_list = [interface['interface_url'],
                        interface['interface_header'],
                        interface['interface_json_payload']]
    result_list = []
    param_define_list = interface['param_define_list']
    for item_to_rephrase in to_rephrase_list:
        i_url += 1
        param_list = ParameterUtil.search_parameter(item_to_rephrase)
        if param_list:
            for item in param_list:
                param_value = next((param for param in param_define_list
                                    if param["parameter_name"] == item.split('==')[0]))['parameter_value']
                value_to_rephrase = ParameterUtil.search_parameter(param_value)
                if value_to_rephrase or 'time.time()' in param_value:
                    for value_info in value_to_rephrase:
                        order, name = value_info.split('|')
                        name = 'json_response' if name == 'json_payload' else name

                        temp_string = 'exec_result_list[{0}]["{1}"]'.format(str(int(order) - 1), name)
                        param_value = param_value.replace('${{{0}}}'.format(value_info), temp_string)
                    a = []
                    exec_string = 'a.append({0})'.format(param_value)
                    exec(exec_string, globals(), locals())
                    param_value = a[0]
                if i_url <= 1 or data_type:
                    # url参数替换不用双引号包裹
                    item_to_rephrase = item_to_rephrase.replace('${{{0}}}'.format(item), '{0}'.
                                                                format(param_value))
                else:
                    item_to_rephrase = item_to_rephrase.replace('${{{0}}}'.format(item), '"{0}"'.
                                                                format(param_value))
        result_list.append(item_to_rephrase.strip())
    return result_list


def execute_fail_email(addr, message, title="{}自动化巡检系统"):
    """
    邮件通知用例运行结果
    :param addr: {'example1': 'example1@huishoubao.com.cn',
                  'example2': 'example2@huishoubao.com.cn'} 可以是多个用户邮箱的字典
    :param message:
    :param title:
    :return:
    """

    kv = dict()
    kv['address'] = addr
    kv['title'] = title.format(app.config['CLOUD_NAME'])
    kv['body'] = message
    kv['str_url'] = 'http://push.huanjixia.com/email-interface'
    try:
        m.email_send(**kv)
    except Exception as e:
        LOGGER.exception_log(str(e))


def get_email_body(use_case_name, interface_name, err_msg, use_case_log_id, result=None):
    body = '用例：“%s”运行失败 <br>失败信息:接口“%s”%s失败, 失败时间%s<br color="red">' \
           '详情请点击：<a href="http://%s/use_case_run_log/detail/%s?' \
           'from_time=%s&to_time=%s">' \
           '用例"%s"运行日志详情</a><br>' \
           % (use_case_name,
              interface_name,
              err_msg,
              datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
              host_name,
              use_case_log_id,
              quote(datetime.now().strftime('%Y-%m-%d %H:%M'), safe=':'),
              quote((datetime.now() + timedelta(hours=1)).strftime('%Y-%m-%d %H:%M'), safe=':'),
              use_case_name
              )
    if result:
        body += '%s<br>' % result
    return body
