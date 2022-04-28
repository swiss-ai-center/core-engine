import os
import yaml
import pydantic
import io
import json

from typing import Union
from fastapi import FastAPI, HTTPException, UploadFile, Depends, Request
from fastapi.responses import RedirectResponse, JSONResponse, StreamingResponse
from .Engine import Engine, Registry
from . import interface

def addRoute(route, body, params={}):
	# Not sure why I have to do this when called by createService...

	if params is None:
		params = {}

	paramsModel = pydantic.create_model("Params", **params)
	
	if type(body) is list:
		async def handler(request: Request, query: paramsModel = Depends()):
			jobData = {}
			jobData.update(query.dict())
			binaries = []
			form = await request.form()
			for name in body:
				obj = form[name]
				if obj.content_type == "application/json":
					payload = await obj.read()
					jobData.update(json.loads(payload))
				else:
					jobData[name] = obj
					binaries.append(name)
			jobId = await engine.newJob(route, jobData, binaries)
			return {"jobId": jobId}
	else:
		bodyType = None
		if type(body) is dict:
			bodyType = pydantic.create_model(route + "Body", **body)
		elif type(body) is str:
			bodyType = UploadFile
		async def handler(data: bodyType, query: paramsModel = Depends()):
			jobData = {}
			jobData.update(query.dict())
			binaries = []
			if bodyType is UploadFile:
				binaries.append(body)
				jobData[body] = data
			else:
				jobData.update(data.dict())
			jobId = await engine.newJob(route, jobData, binaries)
			return {"jobId": jobId}

	app.add_api_route("/services/" + route, handler, methods=["POST"],  response_model=interface.JobResponse)
	# Force the regeneration of the schema
	app.openapi_schema = None

async def startup():
	for endpoint in engine.api:
		addRoute(**engine.api[endpoint])

async def shutdown():
	pass

app = FastAPI(on_startup=[startup], on_shutdown=[shutdown])
registry = Registry.Registry("/tmp/registry")
engine = Engine.Engine(registry, os.environ["APP_ENGINE"] if "APP_ENGINE" in os.environ else None)

@app.get("/tasks/{taskId}/status")
def getTaskStatus(taskId: str):
	status = engine.pollTask(taskId)
	return {"id": taskId, "status": status}

@app.get("/tasks/{taskId}")
def getTaskResult(taskId: str):
	result = engine.getResult(taskId)
	return JSONResponse(result)

@app.get("/tasks/{taskId}/files/{fileName}")
def getTaskResultFile(taskId: str, fileName: str):
	stream = engine.getResultFile(taskId, fileName)
	return StreamingResponse(stream, media_type="application/octet-stream")

@app.post("/services")
def createService(service: Union[interface.ServiceDescription, interface.PipelineDescription]):
	if service.type is interface.ServiceType.SERVICE:
		api = service.api.dict()
		serviceName = api["route"]
		if serviceName not in engine.endpoints:
			engine.createServicePipeline(service.url, api)
			addRoute(**api)
	elif service.type is interface.ServiceType.PIPELINE:
		api = engine.addPipeline(service.dict())
		addRoute(**api)

@app.delete("/services/{serviceName}")
def removeService(serviceName: str):
	if serviceName in engine.endpoints:
		engine.removePipeline(serviceName)
		for i in range(len(app.routes)):
			if app.routes[i].path == "/services/" + serviceName:
				app.routes.pop(i)
				break
		# Force the regeneration of the schema
		app.openapi_schema = None

@app.post("/processing")
async def processCallback(task_id: str, request: Request):
	data = {}
	binaries = []
	
	contentType = request.headers["content-type"].replace(";", "")

	if "application/json" in contentType:
		data.update(await request.json())
	elif "multipart/form-data" in contentType:
		form = await request.form()
		for k in form:
			obj = form[k]
			if obj.content_type == "application/json":
				payload = await obj.read()
				data.update(json.loads(payload))
			else:
				data[k] = obj
				binaries.append(k)

	await engine.processTask(task_id, data, binaries)
