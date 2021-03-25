import datetime

from sqlalchemy import Column, text
from sqlalchemy import Integer, DateTime
from sqlalchemy.ext.declarative import declarative_base

from settings import settings
from .base import Database


AntaptBase = declarative_base(name='AntaptBase')


class ModelBase(AntaptBase):
    __abstract__ = True

    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    create_time = Column(DateTime, server_default=text('NOW()'), default=datetime.datetime.now)
    update_time = Column(DateTime, server_default=text('NOW()'), default=datetime.datetime.now)

    def as_dict(self):
        d = {}
        for column in self.__table__.columns:
            value = getattr(self, column.name)
            if isinstance(value, datetime.datetime):
                d[column.name] = value.strftime("%Y-%m-%d %H:%M:%S")
            else:
                d[column.name] = value

        return d

    @classmethod
    def get_fields(cls):
        return [column.name for column in cls.__table__.columns]


class AntaptDatabase(Database):

    def __init__(self, pool_size: int = 10, pool_recycle: int = 3600):
        super().__init__(
            base=AntaptBase,
            uri=settings.antapt_uri,
            pool_size=pool_size,
            pool_recycle=pool_recycle
        )
