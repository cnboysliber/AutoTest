# -*- coding: utf-8 -*-
from application import session_scope
from application.model.interface import Interface


def add_interface(**kwargs):
    with session_scope() as session:
        interface = Interface(**kwargs)
        session.add(interface)
        session.flush()
        return interface.id


def get_interface(**kwargs):
    if 'interface_name' not in kwargs:
        interface_name = ''
    else:
        interface_name = kwargs.pop('interface_name')
    with session_scope() as session:
        query = session.query(Interface).filter(Interface.interface_name.like('%{0}%'.format(interface_name))).\
            filter_by(**kwargs).filter_by(status=1).order_by(Interface.update_time.desc())
    interface_list = [interface.to_dict() for interface in query]
    return interface_list


def query_single_interface(interface_id):
    with session_scope() as session:
        query = session.query(Interface).filter_by(id=interface_id)
    interface_info = [interface.to_dict() for interface in query][0]
    return interface_info


def query_multi_interface(interface_list):
    with session_scope() as session:
        query = session.query(Interface).filter(Interface.id.in_(interface_list))
    interface_dict = {}
    for use_case in query:
        interface_info = use_case.to_dict()
        interface_id = interface_info['id']
        interface_dict[interface_id] = interface_info
    return interface_dict


def query_interface_count(interface_name=''):
    with session_scope() as session:
        interface_count = session.query(Interface).\
            filter(Interface.interface_name.like('%{0}%'.format(interface_name))).filter_by(status=1).count()
    return interface_count


def modify_interface(**kwargs):
    with session_scope() as session:
        id = kwargs.pop('id')
        session.query(Interface).filter_by(id=id).update(kwargs)


def del_interface(**kwargs):
    with session_scope() as session:
        id = kwargs.pop('id')
        session.query(Interface).filter_by(id=id).update({'status': 0})
