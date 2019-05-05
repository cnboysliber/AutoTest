from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base

from application import engine


Base = declarative_base()


class Encryption(Base):
    __tablename__ = 'encryption_ways'
    __table_args__ = {
        "mysql_engine": "InnoDB",
        "mysql_charset": "utf8"
    }

    id = Column(Integer, primary_key=True)
    encryption_name = Column(String(100), nullable=False, unique=True)
    encryption_method_name = Column(String(100), nullable=False, unique=True)
    create_time = Column(DateTime, default=datetime.utcnow)
    update_time = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'encryption_name': self.encryption_name,
            'encryption_method_name': self.encryption_method_name
        }


Base.metadata.create_all(engine)