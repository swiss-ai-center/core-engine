import os
import asyncio
import pytest
import json
from api.worker import Worker
from aiofile import async_open
from contextlib import AsyncExitStack

# TODO use this code with the new structure to test the service

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
async def test_face_analyzer():
	worker, collect = setup_workers()
	await worker.addTask({"image": await img("test.jpg")})
	finishedTask = await collect.finished()
	await worker.stop()

	assert "result" in finishedTask
	result = finishedTask["result"]

	mockedResult = load("test_analyze_mock.json")

	assert "age" in result
	assert "region" in result
	assert "gender" in result
	assert "race" in result
	assert "dominant_race" in result
	assert "emotion" in result
	assert "dominant_emotion" in result

	assert mockedResult["age"] == result["age"]
	assert mockedResult["region"] == result["region"]
	assert mockedResult["gender"] == result["gender"]
	# assert mockedResult["race"] == result["race"]
	assert mockedResult["dominant_race"] == result["dominant_race"]
	# assert mockedResult["emotion"] == result["emotion"]
	assert mockedResult["dominant_emotion"] == result["dominant_emotion"]
