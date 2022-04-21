import os
import yaml
import pydantic
import io

from fastapi import FastAPI, HTTPException, UploadFile, Depends, Request
from fastapi.responses import RedirectResponse, JSONResponse, StreamingResponse
from .Engine import Engine, Registry
from . import interface

def addRoute(route, body, params={}):
	# Not sure why I have to do this when called by createService...
	if params is None:
		params = {}

	paramsModel = pydantic.create_model("Params", **params)
	bodyType = None
	
	if type(body) is dict:
		bodyType = pydantic.create_model(route + "Body", **body)
	elif type(body) is str:
		bodyType = UploadFile

	async def handler(data: bodyType, query: paramsModel = Depends()):
		jobData = {}
		jobData.update(query.dict())
		binary = None
		if bodyType is UploadFile:
			binary = body
			jobData[body] = data
		else:
			jobData.update(data.dict())
		jobId = await engine.newJob(route, jobData, binary)
		return {"jobId": jobId}

	app.add_api_route("/services/" + route, handler, methods=["POST"],  response_model=interface.JobResponse)
	# Force the regeneration of the schema
	app.openapi_schema = None

async def startup():
	# example pipelines
	example = os.path.join(os.path.dirname(os.path.abspath(__file__)), "example.yaml")
	f = open(example, encoding="utf8")
	pipelines = yaml.load(f, Loader=yaml.FullLoader)
	f.close()
	engine.addPipeline(pipelines["square"])
	engine.addPipeline(pipelines["dummy"])
	
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
	if isinstance(result, io.IOBase):
		return StreamingResponse(result, media_type="application/octet-stream")
	else:
		return JSONResponse(result)

@app.post("/services")
def createService(service: interface.ServiceDescription):
	api = service.api.dict()
	serviceName = api["route"]
	if serviceName not in engine.endpoints:
		engine.createServicePipeline(service.url, api)
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
	binary = None
	
	contentType = request.headers["content-type"].replace(";", "")

	if "application/json" in contentType:
		data.update(await request.json())
	elif "multipart/form-data" in contentType:
		form = await request.form()
		# this does NOT support multiple binaries for now!
		for k in form:
			data[k] = form[k]
			binary = k

	await engine.processTask(task_id, data, binary)
