from application import session_scope
from application.model.batch import Batch, BatchUseCaseRelation
from application.model.email import EmailBatchRelation


def add_batch(**kwargs):
    with session_scope() as session:
        batch = Batch(**kwargs)
        session.add(batch)
        session.flush()
        return batch.id


def get_batch(**kwargs):
    with session_scope() as session:
        query = session.query(Batch).filter_by(**kwargs).filter_by(status=1).order_by(Batch.update_time.desc())
    batch_list = [s_batch.to_dict() for s_batch in query]
    return batch_list


def get_batch_id_to_info():
    with session_scope() as session:
        q = session.query(Batch).filter_by(status=1)
        return {m.id: m.to_dict() for m in q}


def query_batch_count():
    with session_scope() as session:
        batch_count = session.query(Batch).filter_by(status=1).count()
    return batch_count


def modify_batch(**kwargs):
    with session_scope() as session:
        id = kwargs.pop('id')
        session.query(Batch).filter_by(id=id).update(kwargs)
        return id


def del_batch(**kwargs):
    with session_scope() as session:
        id = kwargs.pop('id')
        session.query(Batch).filter_by(id=id).update({'status': 0})
        session.query(BatchUseCaseRelation).filter_by(batch_id=id).update({'status': 0})
        session.query(EmailBatchRelation).filter_by(batch_id=id).update({'status': 0})


def add_batch_use_case_relation(batch_id, use_case_id):
    with session_scope() as session:
        batchUseCaseRelation = BatchUseCaseRelation(batch_id=batch_id, use_case_id=use_case_id)
        session.add(batchUseCaseRelation)


def get_batch_use_case_relation(**kwargs):
    with session_scope() as session:
        query = session.query(BatchUseCaseRelation).filter_by(**kwargs).filter_by(status=1)
    batch_use_case_relation_list = [b_use_case.to_dict() for b_use_case in query]
    return batch_use_case_relation_list


def del_batch_use_case_relation(relation_id):
    with session_scope() as session:
        session.query(BatchUseCaseRelation).\
            filter_by(id=relation_id).update({'status': 0})

