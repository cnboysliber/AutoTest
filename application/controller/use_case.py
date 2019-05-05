# -*- coding:utf-8 -*-
from flask import request, jsonify

from application import app
from application.api import interface as InterfaceAPI
from application.api import use_case as Case_API
from application.util.parameter import *
from application.util import execute_test as Exec
from application.util.exception import try_except
from application.controller import login_required, user_real_name

"""
用例

"""


@app.route('/use_case/add', methods=['POST'])
@login_required
@try_except
def add_use_case():
    """
    功能描述: 添加use_case，只包含用例基础信息
    :return:
    """
    use_case_json = request.get_json(force=True)
    use_case_json['create_by'] = user_real_name()
    use_case_id = Case_API.add_use_case(**use_case_json)
    return jsonify({'success': True, 'res': use_case_id})


@app.route('/use_case/list', methods=['POST'])
@login_required
@try_except
def use_case_list():
    """
    获取use_case列表，不需要获取与use_case关联的interface
    :return:
    """
    param_json = request.get_json(force=True)
    page_index = int(param_json.pop('pageIndex')) if 'pageIndex' in param_json else 1
    page_size = int(param_json.pop('pageSize')) if 'pageSize' in param_json else 10
    result = Case_API.get_use_case(**param_json)
    if page_size == 0:
        return jsonify({'success': True, 'res': result})
    if not(page_index and page_size):
        return jsonify({'success': True, 'res': result})
    return jsonify({'success': True, 'res': result[(page_index - 1) * page_size:page_index * page_size]})


@app.route('/use_case/count', methods=['GET'])
@login_required
@try_except
def use_case_count():
    """
    获取use_case的总个数
    :return:
    """
    result = Case_API.query_use_case_count()
    return jsonify({'success': True, 'res': result})


@app.route('/use_case/detail', methods=['POST'])
@login_required
@try_except
def use_case_detail():
    """
    功能描述: 获取某个use_case的详细信息，包括其包含的interface列表
    1. 根据use_case_id获取use_case基本信息
    2. 根据use_case_id获取use_case与interface的关联信息
    3. 根据关联信息的id查出所有interface的名称信息以及定义的参数信息
    4. 信息整理并返回
    :return:
    """
    use_case_info = Case_API.get_use_case(**request.get_json(force=True))[0]
    use_case_info.update({'interface_list': []})
    relation_interface_list = Case_API.get_relation(use_case_id=use_case_info.get('id'))
    for relation_interface in relation_interface_list:
        relation_interface.pop('use_case_id')
        relation_interface.pop('create_time')
        relation_interface.pop('update_time')
        interface_id = relation_interface.get('interface_id')
        interface_list = InterfaceAPI.get_interface(id=interface_id)
        relation_interface.update({'interface_name': interface_list[0].get('interface_name')})
        para_list = Case_API.get_case_parameter_relation(relation_id=relation_interface['id'])
        relation_interface.update({'param_list': para_list})
        use_case_info['interface_list'].append(relation_interface)
    return jsonify({'success': True, 'res': use_case_info})


@app.route('/use_case/update', methods=['POST'])
@login_required
@try_except
def update_use_case():
    """
    功能描述: 更新use_case内容，不更新与interface的关联
    :return:
    """
    use_case_id = Case_API.modify_use_case(**request.get_json(force=True))
    return jsonify({'success': True, 'res': use_case_id})


@app.route('/use_case/delete', methods=['POST'])
@login_required
@try_except
def del_use_case():
    """
    功能描述: 删除use_case
    :return:
    """

    Case_API.del_use_case(**request.get_json(force=True))
    return jsonify({'success': True})


@app.route('/use_case/execute', methods=['POST'])
@login_required
@try_except
def execute_use_case():
    """
    手动执行某个use_case, 前端等待执行完成返回
    :return:
    """
    use_case_id = request.get_json(force=True)['id']
    environment_id = request.get_json(force=True).get('environment_id', None)
    relation_id = request.get_json(force=True).get('relation_id', None)
    result = Exec.run_use_case(use_case_id, environment_id=environment_id, relation_id=relation_id)
    if 'error' in result:
        return jsonify(result)
    return jsonify({'success': True, 'res': result})


@app.route('/use_case/execute/background', methods=['POST'])
@login_required
@try_except
def execute_use_case_background():
    """
    手动后台运行某个use_case, 不等待直接返回, 需要查看日志确认运行结果
    :return:
    """
    use_case_id = request.get_json(force=True)['id']
    environment_id = request.get_json(force=True)['environment_id']
    Exec.run_use_case_async(use_case_id, environment_id=environment_id)
    return jsonify({'success': True})


@app.route('/use_case/relation/add', methods=['POST'])
@login_required
@try_except
def add_relation():
    """
    功能描述: 将某个interface与某个use_case关联
    1. 关联use_case与interface
    2. 查找interface内parameter信息, 用空值为每个参数在relation下生成记录
    :return:
    """
    param_dict = request.get_json(force=True)
    interface_list = param_dict.get('interface_id')
    if not isinstance(interface_list, list):
        interface_list = [interface_list]
    add_param_dict = {"use_case_id": param_dict.get("use_case_id"), "interface_id": ""}
    for interface_id in interface_list:
        if not interface_id:
            continue
        add_param_dict["interface_id"] = interface_id
        relation_id = Case_API.add_relation(**add_param_dict)
        interface_list = InterfaceAPI.get_interface(id=interface_id)
        the_interface = interface_list[0]
        analysis_str = ''.join([the_interface.get('interface_header'),
                                the_interface.get('interface_json_payload'),
                                the_interface.get('interface_url')])
        param_list = search_parameter(analysis_str)
        for para in param_list:
            if '==' in para:
                parameter_value = para.split('==')[1]
                parameter_name = para.split('==')[0]
            else:
                parameter_value = ''
                parameter_name = para
            Case_API.add_case_parameter_relation(relation_id=relation_id, parameter_name=parameter_name,
                                                 parameter_value=parameter_value)
    return jsonify({'success': True})


@app.route('/use_case/copy/interface', methods=['POST'])
@login_required
@try_except
def use_case_copy_interface():
    """
    复制用例时同时复制用例接口和参数值
    :return:
    """
    param_dict = request.get_json(force=True)
    interface_list = param_dict.get('interface_list')
    if not isinstance(interface_list, list):
        interface_list = [interface_list]
    add_param_dict = {"use_case_id": param_dict.get("use_case_id"), "interface_id": ""}
    for interface in interface_list:
        if not interface['interface_id']:
            continue
        add_param_dict["interface_id"] = interface['interface_id']
        relation_id = Case_API.add_relation(**add_param_dict)
        param_list = interface['param_list']
        for para in param_list:
            parameter_value = para['parameter_value']
            parameter_name = para['parameter_name']
            Case_API.add_case_parameter_relation(relation_id=relation_id, parameter_name=parameter_name,
                                                 parameter_value=parameter_value)
    return jsonify({'success': True})


@app.route('/use_case/relation/update_eval', methods=['POST'])
@login_required
@try_except
def update_eval():
    """
    更新eval_string的值
    :return:
    """
    Case_API.update_eval_relation(**request.get_json(force=True))
    return jsonify({'success': True})


@app.route('/use_case/relation/delete', methods=['POST'])
@login_required
@try_except
def del_relation():
    """
    功能描述: 解除某个interface与use_case的关联
    :return:
    """
    id_to_delete = request.get_json(force=True)['id']
    Case_API.del_relation(id_to_delete)
    return jsonify({'success': True})


@app.route('/use_case/relation/reorder', methods=['POST'])
@login_required
@try_except
def reorder_relation():
    """
    功能描述: 重新排序某个interface在use_case中的顺序
    :return:
    """
    relation_id = request.get_json(force=True)['id']
    new_order = request.get_json(force=True)['new_order']
    Case_API.reorder_relation(relation_id, new_order)
    return jsonify({'success': True})


@app.route('/use_case/relation/update/interface_delay', methods=['POST'])
@login_required
@try_except
def modify_interface_delay_relation():
    """
    功能描述: 更新interface和use_case关系表中的interface_delay
    :return:
    """
    relation_id = request.get_json(force=True)['id']
    interface_delay = request.get_json(force=True)['interface_delay']
    Case_API.modify_interface_delay_relation(relation_id, interface_delay)
    return jsonify({'success': True})


@app.route('/use_case/relation/parameter/modify', methods=['POST'])
@login_required
@try_except
def relation_update_parameter():
    """
    功能描述: 更新某个use_case传给interface的参数的信息
    :return:
    """
    Case_API.modify_case_parameter_relation(**request.get_json(force=True))
    return jsonify({'success': True})
