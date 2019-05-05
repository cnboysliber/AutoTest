# -*- coding:utf-8 -*-
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from application import engine

Base = declarative_base()


class Parameter(Base):
    __tablename__ = 'parameter'
    __table_args__ = {
        "mysql_engine": "InnoDB",
        "mysql_charset": "utf8"
    }

    id = Column(Integer, primary_key=True)
    parameter_name = Column(String(128), nullable=False, unique=True)
    value = Column(String(1000), nullable=False)
    create_by = Column(String(50), nullable=False)
    create_time = Column(DateTime, default=datetime.utcnow)
    update_time = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'parameter_name': self.parameter_name,
            'value': self.value,
            'create_by': self.create_by,
            'create_time': self.create_time,
            'update_time': self.update_time
        }


Base.metadata.create_all(engine)
