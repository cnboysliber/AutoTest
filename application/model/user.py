# -*- coding:utf-8 -*-
from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.ext.declarative import declarative_base
from application import engine

Base = declarative_base()


class User(Base):
    __tablename__ = 'user'
    __table_args__ = {
        "mysql_engine": "InnoDB",
        "mysql_charset": "utf8"
    }

    id = Column(Integer, primary_key=True)
    username = Column(String(20), nullable=False, unique=True)
    password = Column(String(100))
    superuser = Column(Boolean, default=False, nullable=False)
    full_name = Column(String(50), nullable=False)
    email = Column(String(50))
    create_time = Column(DateTime, default=datetime.utcnow)
    update_time = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    status = Column(Integer, default=1, nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'superuser': self.superuser,
            'full_name': self.full_name,
            'email': self.email
        }


Base.metadata.create_all(engine)
