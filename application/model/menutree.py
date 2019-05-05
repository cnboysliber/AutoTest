from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base

from application import engine

Base = declarative_base()


class BusinessLine(Base):
    __tablename__ = 'business_line'
    __table_args__ = {
        "mysql_engine": "InnoDB",
        "mysql_charset": "utf8"
    }

    id = Column(Integer, primary_key=True)
    business_name = Column(String(100), nullable=True)
    # create_time = Column(DateTime, default=datetime.utcnow)
    # update_time = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    status = Column(Integer, default=1, nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'business_name': self.business_name,
        }


class SystemLine(Base):
    __tablename__ = 'system_line'
    __table_args__ = {
        "mysql_engine": "InnoDB",
        "mysql_charset": "utf8"
    }

    id = Column(Integer, primary_key=True)
    business_line_id = Column(Integer, nullable=True)
    system_name = Column(String(100), nullable=True)
    # create_time = Column(DateTime, default=datetime.utcnow)
    # update_time = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    status = Column(Integer, default=1, nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'business_line_id': self.business_line_id,
            'system_name': self.system_name
        }


class FunctionLine(Base):
    __tablename__ = 'function_line'
    __table_args__ = {
        "mysql_engine": "InnoDB",
        "mysql_charset": "utf8"
    }

    id = Column(Integer, primary_key=True)
    system_line_id = Column(Integer, nullable=True)
    function_name = Column(String(100), nullable=True)
    # create_time = Column(DateTime, default=datetime.utcnow)
    # update_time = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    status = Column(Integer, default=1, nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'system_line_id': self.system_line_id,
            'function_name': self.function_name,
        }


Base.metadata.create_all(engine)
