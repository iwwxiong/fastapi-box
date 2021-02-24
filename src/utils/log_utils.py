import logging

from settings import settings


class LoggerHelper(object):

    def __init__(
        self, name: str,
        level: str = settings.logger_level,
        formatter: str = settings.logger_formatter,
        datefmt: str = "%Y-%m-%d %H:%M:%S"
    ):
        self.name = name
        self.level = level
        self.format = formatter
        self.datefmt = datefmt

    def get_logger(self):
        logging.getLogger("requests").setLevel(logging.WARNING)
        logging.getLogger("urllib3").setLevel(logging.WARNING)
        logging.basicConfig(
            level=self.level,
            format=self.format,
            datefmt=self.datefmt
        )

        logger = logging.getLogger(self.name)

        return logger
