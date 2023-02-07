import pytest
from logger.logger import get_logger
from config import get_settings
from storage.service import StorageService
from fastapi import UploadFile
from fastapi.testclient import TestClient
from database import get_session
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool
from main import app


@pytest.fixture(name="storage")
def storage_fixture():
    settings = get_settings()
    logger = get_logger(settings)

    storage = StorageService(logger=logger, settings=settings)

    yield storage


@pytest.fixture(name="session")
def session_fixture():
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )

    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:
        yield session


@pytest.fixture(name="client")
def client_fixture(session: Session):
    def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override

    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


@pytest.fixture(name="misconfigured_client")
def misconfigured_client_fixture(session: Session):
    def get_session_override():
        return session

    def get_settings_override():
        settings = get_settings()
        settings.s3_host = "http://wrong-s3.host"

        return settings

    app.dependency_overrides[get_session] = get_session_override
    app.dependency_overrides[get_settings] = get_settings_override

    with TestClient(app) as client:
        yield client
    app.dependency_overrides.clear()


def test_upload_file(client: TestClient):
    file_to_upload = open("tests/test.json", "rb")

    response = client.post("/storage", files={"file": file_to_upload})
    json = response.json()
    file_key = json["key"]
    file_extension = file_key.split(".")[1]

    assert response.status_code == 200
    assert file_extension == "json"


def test_download_file(client: TestClient):
    file_to_upload = open("tests/test.json", "rb")

    response = client.post("/storage", files={"file": file_to_upload})
    json = response.json()
    file_key = json["key"]

    response = client.get(f"/storage/{file_key}")

    assert response.status_code == 200
    assert response.content == b'{"test": "this is a text file for testing purposes"}\n'


def test_delete_file(client: TestClient):
    file_to_upload = open("tests/test.json", "rb")

    response = client.post("/storage", files={"file": file_to_upload})
    json = response.json()
    file_key = json["key"]

    response = client.delete(f"/storage/{file_key}")

    assert response.status_code == 204


def test_download_wrong_file(client: TestClient):
    response = client.get("/storage/wrong_file_key")

    assert response.status_code == 404


def test_delete_wrong_file(client: TestClient):
    response = client.delete("/storage/wrong_file_key")

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_file_as_bytes(storage: StorageService):
    file_to_upload = UploadFile(filename="test.json", file=open("tests/test.json", "rb"))
    file_key = await storage.upload(file_to_upload)

    file = await storage.get_file_as_bytes(file_key)
    assert file == b'{"test": "this is a text file for testing purposes"}\n'


@pytest.mark.asyncio
async def test_get_file_as_chunks(storage: StorageService):
    file_to_upload = UploadFile(filename="test.json", file=open("tests/test.json", "rb"))
    file_key = await storage.upload(file_to_upload)

    chunks = []
    async for chunk in storage.get_file_as_chunks(file_key):
        chunks.append(chunk)

    assert b"".join(chunks) == b'{"test": "this is a text file for testing purposes"}\n'


def test_upload_file_with_misconfigured_client(misconfigured_client: TestClient):
    file_to_upload = open("tests/test.json", "rb")

    response = misconfigured_client.post("/storage", files={"file": file_to_upload})

    assert response.status_code == 500


@pytest.mark.asyncio
async def test_check_storage_availability(storage: StorageService):
    with pytest.raises(SystemExit) as e:
        await storage.check_storage_availability()
    assert e.type == SystemExit
    assert e.value.code == 1
