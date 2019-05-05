# -*- coding:utf-8 -*-
from datetime import datetime
from application.config.default import *
from dateutil.rrule import rrule, DAILY
from functools import wraps
from flask import make_response
from application import app


# 处理日志模块对于分表和按时间查询参数的装饰器
@app.context_processor
def run_log_table_decorator(func):
    def wrapper(**kwargs):
        """
        对被装饰的函数的参数进行类型处理
        :param kwargs:
            from_time和to_time表示起止时间，table_name_fix_lst用于存储表格名称后缀
        :return:
        """
        fmt_str = (datetime.strftime(datetime.utcnow(), QUERY_TIME_FMT))
        if not('from_time' in kwargs or 'to_time' in kwargs):
            kwargs.update({'table_name_fix_lst': [fmt_str[:CONSTANT_LEN]]})
        else:
            from_time = kwargs.get('from_time').strip() if kwargs.get('from_time', None) else None
            to_time = kwargs.get('to_time').strip() if kwargs.get('to_time', None) else fmt_str.strip()
            table_to_time = to_time[:CONSTANT_LEN]
            if not from_time:
                table_from_time = table_to_time
            else:
                table_from_time = from_time[:CONSTANT_LEN]
            dt_table_from_time, dt_table_to_time = multi_strptime(table_from_time, table_to_time,
                                                                  str_format=TABLE_TIME_FMT)
            table_name_fix_lst = [dt.strftime(TABLE_TIME_FMT) for dt in rrule(DAILY,
                                                                              dtstart=dt_table_from_time,
                                                                              until=dt_table_to_time)]
            dt_from_time, dt_to_time = multi_strptime(from_time, to_time)
            kwargs.update({
                'table_name_fix_lst': table_name_fix_lst,
                'from_time': dt_from_time,
                'to_time': dt_to_time
            })
        return func(**kwargs)
    return wrapper


# 批量把字符串格式生成datetime格式
def multi_strptime(*args, str_format=QUERY_TIME_FMT):
    dt_time = []
    for dt_arg in args:
        if dt_arg is None:
            dt_time.append(None)
            continue
        dt_time.append(datetime.strptime(dt_arg, str_format))
    return tuple(dt_time)


# 去掉浏览器缓存装饰器
def no_cache(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        response = make_response(func(*args, **kwargs))
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        return response
    return wrapper


def report_table_decorator(func):
    @wraps(func)
    def wrapper(**kwargs):
        fmt_str = (datetime.strftime(datetime.utcnow(), TABLE_FMT))
        kwargs.update({'table_name': [fmt_str]})  # 按年分表
        return func(**kwargs)
    return wrapper













