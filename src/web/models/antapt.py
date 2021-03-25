
import typing

from sqlalchemy import Column
from sqlalchemy import String, Integer

from db.antapt import ModelBase


class Users(ModelBase):
    __tablename__ = "users"

    ROLE_ADMIN = "admin"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(32), unique=True, index=True, nullable=False)
    salt = Column(String(32), nullable=False)
    password = Column(String(32), nullable=False)
    role = Column(String(10), nullable=False)

    def __repr__(self) -> str:
        return f"<User(username={self.username}, role={self.role}"

    def as_dict(self) -> typing.Dict:
        return {
            "uid": self.id,
            "username": self.username,
            "role": self.role
        }
