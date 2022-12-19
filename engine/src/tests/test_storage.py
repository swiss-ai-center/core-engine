import asyncio
import pytest
from storage import Storage
from logger import Logger
from config import Settings


@pytest.fixture(name="storage")
def storage_fixture():
    logger = Logger()
    settings = Settings()

    storage = Storage(logger=logger, settings=settings)

    yield storage


def test_storage(storage: Storage):
    loop = asyncio.get_event_loop()

    loop.run_until_complete(
        storage.begin_multipart_upload(
            source_path='./large.txt',
            s3_destination_folder_path='large',
        )
    )
