from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base

from application import engine

Base = declarative_base()


class Batch(Base):
    __tablename__ = 'batch'
    __table_args__ = {
        "mysql_engine": "InnoDB",
        "mysql_charset": "utf8"
    }

    id = Column(Integer, primary_key=True)
    batch_name = Column(String(100), nullable=False)
    environment_id = Column(Integer, nullable=False, default=0)
    auto_run = Column(Boolean, nullable=False, default=False)
    alarm_monitor = Column(Boolean, nullable=False, default=False)
    create_by = Column(String(50), nullable=False)
    create_time = Column(DateTime, default=datetime.utcnow)
    update_time = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    status = Column(Integer, default=1, nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'batch_name': self.batch_name,
            'environment_id': self.environment_id,
            'auto_run': self.auto_run,
            'alarm_monitor': self.alarm_monitor,
            'create_by': self.create_by,
            'create_time': self.create_time,
            'update_time': self.update_time
        }


class BatchUseCaseRelation(Base):
    __tablename__ = 'batch_use_case_relation'
    __table_args__ = {
        "mysql_engine": "InnoDB",
        "mysql_charset": "utf8"
    }

    id = Column(Integer, primary_key=True)
    batch_id = Column(Integer, nullable=False)
    use_case_id = Column(Integer, nullable=False)
    create_time = Column(DateTime, default=datetime.utcnow)
    update_time = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    status = Column(Integer, default=1, nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'batch_id': self.batch_id,
            'use_case_id': self.use_case_id,
            'create_time': self.create_time,
            'update_time': self.update_time
        }


Base.metadata.create_all(engine)
