# -*- coding: utf-8 -*-
from sqlalchemy import func, select, desc
from application.util.decorator import *
from application.model.run_log import *


@run_log_table_decorator
def add_batch_run_log(**kwargs):
    table = get_batch_run_log_table(kwargs.pop('table_name_fix_lst')[0])
    sql = table.insert(kwargs)
    return exec_change(sql, **kwargs).inserted_primary_key[0]


@run_log_table_decorator
def get_multi_batch_run_log_info(**kwargs):
    table_name_fix_lst = kwargs.pop('table_name_fix_lst')
    batch_id = kwargs.get('batch_id')
    batch_run_log_id = kwargs.get('id')
    from_time = kwargs.get('from_time')
    to_time = kwargs.get('to_time')
    page_index = kwargs.get('pageIndex')
    page_size = kwargs.get('pageSize')
    page_index = int(page_index) if page_index else 1
    page_size = int(page_size) if page_size else 10
    index = (page_index-1)*page_size
    ret = []
    total_count = 0
    for table_name in table_name_fix_lst[::-1]:
        table = get_batch_run_log_table(table_name)
        batch_list = [batch_id] if not isinstance(batch_id, list) else batch_id
        count_sql = select([func.count()]).select_from(table)
        if len(table_name_fix_lst) == 1 and to_time:
            sql = table.select().where(table.c.start_time.__le__(to_time))
            count_sql = count_sql.where(table.c.start_time.__le__(to_time))
            if from_time:
                sql = sql.where(table.c.start_time.__gt__(from_time))
                count_sql = count_sql.where(table.c.start_time.__gt__(from_time))
        elif table_name == table_name_fix_lst[0] and from_time:
            sql = table.select().where(table.c.start_time.__gt__(from_time))
            count_sql = count_sql.where(table.c.start_time.__gt__(from_time))
        elif table_name == table_name_fix_lst[-1] and to_time:
            sql = table.select().where(table.c.start_time.__le__(to_time))
            count_sql = count_sql.where(table.c.start_time.__le__(to_time))
        else:
            sql = table.select()
        if batch_id:
            sql = sql.where(table.c.batch_id.in_(batch_list))
            count_sql = count_sql.where(table.c.batch_id.in_(batch_list))
        if batch_run_log_id:
            sql = sql.where(table.c.id == batch_run_log_id).order_by(desc(table.c.start_time))
            count_sql = count_sql.where(table.c.id == batch_run_log_id)
        else:
            sql = sql.order_by(desc(table.c.start_time))

        count = exec_query(count_sql, is_list=True)[0]['count_1']
        total_count += count
        limit = page_size - len(ret)
        if limit == 0:
            break
        if index >= total_count:
            continue
        elif index >= total_count - count - 1:
            offset_num = count - (total_count - index)
            index += total_count - index
        else:
            offset_num = 0
            sql = sql.offset(offset_num).limit(limit)
            ret += exec_query(sql, is_list=True)
            break
        sql = sql.offset(offset_num).limit(limit)
        ret += exec_query(sql, is_list=True)
    return ret


@run_log_table_decorator
def get_batch_run_log_info(**kwargs):
    table_name_fix_lst = kwargs.pop('table_name_fix_lst')
    batch_id = kwargs.get('batch_id')
    batch_run_log_id = kwargs.get('id')
    from_time = kwargs.get('from_time')
    to_time = kwargs.get('to_time')
    ret = []
    for table_name in table_name_fix_lst:
        table = get_batch_run_log_table(table_name)
        batch_list = [batch_id] if not isinstance(batch_id, list) else batch_id
        if len(table_name_fix_lst) == 1 and to_time:
            sql = table.select().where(table.c.start_time.__le__(to_time))
            if from_time:
                sql = sql.where(table.c.start_time.__gt__(from_time))
        elif table_name == table_name_fix_lst[0] and from_time:
            sql = table.select().where(table.c.start_time.__gt__(from_time))
        elif table_name == table_name_fix_lst[-1] and to_time:
            sql = table.select().where(table.c.start_time.__le__(to_time))
        else:
            sql = table.select()
        if batch_id:
            sql = sql.where(table.c.batch_id.in_(batch_list))
        if batch_run_log_id:
            sql = sql.where(table.c.id == batch_run_log_id).order_by(desc(table.c.start_time))
        else:
            sql = sql.order_by(desc(table.c.start_time))
        ret += exec_query(sql, is_list=True)
    return ret


@run_log_table_decorator
def get_batch_run_log_count(**kwargs):
    table_name_fix_lst = kwargs.pop('table_name_fix_lst')
    from_time = kwargs.get('from_time')
    to_time = kwargs.get('to_time')
    count = 0
    for table_name in table_name_fix_lst:
        table = get_batch_run_log_table(table_name)
        sql = select([func.count()]).select_from(table)

        if len(table_name_fix_lst) == 1 and to_time:
            if from_time:
                sql = sql.where(table.c.start_time.__gt__(from_time))
            sql = sql.where(table.c.start_time.__le__(to_time))
        elif table_name == table_name_fix_lst[0] and from_time:
            sql = sql.where(table.c.start_time.__gt__(from_time))
        elif table_name == table_name_fix_lst[-1] and to_time:
            sql = sql.where(table.c.start_time.__le__(to_time))

        count += exec_query(sql, is_list=True)[0]['count_1']
    return count


@run_log_table_decorator
def modify_batch_run_log(**kwargs):
    table = get_batch_run_log_table(kwargs.pop('table_name_fix_lst')[0])
    id = kwargs.pop('id')
    sql = table.update(table.c.id == id).values(**kwargs)
    return exec_change(sql)


@run_log_table_decorator
def add_use_case_run_log(**kwargs):
    table = get_use_case_run_log_table(kwargs.pop('table_name_fix_lst')[0])
    if table is None:
        LOGGER.exception_log('add_use_case_run_log获取usecase表对象失败')
    else:
        LOGGER.info_log('add_use_case_run_log插入日志类型{}，日志对象：{}'.format(type(table), dir(table)))
    sql = table.insert(kwargs)
    LOGGER.info_log('插入日志内容：{}'.format(str(kwargs)))
    ret = exec_change(sql, **kwargs)
    try:
        primary_key = ret.inserted_primary_key[0] or ret.lastrowid
        if not primary_key:
            LOGGER.exception_log('返回主键异常，为空, 返回结果：%s' % str(primary_key))
    except Exception as e:
        LOGGER.exception_log('返回值：{}, 异常信息{}'.format(str(ret), str(e)))
        raise
    return primary_key


@run_log_table_decorator
def get_use_case_run_log_count(**kwargs):
    table_name_fix_lst = kwargs.pop('table_name_fix_lst')
    batch_run_log_id = kwargs.get('batch_run_log_id')
    use_case_id = kwargs.get('use_case_id')
    from_time = kwargs.get('from_time')
    to_time = kwargs.get('to_time')
    is_pass = kwargs.get('is_pass')
    auto_run = kwargs.get('auto_run', None)
    count = 0
    for table_name in table_name_fix_lst:
        table = get_use_case_run_log_table(table_name)
        if table is None:
            LOGGER.exception_log('get_use_case_run_log_count获取usecase表对象失败')
        sql = select([func.count()]).select_from(table)
        if len(table_name_fix_lst) == 1 and to_time:
            sql = sql.where(table.c.start_time.__le__(to_time))
            if from_time:
                sql = sql.where(table.c.start_time.__gt__(from_time))
        elif table_name == table_name_fix_lst[0] and from_time:
            sql = sql.where(table.c.start_time.__gt__(from_time))
        elif table_name == table_name_fix_lst[-1] and to_time:
            sql = sql.where(table.c.start_time.__le__(to_time))
        if batch_run_log_id:
            batch_run_log_id = [batch_run_log_id] if not isinstance(batch_run_log_id, list) else batch_run_log_id
            sql = sql.where(table.c.batch_run_log_id.in_(batch_run_log_id))
        if use_case_id or use_case_id == []:
            use_case_id = [use_case_id] if not isinstance(use_case_id, list) else use_case_id
            sql = sql.where(table.c.use_case_id.in_(use_case_id))
        if is_pass in ['0', '1']:
            sql = sql.where(table.c.is_pass == is_pass)
        if auto_run:
            sql = sql.where(table.c.auto_run == 1)

        count += exec_query(sql, is_list=True)[0]['count_1']
    return count


@run_log_table_decorator
def modify_use_case_run_log(**kwargs):
    table = get_use_case_run_log_table(kwargs.pop('table_name_fix_lst')[0])
    if table is None:
        LOGGER.exception_log('modify_use_case_run_log获取usecase表对象失败')
    id = kwargs.pop('id')
    sql = table.update(table.c.id == id).values(**kwargs)
    return exec_change(sql)


@run_log_table_decorator
def get_use_case_run_log(**kwargs):
    table_name_fix_lst = kwargs.pop('table_name_fix_lst')
    use_case_id = kwargs.get('use_case_id')
    from_time = kwargs.get('from_time')
    to_time = kwargs.get('to_time')
    batch_run_log_id = kwargs.get('batch_run_log_id')
    page_index = kwargs.get('pageIndex')
    page_size = kwargs.get('pageSize')
    is_pass = kwargs.get('is_pass', None)
    auto_run = kwargs.get('auto_run', None)
    page_index = int(page_index) if page_index else None
    page_size = int(page_size) if page_size else None
    if page_size:
        index = (page_index - 1) * page_size
    else:
        index = -1
    total_count = 0
    ret = []
    for table_name in table_name_fix_lst[::-1]:
        table = get_use_case_run_log_table(table_name)
        if table is None:
            LOGGER.exception_log('get_use_case_run_log获取usecase表对象失败')
        sql = table.select()
        count_sql = select([func.count()]).select_from(table)
        use_case_list = [use_case_id] if not isinstance(use_case_id, list) else use_case_id
        if len(table_name_fix_lst) == 1 and to_time:
            sql = sql.where(table.c.start_time.__le__(to_time))
            count_sql = count_sql.where(table.c.start_time.__le__(to_time))
            if from_time:
                sql = sql.where(table.c.start_time.__gt__(from_time))
                count_sql = count_sql.where(table.c.start_time.__gt__(from_time))

        elif table_name == table_name_fix_lst[0] and from_time:
            sql = sql.where(table.c.start_time.__gt__(from_time))
            count_sql = count_sql.where(table.c.start_time.__gt__(from_time))

        elif table_name == table_name_fix_lst[-1] and to_time:
            sql = sql.where(table.c.start_time.__le__(to_time))
            count_sql = count_sql.where(table.c.start_time.__le__(to_time))

        if use_case_id or use_case_id == []:
            sql = sql.where(table.c.use_case_id.in_(use_case_list)).order_by(desc(table.c.start_time))
            count_sql = count_sql.where(table.c.use_case_id.in_(use_case_list))
        else:
            sql = sql.order_by(desc(table.c.start_time))
        if batch_run_log_id:
            sql = sql.where(table.c.batch_run_log_id == batch_run_log_id)
            count_sql = count_sql.where(table.c.batch_run_log_id == batch_run_log_id)
        if is_pass in ['0', '1']:
            sql = sql.where(table.c.is_pass == is_pass)
            count_sql = count_sql.where(table.c.is_pass == is_pass)
        if auto_run:
            sql = sql.where(table.c.auto_run == 1)
            count_sql = count_sql.where(table.c.auto_run == 1)
        if not page_size:
            ret += exec_query(sql, is_list=True)
            continue
        count = exec_query(count_sql, is_list=True)[0]['count_1']
        total_count += count
        limit = page_size - len(ret)
        if limit == 0:
            break
        if index >= total_count:
            continue
        elif index >= total_count - count - 1:
            offset_num = count - (total_count - index)
            index += total_count - index
        else:
            offset_num = 0
            sql = sql.offset(offset_num).limit(limit)
            ret += exec_query(sql, is_list=True)
            break
        sql = sql.offset(offset_num).limit(limit)
        ret += exec_query(sql, is_list=True)
    return ret


@run_log_table_decorator
def add_interface_run_log(**kwargs):
    table = get_interface_run_log_table(kwargs.pop('table_name_fix_lst')[0])
    sql = table.insert(kwargs)
    return exec_change(sql, **kwargs).inserted_primary_key[0]


@run_log_table_decorator
def get_interface_run_log(**kwargs):
    table_name_fix_lst = kwargs.pop('table_name_fix_lst')
    interface_id = kwargs.get('interface_id')
    limit = kwargs.get('limit')
    from_time = kwargs.get('from_time')
    to_time = kwargs.get('to_time')
    use_case_run_log_id = kwargs.get('use_case_run_log_id')
    ret = []
    for table_name in table_name_fix_lst:
        table = get_interface_run_log_table(table_name)

        interface_list = [interface_id] if not isinstance(interface_id, list) else interface_id
        if len(table_name_fix_lst) == 1 and to_time:
            sql = table.select().where(table.c.end_time.__le__(to_time))
            if from_time:
                sql = sql.where(table.c.end_time.__gt__(from_time))
        elif table_name == table_name_fix_lst[0] and from_time:
            sql = table.select().where(table.c.end_time.__gt__(from_time))
        elif table_name == table_name_fix_lst[-1] and to_time:
            sql = table.select().where(table.c.end_time.__le__(to_time))
        else:
            sql = table.select()

        if interface_id:
            sql = sql.where(table.c.interface_id.in_(interface_list))
        else:
            sql = table.select()
        if use_case_run_log_id:
            sql = sql.where(table.c.use_case_run_log_id == use_case_run_log_id)
        sql = sql.order_by(table.c.end_time)
        if limit:
            sql = sql.limit(limit)
        ret += exec_query(sql, is_list=True)
    return ret


@run_log_table_decorator
def modify_interface_run_log(**kwargs):
    table = get_interface_run_log_table(kwargs.pop('table_name_fix_lst')[0])
    id = kwargs.pop('id')
    sql = table.update(table.c.id == id).values(**kwargs)
    return exec_change(sql, **kwargs).inserted_primary_key[0]




