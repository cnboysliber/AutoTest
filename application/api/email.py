from application import session_scope
from application.model.email import Email, \
    EmailFunctionRelation as EFR, EmailBatchRelation as EBR, EmailBatchRelation


def add_email_account(**kwargs):
    with session_scope() as session:
        email = Email(**kwargs)
        session.add(email)
        session.flush()
        return email.id


def update_email_account(**kwargs):
    email_id = kwargs.pop('email_id')
    with session_scope() as session:
        session.query(Email).filter_by(id=email_id).filter_by(status=1).update(kwargs)


def query_email_account():
    with session_scope() as session:
        query = session.query(Email).filter_by(status=1)
        email_list = [email.to_dict() for email in query]
        return email_list


def query_email_id_to_info():
    with session_scope() as session:
        query = session.query(Email).filter_by(status=1)
        return {m.id: m.to_dict() for m in query}


def del_email_account(**kwargs):
    email_id = kwargs.pop('id')
    with session_scope() as session:
        session.query(Email).filter_by(id=email_id).update({'status': 0})
        session.query(EFR).filter_by(email_id=email_id).update({'status': 0})
        session.query(EmailBatchRelation).filter_by(email_id=email_id).update({'status': 0})


def add_email_function(email_id, function_id):
    function_ids = [function_id] if not isinstance(function_id, list) else function_id
    with session_scope() as session:
        for function_id in function_ids:
            relation = EFR(email_id=email_id, function_id=function_id)
            session.add(relation)


def query_email_by_function_id(function_id):
    with session_scope() as session:
        q = session.query(EFR).\
            filter_by(function_id=function_id).\
            filter_by(status=1)
        email_id_list = [email.email_id for email in q]
        email = session.query(Email).\
            filter(Email.id.in_(email_id_list)).\
            filter_by(status=1)
        return [m.to_dict() for m in email]


def get_function_id_by_email_id(email_id):
    with session_scope() as session:
        relation = session.query(EFR).\
            filter_by(email_id=email_id).\
            filter_by(status=1)
        return [m.function_id for m in relation]


def del_email_function_relation(email_id, function_ids):
    function_ids = [function_ids] if not isinstance(function_ids, list) else function_ids
    with session_scope() as session:
        for function_id in function_ids:
            session.query(EFR).\
                filter_by(function_id=function_id).\
                filter_by(email_id=email_id).\
                update({'status': 0})


def get_batch_id_by_email_id(email_id):
    with session_scope() as session:
        relation = session.query(EBR).filter_by(email_id=email_id, status=1)
        batch_list = [m.batch_id for m in relation]
        return batch_list


def add_email_batch(email_id, batch_ids):
    batch_ids = [batch_ids] if not isinstance(batch_ids, list) else batch_ids
    with session_scope() as session:
        for batch_id in batch_ids:
            session.add(EBR(email_id=email_id, batch_id=batch_id))


def get_email_batch():
    with session_scope() as session:
        relation = session.query(EBR).filter_by(status=1)
        email_to_batchs = {}
        for m in relation:
            if m.email_id in email_to_batchs:
                email_to_batchs[m.email_id].append(m.batch_id)
            else:
                email_to_batchs[m.email_id] = [m.batch_id]
        return email_to_batchs


def delete_email_batch(email_id, batch_ids):
    batch_ids = [batch_ids] if not isinstance(batch_ids, list) else batch_ids
    with session_scope() as session:
        for batch_id in batch_ids:
            session.query(EBR).filter_by(email_id=email_id, batch_id=batch_id).update({'status': 0})


if __name__ == '__main__':
    count = query_email_account()
    print(count)

