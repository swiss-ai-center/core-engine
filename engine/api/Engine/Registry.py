import io
import os
import asyncio
import aioboto3
import uuid

from contextlib import AsyncExitStack
from .Enums import StorageType
from .Errors import ItemNotFound
from .Pipeline import Pipeline

class Registry():
	def __init__(self, storage, storageType=StorageType.LOCAL):
		self.storageType = storageType
		self.storage = storage
		self.data = {"pipelines": {}, "jobs": {}, "tasks": {}}

	# Because we can't make the constructor async -_-
	@staticmethod
	async def create(s3_url=None, s3_zone=None, s3_key=None, s3_secret=None, s3_bucket=None, binFolder=None, storageType=StorageType.LOCAL):
		storage = None

		if storageType == StorageType.S3:
			try:
				stack = AsyncExitStack()
				session = aioboto3.Session()
				s3ctx = session.resource("s3", endpoint_url=s3_url, region_name=s3_zone, aws_secret_access_key=s3_secret, aws_access_key_id=s3_key)
				s3 = await stack.enter_async_context(s3ctx)
				bucket = None
				async for b in s3.buckets.all():
					if b.name == s3_bucket:
						bucket = b
						break
				if bucket is None:
					bucket = await s3.create_bucket(Bucket=s3_bucket)
				storage = bucket
			except Exception as e:
				print("Failed to connect to S3, using local storage", e)
				storageType = StorageType.LOCAL

		elif storageType == StorageType.LOCAL:
			if binFolder is None:
				binFolder = "/tmp/registry"
			if not os.path.isdir(binFolder):
				os.makedirs(binFolder)
				storage = binFolder

		r = Registry(storage, storageType)
		return r

	def uid(self):
		return uuid.uuid1().hex

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
		if self.storageType == StorageType.LOCAL:
			w = open(os.path.join(self.storage, uid), "wb")
			w.write(await stream.read())
			w.close()
		elif self.storageType == StorageType.S3:
			binId = "binaries/" + uid
			data = await stream.read()
			await self.storage.put_object(Key=binId, Body=io.BytesIO(data))
		return uid

	async def getS3Obj(self, uid):
		if self.storageType == StorageType.S3:
			binId = "binaries/" + uid
			obj = await self.storage.Object(binId)
			try:
				await obj.load()
				# At this point we know obj exists
				return obj
			except:
				raise ItemNotFound("No such binary: " + uid)
		return None

	async def getBinaryStream(self, uid):
		if self.storageType == StorageType.LOCAL:
			return open(os.path.join(self.storage, uid), "rb")
		elif self.storageType == StorageType.S3:
			obj = await self.getS3Obj(uid)
			stream = io.BytesIO()
			await obj.download_fileobj(stream)
			stream.seek(0)
			return stream

	async def removeBinary(self, uid):
		if self.storageType == StorageType.LOCAL:
			os.remove(os.path.join(self.storage, uid))
		elif self.storageType == StorageType.S3:
			obj = await self.getS3Obj(uid)
			await obj.delete()
