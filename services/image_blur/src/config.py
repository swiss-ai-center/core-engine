from enum import Enum
from functools import lru_cache
from pydantic import BaseSettings


class Environment(str, Enum):
    PRODUCTION = "production"
    DEVELOPMENT = "development"
    TEST = "test"


class LogLevel(str, Enum):
    CRITICAL = "critical"
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"
    DEBUG = "debug"


class Settings(BaseSettings):
    engine_url: str = "http://localhost:8000"
    service_url: str = "http://localhost:8001"
    environment: Environment = Environment.PRODUCTION
    max_tasks: int = 50
    log_level: LogLevel = LogLevel.INFO
    engine_announce_retries: int = 5
    engine_announce_retry_delay: int = 3

    class Config:
        env_file = "../.env"


@lru_cache()
def get_settings():
    return Settings()
