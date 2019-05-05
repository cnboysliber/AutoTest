# -*- coding: utf-8 -*-
from flask import request, jsonify

from application import app
from application.api import interface as InterfaceAPI
from application.api import use_case as UseCaseAPI
from application.util.parameter import search_parameter
from application.util.exception import try_except
from application.controller import login_required, user_real_name, cur_user


@app.route('/interface/add', methods=['POST'])
@login_required
@try_except
def add_interface():
    """
    添加interface
    """
    interface_json = request.get_json()
    interface_json['create_by'] = user_real_name()
    result = InterfaceAPI.add_interface(**interface_json)
    return jsonify({'success': True, 'res': result})


@app.route('/interface/info', methods=['POST'])
@login_required
@try_except
def get_interface():
    """
    根据过滤规则获取interface列表, 无规则则返回所有interface
    """
    param_json = request.get_json()
    page_index = int(param_json.pop('pageIndex')) if 'pageIndex' in param_json else 1
    page_size = int(param_json.pop('pageSize')) if 'pageSize' in param_json else 10
    result = InterfaceAPI.get_interface(**param_json)
    if not (page_index and page_size):
        return jsonify({'success': True, 'res': result})
    return jsonify({'success': True, 'res': result[(page_index - 1) * page_size:page_index * page_size]})


@app.route('/interface/count', methods=['POST'])
@login_required
@try_except
def query_interface_count():
    """
    获取数据库中所有interface的总个数
    """
    result = InterfaceAPI.query_interface_count(**request.get_json())
    return jsonify({'success': True, 'res': result})


@app.route('/interface/update', methods=['POST'])
@login_required
@try_except
def modify_interface():
    """
    更新interface信息
    1. 获取原interface参数信息
    2. 将更新的interface内容写入数据库
    3. 如果新旧参数无区别, 结束并返回
    4. 如果新旧参数有区别, 更新所有use_case传给此interface的参数记录
    """
    interface_id = request.get_json().get('id')
    interface_old_info = InterfaceAPI.get_interface(id=interface_id)[0]
    InterfaceAPI.modify_interface(**request.get_json())
    interface_new_info = InterfaceAPI.get_interface(id=interface_id)[0]
    relation_list = UseCaseAPI.get_relation(interface_id=interface_id)
    old_analysis_str = ''.join([interface_old_info.get('interface_header'),
                                interface_old_info.get('interface_json_payload'),
                                interface_old_info.get('interface_url')])
    new_analysis_str = ''.join([interface_new_info.get('interface_header'),
                                interface_new_info.get('interface_json_payload'),
                                interface_new_info.get('interface_url')])
    old_param_list = search_parameter(old_analysis_str)
    new_param_list = search_parameter(new_analysis_str)
    update_param_list = list(set(old_param_list) ^ set(new_param_list))
    if len(update_param_list) == 0:
        return jsonify({'success': True})
    else:
        for param in update_param_list:
            if '==' in param:
                parameter_value = param.split('==')[1]
                parameter_name = param.split('==')[0]
            else:
                parameter_value = ''
                parameter_name = param
            if param in old_param_list:
                for p_relation in relation_list:
                    UseCaseAPI.del_case_parameter_relation(parameter_name=parameter_name, relation_id=p_relation['id'])
            else:  # 新增参数添加到各个用例中去
                for relation in relation_list:
                    kwargs = {'relation_id': relation['id'],
                              'parameter_name': parameter_name,
                              'parameter_value': parameter_value}
                    UseCaseAPI.add_case_parameter_relation(**kwargs)
    return jsonify({'success': True})


@app.route('/interface/delete', methods=['POST'])
@login_required
@try_except
def delete_interface():
    """
    删除某个interface
    1. 将interface数据从数据库中标记为已删除
    2. 将所有use_case与此interface的关联关系标记为已删除
    3. 将所有use_case传给此interface的参数记录标记为已删除
    """
    user_id = cur_user()
    interface_id = request.get_json().get('id')
    relation_list = UseCaseAPI.get_relation(interface_id=interface_id)
    if relation_list and user_id not in app.config['SUPER_MANAGER']:
        return jsonify({'success': False, 'error': '存在关联用例, 需解除关联用例（或者管理员）删除'})
    for interface_relation in relation_list:
        parameter_info = UseCaseAPI.get_case_parameter_relation(id=interface_relation['id'])
        for s_prama_relation in parameter_info:
            UseCaseAPI.del_case_parameter_relation(id=s_prama_relation['id'])
        UseCaseAPI.del_relation(interface_relation['id'])
    InterfaceAPI.del_interface(**request.get_json())
    return jsonify({'success': True})
