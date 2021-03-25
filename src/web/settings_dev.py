from pydantic import BaseSettings


class AppSettings(BaseSettings):

    debug: bool = True
    logger_level: str = "DEBUG"


class Settings(AppSettings):
    pass


settings = Settings()
