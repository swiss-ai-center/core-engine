import copy
import io
import os
import pytest
from common_code.logger.logger import get_logger, Logger
from fastapi import UploadFile, HTTPException
from testcontainers.minio import MinioContainer

from storage.service import StorageService
import storage.controller as storage_controller
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


@pytest.fixture(name="storage_service_wrong_bucket")
def storage_service_wrong_bucket_fixture(logger: Logger, minio: MinioContainer):
    settings = copy.deepcopy(get_settings())

    settings.s3_host = f"http://localhost:{minio.get_exposed_port(9000)}"
    settings.s3_bucket = "bucket-not-found"

    storage_service = StorageService(logger=logger, settings=settings)

    yield storage_service


@pytest.mark.asyncio
async def test_storage_controller_can_upload(storage_service: StorageService):
    filename = "test"
    extension = ".txt"

    file = UploadFile(
        filename=f"{filename}{extension}",
        file=io.BytesIO(b"this is a test"),
    )

    response = await storage_controller.upload(
        file=file,
        storage_service=storage_service,
    )

    key = response.key

    uuid = os.path.splitext(key)[0]

    assert key == f"{UUID(uuid)}{extension}"


@pytest.mark.asyncio
async def test_storage_controller_cannot_upload(storage_service_wrong_bucket: StorageService):
    with pytest.raises(HTTPException) as exception_info:
        await storage_controller.upload(
            file=UploadFile(
                filename="this_will_not_work.txt",
                file=io.BytesIO(b"this is an unsuccessful test"),
            ),
            storage_service=storage_service_wrong_bucket,
        )

    exception = exception_info.value

    assert exception.status_code == 500
    assert exception.detail == "File Cannot Be Uploaded"


@pytest.mark.asyncio
async def test_storage_controller_can_download(storage_service: StorageService, logger: Logger):
    file = UploadFile(
        filename="test.txt",
        file=io.BytesIO(b"this is a test"),
    )

    response = await storage_controller.upload(
        file=file,
        storage_service=storage_service,
    )

    key = response.key

    response = await storage_controller.download(
        key=key,
        storage_service=storage_service,
        logger=logger,
    )

    chunks = [chunk async for chunk in response.body_iterator]

    # Reset the stream
    await file.seek(0)

    assert await file.read() == b"".join(chunks)


@pytest.mark.asyncio
async def test_storage_controller_download_file_not_found(storage_service: StorageService, logger: Logger):
    with pytest.raises(HTTPException) as exception_info:
        await storage_controller.download(
            key="file-not-found",
            storage_service=storage_service,
            logger=logger,
        )

    exception = exception_info.value

    assert exception.status_code == 404
    assert exception.detail == "File Not Found"


@pytest.mark.asyncio
async def test_storage_controller_cannot_download(storage_service_wrong_bucket: StorageService, logger: Logger):
    with pytest.raises(HTTPException) as exception_info:
        await storage_controller.download(
            key="file-not-found",
            storage_service=storage_service_wrong_bucket,
            logger=logger,
        )

    exception = exception_info.value

    assert exception.status_code == 500
    assert exception.detail == "File Cannot Be Checked"


@pytest.mark.asyncio
async def test_storage_controller_can_delete(storage_service: StorageService, logger: Logger):
    file = UploadFile(
        filename="test.txt",
        file=io.BytesIO(b"this is a test"),
    )

    response = await storage_controller.upload(
        file=file,
        storage_service=storage_service,
    )

    key = response.key

    response = await storage_controller.delete(
        key=key,
        storage_service=storage_service,
        logger=logger,
    )

    assert response is None


@pytest.mark.asyncio
async def test_storage_controller_delete_file_not_found(storage_service: StorageService, logger: Logger):
    with pytest.raises(HTTPException) as exception_info:
        await storage_controller.delete(
            key="file-not-found",
            storage_service=storage_service,
            logger=logger,
        )

    exception = exception_info.value

    assert exception.status_code == 404
    assert exception.detail == "File Not Found"


@pytest.mark.asyncio
async def test_storage_controller_cannot_delete(storage_service_wrong_bucket: StorageService, logger: Logger):
    with pytest.raises(HTTPException) as exception_info:
        await storage_controller.delete(
            key="file-not-found",
            storage_service=storage_service_wrong_bucket,
            logger=logger,
        )

    exception = exception_info.value

    assert exception.status_code == 500
    assert exception.detail == "File Cannot Be Checked"
