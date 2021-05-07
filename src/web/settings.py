import os
from pydantic import BaseSettings


class AppSettings(BaseSettings):

    debug: bool = False
    time_zone: str = "Asia/Shanghai"
    logger_level: str = "INFO"
    logger_formatter: str = "%(asctime)s [%(name)s] %(funcName)s[line:%(lineno)d] %(levelname)-7s: %(message)s"
    secret_key: str = "1@3$5^7*9)"


class DatabaseSettings(BaseSettings):
    _db_port = os.getenv("POSTGRESQL_PORT") or "5432"
    _db_password = os.getenv("REDIS_PASSWORD") or "password"
    fastapi_uri: str = f"postgresql+asyncpg://postgres:{_db_password}@fastapi-postgresql:{_db_port}/fastapi"


class RedisSettings(BaseSettings):
    _redis_port = os.getenv("REDIS_PORT") or "6379"
    _redis_password = os.getenv("REDIS_PASSWORD") or "password"
    fastapi_redis_uri: str = f"redis://:{_redis_password}@fastapi-redis:{_redis_port}/0?encoding=utf-8"


class DataFileSettings(BaseSettings):

    basedir: str = "/app/web/data"
    runtimedir: str = "/app/runtimedir"


class Settings(AppSettings, DatabaseSettings, RedisSettings, DataFileSettings):
    pass


settings = Settings()

env = os.getenv("FASTAPI_ENV")
print(f"FASTAPI_ENV = {env}")
if env == "development":
    from settings_dev import settings as dev_settings
    for k, v in dev_settings:
        if hasattr(settings, k):
            setattr(settings, k, v)
elif env == "test":
    from settings_test import settings as test_settings
    for k, v in test_settings:
        if hasattr(settings, k):
            setattr(settings, k, v)
