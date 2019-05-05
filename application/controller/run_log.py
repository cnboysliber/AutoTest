# -*- coding:utf-8 -*-
from datetime import datetime
from application.config.default import QUERY_TIME_FMT
from flask import request, jsonify
from application.api import run_log as RunLogAPI
from application.api import use_case as UseCaseAPI
from application.api import interface as InterfaceAPI
from application.api import batch as BatchAPI
from application import app
from application.util import *
from application.util.exception import try_except
from application.controller import login_required


@app.route('/run_log/batch/add', methods=['POST'])
@login_required
@try_except
def add_batch_run_log():
    """
    :return:
    """
    result = RunLogAPI.add_batch_run_log(**request.get_json())
    return jsonify({'success': True, 'res': str(result)})


@app.route('/run_log/batch/info', methods=['POST'])
@login_required
@try_except
def get_multi_batch_run_log_info():
    """
    :return:
    """
    from_time = request.get_json().get('from_time', None)
    to_time = request.get_json().get('to_time', None)
    if from_time:
        from_time = shanghai_to_utc_timezone(datetime.strptime(from_time, QUERY_TIME_FMT))
        request.get_json().update({"from_time": from_time.strftime(QUERY_TIME_FMT)})
    if to_time:
        to_time = shanghai_to_utc_timezone(datetime.strptime(to_time, QUERY_TIME_FMT))
        request.get_json().update({"to_time": to_time.strftime(QUERY_TIME_FMT)})
    param_json = request.get_json()
    '' if 'pageIndex' in param_json else param_json.update({'pageIndex': 1})
    '' if 'pageSize' in param_json else param_json.update({'pageSize': 30})
    result = RunLogAPI.get_multi_batch_run_log_info(**request.get_json())
    result = result
    for batch_run_log_dict in result:
        batch_run_log = BatchAPI.get_batch(id=batch_run_log_dict.get('batch_id'))
        if batch_run_log:
            batch_run_log = batch_run_log[0]
        else:
            batch_run_log_dict['batch_name'] = '批次不存在'
            continue
        batch_run_log_dict['batch_name'] = batch_run_log.get('batch_name')
        start_time = utc_to_shanghai_timezone(batch_run_log_dict.get('start_time'))
        end_time = utc_to_shanghai_timezone(batch_run_log_dict.get('end_time'))
        batch_run_log_dict.update({'start_time': datetime.strftime(start_time, QUERY_TIME_FMT)})
        if end_time:
            batch_run_log_dict.update({'end_time': datetime.strftime(end_time, QUERY_TIME_FMT)})
    return jsonify({'success': True, 'res': result})


@app.route('/run_log/batch/count', methods=['POST'])
@login_required
@try_except
def get_batch_run_log_count():
    """
    :return:
    """
    from_time = request.get_json().get('from_time', None)
    to_time = request.get_json().get('to_time', None)
    if from_time:
        from_time = shanghai_to_utc_timezone(datetime.strptime(from_time, QUERY_TIME_FMT))
        request.get_json().update({"from_time": from_time.strftime(QUERY_TIME_FMT)})
    if to_time:
        to_time = shanghai_to_utc_timezone(datetime.strptime(to_time, QUERY_TIME_FMT))
        request.get_json().update({"to_time": to_time.strftime(QUERY_TIME_FMT)})
    result = RunLogAPI.get_batch_run_log_count(**request.get_json())
    return jsonify({'success': True, 'res': result})


@app.route('/run_log/use_case/add', methods=['POST'])
@login_required
@try_except
def add_use_case_run_log():
    """
    :return:
    """
    RunLogAPI.add_use_case_run_log(**request.get_json())
    return jsonify({'success': True})


@app.route('/run_log/use_case/count', methods=['POST'])
@login_required
@try_except
def get_use_case_run_log_count():
    """
    :return:
    """
    param_kwarg = request.get_json()
    from_time = param_kwarg.get('from_time', None)
    to_time = param_kwarg.get('to_time', None)
    function_id = param_kwarg.get('function_id', None)
    use_case_name = param_kwarg.get('use_case_name', None)
    if from_time:
        from_time = shanghai_to_utc_timezone(datetime.strptime(from_time, QUERY_TIME_FMT))
        param_kwarg.update({"from_time": from_time.strftime(QUERY_TIME_FMT)})
    if to_time:
        to_time = shanghai_to_utc_timezone(datetime.strptime(to_time, QUERY_TIME_FMT))
        param_kwarg.update({"to_time": to_time.strftime(QUERY_TIME_FMT)})
    if function_id:
        use_case_info_list = UseCaseAPI.get_use_case(function_id=function_id)
        use_case_list = [use_case_info.get('id') for use_case_info in use_case_info_list]
        param_kwarg['use_case_id'] = use_case_list
    if use_case_name:
        use_case_info_list = UseCaseAPI.get_use_case_by_name(use_case_name)
        use_case_list = [use_case_info.get('id') for use_case_info in use_case_info_list]
        param_kwarg['use_case_id'] = use_case_list

    result = RunLogAPI.get_use_case_run_log_count(**param_kwarg)
    return jsonify({'success': True, 'res': result})


@app.route('/run_log/use_case/info', methods=['POST'])
@login_required
@try_except
def get_use_case_run_log():
    """
    :return:
    """
    from_time = request.get_json().get('from_time', None)
    to_time = request.get_json().get('to_time', None)
    function_id = request.get_json().get('function_id', None)
    use_case_name = request.get_json().get('use_case_name', None)
    if from_time:
        from_time = shanghai_to_utc_timezone(datetime.strptime(from_time, QUERY_TIME_FMT))
        request.get_json().update({"from_time": from_time.strftime(QUERY_TIME_FMT)})
    if to_time:
        to_time = shanghai_to_utc_timezone(datetime.strptime(to_time, QUERY_TIME_FMT))
        request.get_json().update({"to_time": to_time.strftime(QUERY_TIME_FMT)})

    if function_id:
        use_case_info_list = UseCaseAPI.get_use_case(function_id=function_id)
        use_case_list = [use_case_info.get('id') for use_case_info in use_case_info_list]
        request.get_json()['use_case_id'] = use_case_list
    if use_case_name:
        use_case_info_list = UseCaseAPI.get_use_case_by_name(use_case_name)
        use_case_list = [use_case_info.get('id') for use_case_info in use_case_info_list]
        request.get_json()['use_case_id'] = use_case_list

    '' if 'pageIndex' in request.get_json() else request.get_json().update({'pageIndex': 1})
    '' if 'pageSize' in request.get_json() else request.get_json().update({'pageSize': 10})

    result = RunLogAPI.get_use_case_run_log(**request.get_json())
    use_case_id_list = [info['use_case_id'] for info in result]
    use_case_info_dict = UseCaseAPI.get_multi_use_case(use_case_id_list)
    for use_case_run_log_dict in result:
        use_case_id = use_case_run_log_dict.get('use_case_id')
        use_case_info = use_case_info_dict[use_case_id]
        use_case_name = use_case_info.get('use_case_name')
        use_case_run_log_dict.update({'use_case_name': use_case_name})
        start_time = utc_to_shanghai_timezone(use_case_run_log_dict.get('start_time'))
        end_time = utc_to_shanghai_timezone(use_case_run_log_dict.get('end_time'))
        use_case_run_log_dict.update({'start_time': datetime.strftime(start_time, QUERY_TIME_FMT)})
        if end_time:
            use_case_run_log_dict.update({'end_time': datetime.strftime(end_time, QUERY_TIME_FMT)})
        else:
            use_case_run_log_dict.update({'end_time': datetime.strftime(start_time, QUERY_TIME_FMT)})
    return jsonify({'success': True, 'res': result})


@app.route('/run_log/use_case/add', methods=['POST'])
@login_required
@try_except
def add_interface_run_log():
    """
    :return:
    """
    RunLogAPI.add_interface_run_log(**request.get_json())
    return jsonify({'success': True})


@app.route('/run_log/interface/info', methods=['POST'])
@login_required
@try_except
def get_interface_run_log():
    """
    :param: 必须需要传入use_case_run_log_id
    :return:
    """
    from_time = request.get_json().get('from_time', None)
    to_time = request.get_json().get('to_time', None)
    if from_time:
        from_time = shanghai_to_utc_timezone(datetime.strptime(from_time, QUERY_TIME_FMT))
        request.get_json().update({"from_time": from_time.strftime(QUERY_TIME_FMT)})
    if to_time:
        to_time = shanghai_to_utc_timezone(datetime.strptime(to_time, QUERY_TIME_FMT))
        request.get_json().update({"to_time": to_time.strftime(QUERY_TIME_FMT)})
    result = RunLogAPI.get_interface_run_log(**request.get_json())
    interface_id_list = [info['interface_id'] for info in result]
    interface_dict = InterfaceAPI.query_multi_interface(interface_id_list)
    for interface_run_log_dict in result:
        interface_id = interface_run_log_dict.get('interface_id')
        interface_info = interface_dict[interface_id]
        interface_name = interface_info.get('interface_name')
        interface_run_log_dict.update({'interface_name': interface_name})
        start_time = utc_to_shanghai_timezone(interface_run_log_dict.get('start_time'))
        end_time = utc_to_shanghai_timezone(interface_run_log_dict.get('end_time'))
        interface_run_log_dict.update({'start_time': datetime.strftime(start_time, QUERY_TIME_FMT)})
        if end_time:
            interface_run_log_dict.update({'end_time': datetime.strftime(end_time, QUERY_TIME_FMT)})
    return jsonify({'success': True, 'res': result})
