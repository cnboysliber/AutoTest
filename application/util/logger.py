import socket

from datetime import datetime

from application.util import hsbpythonlog as LOGGER


# log内容
LOG_FORMAT_STRING = '{0}|{1}|{2}|{3}|{4}|{5}|{6}|{7}|{8}'

# 所在节点ID
HOSTNAME = socket.gethostname()

LOGGER.log_initialize("InspectSys", False)


def request_log(target_name, target_id, interface, code, cost_time):
    """
    常规上报（调用成功或错误或超时均上报，内部错误不上报）
    全部传入param都为string
    :param target_name:             被调方ID, 目标服务名
    :param target_id:               被调方节点ID, 暂时用目标服务名
    :param interface:               方法ID, 接口名
    :param code:                    返回码, 0表示成功，非0失败
    :param cost_time:               耗时, 单位毫秒
    :return:
    """
    url_param_string = LOG_FORMAT_STRING.format(
        '1',
        datetime.now().strftime('%Y%m%d'),
        'InspectSys',
        HOSTNAME,
        target_name,
        target_id,
        interface,
        code,
        cost_time
    )
    LOGGER.log_report(url_param_string)


def exception_log(error_str):
    """
    记录error log
    :param error_str:               异常内容
    :return:
    """
    LOGGER.log_error(error_str)


def info_log(info_str):
    """
        记录info log
        :param info_str:               记录内容
        :return:
        """
    LOGGER.log_info(str(info_str))
