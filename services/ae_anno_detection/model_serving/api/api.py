import os
import httpx
import logging

import pandas as pd
from fastapi import FastAPI, UploadFile

from .worker import Worker, Callback
from .cron import Timer
from . import interface

async def notifyEngine():
	serviceDescr = {"url": service + "/compute", "api": interface.engineAPI(), "type": "service"}
	try:
		res = await client.post(engine + "/services", json=serviceDescr)
		if res.status_code != 200:
			logging.getLogger("uvicorn").warning("Failed to notify the engine, request returned " + str(res.status_code))
	except Exception as e:
		logging.getLogger("uvicorn").warning("Failed to notify the engine: " + str(e))

async def startup():
	worker.chain(callback)
	callback.start()
	worker.start()

	# Announce ourself to the engine
	if engine is not None and service is not None:
		await notifyEngine()
		tick = int(os.environ["APP_NOTIFY_CRON"]) if "APP_NOTIFY_CRON" in os.environ else 30
		notifyEngineTimer = Timer(
			timeout=tick,
			callback=notifyEngine)
		notifyEngineTimer.start()
		timers.append(notifyEngineTimer)

async def shutdown():
	for timer in timers:
		timer.stop()

	await worker.stop()
	await callback.stop()

engine = os.environ["APP_ENGINE"] if "APP_ENGINE" in os.environ else None
service = os.environ["APP_SERVICE"] if "APP_SERVICE" in os.environ else None

client = httpx.AsyncClient()
worker = Worker()
callback = Callback()
app = FastAPI(on_startup=[startup], on_shutdown=[shutdown])
timers = []

@app.post("/compute", response_model=interface.TaskId)
async def post(text: UploadFile, callback_url: str = None, task_id: str = None):
	if task_id is None:
		task_id = str(interface.uid())
	# with open("test.txt", "wb") as f:
	# 	f.write(text.file.read())
	task = {"callback_url": callback_url, "task_id": task_id, "text": text}
	await worker.addTask(task)
	return interface.TaskId(task_id=task_id)
