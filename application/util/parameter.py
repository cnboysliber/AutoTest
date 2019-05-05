import re
import random
from application.util.encryption import calc_md5


def search_parameter(input_string):
    """
    在给定字符串中查找被 ${} 包裹的所有参数, 并以列表返回
    :param input_string:        给定用来搜索参数的字符串
    :return:                    参数列表
    """
    pattern = re.compile(r'\${[^${}]*}')
    match_result = pattern.findall(input_string)
    param_list = []
    for item in match_result:
        param_list.append(item.replace('${', '').replace('}', ''))
    return param_list


def random_length_seq(input_string):
    """

    :param input_string:
    :return:
    """
    digits = '0123456789'
    str_letters = 'abcdefghigklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
    param_pattern = re.compile(r'\(([^${}]*)\)')
    param = param_pattern.findall(input_string)[0].split(',')
    start_str = ''
    if 'str' in input_string and param[1]:
        param_length = param[1]
        random_str = digits + str_letters
        if len(param) == 3:
            start_str = param[-1].strip().strip("'").strip("\"")
    else:
        if 'int' != param[0]:
            param_length = param[0]
        else:
            param_length = param[1]
        random_str = digits
        if len(param) == 2:
            start_str = param[-1].strip().strip("'").strip("\"")
    if len(start_str) > int(param_length):
        return start_str
    return ''.join([start_str] + [random.choice(random_str) for _ in range(int(param_length)-len(start_str))])


def param_2_md5(input_string):
    """
    输入字符MD5加密
    :param input_string:
    :return:
    """
    param_pattern = re.compile(r'\$md5\(([^${}]*)\)')
    param = param_pattern.findall(input_string)[0].split(',')
    return calc_md5(param[0]).lower()


