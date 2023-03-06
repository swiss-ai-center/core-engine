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
    host: str = "http://localhost:8080"
    environment: Environment = Environment.PRODUCTION
    log_level: LogLevel = LogLevel.INFO
    database_url: str = "sqlite:///../engine.db"
    database_connect_args: dict[str, bool | str | int] = {"check_same_thread": False}
    s3_access_key_id: str
    s3_secret_access_key: str
    s3_region: str = "eu-central-2"
    s3_host: str
    s3_bucket: str
    check_services_availability_interval: int = 30

    class Config:
        env_file = "../.env"


@lru_cache()
def get_settings():
    return Settings()
