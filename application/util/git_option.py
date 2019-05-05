# -*- coding:utf-8 -*-
import os
import re
from datetime import datetime
from application.util.parameter import search_parameter


def create_tag(soft_name, work_path):
    cur_wk_path = os.getcwd()
    os.chdir(work_path)
    work_path_cmd = 'cd %s' % work_path
    os.system('%s;git checkout master; git pull origin master' % work_path_cmd)
    tag_name = get_new_tag(work_path, soft_name)
    option_cmd = ';'.join([work_path_cmd, 'git pull origin master', 'git tag %s' % tag_name,
                           'git push origin %s' % tag_name])
    res = os.system(option_cmd)
    os.chdir(cur_wk_path)
    if res == 0:
        return tag_name
    return False


def delete_tag(work_path, tag_name):
    option_cmd = ';'.join(['cd %s' % work_path, 'git tag -d %s' % tag_name, 'git push origin --delete %s' % tag_name])
    res = os.system(option_cmd)
    if res == 0:
        return True
    return False


def get_all_tags(work_path):
    work_path_cmd = 'cd %s' % work_path
    show_tags_cmd = ';'.join([work_path_cmd, 'git tag'])
    tags_list = os.popen(show_tags_cmd).readlines()
    return tags_list


def get_new_tag(work_path, soft_name='AutoTest'):
    tag_list = get_all_tags(work_path)
    soft_tags_list = [tag.splitlines()[0] for tag in tag_list if '{0}-test-v'.format(soft_name) in tag]
    if not soft_tags_list:
        return '{0}-test-v0.0.1'.format(soft_name)

    major_pattern = re.compile(r'-test-v(\d).\d.\d')
    max_major_ver_num = max([major_pattern.findall(name)[0] for name in soft_tags_list if major_pattern.findall(name)])
    child_pattern = re.compile(r'-test-v%d.(\d).\d' % int(max_major_ver_num))
    max_child_ver_num = max([child_pattern.findall(name)[0] for name in soft_tags_list if child_pattern.findall(name)])
    phase_pattern = re.compile(r'-test-v%d.%d.(\d)' % (int(max_major_ver_num), int(max_child_ver_num)))
    max_phase_num = max([phase_pattern.findall(name)[0] for name in soft_tags_list if phase_pattern.findall(name)])
    if int(max_phase_num) < 9:
        new_tag_name = '{0}-test-v{1}.{2}.{3}'.format(soft_name, str(max_major_ver_num), str(max_child_ver_num),
                                                      str(int(max_phase_num)+1))
    elif int(max_child_ver_num) < 9:
        new_tag_name = '{0}-test-v{1}.{2}.0'.format(soft_name, str(max_major_ver_num), str(int(max_child_ver_num)+1))
    else:
        new_tag_name = '{0}-test-v{1}.0.0'.format(soft_name, str(int(max_major_ver_num)+1))
    return new_tag_name


def update_repo_file(repo_path, file_path, src=None, dst=None):
    """
    原字符串为空时，替换文件中${}包裹的字符串
    :param repo_path
    :param file_path:
    :param src:
    :param dst:
    :return:
    """
    push_cmd = 'cd %s; git pull' % repo_path
    ret = os.system(push_cmd)
    if ret != 0:
        return False
    if not dst:
        dst = datetime.now().strftime('%Y-%m-%D %H:%M:%S')
    with open(file_path, 'r') as fp:
        fdata = str(fp.read())
        if src:
            new_fdata = fdata.replace(src, dst)
        else:
            src_list = search_parameter(fdata)
            for src in src_list:
                fdata = fdata.replace(src, dst)
            new_fdata = fdata
    with open(file_path, 'w') as fp:
        fp.write(new_fdata)

    ret = git_push_remote(repo_path, file_path)
    if not ret:
        return False
    return True


def git_push_remote(repo_path, file_path, msg='AutoTest Commit to Remote'):
    commit_cmd = 'cd %s;git commit -m "%s" %s' % (repo_path, msg, file_path)
    if os.system(commit_cmd):
        return False
    push_cmd = 'cd %s;git push' % repo_path
    if os.system(push_cmd):
        return False
    return True


