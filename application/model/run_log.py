# -*- coding:utf-8 -*-
import time
from datetime import datetime
from application import engine
from application.util.redis_lock import deco, RedisLock
from sqlalchemy import Table, MetaData, Column, Integer, String, Float, Boolean, TEXT
from sqlalchemy.dialects.mysql import TIMESTAMP, MEDIUMTEXT
from application import app
if not app.config['DEBUG']:
    from application.util import logger as LOGGER
else:
    from application.util import LocalLogger as LOGGER


meta = MetaData(bind=engine)
batch_run_log_table = {}
use_case_run_log_table = {}
interface_run_log_table = {}


# 用例脚本的运行日记表
def get_batch_run_log_table(table_name):
    table = batch_run_log_table.get('batch_run_log_{0}'.format(table_name), None)
    if table is None:
        return create_batch_run_log_table(table_name)
    return table


# 用例脚本的运行日记表
def get_use_case_run_log_table(table_name):
    table = use_case_run_log_table.get('use_case_run_log_{0}'.format(table_name), None)
    if table is None:
        return create_use_case_run_log_table(table_name)
    return table


# 接口的运行日记表
def get_interface_run_log_table(table_name):
    table = interface_run_log_table.get('interface_run_log_{0}'.format(table_name), None)
    if table is None:
        print('create table:{}'.format(table_name))
        LOGGER.info_log('create table:{}'.format(table_name))
        return create_interface_run_log_table(table_name)
    return table


# @deco(RedisLock('batch_run_log_lock'))
def create_batch_run_log_table(table_name, bind=engine):
    table = Table('batch_run_log_{0}'.format(table_name), meta,
                  Column('id', Integer, primary_key=True, autoincrement=True),
                  Column('batch_id', Integer, nullable=False),
                  Column('use_case_count', Integer, nullable=False),
                  Column('pass_rate', Integer, default=-1, nullable=False),  # 百分比，-1表示未执行完成
                  Column('start_time', TIMESTAMP(fsp=3), default=datetime.utcnow),
                  Column('end_time', TIMESTAMP(fsp=3)),
                  Column('cost_time', Float, default=0),
                  Column('create_time', TIMESTAMP(fsp=3), default=datetime.utcnow, nullable=False),
                  extend_existing=True,
                  )
    table.create(bind=bind, checkfirst=True)

    batch_run_log_table['batch_run_log_{0}'.format(table_name)] = table
    return table


# @deco(RedisLock('use_case_run_log_lock'))
def create_use_case_run_log_table(table_name, bind=engine):
    table = Table('use_case_run_log_{0}'.format(table_name), meta,
                  Column('id', Integer, primary_key=True, autoincrement=True),
                  Column('batch_run_log_id', Integer),
                  Column('use_case_id', Integer, nullable=False),
                  Column('is_pass', Boolean, default=False),
                  Column('start_time', TIMESTAMP(fsp=3), default=datetime.utcnow),
                  Column('end_time', TIMESTAMP(fsp=3)),
                  Column('create_time', TIMESTAMP(fsp=3), default=datetime.utcnow),
                  Column('cost_time', Float, nullable=False, default=0),
                  Column('auto_run', Boolean, default=False),
                  extend_existing=True,
                  )
    table.create(bind=bind, checkfirst=True)

    use_case_run_log_table['use_case_run_log_{0}'.format(table_name)] = table
    return table


@deco(RedisLock('interface_run_log_lock'))
def create_interface_run_log_table(table_name, bind=engine):
    table = Table('interface_run_log_{0}'.format(table_name), meta,
                  Column('id', Integer, primary_key=True, autoincrement=True),
                  Column('use_case_run_log_id', Integer, nullable=False),
                  Column('interface_id', Integer, nullable=False),
                  Column('s_header', TEXT),  # 发送的header
                  Column('s_payload', MEDIUMTEXT),  # 发送的payload
                  Column('r_code', String(10)),  # 返回的HTTP code
                  Column('r_header', TEXT),  # 返回的HTTP header
                  Column('r_payload', TEXT),  # 返回的json
                  Column('is_pass', Boolean, nullable=False),
                  Column('cost_time', Float, nullable=False, default=0),
                  Column('start_time', TIMESTAMP(fsp=3), default=datetime.utcnow),
                  Column('end_time', TIMESTAMP(fsp=3), nullable=False),
                  Column('error_message', String(2000)),
                  extend_existing=True,
                  )
    table.create(bind=bind, checkfirst=True)

    interface_run_log_table['interface_run_log_{0}'.format(table_name)] = table

    return table


def exec_query(sql, is_list=False):
    conn = engine.connect()
    try:
        ret = []
        for one in conn.execute(sql).fetchall():
            ret.append(dict(one.items()))
        if not is_list:
            return ret if len(ret) != 1 else ret[0]
        return ret
    except Exception as e:
        raise e
    finally:
        conn.close()


def exec_change(sql, **params):
    try:
        with engine.connect() as conn:
            trans = conn.begin()
            ret = conn.execute(sql)
            trans.commit()
            return ret
    except Exception as e:
        LOGGER.exception_log('数据写入数据库失败：{}, sql语句：{}'.format(str(e), params))
        raise


def drop_all():
    meta.reflect(engine)
    meta.drop_all()


def create_all():
    meta.reflect(engine)
    meta.create_all()
