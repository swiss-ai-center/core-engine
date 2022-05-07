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
	
	async def load(self):
		pipelines = await self.registry.getPipelines()
		for pipeline in pipelines:
			endpoint = Pipeline.api(pipeline)["route"]
			if endpoint is not None:
				self.endpoints[endpoint] = str(pipeline["_id"])
				self.api[endpoint] = Pipeline.api(pipeline)
	
	async def addPipeline(self, pipeline):
		pid = await self.registry.addPipeline(pipeline)
		api = Pipeline.api(pipeline)
		endpoint = api["route"]
		if endpoint is not None:
			self.endpoints[endpoint] = pid
			self.api[endpoint] = api
		return api

	async def removePipeline(self, endpoint):
		if endpoint not in self.endpoints:
			raise ItemNotFound("Pipeline {endpoint} not found".format(endpoint=endpoint))
		pid = self.endpoints[endpoint]
		await self.registry.removePipeline(pid)
		self.endpoints.pop(endpoint)
		self.api.pop(endpoint)
	
	async def newJob(self, endpoint, data, binaries=[]):
		if endpoint not in self.endpoints:
			raise ItemNotFound("Pipeline {endpoint} not found".format(endpoint=endpoint))
		
		pipelineId = self.endpoints[endpoint]
		pipelineTemplate = await self.registry.getPipeline(pipelineId)
		job = Pipeline.build(pipelineTemplate["nodes"], pipelineId)
		job.node(job.entry).before()
		await self.registry.saveJob(job)
		taskId = await self.registry.addTask({"job": job._id, "node": job.entry})
		requestId = await self.registry.addTask({"job": job._id})
		await self.processTask(taskId, data, binaries)
		return requestId

	async def processTask(self, taskId, data, binaries=[]):
		task = await self.registry.popTask(taskId)
		if task is None:
			raise ItemNotFound("Task {taskId} not found".format(taskId=taskId))
		
		job = await self.registry.getJob(task["job"])
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
				taskId = await self.registry.addTask({"job": job._id, "node": nextId})
				toProcess.append((succ, taskId))
		
		if finishedNode.type == NodeType.END:
			job.status = Status.FINISHED

		job.touch()
		await self.registry.saveJob(job)
		
		# Refactor this?!
		for item in toProcess:
			node, taskId = item
			# Race condition if we are processing multiple generic nodes here, because each one of them will call processTask and pipeline data will be overwritten
			await node.process(taskId)
	
	async def pollTask(self, taskId):
		task = await self.registry.getTask(taskId)
		if task is None:
			raise ItemNotFound("Task {taskId} not found".format(taskId=taskId))
		job = await self.registry.getJob(task["job"])
		if job is None:
			raise ItemNotFound("Job for task {taskId} not found".format(taskId=taskId))
		
		return job.status
	
	async def getResult(self, taskId):
		task = await self.registry.getTask(taskId)
		if task is None:
			raise ItemNotFound("Task {taskId} not found".format(taskId=taskId))
		
		job = await self.registry.getJob(task["job"])
		if job is None:
			raise ItemNotFound("Job for task {taskId} not found".format(taskId=taskId))

		if job.status != Status.FINISHED:
			raise NotFinished("Pipeline is not finished ({status})".format(status=job.status))

		out = job.node(job.end).out
		for key in job.node(job.end).out:
			identifier = str.join(".", [job.end, "out", key])
			if identifier in job.binaries:
				out[key] = "{engine}/tasks/{taskId}/files/{name}".format(engine=self.externalRoute, taskId=taskId, name=key)
		return out
	
	async def getResultFile(self, taskId, fileName):
		task = await self.registry.getTask(taskId)
		if task is None:
			raise ItemNotFound("Task {taskId} not found".format(taskId=taskId))
		
		job = await self.registry.getJob(task["job"])
		if job is None:
			raise ItemNotFound("Job for task {taskId} not found".format(taskId=taskId))

		if job.status != Status.FINISHED:
			raise NotFinished("Pipeline is not finished ({status})".format(status=job.status))

		identifier = str.join(".", [job.end, "out", fileName])

		if identifier not in job.binaries:
			raise ItemNotFound("No file named " + fileName + " for task " + taskId)

		binUid = job.binaries[identifier]
		return await self.registry.getBinaryStream(binUid)

	async def getJobRaw(self, taskId):
		task = await self.registry.getTask(taskId)
		if task is None:
			raise ItemNotFound("Task {taskId} not found".format(taskId=taskId))
		
		job = await self.registry.getJob(task["job"])
		if job is None:
			raise ItemNotFound("Job for task {taskId} not found".format(taskId=taskId))
		
		return job.data

	async def createServicePipeline(self, url, api):
		name = api["route"]

		entry = {"type": NodeType.ENTRY, "id": name + "-entry", "api": api, "next": [name + "-component"]}
		component = {"type": NodeType.SERVICE, "id": name + "-component", "url": url, "next": [name + "-end"]}
		end = {"type": NodeType.END, "id": name + "-end"}
		
		pipeline = {"nodes": [entry, component, end]}
		await self.addPipeline(pipeline)

	async def clean(self, delta):
		now = datetime.datetime.utcnow()
		for job in await self.registry.getAllJobs():
			if now - job.timestamp() > delta:
				binUids = set([job.binaries[binary] for binary in job.binaries])
				for binUid in binUids:
					await self.registry.removeBinary(binUid)
				await self.registry.removeJob(job._id)
	
	async def getStats(self):
		# Reverse id to endpoints
		models = {}
		for e in self.endpoints:
			pid = self.endpoints[e]
			models[pid] = e
		
		endpoints = dict.fromkeys(self.endpoints, 0)
		undef = 0

		running = 0
		finished = 0
		failed = 0
		
		jobs = await self.registry.getAllJobs()
		for job in jobs:
			if job.status == Status.RUNNING: running += 1
			elif job.status == Status.FINISHED: finished += 1
			elif job.status == Status.ERROR: failed += 1
			
			eid = job.model
			if eid in models:
				endpoint = models[eid]
				endpoints[endpoint] += 1
			else:
				undef += 1
		
		if undef > 0:
			endpoints["UNDEFINED"] = undef

		stats = {}
		stats["jobs"] = {"total": len(jobs), "running": running, "finished": finished, "failed": failed}
		stats["services"] = endpoints

		return stats
	
	async def getPipelines(self):
		return self.registry.getPipelines()

	async def getPipeline(self, name):
		if name not in self.endpoints:
			raise ItemNotFound("Pipeline {name} not found".format(name=name))
		pipelineId = self.endpoints[name]
		pipelineTemplate = await self.registry.getPipeline(pipelineId)
		return pipelineTemplate

# Race condition when processingFinished is called simultaneously for one same pipeline?
# We should put processTask in a worker!
