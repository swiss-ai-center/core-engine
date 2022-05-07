import io
import os
import asyncio
import aioboto3
import uuid
import datetime
import copy
import motor.motor_asyncio

from bson.objectid import ObjectId
from contextlib import AsyncExitStack
from .Enums import StorageType, DBType
from .Errors import ItemNotFound
from .Pipeline import Pipeline

class Registry():
	def __init__(self, storage, db, storageType=StorageType.LOCAL, dbType=DBType.MEMORY):
		self.storage = storage
		self.db=db
		self.storageType = storageType
		self.dbType = dbType

	# Because we can't make the constructor async -_-
	@staticmethod
	async def create(s3_url=None, s3_zone=None, s3_key=None, s3_secret=None, s3_bucket=None, binFolder=None, storageType=StorageType.LOCAL, mongo_uri=None, mongo_db=None, dbType=DBType.MEMORY):
		storage = None
		db = None

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
				print("Failed to connect to S3, using local storage:", e)
				storageType = StorageType.LOCAL

		if storageType == StorageType.LOCAL:
			if binFolder is None:
				binFolder = "/tmp/registry"
			if not os.path.isdir(binFolder):
				os.makedirs(binFolder)
				storage = binFolder
		
		if dbType == DBType.MONGO:
			try:
				client = motor.motor_asyncio.AsyncIOMotorClient(mongo_uri)
				db = client[mongo_db]
				colls = await db.list_collection_names()
				if "pipelines" not in colls: await db.create_collection("pipelines")
				if "jobs" not in colls: await db.create_collection("jobs")
				if "tasks" not in colls: await db.create_collection("tasks")

			except Exception as e:
				print("Failed to connect to mongo, using memory:", e)
				dbType = DBType.MEMORY
		
		if dbType == DBType.MEMORY:
			db = {"pipelines": {}, "jobs": {}, "tasks": {}}

		r = Registry(storage, db, storageType, dbType)
		return r

	def uid(self):
		return uuid.uuid1().hex

	async def getPipelines(self):
		if self.dbType == DBType.MEMORY:
			return self.db["pipelines"].values()
		elif self.dbType == DBType.MONGO:
			search = self.db.pipelines.find()
			return [p async for p in search]

	async def getPipeline(self, pipelineId):
		if self.dbType == DBType.MEMORY:
			return self.db["pipelines"][pipelineId]
		elif self.dbType == DBType.MONGO:
			return await self.db.pipelines.find_one({"_id": ObjectId(pipelineId)})

	async def addPipeline(self, pipeline):
		pipelineId = None
		if self.dbType == DBType.MEMORY:
			pipelineId = self.uid()
			pipeline["_id"] = pipelineId
			self.db["pipelines"][pipelineId] = pipeline
		elif self.dbType == DBType.MONGO:
			inserted = await self.db.pipelines.insert_one(pipeline)
			pipelineId = str(inserted.inserted_id)
		return pipelineId

	async def removePipeline(self, pid):
		if self.dbType == DBType.MEMORY:
			self.db["pipelines"].pop(pid)
		elif self.dbType == DBType.MONGO:
			await self.db.pipelines.delete_one({"_id": ObjectId(pid)})

	async def saveJob(self, job):
		if self.dbType == DBType.MEMORY:
			if "_id" not in job.data: job.data["_id"] = self.uid()
			jobId = job._id
			self.db["jobs"][jobId] = job.data
		elif self.dbType == DBType.MONGO:
			if "_id" not in job.data:
				inserted = await self.db.jobs.insert_one(job.data)
				job.data["_id"] = str(inserted.inserted_id)
			else:
				jobData = copy.deepcopy(job.data)
				jobId = jobData.pop("_id")
				await self.db.jobs.find_one_and_replace({"_id": ObjectId(jobId)}, jobData)

	async def getJob(self, jobId):
		if self.dbType == DBType.MEMORY:
			if jobId in self.db["jobs"]:
				return Pipeline(self.db["jobs"][jobId])
		else:
			jobData = await self.db.jobs.find_one({"_id": ObjectId(jobId)})
			if jobData is not None:
				return Pipeline(jobData)
		return None

	async def getAllJobs(self):
		if self.dbType == DBType.MEMORY:
			return [Pipeline(job) for job in self.db["jobs"].values()]
		elif self.dbType == DBType.MONGO:
			search = self.db.jobs.find()
			return [Pipeline(j) async for j in search]
	
	async def removeJob(self, jobId):
		if self.dbType == DBType.MEMORY:
			self.db["jobs"].pop(jobId)
		elif self.dbType == DBType.MONGO:
			await self.db.jobs.delete_one({"_id": ObjectId(jobId)})

	async def addTask(self, task):
		taskId = None
		if self.dbType == DBType.MEMORY:
			taskId = self.uid()
			self.db["tasks"][taskId] = task
		elif self.dbType == DBType.MONGO:
			inserted = await self.db.tasks.insert_one(task)
			taskId = str(inserted.inserted_id)
		return taskId
	
	async def getTask(self, taskId):
		if self.dbType == DBType.MEMORY:
			if taskId in self.db["tasks"]:
				return self.db["tasks"][taskId]
		else:
			return await self.db.tasks.find_one({"_id": ObjectId(taskId)})
		return None

	async def popTask(self, taskId):
		if self.dbType == DBType.MEMORY:
			if taskId in self.db["tasks"]:
				return self.db["tasks"].pop(taskId)
		else:
			return await self.db.tasks.find_one_and_delete({"_id": ObjectId(taskId)})
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
	
	async def clean(self, delta):
		if self.storageType == StorageType.S3:
			now = datetime.datetime.utcnow()
			async for obj in self.storage.objects.all():
				if now - obj.last_modified > delta:
					await obj.delete()
