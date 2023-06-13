import pytest
from testcontainers.minio import MinioContainer

from config import get_settings


@pytest.fixture(scope="session", autouse=True, name="minio")
def minio_fixture():
    settings = get_settings()

    config = MinioContainer(
        access_key=settings.s3_access_key_id,
        secret_key=settings.s3_secret_access_key,
    )

    with config as minio:
        client = minio.get_client()
        client.make_bucket(settings.s3_bucket)

        yield minio
