import os
import asyncio
import pytest
import json
import io
import hashlib

from PIL import Image
from api.worker import Worker
from aiofile import async_open
from contextlib import AsyncExitStack

def checksum(data):
	res = hashlib.sha256(data)
	return res.hexdigest()

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
async def test_analyze():
	worker, collect = setup_workers()
	await worker.addTask({"operation": "analyze", "image": await img("test.jpg")})
	finishedTask = await collect.finished()
	await worker.stop()

	assert "result" in finishedTask
	result = finishedTask["result"]
	assert result["format"] == "image/jpeg"
	assert result["width"] == 1092
	assert result["height"] == 700

@pytest.mark.asyncio
async def test_resize():
	worker, collect = setup_workers()
	await worker.addTask({"operation": "resize", "image": await img("test.jpg"), "settings": await dictToJsonStream({"width": 500, "height": 200})})
	finishedTask = await collect.finished()
	await worker.stop()

	assert "result" in finishedTask
	result = finishedTask["result"]
	assert type(result) is bytes
	resized = Image.open(io.BytesIO(result))
	assert resized.width == 500
	assert resized.height == 200

@pytest.mark.asyncio
async def test_blur():
	worker, collect = setup_workers()
	await worker.addTask({"operation": "blur", "image": await img("test.jpg"), "areas": await dictToJsonStream({"areas": [[136, 11, 333, 220]]})})
	finishedTask = await collect.finished()
	await worker.stop()

	testImg = await img("test_blur_mock.jpg")

	assert "result" in finishedTask
	result = finishedTask["result"]

	assert type(result) is bytes
	assert checksum(result) == checksum(await testImg.read())

@pytest.mark.asyncio
async def test_crop():
	worker, collect = setup_workers()
	await worker.addTask({"operation": "crop", "image": await img("test.jpg"), "areas": await dictToJsonStream({"areas": [[136, 11, 333, 220]]})})

	finishedTask = await collect.finished()
	await worker.stop()

	testImg = await img("test_crop_mock.jpg")

	assert "result" in finishedTask
	result = finishedTask["result"]

	assert type(result) is bytes
	assert checksum(result) == checksum(await testImg.read())


@pytest.mark.asyncio
async def test_greyscale():
	worker, collect = setup_workers()
	await worker.addTask({"operation": "greyscale", "image": await img("test.jpg")})
	finishedTask = await collect.finished()
	await worker.stop()

	testImg = await img("test_greyscale_mock.jpg")
	assert "result" in finishedTask
	result = finishedTask["result"]

	assert type(result) is bytes
	assert checksum(result) == checksum(await testImg.read())

@pytest.mark.asyncio
async def test_convert():
	worker, collect = setup_workers()
	await worker.addTask({"operation": "convert", "image": await img("test.jpg"), "format": await dictToJsonStream({"format": "png"})})
	finishedTask = await collect.finished()
	await worker.stop()

	assert "result" in finishedTask
	result = finishedTask["result"]

	assert type(result) is bytes
	assert Image.open(io.BytesIO(result)).format == "PNG"
