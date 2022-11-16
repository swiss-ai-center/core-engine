from functools import lru_cache
from pydantic import BaseSettings

class Settings(BaseSettings):
    app_name: str = "Awesome API"
    admin_email: str
    items_per_user: int = 50

    class Config:
        env_file = "../.env"

@lru_cache()
def get_settings():
    return Settings()
