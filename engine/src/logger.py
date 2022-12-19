import logging
import os


class Logger:
    def __init__(self):
        self.logger = logging.getLogger('uvicorn')
        self.logger.setLevel(os.environ["APP_LOG_LEVEL"] if "APP_LOG_LEVEL" in os.environ else "INFO")

    def set_level(self, level):
        self.logger.setLevel(level)

    def debug(self, message):
        self.logger.debug(message)

    def info(self, message):
        self.logger.info(message)

    def warning(self, message):
        self.logger.warning(message)

    def error(self, message):
        self.logger.error(message)

    def critical(self, message):
        self.logger.critical(message)
