import copy
import io
import os
import pytest
from common_code.logger.logger import get_logger, Logger
from testcontainers.minio import MinioContainer
from config import get_settings
from storage.service import StorageService
from fastapi import UploadFile
from fastapi.testclient import TestClient
from database import get_session
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool
from main import app
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


@pytest.fixture(name="session")
def session_fixture():
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )

    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:
        yield session


@pytest.fixture(name="client")
def client_fixture(session: Session, storage_service: StorageService):
    def get_session_override():
        return session

    def storage_service_override():
        return storage_service

    app.dependency_overrides[get_session] = get_session_override
    app.dependency_overrides[StorageService] = storage_service_override

    client = TestClient(app)

    yield client

    app.dependency_overrides.clear()


@pytest.fixture(name="misconfigured_client")
def misconfigured_client_fixture(session: Session, storage_service_wrong_bucket: StorageService):
    def get_session_override():
        return session

    def storage_service_override():
        return storage_service_wrong_bucket

    app.dependency_overrides[get_session] = get_session_override
    app.dependency_overrides[StorageService] = storage_service_override

    client = TestClient(app)

    yield client

    app.dependency_overrides.clear()


def test_storage_can_upload(client: TestClient):
    filename = "test"
    extension = ".txt"

    file = UploadFile(
        filename=f"{filename}{extension}",
        file=io.BytesIO(b"this is a test"),
    )

    response = client.post("/storage", files={
        "file": (file.filename, file.file, file.content_type)
    })

    json = response.json()
    key = json["key"]

    uuid = os.path.splitext(key)[0]

    assert key == f"{UUID(uuid)}{extension}"


def test_storage_cannot_upload(misconfigured_client: TestClient):
    file = UploadFile(
        filename="this_will_not_work.txt",
        file=io.BytesIO(b"this is an unsuccessful test"),
    )

    response = misconfigured_client.post("/storage", files={
        "file": (file.filename, file.file, file.content_type)
    })

    json = response.json()
    detail = json["detail"]

    assert response.status_code == 500
    assert detail == "File Cannot Be Uploaded"


def test_storage_can_download(client: TestClient):
    file = UploadFile(
        filename="test.txt",
        file=io.BytesIO(b"this is a test"),
    )

    response = client.post("/storage", files={
        "file": (file.filename, file.file, file.content_type)
    })

    json = response.json()
    key = json["key"]

    response = client.get(f"/storage/{key}")

    assert response.status_code == 200
    assert response.content == b"this is a test"


def test_storage_download_file_not_found(client: TestClient):
    response = client.get("/storage/file-not-found")

    json = response.json()
    detail = json["detail"]

    assert response.status_code == 404
    assert detail == "File Not Found"


def test_storage_cannot_download(misconfigured_client: TestClient):
    response = misconfigured_client.get("/storage/file-not-found")

    json = response.json()
    detail = json["detail"]

    assert response.status_code == 500
    assert detail == "File Cannot Be Checked"


def test_storage_can_delete(client: TestClient):
    file = UploadFile(
        filename="test.txt",
        file=io.BytesIO(b"this is a test"),
    )

    response = client.post("/storage", files={
        "file": (file.filename, file.file, file.content_type)
    })

    json = response.json()
    key = json["key"]

    response = client.delete(f"/storage/{key}")

    assert response.status_code == 204


def test_storage_delete_file_not_found(client: TestClient):
    response = client.delete("/storage/file-not-found")

    json = response.json()
    detail = json["detail"]

    assert response.status_code == 404
    assert detail == "File Not Found"


def test_storage_cannot_delete(misconfigured_client: TestClient):
    response = misconfigured_client.delete("/storage/file-not-found")

    json = response.json()
    detail = json["detail"]

    assert response.status_code == 500
    assert detail == "File Cannot Be Checked"

#
# def test_delete_file(client: TestClient):
#     file_to_upload = open("tests/test.json", "rb")
#
#     response = client.post("/storage", files={"file": file_to_upload})
#     json = response.json()
#     file_key = json["key"]
#
#     response = client.delete(f"/storage/{file_key}")
#
#     assert response.status_code == 204
#
#
# def test_download_wrong_file(client: TestClient):
#     response = client.get("/storage/wrong_file_key")
#
#     assert response.status_code == 404
#
#
# def test_delete_wrong_file(client: TestClient):
#     response = client.delete("/storage/wrong_file_key")
#
#     assert response.status_code == 404
#
#
# @pytest.mark.asyncio
# async def test_get_file_as_bytes(storage: StorageService):
#     file_to_upload = UploadFile(filename="test.json", file=open("tests/test.json", "rb"))
#     file_key = await storage.upload(file_to_upload)
#
#     file = await storage.get_file_as_bytes(file_key)
#     assert file == b'{"test": "this is a text file for testing purposes"}\n'
#
#
# @pytest.mark.asyncio
# async def test_get_file_as_chunks(storage: StorageService):
#     file_to_upload = UploadFile(filename="test.json", file=open("tests/test.json", "rb"))
#     file_key = await storage.upload(file_to_upload)
#
#     chunks = []
#     for chunk in await storage.get_file_as_chunks(file_key):
#         chunks.append(chunk)
#
#     assert bytes(chunks) == b'{"test": "this is a text file for testing purposes"}\n'
#
#
# def test_upload_file_with_misconfigured_client(misconfigured_client: TestClient):
#     file_to_upload = open("tests/test.json", "rb")
#
#     response = misconfigured_client.post("/storage", files={"file": file_to_upload})
#
#     assert response.status_code == 500
#
#
# @pytest.mark.asyncio
# async def test_check_storage_availability(storage: StorageService):
#     with pytest.raises(SystemExit) as e:
#         await storage.check_storage_availability()
#     assert e.type == SystemExit
#     assert e.value.code == 1
