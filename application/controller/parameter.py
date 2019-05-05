# -*- coding: utf-8 -*-
from flask import request, jsonify

from application import app
from application.api import parameter as ParameterAPI
from application.util.exception import try_except
from application.controller import login_required, user_real_name


@app.route('/parameter/add', methods=['POST'])
@login_required
@try_except
def add_parameter():
    """
    添加parameter
    """
    parameter_json = request.get_json()
    parameter_name = parameter_json['parameter_name']
    if len(ParameterAPI.get_parameter(parameter_name=parameter_name)) > 0:
        return jsonify({'success': False, 'error': '重复的parameter名'})
    parameter_json['create_by'] = user_real_name()
    parameter_id = ParameterAPI.add_parameter(**parameter_json)
    return jsonify({'success': True, 'res': parameter_id})


@app.route('/parameter/info', methods=['POST'])
@login_required
@try_except
def parameter_info():
    """
    获取parameter列表
    :param
        pageIndex, 需要第几页
        pageSize, 页面显示个数
    :return
    """
    param_json = request.get_json()
    page_index = int(param_json.pop('pageIndex')) if 'pageIndex' in param_json else 1
    page_size = int(param_json.pop('pageSize')) if 'pageSize' in param_json else 10
    result = ParameterAPI.get_parameter(**param_json)
    return jsonify({'success': True, 'res': result[(page_index - 1) * page_size:page_index * page_size]})


@app.route('/parameter/count', methods=['GET'])
@login_required
@try_except
def parameter_count():
    """
    获取parameter总个数
    """
    result = ParameterAPI.query_parameter_count()
    return jsonify({'success': True, 'res': result})


@app.route('/parameter/update', methods=['POST'])
@login_required
@try_except
def update_parameter():
    """
    修改parameter
    """
    parameter_id = ParameterAPI.modify_parameter(**request.get_json())
    return jsonify({'success': True, 'res': parameter_id})


@app.route('/parameter/delete', methods=['POST'])
@login_required
@try_except
def delete_parameter():
    """
    删除parameter
    """
    ParameterAPI.del_parameter(**request.get_json())
    return jsonify({'success': True})
