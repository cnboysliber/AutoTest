# -*- coding:utf-8 -*-
from flask import request, jsonify
from application import app
from application.util.exception import try_except
from application.controller import login_required
from application.util import git_option as gitAPI


@app.route('/git/create_tag', methods=['POST'])
@login_required
@try_except
def create_tag():
    """
    功能描述: 创建一个tag
    :return:
    """
    soft_name = request.get_json()['soft_name']
    work_path = request.get_json()['work_path']
    if not (soft_name or work_path):
        return jsonify({'success': False, 'res': '参数错误'})
    tag = gitAPI.create_tag(soft_name, work_path)
    if not tag:
        return jsonify({'success': False, 'res': '创建tag失败'})
    return jsonify({'success': True, 'res': tag})


@app.route('/git/delete_tag', methods=['POST'])
@login_required
@try_except
def delete_tag():
    """
    功能描述: 删除一个tag
    :param: work_path Repo的绝对路径
    :return:
    """
    tag_name = request.get_json()['tag_name']
    work_path = request.get_json()['work_path']
    if not (tag_name or work_path):
        return jsonify({'success': False, 'res': '参数错误'})
    tag = gitAPI.delete_tag(work_path, tag_name)
    if not tag:
        return jsonify({'success': False, 'res': '删除tag失败'})
    return jsonify({'success': True, 'res': '删除tag[%s]成功' % tag_name})


@app.route('/git/update', methods=['POST'])
@login_required
@try_except
def update_file():
    """
    功能描述: 更新文件内容并提交
    src 替换的原字符串
    dst 目的字符串
    file_path 文件的绝对路劲
    :return:
    """
    src = request.get_json().get('src', None)
    dst = request.get_json().get('dst', None)
    file_path = request.get_json().get('file_path', None)
    repo_path = request.get_json().get('repo_path', None)
    if not (file_path and repo_path):
        return jsonify({'success': False, 'res': '参数错误'})
    ret = gitAPI.update_repo_file(repo_path, file_path, src, dst)
    if not ret:
        return jsonify({'success': False, 'res': '更新文件失败'})
    return jsonify({'success': True, 'res': '更新成功'})





