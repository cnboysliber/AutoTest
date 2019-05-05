# -*- coding: utf-8 -*-
from sqlalchemy import func, select, desc
from application.util.decorator import *
from application.model.report import *


@report_table_decorator
def add_minutes_report(**kwargs):
    table = get_minutes_report_table(kwargs.pop('table_name')[0])
    sql = table.insert(kwargs)
    return exec_change(sql).inserted_primary_key[0]


@report_table_decorator
def add_day_report(**kwargs):
    table = get_day_report_table(kwargs.pop('table_name')[0])
    sql = table.insert(kwargs)
    return exec_change(sql).inserted_primary_key[0]


@report_table_decorator
def add_week_report(**kwargs):
    table = get_week_report_table(kwargs.pop('table_name')[0])
    sql = table.insert(kwargs)
    return exec_change(sql).inserted_primary_key[0]


@report_table_decorator
def add_month_report(**kwargs):
    table = get_month_report_table(kwargs.pop('table_name')[0])
    sql = table.insert(kwargs)
    return exec_change(sql).inserted_primary_key[0]


@report_table_decorator
def modify_day_report(**kwargs):
    table = get_day_report_table(kwargs.pop('table_name')[0])
    id = kwargs.pop('id')
    sql = table.update(table.c.id == id).values(**kwargs)
    return exec_change(sql)


@report_table_decorator
def modify_week_report(**kwargs):
    table = get_week_report_table(kwargs.pop('table_name')[0])
    id = kwargs.pop('id')
    sql = table.update(table.c.id == id).values(**kwargs)
    return exec_change(sql)


@report_table_decorator
def modify_month_report(**kwargs):
    table = get_month_report_table(kwargs.pop('table_name')[0])
    id = kwargs.pop('id')
    sql = table.update(table.c.id == id).values(**kwargs)
    return exec_change(sql)


@report_table_decorator
def get_minutes_report_info(**kwargs):
    table_name_fix_lst = kwargs.pop('table_name')
    function_id = kwargs.get('function_id')
    from_time = kwargs.get('from_time')
    to_time = kwargs.get('to_time')
    limit = kwargs.get('limit')
    ret = []
    for table_name in table_name_fix_lst[::-1]:
        table = get_minutes_report_table(table_name)
        sql = table.select()
        function_list = [function_id] if not isinstance(function_id, list) else function_id
        if len(table_name_fix_lst) == 1 and to_time:
            sql = sql.where(table.c.create_time.__le__(to_time))
            if from_time:
                sql = sql.where(table.c.create_time.__ge__(from_time))
        elif table_name == table_name_fix_lst[0] and from_time:
            sql = sql.where(table.c.create_time.__ge__(from_time))
        elif table_name == table_name_fix_lst[-1] and to_time:
            sql = sql.where(table.c.create_time.__le__(to_time))
        if function_id:
            sql = sql.where(table.c.function_id.in_(function_list)).order_by(desc(table.c.create_time))
        else:
            sql = sql.order_by(desc(table.c.create_time))

        if limit:
            sql.limit(limit)
        ret += exec_query(sql, is_list=True)
    return ret


@report_table_decorator
def get_day_report_info(**kwargs):
    table_name_fix_lst = kwargs.pop('table_name')
    function_id = kwargs.get('function_id')
    from_time = kwargs.get('from_time')
    to_time = kwargs.get('to_time')
    limit = kwargs.get('limit')
    ret = []
    for table_name in table_name_fix_lst:
        table = get_day_report_table(table_name)
        sql = table.select()
        function_id = [function_id] if function_id and not isinstance(function_id, list) else None
        if len(table_name_fix_lst) == 1 and to_time:
            sql = sql.where(table.c.create_time.__le__(to_time))
            if from_time:
                sql = sql.where(table.c.create_time.__ge__(from_time))
        elif table_name == table_name_fix_lst[0] and from_time:
            sql = sql.where(table.c.create_time.__ge__(from_time))
        elif table_name == table_name_fix_lst[-1] and to_time:
            sql = sql.where(table.c.create_time.__le__(to_time))

        if function_id:
            sql = sql.where(table.c.function_id.in_(function_id)).order_by(desc(table.c.create_time))
        else:
            sql = sql.order_by(desc(table.c.create_time))

        if limit:
            sql = sql.limit(limit)
        result = exec_query(sql, is_list=True)
        ret += result
    return ret


@report_table_decorator
def get_week_report_info(**kwargs):
    table_name_fix_lst = kwargs.pop('table_name')
    function_id = kwargs.get('function_id')
    from_time = kwargs.get('from_time')
    to_time = kwargs.get('to_time')
    limit = kwargs.get('limit')
    ret = []
    for table_name in table_name_fix_lst:
        table = get_week_report_table(table_name)
        sql = table.select()
        function_id = [function_id] if function_id and not isinstance(function_id, list) else None
        if len(table_name_fix_lst) == 1 and to_time:
            sql = sql.where(table.c.create_time.__le__(to_time))
            if from_time:
                sql = sql.where(table.c.create_time.__ge__(from_time))
        elif table_name == table_name_fix_lst[0] and from_time:
            sql = sql.where(table.c.create_time.__ge__(from_time))
        elif table_name == table_name_fix_lst[-1] and to_time:
            sql = sql.where(table.c.create_time.__le__(to_time))

        if function_id:
            sql = sql.where(table.c.function_id.in_(function_id)).order_by(desc(table.c.create_time))
        else:
            sql = sql.order_by(desc(table.c.create_time))

        if limit:
            sql = sql.limit(limit)
        result = exec_query(sql, is_list=True)
        ret += result
    return ret


@report_table_decorator
def get_month_report_info(**kwargs):
    table_name_fix_lst = kwargs.pop('table_name')
    function_id = kwargs.get('function_id')
    from_time = kwargs.get('from_time')
    to_time = kwargs.get('to_time')
    limit = kwargs.get('limit')
    ret = []
    for table_name in table_name_fix_lst:
        table = get_month_report_table(table_name)
        sql = table.select()
        function_id = [function_id] if function_id and not isinstance(function_id, list) else None
        if len(table_name_fix_lst) == 1 and to_time:
            sql = sql.where(table.c.create_time.__le__(to_time))
            if from_time:
                sql = sql.where(table.c.create_time.__ge__(from_time))
        elif table_name == table_name_fix_lst[0] and from_time:
            sql = sql.where(table.c.create_time.__ge__(from_time))
        elif table_name == table_name_fix_lst[-1] and to_time:
            sql = sql.where(table.c.create_time.__le__(to_time))

        if function_id:
            sql = sql.where(table.c.function_id.in_(function_id)).order_by(desc(table.c.create_time))
        else:
            sql = sql.order_by(desc(table.c.create_time))

        if limit:
            sql = sql.limit(limit)
        result = exec_query(sql, is_list=True)
        ret += result
    return ret

