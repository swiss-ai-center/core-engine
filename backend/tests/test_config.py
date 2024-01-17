from config import get_settings, Environment, LogLevel


def test_config_from_env_file():
    settings = get_settings()

    assert settings.host == "http://localhost:8080"
    assert settings.environment == Environment.DEVELOPMENT
    assert settings.log_level == LogLevel.DEBUG
    assert settings.database_url == "sqlite:///../core-engine.db"
    assert settings.database_connect_args == {"check_same_thread": 0}
    assert settings.s3_access_key_id == "minio"
    assert settings.s3_secret_access_key == "minio123"
    assert settings.s3_region == "eu-central-2"
    assert settings.s3_host == "http://localhost:9000"
    assert settings.s3_bucket == "engine"
    assert settings.check_services_availability_interval == 30
