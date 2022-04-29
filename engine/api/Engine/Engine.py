import asyncio
import httpx
import datetime

from .Pipeline import Pipeline, Node
from .Enums import Status, NodeType
from .Errors import ItemNotFound, NotFinished

class Engine():
	def __init__(self, registry, route, externalRoute):
		self.registry = registry
		self.route = route
		self.externalRoute = externalRoute
		self.client = httpx.AsyncClient()
		self.endpoints = {}
		self.api = {}
		
		self.load()
	
	def load(self):
		pipelines = self.registry.getPipelines()
		for pipeline in pipelines:
			endpoint = Pipeline.endpoint(pipeline)
			if endpoint is not None:
				self.endpoints[endpoint] = pipeline["_id"]
				self.api[endpoint] = Pipeline.api(pipeline)
	
	def addPipeline(self, pipeline):
		pid = self.registry.addPipeline(pipeline)
		api = Pipeline.api(pipeline)
		endpoint = api["route"]
		if endpoint is not None:
			self.endpoints[endpoint] = pid
			self.api[endpoint] = api
		return api

	def removePipeline(self, endpoint):
		if endpoint not in self.endpoints:
			raise ItemNotFound("Pipeline {endpoint} not found".format(endpoint=endpoint))
		pid = self.endpoints[endpoint]
		self.registry.removePipeline(pid)
		self.endpoints.pop(endpoint)
		self.api.pop(endpoint)
	
	async def newJob(self, endpoint, data, binaries=[]):
		if endpoint not in self.endpoints:
			raise ItemNotFound("Pipeline {endpoint} not found".format(endpoint=endpoint))
		
		pipelineId = self.endpoints[endpoint]
		pipelineTemplate = self.registry.getPipeline(pipelineId)
		job = Pipeline.build(pipelineTemplate["nodes"])
		job.node(job.entry).before()
		self.registry.saveJob(job)
		taskId = self.registry.addTask({"job": job._id, "node": job.entry})
		requestId = self.registry.addTask({"job": job._id})
		await self.processTask(taskId, data, binaries)
		return requestId

	async def processTask(self, taskId, data, binaries=[]):
		task = self.registry.popTask(taskId)
		if task is None:
			raise ItemNotFound("Task {taskId} not found".format(taskId=taskId))
		
		job = self.registry.getJob(task["job"])
		if job is None:
			raise ItemNotFound("Job for task {taskId} not found".format(taskId=taskId))
		
		job.hide("_engine", self)
		nodeId = task["node"]
		finishedNode = job.node(nodeId)
		
		# Process binary input if any
		for binary in binaries:
			stream = data[binary]
			binUid = await self.registry.storeBinary(stream)
			data[binary] = binUid
			job.binaries[str.join(".", [nodeId, "out", binary])] = binUid

		finishedNode.finished = True
		finishedNode.after(data)
		
		# Refactor this?!
		toProcess = []
		
		for nextId in finishedNode.next:
			succ = job.node(nextId)
			if succ.ready():
				succ.before()
				taskId = self.registry.addTask({"job": job._id, "node": nextId})
				toProcess.append((succ, taskId))
		
		if finishedNode.type == NodeType.END:
			job.status = Status.FINISHED

		job.touch()
		self.registry.saveJob(job)
		
		# Refactor this?!
		for item in toProcess:
			node, taskId = item
			await node.process(taskId)
	
	def pollTask(self, taskId):
		task = self.registry.getTask(taskId)
		if task is None:
			raise ItemNotFound("Task {taskId} not found".format(taskId=taskId))
		job = self.registry.getJob(task["job"])
		if job is None:
			raise ItemNotFound("Job for task {taskId} not found".format(taskId=taskId))
		
		return job.status
	
	def getResult(self, taskId):
		task = self.registry.getTask(taskId)
		if task is None:
			raise ItemNotFound("Task {taskId} not found".format(taskId=taskId))
		
		job = self.registry.getJob(task["job"])
		if job is None:
			raise ItemNotFound("Job for task {taskId} not found".format(taskId=taskId))

		if job.status is not Status.FINISHED:
			raise NotFinished("Pipeline is not finished ({status})".format(status=job.status))

		out = job.node(job.end).out
		for key in job.node(job.end).out:
			identifier = str.join(".", [job.end, "out", key])
			if identifier in job.binaries:
				out[key] = "{engine}/tasks/{taskId}/files/{name}".format(engine=self.externalRoute, taskId=taskId, name=key)
		return out
	
	def getResultFile(self, taskId, fileName):
		task = self.registry.getTask(taskId)
		if task is None:
			raise ItemNotFound("Task {taskId} not found".format(taskId=taskId))
		
		job = self.registry.getJob(task["job"])
		if job is None:
			raise ItemNotFound("Job for task {taskId} not found".format(taskId=taskId))

		if job.status is not Status.FINISHED:
			raise NotFinished("Pipeline is not finished ({status})".format(status=job.status))

		identifier = str.join(".", [job.end, "out", fileName])

		if identifier not in job.binaries:
			raise ItemNotFound("No file named " + filename + " for task " + taskId)

		binUid = job.binaries[identifier]
		return self.registry.getBinaryStream(binUid)

	def createServicePipeline(self, url, api):
		name = api["route"]

		entry = {"type": NodeType.ENTRY, "id": name + "-entry", "api": api, "next": [name + "-component"]}
		component = {"type": NodeType.SERVICE, "id": name + "-component", "url": url, "next": [name + "-end"]}
		end = {"type": NodeType.END, "id": name + "-end"}
		
		pipeline = {"nodes": [entry, component, end]}
		self.addPipeline(pipeline)

	async def clean(self, delta):
		now = datetime.datetime.utcnow()
		for job in self.registry.getAllJobs():
			if now - job.timestamp() > delta:
				binUids = set([job.binaries[binary] for binary in job.binaries])
				for binUid in binUids:
					self.registry.removeBinary(binUid)
				self.registry.removeJob(job._id)

# Race condition when processingFinished is called simultaneously for one same pipeline?
