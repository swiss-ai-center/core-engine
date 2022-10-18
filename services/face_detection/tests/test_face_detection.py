import os
import asyncio
import pytest
import json
from api.worker import Worker
from aiofile import async_open
from contextlib import AsyncExitStack

def imgPath(name):
	return os.path.join(os.path.dirname(os.path.realpath(__file__)), name)

async def img(name):
	stack = AsyncExitStack()
	fctx = async_open(imgPath(name), "rb")
	f = await stack.enter_async_context(fctx)
	return f

async def dictToJsonStream(data):
	raw = json.dumps(data).encode("utf8")
	return AsyncReader(raw)

def load(name):
	f = open(imgPath(name), "rt")
	data = json.load(f)
	f.close()
	return data

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

@pytest.mark.asyncio
async def test_face_detection():
	worker, collect = setup_workers()
	await worker.addTask({"image": await img("test.jpg")})
	finishedTask = await collect.finished()
	await worker.stop()

	assert "result" in finishedTask
	result = finishedTask["result"]

	mockedResult = load("test_area_mock.json")

	assert "answer" in result
	assert "answer" in mockedResult

	assert mockedResult["answer"] == result["answer"]

	i = 0
	for x in mockedResult["answer"]:
		assert x == result["answer"][i]
		i += 1
