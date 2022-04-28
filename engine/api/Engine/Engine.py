import asyncio
import httpx
from .Pipeline import Pipeline, Node
from .Enums import Status, NodeType

class Engine():
	def __init__(self, registry, route):
		self.registry = registry
		self.route = route
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
	
	def removePipeline(self, endpoint):
		if endpoint not in self.endpoints:
			raise Exception
		pid = self.endpoints[endpoint]
		self.registry.removePipeline(pid)
		self.endpoints.pop(endpoint)
		self.api.pop(endpoint)
	
	async def newJob(self, endpoint, data, binaries=[]):
		if endpoint not in self.endpoints:
			raise Exception
		
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
			raise Exception
		
		job = self.registry.getJob(task["job"])
		if job is None:
			raise Exception
		
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
		
		self.registry.saveJob(job)
		
		# Refactor this?!
		for item in toProcess:
			node, taskId = item
			await node.process(taskId)
	
	def pollTask(self, taskId):
		task = self.registry.getTask(taskId)
		if task is None:
			return Status.NA
		job = self.registry.getJob(task["job"])
		if job is None:
			return Status.NA
		
		return job.status
	
	def getResult(self, taskId):
		task = self.registry.getTask(taskId)
		if task is None:
			raise Exception
		
		job = self.registry.getJob(task["job"])
		if job is None:
			raise Exception
		
		out = job.node(job.end).out
		for key in job.node(job.end).out:
			identifier = str.join(".", [job.end, "out", key])
			if identifier in job.binaries:
				out[key] = "{engine}/tasks/{taskId}/files/{name}".format(engine=self.route, taskId=taskId, name=key)
		return out
	
	def getResultFile(self, taskId, fileName):
		task = self.registry.getTask(taskId)
		if task is None:
			raise Exception
		
		job = self.registry.getJob(task["job"])
		if job is None:
			raise Exception
		
		identifier = str.join(".", [job.end, "out", fileName])
		binUid = job.binaries[identifier]
		return self.registry.getBinaryStream(binUid)

	def createServicePipeline(self, url, api):
		name = api["route"]

		entry = {"type": NodeType.ENTRY, "id": name + "-entry", "api": api, "next": [name + "-component"]}
		component = {"type": NodeType.SERVICE, "id": name + "-component", "url": url, "next": [name + "-end"]}
		end = {"type": NodeType.END, "id": name + "-end"}
		
		pipeline = {"nodes": [entry, component, end]}
		self.addPipeline(pipeline)

# Race condition when processingFinished is called simultaneously for one same pipeline?
