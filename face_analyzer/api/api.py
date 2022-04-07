import asyncio
from fastapi import FastAPI, File, UploadFile

from .worker import Worker, Callback
from . import interface
import json

async def startup():
	worker.chain(callback)
	callback.start()
	worker.start()

async def shutdown():
	await worker.stop()
	await callback.stop()

stackResult = []
worker = Worker(stackResult)
callback = Callback(stackResult)
app = FastAPI(on_startup=[startup], on_shutdown=[shutdown])

# Implement me!!! Define meaningful routes here, using input objects from "interface" or UploadFile + query params

# # This is a route for a service that only takes json input, which structure should be a interface.Job object
# @app.post("/compute", response_model = interface.TaskId)
# async def post(data: interface.Job, callback_url: str = None, task_id: str = None):
# 	if task_id is None:
# 		task_id = str(interface.uid())
# 	task = {"callback_url": callback_url, "task_id": task_id, "data": data.dict()}
# 	await worker.addTask(task)
# 	return interface.TaskId(task_id=task_id)

# This is a route for a service that takes a binary file as input, plus a custom "data1" query param
@app.post("/compute", response_model = interface.TaskId)
async def post(img: UploadFile, callback_url: str = None, task_id: str = None):
	if task_id is None:
		task_id = str(interface.uid())
	task = {"callback_url": callback_url, "task_id": task_id, "img": img}
	print("[API] process")
	await worker.addTask(task)
	return interface.TaskId(task_id=task_id)

@app.post("/result", response_model = interface.TaskId)
async def post(callback_url: str = None, task_id: str = None):
	if task_id is None:
		task_id = str(interface.uid())
	t = interface.TaskId(task_id=task_id)
	print(type(t), t)
	if(not stackResult):
		return t
	el = stackResult.pop(0)
	t = interface.TaskId(task_id=json.dumps(el))	
	return t
