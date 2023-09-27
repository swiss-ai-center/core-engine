import copy
import io
import os
import pytest
from botocore.exceptions import ClientError
from common_code.logger.logger import get_logger, Logger
from fastapi import UploadFile
from testcontainers.minio import MinioContainer

from common.exceptions import NotFoundException, InternalServerErrorException
from storage.service import StorageService
from config import get_settings
from uuid import UUID


@pytest.fixture(name="logger")
def logger_fixture():
    settings = get_settings()
    logger = get_logger(settings)

    yield logger


@pytest.fixture(name="storage_service")
def storage_service_fixture(logger: Logger, minio: MinioContainer):
    settings = get_settings()

    settings.s3_host = f"http://localhost:{minio.get_exposed_port(9000)}"

    storage_service = StorageService(logger=logger, settings=settings)

    yield storage_service


@pytest.fixture(name="storage_service_wrong_s3_host")
def storage_service_wrong_s3_host_fixture(logger: Logger):
    settings = copy.deepcopy(get_settings())

    settings.s3_host = "http://host-not-found.localhost"

    storage_service = StorageService(logger=logger, settings=settings)

    yield storage_service


@pytest.fixture(name="storage_service_wrong_bucket")
def storage_service_wrong_bucket_fixture(logger: Logger, minio: MinioContainer):
    settings = copy.deepcopy(get_settings())

    settings.s3_host = f"http://localhost:{minio.get_exposed_port(9000)}"
    settings.s3_bucket = "bucket-not-found"

    storage_service = StorageService(logger=logger, settings=settings)

    yield storage_service


@pytest.mark.asyncio
async def test_storage_service_can_connect(storage_service: StorageService):
    await storage_service.check_storage_availability()


@pytest.mark.asyncio
async def test_storage_service_cannot_connect(storage_service_wrong_s3_host: StorageService):
    with pytest.raises(SystemExit):
        await storage_service_wrong_s3_host.check_storage_availability()


@pytest.mark.asyncio
async def test_storage_service_can_upload(storage_service: StorageService):
    filename = "test"
    extension = ".txt"

    key = await storage_service.upload(
        UploadFile(
            filename=f"{filename}{extension}",
            file=io.BytesIO(b"this is a test"),
        )
    )

    uuid = os.path.splitext(key)[0]

    assert key == f"{UUID(uuid)}{extension}"


@pytest.mark.asyncio
async def test_storage_service_cannot_upload(storage_service_wrong_bucket: StorageService):
    with pytest.raises(InternalServerErrorException, match="File Cannot Be Uploaded"):
        await storage_service_wrong_bucket.upload(
            UploadFile(
                filename="this_will_not_work.txt",
                file=io.BytesIO(b"this is an unsuccessful test"),
            )
        )


@pytest.mark.asyncio
async def test_storage_service_check_if_file_exists(storage_service: StorageService):
    key = await storage_service.upload(
        UploadFile(
            filename="test.txt",
            file=io.BytesIO(b"this is a test"),
        )
    )

    await storage_service.check_if_file_exists(key)


@pytest.mark.asyncio
async def test_storage_service_check_if_file_exists_file_not_found(storage_service: StorageService):
    with pytest.raises(NotFoundException, match="File Not Found"):
        await storage_service.check_if_file_exists("file-not-found")


@pytest.mark.asyncio
async def test_storage_service_check_if_file_exists_bucket_not_found(storage_service_wrong_bucket: StorageService):
    with pytest.raises(InternalServerErrorException, match="File Cannot Be Checked"):
        await storage_service_wrong_bucket.check_if_file_exists("file-not-found")


@pytest.mark.asyncio
async def test_storage_service_get_file_as_bytes(storage_service: StorageService):
    file = UploadFile(
        filename="test.txt",
        file=io.BytesIO(b"this is a test"),
    )

    key = await storage_service.upload(file)

    uploaded_file = await storage_service.get_file_as_bytes(key)

    # Reset the stream
    await file.seek(0)

    assert await file.read() == uploaded_file


@pytest.mark.asyncio
async def test_storage_service_get_file_as_chunks(storage_service: StorageService):
    file = UploadFile(
        filename="test.txt",
        file=io.BytesIO(b"this is a test"),
    )

    key = await storage_service.upload(file)

    chunks = [chunk async for chunk in storage_service.get_file_as_chunks(key)]

    # Reset the stream
    await file.seek(0)

    assert await file.read() == b"".join(chunks)


@pytest.mark.asyncio
async def test_storage_service_delete_file(storage_service: StorageService):
    key = await storage_service.upload(
        UploadFile(
            filename="test.txt",
            file=io.BytesIO(b"this is a test"),
        )
    )

    await storage_service.check_if_file_exists(key)

    await storage_service.delete(key)

    with pytest.raises(NotFoundException, match="File Not Found"):
        await storage_service.check_if_file_exists(key)


@pytest.mark.asyncio
async def test_storage_service_delete_nonexistent_file(storage_service: StorageService):
    await storage_service.delete("file-not-found")


@pytest.mark.asyncio
async def test_storage_service_delete_bucket_not_found(storage_service_wrong_bucket: StorageService):
    with pytest.raises(ClientError, match="The specified bucket does not exist"):
        await storage_service_wrong_bucket.delete("file-not-found")
