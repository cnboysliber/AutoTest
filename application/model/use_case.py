# -*- coding: utf-8 -*-
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base

from application import engine

Base = declarative_base()


class UseCase(Base):
    __tablename__ = 'use_case'
    __table_args__ = {
        "mysql_engine": "InnoDB",
        "mysql_charset": "utf8"
    }

    id = Column(Integer, primary_key=True)
    environment_id = Column(Integer, nullable=False)
    use_case_name = Column(String(100), nullable=False)
    pre_condition = Column(String(1000))
    desc = Column(String(1000))
    post_condition = Column(String(1000))
    use_case_type = Column(Integer, default=0, nullable=False)
    create_by = Column(String(50), nullable=False)
    create_time = Column(DateTime, default=datetime.utcnow)
    update_time = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    status = Column(Integer, default=1, nullable=False)
    function_id = Column(Integer, default=0, nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'environment_id': self.environment_id,
            'use_case_name': self.use_case_name,
            'pre_condition': self.pre_condition,
            'desc': self.desc,
            'type': self.use_case_type,
            'post_condition': self.post_condition,
            'create_by': self.create_by,
            'create_time': self.create_time,
            'update_time': self.update_time,
            'function_id': self.function_id
        }


class UseCaseInterfaceRelation(Base):
    __tablename__ = 'use_case_interface_relation'
    __table_args__ = {
        "mysql_engine": "InnoDB",
        "mysql_charset": "utf8"
    }

    id = Column(Integer, primary_key=True)
    use_case_id = Column(Integer, nullable=False)
    interface_id = Column(Integer, nullable=False)
    order = Column(Integer, nullable=False)
    eval_string = Column(String(1000), nullable=False, default='')
    interface_delay = Column(Integer, nullable=False, default=0)
    create_time = Column(DateTime, default=datetime.utcnow)
    update_time = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    status = Column(Integer, default=1, nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'use_case_id': self.use_case_id,
            'interface_id': self.interface_id,
            'order': self.order,
            'eval_string': self.eval_string,
            'interface_delay': self.interface_delay,
            'create_time': self.create_time,
            'update_time': self.update_time
        }


class UseCaseParameterRelation(Base):
    __tablename__ = 'use_case_parameter_relation'
    __table_args__ = {
        "mysql_engine": "InnoDB",
        "mysql_charset": "utf8"
    }

    id = Column(Integer, primary_key=True)
    relation_id = Column(Integer, nullable=False)
    parameter_name = Column(String(128), nullable=False)
    parameter_value = Column(String(1000))
    create_time = Column(DateTime, default=datetime.utcnow)
    update_time = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    status = Column(Integer, default=1, nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'relation_id': self.relation_id,
            'parameter_name': self.parameter_name,
            'parameter_value': self.parameter_value,
            'create_time': self.create_time,
            'update_time': self.update_time
        }


Base.metadata.create_all(engine)
