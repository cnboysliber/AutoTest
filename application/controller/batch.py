# -*- coding:utf-8 -*-
import os
from flask import request, jsonify

from application import app
from application.api import batch as BatchAPI
from application.api import use_case as UseCaseAPI
from application.api import menutree as MenuTreeAPI
from application.util import execute_test as Exec
from application.util.exception import try_except
from application.controller import login_required, user_real_name, localhost_required


@app.route('/batch/add', methods=['POST'])
@login_required
@try_except
def add_batch():
    """
    create batch for use case
    :return:
    """
    batch_json = request.get_json()
    batch_json['create_by'] = user_real_name()
    batch_id = BatchAPI.add_batch(**batch_json)
    return jsonify({'success': True, 'res': batch_id})


@app.route('/batch/info', methods=['POST'])
@login_required
@try_except
def get_batch():
    """
    query batch of use case
    :return:
    """
    param_json = request.get_json()
    page_index = int(param_json.pop('pageIndex')) if 'pageIndex' in param_json else 1
    page_size = int(param_json.pop('pageSize')) if 'pageSize' in param_json else 10
    result = BatchAPI.get_batch(**param_json)
    return jsonify({'success': True, 'res': result[(page_index - 1) * page_size:page_index * page_size]})


@app.route('/batch/all', methods=['POST'])
@login_required
@try_except
def get_all_batch():
    """
    query batch of use case
    :return:
    """
    param_json = request.get_json()
    result = BatchAPI.get_batch(**param_json)
    return jsonify({'success': True, 'res': result})


@app.route('/batch/detail', methods=['POST'])
@login_required
@try_except
def batch_detail():
    """

    :return:
    """
    batch = BatchAPI.get_batch(**request.get_json())[0]
    relation_list = BatchAPI.get_batch_use_case_relation(batch_id=batch['id'])
    batch['use_case_list'] = []
    for relation in relation_list:
        use_case = UseCaseAPI.get_use_case(id=relation['use_case_id'])[0]
        batch['use_case_list'].append({
            'id': relation['id'],
            'use_case_name': use_case['use_case_name'],
            'desc': use_case['desc']
        })
    return jsonify({'success': True, 'res': batch})


@app.route('/batch/count', methods=['GET'])
@login_required
@try_except
def query_batch_count():
    """
    query batch count of use case
    :return:
    """
    result = BatchAPI.query_batch_count()
    return jsonify({'success': True, 'res': result})


@app.route('/batch/update', methods=['POST'])
@login_required
@try_except
def modify_batch():
    """
    update batch for use case
    :return:
    """
    batch_id = BatchAPI.modify_batch(**request.get_json())
    return jsonify({'success': True, 'res': batch_id})


@app.route('/batch/delete', methods=['POST'])
@login_required
@try_except
def delete_batch():
    """
    删除用例批次，并解除批次关联的用例
    :return:
    """
    BatchAPI.del_batch(**request.get_json())
    return jsonify({'success': True})


@app.route('/batch/relation/add', methods=['POST'])
@login_required
@try_except
def add_batch_use_case_relation():
    """
    往某一个批次添加用例
    :return:
    """
    batch_id = request.get_json()['batch_id']
    use_case_list = request.get_json()['use_case_id']
    if not isinstance(use_case_list, list):
        use_case_list = [use_case_list]
    for use_case_id in use_case_list:
        if use_case_id:
            BatchAPI.add_batch_use_case_relation(batch_id, use_case_id)
    return jsonify({'success': True})


@app.route('/batch/relation/info', methods=['POST'])
@login_required
@try_except
def get_batch_use_case_relation():
    """
    查询某一个批次已添加的用例列表
    :return:{'success': True, 'res': relation_use_case_list}    """
    result = BatchAPI.get_batch_use_case_relation(**request.get_json())
    relation_use_case_id_list = [(res.get('use_case_id'), res.get('id')) for res in result]
    use_case_info_lst = []
    for relation_id_use_case_id_tuple in relation_use_case_id_list:
        use_case_info = UseCaseAPI.get_use_case(id=relation_id_use_case_id_tuple[0])[0]
        use_case_info.update({'id': relation_id_use_case_id_tuple[1]})
        use_case_info_lst.append(use_case_info)
    batch_use_case_relation_info = result[-1]
    batch_use_case_relation_info.pop('use_case_id')
    batch_use_case_relation_info.pop('id')
    batch_use_case_relation_info.update({'use_case_info': use_case_info_lst})
    return jsonify({'success': True, 'res': batch_use_case_relation_info})


@app.route('/batch/relation/delete', methods=['POST'])
@login_required
@try_except
def del_batch_use_case_relation():
    """
    删除某一个批次已添加的用例列表
    :return:{'success': True, 'res': relation_use_case_list}
    """
    relation_id = request.get_json()['id']
    BatchAPI.del_batch_use_case_relation(relation_id)
    return jsonify({'success': True})


@app.route('/batch/execute', methods=['POST'])
@login_required
@try_except
def batch_execute():
    batch_id = request.get_json()['id']
    batch_info = BatchAPI.get_batch(id=batch_id)[0]
    Exec.run_batch(batch_id, batch_info['environment_id'])
    return jsonify({'success': True})


@app.route('/batch/auto_run')
@localhost_required
@try_except
def batch_auto_run():
    batch_list = BatchAPI.get_batch(auto_run=True)
    for batch in batch_list:
        Exec.run_batch(batch['id'], environment_id=batch['environment_id'], auto_run=True,
                       alarm_monitor=batch['alarm_monitor'])
    return jsonify({'success': True})


@app.route('/batch/search/use_case/list', methods=['POST'])
@login_required
@try_except
def batch_search_use_case_list():
    """
    获取use_case列表，不需要获取与use_case关联的interface
    :return:
    """
    param_json = request.get_json(force=True)
    result = UseCaseAPI.get_use_case(**param_json)
    function_info_dict = MenuTreeAPI.query_line_relation()
    for use_case_info in result:
        if use_case_info['function_id']:
            use_case_info.update(function_info_dict[use_case_info['function_id']])
        else:
            print(use_case_info)
    return jsonify({'success': True, 'res': result})
