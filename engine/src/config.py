from enum import Enum
from functools import lru_cache
from pydantic import BaseSettings


class Environment(str, Enum):
    PRODUCTION = "production"
    DEVELOPMENT = "development"
    TEST = "test"

    CRITICAL
ERROR
WARNING
INFO
DEBUG
NOTSET


class LogLevel(str, Enum):
    PRODUCTION = "production"
    DEVELOPMENT = "development"
    TEST = "test"

class Settings(BaseSettings):
    environment: Environment = Environment.PRODUCTION
    log_level: 
    aws_access_key_id: str
    aws_secret_access_key: str
    aws_region: str = "eu-central-2"
    database_url: str = "sqlite:///../engine.db"
    database_connect_args: dict[str, bool | str | int] = {"check_same_thread": False}
    s3_host: str
    s3_bucket: str

    class Config:
        env_file = "../.env"


@lru_cache()
def get_settings():
    return Settings()
