from pydantic import BaseSettings


class AppSettings(BaseSettings):

    debug: bool = False
    time_zone: str = "Asia/Shanghai"
    logger_level: str = "INFO"
    logger_formatter: str = "%(asctime)s [%(name)s] %(funcName)s[line:%(lineno)d] %(levelname)-7s: %(message)s"
    secret_key: str = "0123456789abcdefghijklmnopqrstuvwxyz"


class DatabaseSettings(BaseSettings):

    antapt_uri = "postgresql://postgres:password@127.0.0.1:15432/iwwxiong"


class RedisSettings(BaseSettings):

    webapi_redis_uri = "redis://:password@127.0.0.1:16379/0?encoding=utf-8"


class Settings(AppSettings, DatabaseSettings, RedisSettings):
    pass


settings = Settings()
