# -*- coding: utf-8 -*-
from application import session_scope
from application.model.parameter import Parameter


def add_parameter(**kwargs):
    with session_scope() as session:
        parameter = Parameter(**kwargs)
        session.add(parameter)
        session.flush()
        return parameter.id


def get_parameter(**kwargs):
    with session_scope() as session:
        query = session.query(Parameter).filter_by(**kwargs).order_by(Parameter.update_time.desc())
    parameter_list = [param.to_dict() for param in query]
    return parameter_list


def query_parameter_count():
    with session_scope() as session:
        parameter_count = session.query(Parameter).count()
    return parameter_count


def modify_parameter(**kwargs):
    with session_scope() as session:
        id = kwargs.pop('id')
        session.query(Parameter).filter_by(id=id).update(kwargs)
        return id


def del_parameter(**kwargs):
    with session_scope() as session:
        id = kwargs.pop('id')
        session.query(Parameter).filter_by(id=id).delete(synchronize_session=False)
