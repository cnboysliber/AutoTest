# -*- coding:utf-8 -*-

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, TEXT
from sqlalchemy.ext.declarative import declarative_base

from application import engine

Base = declarative_base()


class Interface(Base):
    __tablename__ = 'interface'
    __table_args__ = {
        "mysql_engine": "InnoDB",
        "mysql_charset": "utf8"
    }

    id = Column(Integer, primary_key=True)
    interface_name = Column(String(100), nullable=False)
    interface_entry = Column(Integer, nullable=False)  # 入口
    interface_encryption = Column(Integer, nullable=False, default=0)
    interface_url = Column(String(1000), nullable=False)
    interface_method = Column(String(20), nullable=False)
    interface_header = Column(String(1000))
    interface_json_payload = Column(TEXT)
    body_type = Column(Integer, nullable=False, default=0)  # 消息体类型， 0为json， 1为form
    create_by = Column(String(50), nullable=False)
    create_time = Column(DateTime, default=datetime.utcnow)
    update_time = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    status = Column(Integer, default=1, nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'interface_name': self.interface_name,
            'interface_entry': self.interface_entry,
            'interface_encryption': self.interface_encryption,
            'interface_url': self.interface_url,
            'interface_method': self.interface_method,
            'interface_header': self.interface_header,
            'interface_json_payload': self.interface_json_payload,
            'create_by': self.create_by,
            'create_time': self.create_time,
            'update_time': self.update_time,
            'body_type': self.body_type
        }


Base.metadata.create_all(engine)
