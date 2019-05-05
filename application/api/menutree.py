# -*- coding:utf-8
from application import session_scope
from application.model.menutree import *


def add_business_line(**kwargs):
    with session_scope() as session:
        business_line = BusinessLine(**kwargs)
        session.add(business_line)
        session.flush()
        return business_line.id


def del_business_line(**kwargs):
    business_id = kwargs.get('id')
    if not isinstance(business_id, list):
        business_id = [business_id]
    with session_scope() as session:
        query = session.query(BusinessLine)
        query.filter(BusinessLine.id.in_(business_id)).delete(synchronize_session=False)
    return business_id


def add_system_line(**kwargs):
    with session_scope() as session:
        system_line = SystemLine(**kwargs)
        session.add(system_line)
        session.flush()
        return system_line.id


def del_system_line(**kwargs):
    system_line_id = kwargs.get('id')
    if not isinstance(system_line_id, list):
        system_line_id = [system_line_id]
    with session_scope() as session:
        query = session.query(SystemLine)
        query.filter(SystemLine.id.in_(system_line_id)).delete(synchronize_session=False)
    return system_line_id


def add_function_line(**kwargs):
    with session_scope() as session:
        function_line = FunctionLine(**kwargs)
        session.add(function_line)
        session.flush()
        return function_line.id


def del_function_line(**kwargs):
    function_id = kwargs.get('id')
    if not isinstance(function_id, list):
        function_id = [function_id]
    with session_scope() as session:
        query = session.query(FunctionLine)
        query.filter(FunctionLine.id.in_(function_id)).delete(synchronize_session=False)
    return function_id


def query_business_line(**kwargs):
    with session_scope() as session:
        query = session.query(BusinessLine).filter_by(**kwargs).filter_by(status=1)
    business_list = [business.to_dict() for business in query]
    return business_list


def query_system_line(**kwargs):
    with session_scope() as session:
        query = session.query(SystemLine).filter_by(**kwargs).filter_by(status=1)
    system_line_list = [system_line.to_dict() for system_line in query]
    return system_line_list


def query_function_line(**kwargs):
    with session_scope() as session:
        query = session.query(FunctionLine).filter_by(**kwargs).filter_by(status=1)
    function_line_list = [function_line.to_dict() for function_line in query]
    return function_line_list


def query_all_line_relation(**kwargs):
    with session_scope() as session:
        system_info = session.query(SystemLine).filter_by(**kwargs).filter_by(status=1)
        function_line_list = [system_line.to_dict() for system_line in system_info]
        return function_line_list


def query_line_relation(**kwargs):
    with session_scope() as session:
        busines_query = session.query(BusinessLine).filter_by(**kwargs).filter_by(status=1)
        system_query = session.query(SystemLine).filter_by(**kwargs).filter_by(status=1)
        function_query = session.query(FunctionLine).filter_by(**kwargs).filter_by(status=1)
        business_line_dict = {}
        for query in busines_query:
            business_line_info = query.to_dict()
            business_line_dict[business_line_info['id']] = business_line_info
        system_line_dict = {}
        for query in system_query:
            system_line_info = query.to_dict()
            system_line_dict[system_line_info['id']] = system_line_info
        function_dict = {}
        for function_obj in function_query:
            function_info = function_obj.to_dict()
            if not function_info['id']:
                continue
            system_line_id = function_info['system_line_id']
            business_line_id = system_line_dict[system_line_id].get('business_line_id')
            business_name = business_line_dict[business_line_id].get('business_name')
            system_name = system_line_dict[system_line_id].get('system_name')
            function_name = function_info['function_name']
            function_dict[function_info['id']] = {'business_name': business_name, 'system_name': system_name,
                                                  'function_name': function_name, 'system_line_id': system_line_id,
                                                  'business_line_id': business_line_id,
                                                  'function_line_id': function_info['id']}
        return function_dict











