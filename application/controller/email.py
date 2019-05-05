# -*- coding:utf-8 -*-
from flask import request, jsonify

from application import app
from application.controller import login_required, localhost_required
from application.util.exception import try_except
from application.api import email as EmailAPI
from application.util import scheduler as schd


@app.route('/email/send', methods=['GET'])
@try_except
@localhost_required
def email_send():
    """
    发送email到指定邮箱
    :return:
    #TODO: 发送邮件时发件人设置，等邮件系统改好后添加
    """

    ret = schd.send_report_to_email()
    if ret:
        return jsonify({'success': True})
    else:
        return jsonify({'success': False, 'res': '发送失败:{}'.format(ret[-1])})


@app.route('/email/account/add', methods=['POST'])
@login_required
@try_except
def email_account_add():
    """
    添加要发送的邮箱地址
    :return:
    """
    kwarg = request.get_json()
    if not (kwarg.get('email_name') and kwarg.get('email_address')):
        return jsonify({'success': False, 'error': '用户名或地址不能为空'})
    elif '@' not in kwarg.get('email_address'):
        return jsonify({'success': False, 'error': '邮箱格式错误请正确填写（template@huishoubao.com.cn）'})
    else:
        EmailAPI.add_email_account(**request.get_json())
        return jsonify({'success': True})


@app.route('/email/account/delete', methods=['POST'])
@login_required
@try_except
def email_account_delete():
    """
    删除指定的邮箱地址
    :return:
    """
    EmailAPI.del_email_account(**request.get_json())
    return jsonify({'success': True})


@app.route('/email/account/info', methods=['POST'])
@login_required
@try_except
def email_account_info():
    """
    查询邮箱地址
    :return:
    """
    result = EmailAPI.query_email_account()
    return jsonify({'success': True, 'res': result})


@app.route('/email/account/update', methods=['POST'])
@login_required
@try_except
def email_account_update():
    """
    查询邮箱信息更新
    :return:
    """
    kv = request.get_json(force=True)
    result = EmailAPI.update_email_account(**kv)
    return jsonify({'success': True, 'res': result})


@app.route('/email/relation/get_function', methods=['POST'])
@login_required
@try_except
def email_function_relation():
    """

    :return:
    """
    kv = request.get_json(force=True)
    result = EmailAPI.get_function_id_by_email_id(kv['email_id'])
    return jsonify({'success': True, 'res': result})


@app.route('/email/relation/add', methods=['POST'])
@login_required
@try_except
def email_relation_add():
    """
    关联ft和邮箱账号
    :return:
    """
    kv = request.get_json(force=True)
    result = EmailAPI.add_email_function(**kv)
    return jsonify({'success': True, 'res': result})


@app.route('/email/relation/delete', methods=['POST'])
@login_required
@try_except
def email_relation_delete():
    """
    关联ft和邮箱账号
    :return:
    """
    kv = request.get_json(force=True)
    result = EmailAPI.del_email_function_relation(kv['email_id'], kv['function_id'])
    return jsonify({'success': True, 'res': result})


@app.route('/email/relation/get_batch', methods=['POST'])
@login_required
@try_except
def email_batch_relation():
    """
    获取邮箱关联的批次信息
    :return:
    """
    kv = request.get_json(force=True)
    result = EmailAPI.get_batch_id_by_email_id(kv['email_id'])
    return jsonify({'success': True, 'res': result})


@app.route('/email/relation/batch/add', methods=['POST'])
@login_required
@try_except
def email_batch_relation_add():
    """
    关联batch和邮箱账号
    :return:
    """
    kv = request.get_json(force=True)
    print(kv)
    result = EmailAPI.add_email_batch(**kv)
    return jsonify({'success': True, 'res': result})


@app.route('/email/relation/batch/delete', methods=['POST'])
@login_required
@try_except
def email_batch_relation_delete():
    """
    解关联batch和邮箱账号
    :return:
    """
    kv = request.get_json(force=True)
    result = EmailAPI.delete_email_batch(**kv)
    return jsonify({'success': True, 'res': result})
