import json
import os
import asyncio

from .Pipeline import Pipeline

def loadJson(path):
	f = open(path, encoding="utf8")
	data = json.load(f)
	f.close()
	return data

class Registry():
	def __init__(self, binFolder):
		# Load persist file if exists
		persistFile = os.path.join(os.path.dirname(os.path.abspath(__file__)), "persist.json")
		if os.path.isfile(persistFile):
			self.data = loadJson(persistFile)
		else:
			self.data = {"pipelines": {}, "jobs": {}, "tasks": {}}
		
		if not os.path.isdir(binFolder):
			os.makedirs(binFolder)
		
		self.counter = 0
		self.binFolder = binFolder
	
	def uid(self):
		self.counter += 1
		return str(self.counter)

	def getPipelines(self):
		return self.data["pipelines"].values()
	
	def getPipeline(self, pipelineId):
		return self.data["pipelines"][pipelineId]

	def addPipeline(self, pipeline):
		pipelineId = self.uid()
		pipeline["_id"] = pipelineId
		self.data["pipelines"][pipelineId] = pipeline
		return pipelineId

	def removePipeline(self, pid):
		self.data["pipelines"].pop(pid)

	def saveJob(self, job):
		if "_id" not in job.data:
			job.data["_id"] = self.uid()
		jobId = job._id
		self.data["jobs"][jobId] = job.data

	def getJob(self, jobId):
		if jobId in self.data["jobs"]:
			return Pipeline(self.data["jobs"][jobId])
		return None

	def getAllJobs(self):
		return [Pipeline(job) for job in self.data["jobs"].values()]
	
	def removeJob(self, jobId):
		self.data["jobs"].pop(jobId)

	def addTask(self, task):
		taskId = self.uid()
		self.data["tasks"][taskId] = task
		return taskId
	
	def getTask(self, taskId):
		if taskId in self.data["tasks"]:
			return self.data["tasks"][taskId]
		return None

	def popTask(self, taskId):
		if taskId in self.data["tasks"]:
			return self.data["tasks"].pop(taskId)
		return None
	
	async def storeBinary(self, stream):
		uid = self.uid()
		w = open(os.path.join(self.binFolder, uid), "wb")
		w.write(await stream.read())
		w.close()
		return uid

	def getBinaryStream(self, uid):
		return open(os.path.join(self.binFolder, uid), "rb")

	def removeBinary(self, uid):
		os.remove(os.path.join(self.binFolder, uid))
