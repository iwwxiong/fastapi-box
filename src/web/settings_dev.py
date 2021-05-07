from pydantic import BaseSettings


class AppSettings(BaseSettings):

    debug: bool = True
    logger_level: str = "DEBUG"


class DatabaseSettings(BaseSettings):
    fastapi_uri: str = "postgresql+asyncpg://postgres:Foxconn123@127.0.0.1:15432/fastapi"


class RedisSettings(BaseSettings):
    fastapi_redis_uri: str = "redis://:Foxconn123@127.0.0.1:16379/0?encoding=utf-8"


class Settings(AppSettings, DatabaseSettings, RedisSettings):
    pass


settings = Settings()
