from sqlalchemy.ext.mutable import Mutable
from sqlalchemy import create_engine, event, cast
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker
from sqlalchemy.dialects.postgresql import ARRAY

from utils.singleton_utils import Singleton


def register_db_event(db):

    def handle_error(exception_context):
        conn = db.session.connection()
        if conn.in_transaction():
            db.session.rollback()

        if exception_context.is_disconnect is True:
            db._engine.dispose()
            # 重建连接池
            if getattr(db._engine, "pool", None):
                db._engine.pool = db._engine.pool.recreate()

    event.listen(db._engine, "handle_error", handle_error)


class Database(metaclass=Singleton):

    def __init__(self, base, uri: str, pool_size: int = 10, pool_recycle: int = 3600) -> None:
        self.base = base
        self._engine = create_engine(
            uri,
            echo=False,
            encoding="utf-8",
            pool_size=pool_size,
            pool_recycle=pool_recycle)
        self.session = self.make_session()
        register_db_event(self)

    def create_tables(self) -> None:
        self.base.metadata.create_all(self._engine)

    def make_session(self):
        session_factory = sessionmaker(autocommit=False, autoflush=False, bind=self._engine)
        session_class = scoped_session(session_factory)
        return session_class()

    def close(self):
        self.session.close()


class JSONArray(ARRAY):
    """
    sqlalchemy暂不支持 ARRAY(JSON) 类型。使用此类可实现
    """
    def bind_expression(self, bindvalue):
        return cast(bindvalue, self)


class MutableList(Mutable, list):

    def __setitem__(self, key, value):
        list.__setitem__(self, key, value)
        self.changed()

    def __delitem__(self, key):
        list.__delitem__(self, key)
        self.changed()

    def append(self, value):
        list.append(self, value)
        self.changed()

    def pop(self, index=0):
        value = list.pop(self, index)
        self.changed()
        return value

    @classmethod
    def coerce(cls, key, value):
        if not isinstance(value, MutableList):
            if isinstance(value, list):
                return MutableList(value)
            return Mutable.coerce(key, value)
        else:
            return value
