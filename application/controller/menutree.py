# -*- coding: utf-8 -*-
from flask import request, jsonify

from application import app
from application.api import menutree as MenuTreeAPI
from application.api import use_case as Case_API
from application.util.exception import try_except
from application.controller import login_required


@app.route('/menu_tree/business_line/add', methods=['POST'])
@login_required
@try_except
def create_business_line():
    """
    查询所有系统菜单
    :return:
    """
    result = MenuTreeAPI.add_business_line(**request.get_json())
    return jsonify({'success': True, 'res': result})


@app.route('/menu_tree/business_line/delete', methods=['POST'])
@login_required
@try_except
def del_business_line():
    """
    删除指定系统菜单
    :return:
    :param: id 或list
    """
    result = MenuTreeAPI.del_business_line(**request.get_json())
    return jsonify({'success': True, 'res': result})


@app.route('/menu_tree/system_line/add', methods=['POST'])
@login_required
@try_except
def create_system_line():
    """
    查询所有系统菜单
    :return:
    """
    result = MenuTreeAPI.add_system_line(**request.get_json())
    return jsonify({'success': True, 'res': result})


@app.route('/menu_tree/system_line/delete', methods=['POST'])
@login_required
@try_except
def del_system_line():
    """
    查询所有系统菜单
    :return:
    :param: id 或list
    """
    result = MenuTreeAPI.del_system_line(**request.get_json())
    return jsonify({'success': True, 'res': result})


@app.route('/menu_tree/function_line/add', methods=['POST'])
@login_required
@try_except
def create_function_line():
    """
    查询所有系统菜单
    :return:
    :param: id 或list
    """
    result = MenuTreeAPI.add_function_line(**request.get_json())
    return jsonify({'success': True, 'res': result})


@app.route('/menu_tree/function_line/delete', methods=['POST'])
@login_required
@try_except
def del_function_line():
    """
    查询所有系统菜单
    :return:
    """
    result = MenuTreeAPI.del_function_line(**request.get_json())
    return jsonify({'success': True, 'res': result})


@app.route('/menu_tree/system_line/info', methods=['POST'])
@login_required
@try_except
def get_system_line():
    """
    查询所有系统菜单
    :return:
    """
    param_args = request.get_json()
    id = param_args.get('id')
    system_line_id = param_args.get('business_line_id')
    param_args.pop('business_line_id') if 'business_line_id' in param_args and system_line_id is None else None
    param_args.pop('id') if 'id' in param_args and id is None else None
    result = MenuTreeAPI.query_system_line(**request.get_json())
    return jsonify({'success': True, 'res': result})


@app.route('/menu_tree/business_line/info', methods=['POST'])
@login_required
@try_except
def get_business_line():
    """
    查询所有业务菜单
    :return:
    """
    result = MenuTreeAPI.query_business_line(**request.get_json())
    return jsonify({'success': True, 'res': result})


@app.route('/menu_tree/function_line/info', methods=['POST'])
@login_required
@try_except
def get_function_line():
    """
    查询所有功能模块菜单
    :return:
    """
    param_args = request.get_json()
    id = param_args.get('id')
    system_line_id = param_args.get('system_line_id')
    param_args.pop('system_line_id') if 'system_line_id' in param_args and system_line_id is None else None
    param_args.pop('id') if 'id' in param_args and id is None else None
    result = MenuTreeAPI.query_line_relation(**param_args)
    return jsonify({'success': True, 'res': result})


@app.route('/menu_tree/info', methods=['POST'])
@login_required
@try_except
def get_menu_tree():
    """
    查询所有菜单
    :return:
    """
    re_system = MenuTreeAPI.query_system_line(**request.get_json())
    re_business = MenuTreeAPI.query_business_line(**request.get_json())
    re_function = MenuTreeAPI.query_function_line(**request.get_json())
    use_case_info_list = Case_API.get_use_case_with_function_id(re_function)
    for function_line in re_function:
        function_id = function_line.get('id')
        function_line['use_case_list'] = use_case_info_list[function_id]
    system_line_dict = {}
    for function_line in re_function:
        system_line_id = function_line.get('system_line_id')
        if not system_line_dict.get(system_line_id, None):
            system_line_dict[system_line_id] = [function_line]
        else:
            system_line_dict[system_line_id].append(function_line)

    business_line_info = {}
    for sys_line in re_system:
        business_line_id = sys_line.get('business_line_id')
        system_line_id = sys_line.pop('id')
        function_line = system_line_dict.get(system_line_id, [])
        sys_line['function_line'] = function_line
        if not business_line_info.get(business_line_id, None):
            business_line_info[business_line_id] = [sys_line]
        else:
            business_line_info[business_line_id].append(sys_line)
    menu_tree = []
    for business_line in re_business:
        business_line_id = business_line.get('id')
        business_line['business_name'] = business_line.pop('business_name')
        system_line = business_line_info.get(business_line_id, [])
        business_line['system_line'] = system_line
        menu_tree.append({'business_line': business_line})
    return jsonify({'success': True, 'res': menu_tree})


@app.route('/menu_tree/use_case/count', methods=['POST'])
@login_required
@try_except
def get_use_case_count_from_function_id():
    """
    查询功能模块用例个数
    :param:function_id
    :return:
    """
    result = Case_API.query_use_case_count(**request.get_json())
    return jsonify({'success': True, 'res': result})


@app.route('/menu_tree/use_case/add', methods=['POST'])
@login_required
@try_except
def add_use_case_to_menu_tree():
    """
    创建用例的菜单
    :param:function_id
    :return:
    """
    param_args = request.get_json()
    business_id = int(param_args.get('business_id')) if param_args.get('business_id') else 0
    system_id = int(param_args.get('system_id')) if param_args.get('system_id') else 0
    function_id = int(param_args.get('function_id')) if param_args.get('function_id') else 0
    if not(param_args.get("business_name") or param_args.get("system_name") or param_args.get("system_name")):
        return jsonify({'success': False, 'error': '目录不能为空'})
    if not business_id:
        business_name = MenuTreeAPI.query_business_line(**{"business_name": param_args.get("business_name")})
        if business_name:
            return jsonify({'success': False, 'error': '已存在同名业务线目录'})
        business_id = MenuTreeAPI.add_business_line(**{"business_name": param_args.get("business_name")})
    if not system_id:
        system_name = MenuTreeAPI.query_system_line(**{"system_name": param_args.get("system_name"),
                                                       'business_line_id': business_id})
        if system_name:
            return jsonify({'success': False, 'error': '已存在同名系统线目录'})
        system_id = MenuTreeAPI.add_system_line(**{
            "system_name": param_args.get("system_name"),
            "business_line_id": business_id
        })
    if not function_id:
        function_id = MenuTreeAPI.add_function_line(**{
            "function_name": param_args.get("function_name"),
            "system_line_id": system_id
        })
    param_args.update({
        "business_id": business_id,
        "system_id": system_id,
        "function_id": function_id
    })
    return jsonify({'success': True, 'res': param_args})

