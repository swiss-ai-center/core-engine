from functools import lru_cache
from pydantic import BaseSettings


class Settings(BaseSettings):
    aws_access_key_id: str
    aws_secret_access_key: str
    aws_region: str = "eu-central-2"
    database_url: str = "sqlite:///../engine.db"
    database_connect_args: dict[str, bool | str | int] = {"check_same_thread": False}
    s3_host: str
    s3_bucket_name: str
    s3_multipart_bytes_per_chunk: int
    s3_multiparts_deletation_days_if_transfer_fails: int

    class Config:
        env_file = "../.env"


@lru_cache()
def get_settings():
    return Settings()
