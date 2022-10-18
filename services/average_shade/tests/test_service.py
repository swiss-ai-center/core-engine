import os
import asyncio
import pytest

from api.worker import Worker
from aiofile import async_open
from contextlib import AsyncExitStack

from fastapi.testclient import TestClient
from api.api import app

client = TestClient(app)

def imgPath(name):
	return os.path.join(os.path.dirname(os.path.realpath(__file__)), name)

async def img(name):
	stack = AsyncExitStack()
	fctx = async_open(imgPath(name), "rb")
	f = await stack.enter_async_context(fctx)
	return f

class Collect():
	def __init__(self):
		super().__init__()
		self.result = None
		self.event = asyncio.Event()

	async def addTask(self, task):
		self.result = task
		self.event.set()

	async def finished(self):
		await self.event.wait()
		return self.result

class AsyncReader:
	def __init__(self, raw):
		self.raw = raw

	async def read(self):
		return self.raw

def setup_workers():
	worker = Worker()
	collect = Collect()
	worker.chain(collect)
	worker.start()
	return worker, collect

def test_root_notfound():
	response = client.get("/")
	assert response.status_code == 404

def test_docs():
	response = client.get("/docs")
	assert response.status_code == 200

@pytest.mark.asyncio
async def test_average_shade():
	worker, collect = setup_workers()
	await worker.addTask({"image": await img("test.jpg")})
	finishedTask = await collect.finished()
	await worker.stop()

	assert "result" in finishedTask
	result = finishedTask["result"]
	assert "Red" in result
	assert "Green" in result
	assert "Blue" in result
