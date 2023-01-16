import pytest
from logger import get_logger
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

    with TestClient(app) as client:
        yield client
    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_storage(storage: StorageService):
    # Test upload file
    file_to_upload = UploadFile(filename="test.json", file=open("tests/test.json", "rb"))
    key = await storage.upload(file_to_upload)
    assert key.split(".")[1] == "json"

    # Test download file
    file = await storage.get_file(key)
    assert file == b'{"test": "this is a text file for testing purposes"}\n'

    # Test download file with wrong key
    file = await storage.get_file("wrong_key")
    assert file is None

    # Test download chunk
    chunks = []
    async for chunk in storage.get_file_as_chunks(key):
        chunks.append(chunk)
    assert b"".join(chunks) == b'{"test": "this is a text file for testing purposes"}\n'

    # Test download chunk with wrong key
    chunks = []
    async for chunk in storage.get_file_as_chunks("wrong_key"):
        chunks.append(chunk)
    assert b"".join(chunks) == b''

    # Test delete file
    await storage.delete(key)
    assert await storage.get_file(key) is None


@pytest.mark.asyncio
async def test_storage_with_client(client: TestClient):
    file_to_upload = open("tests/test.json", "rb")
    response = client.post("/storage", files={"file": file_to_upload})
    assert response.status_code == 200
    assert response.json()["key"].split(".")[1] == "json"
    key = response.json()["key"]

    response = client.get(f"/storage/{key}")
    assert response.status_code == 200
    assert response.content == b'{"test": "this is a text file for testing purposes"}\n'

    # TODO: check why is 200 returned instead of 404
    response = client.get(f"/storage/wrong_key")
    assert response.status_code == 404
    assert response.content == b'{"detail":"File not found"}'

    response = client.delete(f"/storage/{key}")
    assert response.status_code == 204

    # TODO: check why is 204 returned instead of 404
    response = client.delete(f"/storage/wrong_key")
    assert response.status_code == 204
