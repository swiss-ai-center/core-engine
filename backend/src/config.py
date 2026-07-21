from enum import Enum
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


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
    model_config = SettingsConfigDict(env_file=("../.env", ".env"), extra="ignore")

    host: str = "http://localhost:8080"
    environment: Environment = Environment.PRODUCTION
    log_level: LogLevel = LogLevel.INFO
    database_url: str = "sqlite:///../core-engine.db"
    database_connect_args: dict[str, bool | str | int] = {}
    s3_access_key_id: str
    s3_secret_access_key: str
    s3_region: str = "eu-central-2"
    s3_host: str
    s3_bucket: str
    check_services_availability_interval: int = 30
    sentry_dsn: str
    # Secret used to sign JWTs and fastapi-users tokens.
    # Loaded from the AUTH_SECRET environment variable (see .env); no default
    # on purpose so the app refuses to start without one.
    auth_secret: str
    # First admin bootstrap (ADMIN_EMAIL / ADMIN_PASSWORD_HASH env vars, e.g.
    # from a Kubernetes secret): created at startup if this email does not
    # exist yet. The password is provided already hashed (bcrypt/argon2),
    # never in clear text. Both unset = bootstrap skipped.
    admin_email: str | None = None
    admin_password_hash: str | None = None
    # Authentication token lifetime, in seconds
    auth_token_ttl: int = 3600  # 1 hour


@lru_cache()
def get_settings():
    return Settings()
