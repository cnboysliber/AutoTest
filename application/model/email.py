from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base

from application import engine

Base = declarative_base()


class Email(Base):
    __tablename__ = 'email'
    __table_args__ = {
        "mysql_engine": "InnoDB",
        "mysql_charset": "utf8"
    }

    id = Column(Integer, primary_key=True)
    email_name = Column(String(50), nullable=False)
    email_address = Column(String(50), nullable=False)
    status = Column(Integer, nullable=False, default=1)
    create_time = Column(DateTime, default=datetime.utcnow)
    update_time = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    def to_dict(self):
        return {
            'id': self.id,
            'email_name': self.email_name,
            'email_address': self.email_address,
            'create_time': self.create_time,
            'update_time': self.update_time
        }


class EmailFunctionRelation(Base):
    __tablename__ = 'email_function'
    __table_args__ = {
        "mysql_engine": "InnoDB",
        "mysql_charset": "utf8"
    }
    id = Column(Integer, primary_key=True)
    email_id = Column(Integer, nullable=False)
    function_id = Column(Integer, nullable=False)
    status = Column(Integer, nullable=False, default=1)
    create_time = Column(DateTime, default=datetime.now)
    update_time = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    def to_dict(self):
        return {
            'id': self.id,
            'email_id': self.email_id,
            'function_id': self.function_id,
            'create_time': self.create_time,
            'update_time': self.update_time
        }


class EmailBatchRelation(Base):
    __tablename__ = 'email_batch'
    __table_args__ = {
        "mysql_engine": "InnoDB",
        "mysql_charset": "utf8"
    }
    id = Column(Integer, primary_key=True)
    email_id = Column(Integer, nullable=False)
    batch_id = Column(Integer, nullable=False)
    status = Column(Integer, nullable=False, default=1)
    create_time = Column(DateTime, default=datetime.now)
    update_time = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    def to_dict(self):
        return {
            'id': self.id,
            'email_id': self.email_id,
            'batch_id': self.batch_id,
            'create_time': self.create_time,
            'update_time': self.update_time
        }


Base.metadata.create_all(engine)
