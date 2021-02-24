
import typing
import datetime

from sqlalchemy import Column, text
from sqlalchemy import String, DateTime, Integer

from db.antapt import ModelBase


class Users(ModelBase):
    __tablename__ = "users"

    ROLE_ADMIN = 'admin'
    ROLE_LOG = 'log'
    ROLE_AUDIT = 'audit'

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(32), unique=True, index=True, nullable=False)
    password = Column(String(32), nullable=False)
    salt = Column(String(32), nullable=False)
    role = Column(String(10), nullable=False)
    last_login_time = Column(DateTime, server_default=text('NOW()'), default=datetime.datetime.now)

    def as_dict(self) -> typing.Dict:
        return {
            "id": self.id,
            "username": self.username,
            "role": self.role,
            "last_login_time": self.last_login_time.strftime("%Y-%m-%d %H:%M:%S")
        }
