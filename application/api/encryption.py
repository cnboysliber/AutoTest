from application import session_scope
from application.model.encryption import Encryption


def get_encryption_list():
    with session_scope() as session:
        query = session.query(Encryption).all()
        encryption_list = [encryption.to_dict() for encryption in query]
    return encryption_list


def get_encryption_method(encryption_id):
    with session_scope() as session:
        query = session.query(Encryption).filter_by(id=encryption_id).one()
        return query.encryption_method_name


def get_encryption_id_to_name():
    with session_scope() as session:
        query = session.query(Encryption).all()
        encryption_id_to_name = {}
        for encryption in query:
            encryption_id_to_name[encryption.id] = encryption.encryption_method_name
        return encryption_id_to_name
