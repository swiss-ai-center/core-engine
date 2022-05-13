import copy
import json
import datetime
import httpx

from .Enums import Status, NodeType

def resolveObjectAttr(obj, pathStr):
	data = obj
	path = pathStr.split(".")

	for p in path:
		if type(data) is dict and p in data:
			data = data[p]
		elif hasattr(data, p):
			data = getattr(data, p)

	return data

class Context(object):
	def __init__(self, ctx):
		if "_id" in ctx and type(ctx["_id"]) is not str: ctx["_id"] = str(ctx["_id"])
		super().__setattr__("data", ctx)
		super().__setattr__("hidden", {})

	def __getattr__(self, key):
		if key in self.data:
			return self.data[key]
		elif key in self.hidden:
			return self.hidden[key]
		raise AttributeError

	def __setattr__(self, key, value):
		self.data[key] = value

	def hide(self, key, value):
		self.hidden[key] = value

class Pipeline(Context):
	def __init__(self, ctx):
		super().__init__(ctx)

	def node(self, nodeId):
		if nodeId in self.nodes:
			nodeData = self.nodes[nodeId]
			nodeType = nodeData["type"]
			n = NodeFactories[nodeType](nodeData)
			n.hide("_pipeline", self)
			return n
		return None

	def touch(self):
		self.lastUpdate = datetime.datetime.utcnow().isoformat()

	def fail(self, error=""):
		self.status = Status.ERROR
		self.error = error

	def timestamp(self):
		return datetime.datetime.fromisoformat(self.lastUpdate)

	@staticmethod
	def build(nodes, templateId=None):
		p = Pipeline({})
		p.nodes = {}
		p.binaries = {}
		p.entry = None
		p.end = None
		p.status = Status.RUNNING
		p.error = None
		p.lastUpdate = None
		p.model = templateId

		for nodeDef in nodes:
			nodeType = nodeDef["type"]
			nodeId = nodeDef["id"]
			n = NodeFactories[nodeType]({})
			n.build(**nodeDef)
			p.nodes[nodeId] = n.data

			if n.type == NodeType.ENTRY:
				p.entry = nodeId
			elif n.type == NodeType.END:
				p.end = nodeId

		# Process successors
		for nodeId in p.nodes:
			node = p.node(nodeId)
			for succ in node.next:
				p.node(succ).predecessors.append(nodeId)

		p.touch()
		return p

	@staticmethod
	def api(pipeline):
		for nodeDef in pipeline["nodes"]:
			if nodeDef["type"] == NodeType.ENTRY:
				return nodeDef["api"]
		return None

class Node(Context):
	def __init__(self, ctx):
		super().__init__(ctx)

	def build(self, id, type=NodeType.NODE, params={}, input=None, next=[], ready=None, before=None, after=None, **kwargs):
		self.id = id
		self.type = type
		self.params = copy.deepcopy(params)
		self.in_directive = input
		self.next = copy.deepcopy(next)
		self.ready_func = ready
		self.before_func = before
		self.after_func = after
		self.input = {}
		self.out = {}
		self.finished = False
		self.predecessors = []

	def ready(self):
		isReady = True
		if self.ready_func is None:
			for pred in self.predecessors:
				if not self._pipeline.node(pred).finished:
					isReady = False
					break

		# Call specific ready function
		else:
			try:
				locs = self.locals()
				# Inject modifiable object
				status = Context({})
				status.ready = isReady
				locs["status"] = status
				exec(self.ready_func, locs)
				isReady = status.ready
			except Exception as e:
				self._pipeline.fail("Failed to assert ready state for node {node}: {error}".format(node=self.id, error=e))
				return False

		return isReady

	def before(self):
		locs = self.locals()
		directive = {}

		if self.in_directive is not None:
			directive = self.in_directive
		else:
			for predId in self.predecessors:
				pred = self._pipeline.node(predId)
				for k in pred.out:
					directive[k] = str.join(".", [predId, "out", k])

		for key in directive:
			identifier = directive[key]
			resolvedValue = resolveObjectAttr(locs, identifier)
			self.input[key] = resolvedValue
			if identifier in self._pipeline.binaries:
				inIdentifier = str.join(".", [self.id, "input", key])
				self._pipeline.binaries[inIdentifier] = resolvedValue

		if self.before_func is not None:
			try:
				exec(self.before_func, locs, globals())
			except Exception as e:
				self._pipeline.fail("Failed to pre-process node {node}: {error}".format(node=self.id, error=e))

	async def process(self, taskId):
		binaries = []
		for key in self.input:
			identifier = str.join(".", [self.id, "input", key])
			if identifier in self._pipeline.binaries:
				binaries.append(key)

		for binaryKey in binaries:
			inIdentifier = str.join(".", [self.id, "input", binaryKey])
			outIdentifier = str.join(".", [self.id, "out", binaryKey])
			self._pipeline.binaries[outIdentifier] = self._pipeline.binaries[inIdentifier]
		await self._pipeline._engine.processTask(taskId, self.input)

	def after(self, result):
		self.out = result
		if self.after_func is not None:
			try:
				exec(self.after_func, self.locals(), globals())
			except Exception as e:
				self._pipeline.fail("Failed to post-process node {node}: {error}".format(node=self.id, error=e))

	def locals(self):
		# So much sugar!!!
		loc = {"node": self, "pipeline": self._pipeline, "input": Context(self.input)}
		for nodeId in self._pipeline.nodes:
			loc[nodeId] = self._pipeline.node(nodeId)
		return loc

	def isParent(self, nodeId):
		if nodeId in self.predecessors:
			return True

		for predId in self.predecessors:
			if self._pipeline.node(predId).isParent(nodeId):
				return True

		return False

	def reset(self):
		if self.finished:
			self.finished = False
			self.input = {}
			self.out = {}
			for nextId in self.next:
				self._pipeline.node(nextId).reset()

class NodeEntry(Node):
	def build(self, api, **kwargs):
		super().build(**kwargs)
		self.api = api

class NodeService(Node):
	def build(self, url, **kwargs):
		super().build(**kwargs)
		self.url = url

	async def process(self, taskId):
		binaries = {}
		jsonBody = copy.deepcopy(self.input)

		for key in jsonBody:
			identifier = str.join(".", [self.id, "input", key])
			if identifier in self._pipeline.binaries:
				binUid = self._pipeline.binaries[identifier]
				binaries[key] = await self._pipeline._engine.registry.getBinaryStream(binUid)

		# Remove binaries from body
		[jsonBody.pop(key) for key in binaries.keys()]

		try:
			params = {"callback_url": self._pipeline._engine.route + "/processing", "task_id": taskId}
			if len(binaries) == 0:
				# Pure json service
				await self._pipeline._engine.client.post(self.url, params=params, json=jsonBody)
			else:
				# Multipart request with json and binaries
				binaries["data"] = json.dumps(jsonBody).encode("utf8")
				await self._pipeline._engine.client.post(self.url, params=params, files=binaries)
		except Exception as e:
			self._pipeline.fail("Failed to process service node {node}: {error}".format(node=self.id, error=e))

class NodeBranch(Node):
	def build(self, **kwargs):
		super().build(**kwargs)
		# Using reserved keywords in node def -_-
		self.cond = kwargs["if"]
		self.then = kwargs["then"]
		self.otherwise = kwargs["else"]
		self.resetStatus = False

	async def process(self, taskId):
		try:
			locs = self.locals()
			predicate = eval(self.cond, locs, globals())
			branch = None

			if predicate:
				branch = self.then
			else:
				branch = self.otherwise

			# Now process branch
			data = {}

			if type(branch) is str:
				exec(branch, locs, globals())
			elif type(branch) is dict:
				if "exec" in branch:
					exec(branch["exec"], locs, globals())
				if "next" in branch:
					self.next = branch["next"]
					for nextId in self.next:
						nextnode = self._pipeline.node(nextId)
						if self.isParent(nextId):
							nextnode.reset()
							self.resetStatus = True
						else:
							nextnode.predecessors.append(self.id)
				if "out" in branch:
					for key in branch["out"]:
						identifier = branch["out"][key]
						resolvedValue = resolveObjectAttr(locs, identifier)
						data[key] = resolvedValue
						if identifier in self._pipeline.binaries:
							outIdentifier = str.join(".", [self.id, "out", key])
							self._pipeline.binaries[outIdentifier] = resolvedValue
			await self._pipeline._engine.processTask(taskId, data)
		except Exception as e:
			self._pipeline.fail("Failed to process branch node {node}: {error}".format(node=self.id, error=e))

	def after(self, result):
		super().after(result)
		if self.resetStatus:
			self.resetStatus = False
			self.finished = False

class NodeHTTP(Node):
	def build(self, url, verb="GET", **kwargs):
		super().build(**kwargs)
		self.url = url
		self.verb = verb

	async def process(self, taskId):
		if self.verb == "POST":
			req = self._pipeline._engine.client.post
		elif self.verb == "DELETE":
			req = self._pipeline._engine.client.delete
		elif self.verb == "PUT":
			req = self._pipeline._engine.client.put
		elif self.verb == "PATCH":
			req = self._pipeline._engine.client.patch
		else:
			req = self._pipeline._engine.client.get

		binaries = {}
		jsonBody = copy.deepcopy(self.input)

		for key in jsonBody:
			identifier = str.join(".", [self.id, "input", key])
			if identifier in self._pipeline.binaries:
				binUid = self._pipeline.binaries[identifier]
				binaries[key] = await self._pipeline._engine.registry.getBinaryStream(binUid)

		# Remove binaries from body
		[jsonBody.pop(key) for key in binaries.keys()]

		try:
			if len(binaries) == 0:
				if len(jsonBody) == 0:
					res = await req(self.url)
				else:
					res = await req(self.url, json=jsonBody)
			else:
				# Multipart request with json and binaries
				if len(jsonBody) > 0:
					binaries["data"] = json.dumps(jsonBody).encode("utf8")
				res = await req(self.url, files=binaries)
			if res.status_code != httpx.codes.OK:
				await self._pipeline._engine.processError(taskId, "Request to {url} failed for node {node}: {code}".format(url=self.url, node=self.id, code=res.status_code))
			else:
				data = {}
				binaries = []
				if "application/json" in res.headers["Content-Type"]:
					data = res.json()
				elif len(res.content) > 0:
					data["raw"] = res.content
					binaries.append("raw")
				await self._pipeline._engine.processTask(taskId, data, binaries)
		except Exception as e:
			self._pipeline.fail("Failed to process http node {node}: {error}".format(node=self.id, error=e))

class NodeLoop(Node):
	def build(self, items, nodes, **kwargs):
		super().build(**kwargs)
		self.items = items
		self.nodes = nodes
		self.collect = kwargs["collect"] if "collect" in kwargs else {}

		self.counter = 0
		self.endNode = self.id + "End"

	async def process(self, taskId):
		if self.endNode not in self._pipeline.nodes:
			endNode = Node({})
			endNode.build(**{"id": self.endNode, "type": NodeType.NODE, "input": {}, "next": self.next, "after": self.id + ".out = node.out"})
			self._pipeline.nodes[self.endNode] = endNode.data
			self.next = []
		endNode = self._pipeline.node(self.endNode)

		items = resolveObjectAttr(self.locals(), self.items)
		if type(items) is not list:
			self._pipeline.fail("Can not iterate on " + self.items + " (" + str(type(items)) + ")")
			return

		for i in range(len(items)):
			item = items[i]
			branchNodes = {}
			branchEntryNode = None
			for node in self.nodes:
				# Set new id
				nodeDef = copy.deepcopy(node)
				nodeId = node["id"] + str(self.counter)
				self.counter += 1
				branchNodes[node["id"]] = nodeId
				nodeDef["id"] = nodeId

				# Connect branch end node to loop end node
				if "next" in nodeDef:
					nextList = nodeDef["next"]
					if "loopEnd" in nextList:
						nextList[nextList.index("loopEnd")] = endNode.id
						endNode.predecessors.append(nodeId)

				# Process inputs
				if "input" in nodeDef:
					directive = nodeDef["input"]
					for k in directive:
						if directive[k].startswith("loop."):
							path = directive[k].split(".")
							if path[1] in branchNodes:
								directive[k] = str.join(".", [branchNodes[path[1]]] + path[2:])

				# Build and inject current item
				n = NodeFactories[node["type"]]({})
				n.build(**nodeDef)
				n._loop = item
				self._pipeline.nodes[nodeId] = n.data

				if branchEntryNode is None:
					branchEntryNode = nodeId
					n.predecessors.append(self.id)

			self.next.append(branchEntryNode)
			for k in self.collect:
				path = self.collect[k].split(".")
				endNode.in_directive[k + str(i)] = str.join(".", [branchNodes[path[0]]] + path[1:])

		await self._pipeline._engine.processTask(taskId, {}, [])

	def reset(self):
		self.next = []
		endNode = self._pipeline.node(self.endNode)
		endNode.predecessors = []
		endNode.in_directive = {}
		super().reset()
		endNode.reset()

NodeFactories = {}
NodeFactories[NodeType.NODE] = Node
NodeFactories[NodeType.ENTRY] = NodeEntry
NodeFactories[NodeType.END] = Node
NodeFactories[NodeType.SERVICE] = NodeService
NodeFactories[NodeType.BRANCH] = NodeBranch
NodeFactories[NodeType.HTTP] = NodeHTTP
NodeFactories[NodeType.LOOP] = NodeLoop
