from fastapi import Depends
from config import Settings, get_settings
import logging


class Logger:
    PADDING = '\t'

    def __init__(self, settings: Settings = Depends(get_settings)):
        self.source = __name__
        self.logger = logging.getLogger('uvicorn')
        self.set_level(settings.log_level.value.upper())

    def set_level(self, level):
        self.logger.setLevel(level)

    def set_source(self, source):
        self.source = source

    def debug(self, message):
        self.logger.debug(f'[{self.source}]: {self.PADDING}{message}')

    def info(self, message):
        self.logger.info(f'[{self.source}]: {self.PADDING}{message}')

    def warning(self, message):
        self.logger.warning(f'[{self.source}]: {self.PADDING}{message}')

    def error(self, message):
        self.logger.error(f'[{self.source}]: {self.PADDING}{message}')

    def critical(self, message):
        self.logger.critical(f'[{self.source}]: {self.PADDING}{message}')


def get_logger(settings=Depends(get_settings)):
    return Logger(settings)
