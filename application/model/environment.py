# -*- coding:utf-8 -*-
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, SmallInteger
from sqlalchemy.ext.declarative import declarative_base

from application import engine

Base = declarative_base()


class EnvironmentLine(Base):
    __tablename__ = 'environment_line'
    __table_args__ = {
        "mysql_engine": "InnoDB",
        "mysql_charset": "utf8"
    }
    id = Column(Integer, primary_key=True)
    environment_name = Column(String(100), nullable=False)
    status = Column(SmallInteger, default=1, nullable=False)
    create_time = Column(DateTime, default=datetime.utcnow)
    update_time = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'environment_name': self.environment_name,
            'status': self.status,
            'create_time': self.create_time,
            'update_time': self.update_time
        }


class EnvironmentInfo(Base):
    __tablename__ = 'environment_line_info'
    __table_args__ = {
        "mysql_engine": "InnoDB",
        "mysql_charset": "utf8"
    }
    id = Column(Integer, primary_key=True)
    environment_id = Column(Integer, nullable=False)
    status = Column(SmallInteger, default=1, nullable=False)
    url = Column(String(100), nullable=False)
    map_ip = Column(String(100), nullable=False)
    create_time = Column(DateTime, default=datetime.utcnow)
    update_time = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'environment_id': self.environment_id,
            'status': self.status,
            'url': self.url,
            'map_ip': self.map_ip,
            'create_time': self.create_time,
            'update_time': self.update_time
        }


Base.metadata.create_all(engine)
