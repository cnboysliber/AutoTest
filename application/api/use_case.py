# -*- coding: utf-8 -*-
from sqlalchemy import desc
from application import session_scope
from application.model.use_case import UseCase, UseCaseInterfaceRelation, UseCaseParameterRelation
from application.model.batch import BatchUseCaseRelation


def add_use_case(**kwargs):
    with session_scope() as session:
        use_case = UseCase(**kwargs)
        session.add(use_case)
        session.flush()
        return use_case.id


def get_use_case(**kwargs):
    with session_scope() as session:
        query = session.query(UseCase).filter_by(**kwargs).filter_by(status=1).order_by(UseCase.update_time.desc())
    use_case_list = [use_case.to_dict() for use_case in query]
    return use_case_list


def get_use_case_by_name(use_case_name):
    with session_scope() as session:
        query = session.query(UseCase).filter(UseCase.use_case_name.like('%{0}%'.format(use_case_name))).\
            filter_by(status=1).order_by(UseCase.create_time.desc())
    use_case_list = [use_case.to_dict() for use_case in query]
    return use_case_list


def get_multi_use_case(use_case_list):
    with session_scope() as session:
        query = session.query(UseCase).filter(UseCase.id.in_(use_case_list)).\
            order_by(UseCase.create_time.desc())
    use_case_dict = {}
    for use_case in query:
        use_case_info = use_case.to_dict()
        use_case_id = use_case_info['id']
        use_case_dict[use_case_id] = use_case_info
    return use_case_dict


def get_use_case_with_function_id(function_line_list):
    with session_scope() as session:
        use_case_with_function_line_dict = {}
        for function_info in function_line_list:
            function_id = function_info.get('id')
            query = session.query(UseCase).filter_by(function_id=function_id).filter_by(status=1).\
                order_by(UseCase.create_time.desc())
            use_case_list = [use_case.to_dict() for use_case in query]
            use_case_with_function_line_dict[function_id] = use_case_list
    return use_case_with_function_line_dict


def get_single_use_case(use_case_id):
    with session_scope() as session:
        query = session.query(UseCase).filter_by(id=use_case_id)
    use_case_info = [use_case.to_dict() for use_case in query][0]
    return use_case_info


def query_use_case_count(**kwargs):
    with session_scope() as session:
        use_case_count = session.query(UseCase).filter_by(status=1).filter_by(**kwargs).count()
    return use_case_count


def modify_use_case(**kwargs):
    with session_scope() as session:
        id = kwargs.pop('id')
        session.query(UseCase).filter_by(id=id).update(kwargs)
        return id


def del_use_case(**kwargs):
    """
    删除use_case
    同时将所有该use_case的关联关系清除
    :param kwargs:
    :return:
    """
    with session_scope() as session:
        id = kwargs.pop('id')
        session.query(UseCase).filter_by(id=id).update({'status': 0})
        session.query(BatchUseCaseRelation).filter_by(use_case_id=id).update({'status': 0})
        session.query(UseCaseInterfaceRelation).filter_by(use_case_id=id).update({'status': 0})


def get_max_order(use_case_id):
    """
    获取某use_case下interface的最大order数
    :param use_case_id:         use_case id
    :return:                    最大order数
    """
    with session_scope() as session:
        max_order_relation = session\
            .query(UseCaseInterfaceRelation)\
            .filter_by(use_case_id=use_case_id, status=1)\
            .order_by(desc(UseCaseInterfaceRelation.order))\
            .first()
        if not max_order_relation:
            return 0
        else:
            return max_order_relation.order


def add_relation(use_case_id, interface_id, order=None):
    """
    将某interface与use_case关联
    如未传入order则加入到最后
    如传入order则大于当前order的全部加一
    :param use_case_id:         use_case id
    :param interface_id:        interface id
    :param order:               interface顺序，如果为空加入到最后
    :return:
    """
    with session_scope() as session:
        if not order:
            order = get_max_order(use_case_id) + 1
        else:
            session\
                .query(UseCaseInterfaceRelation)\
                .filter_by(use_case_id=use_case_id)\
                .filter(UseCaseInterfaceRelation.order >= order)\
                .update({'order': UseCaseInterfaceRelation.order + 1})
        relation = UseCaseInterfaceRelation(use_case_id=use_case_id, interface_id=interface_id, order=order)
        session.add(relation)
        session.flush()
        return relation.id


def update_eval_relation(id, eval_string):
    """
    获取某use_case下interface的最大eval_string值
    :param ： id, eval_string
    :return:
    """
    with session_scope() as session:
        session.query(UseCaseInterfaceRelation).filter_by(id=id).update({'eval_string': eval_string})


def get_relation(**kwargs):
    """
    根据传入参数不同获取不同信息：
        use_case_id：获取某个use_case包含的interface
        interface_id：获取某个interface关联的use_case
    :param: use_case_id:
    :return:
    """
    with session_scope() as session:
        query = session\
            .query(UseCaseInterfaceRelation)\
            .filter_by(**kwargs)\
            .filter_by(status=1).order_by(UseCaseInterfaceRelation.order)
        session.expunge_all()
    relation_list = [s_relation.to_dict() for s_relation in query]
    return relation_list


def del_relation(relation_id):
    """
    删除use_case与interface关系
    如果有order大于当前删除order的，全部减一
    :param relation_id:           relation id
    :return:
    """
    with session_scope() as session:
        relation = session.query(UseCaseInterfaceRelation).filter_by(id=relation_id).one()
        current_order = relation.order
        use_case_id = relation.use_case_id
        session.query(UseCaseInterfaceRelation).filter_by(id=relation_id).update({'status': 0})
        session\
            .query(UseCaseInterfaceRelation)\
            .filter_by(use_case_id=use_case_id)\
            .filter(UseCaseInterfaceRelation.order > current_order)\
            .update({'order': UseCaseInterfaceRelation.order - 1})


def modify_interface_delay_relation(relation_id, interface_delay):
    """
    更新关系表中的interface_delay
    :param relation_id:
    :param interface_delay:
    :return:
    """
    with session_scope() as session:
        session.query(UseCaseInterfaceRelation).filter_by(id=relation_id).update({'interface_delay': interface_delay})


def reorder_relation(relation_id, new_order):
    """
    调整某个已有interface的order
    同时将其他影响范围内的interface的order全部加一或者减一
    :return:
    """
    with session_scope() as session:
        relation = session.query(UseCaseInterfaceRelation).filter_by(id=relation_id).one()
        current_order = relation.order
        use_case_id = relation.use_case_id
        if current_order == new_order:
            return
        elif current_order < new_order:
            session\
                .query(UseCaseInterfaceRelation)\
                .filter_by(use_case_id=use_case_id)\
                .filter(UseCaseInterfaceRelation.order > current_order)\
                .filter(UseCaseInterfaceRelation.order <= new_order)\
                .update({'order': UseCaseInterfaceRelation.order - 1})
        elif current_order > new_order:
            session\
                .query(UseCaseInterfaceRelation)\
                .filter_by(use_case_id=use_case_id)\
                .filter(UseCaseInterfaceRelation.order < current_order)\
                .filter(UseCaseInterfaceRelation.order >= new_order)\
                .update({'order': UseCaseInterfaceRelation.order + 1})
        session\
            .query(UseCaseInterfaceRelation)\
            .filter_by(id=relation_id)\
            .update({'order': new_order})


def add_case_parameter_relation(**kwargs):
    """
    添加用例关联参数信息
    :param kwargs:
    :return:
    """
    with session_scope() as session:
        use_case_parameter = UseCaseParameterRelation(**kwargs)
        session.add(use_case_parameter)
        session.flush()
        return use_case_parameter.id


def get_case_parameter_relation(**kwargs):
    """
    查询用例关联参数信息
    :param kwargs:
    :return:
    """
    with session_scope() as session:
        query = session.query(UseCaseParameterRelation).filter_by(**kwargs).filter_by(status=1)
        session.expunge_all()
    parameter_list = [s_param.to_dict() for s_param in query]
    return parameter_list


def modify_case_parameter_relation(**kwargs):
    """
    更新用例关联参数信息
    :param kwargs:
    :return:
    """
    with session_scope() as session:
        id = kwargs.pop('id')
        session.query(UseCaseParameterRelation).filter_by(id=id).update(kwargs)


def del_case_parameter_relation(**kwargs):
    """
    删除用例关联参数
    :param kwargs:
    :return:
    """
    with session_scope() as session:
        session.query(UseCaseParameterRelation).filter_by(**kwargs).update({'status': 0})
