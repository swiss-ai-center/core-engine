import copy
import json
import datetime

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
			n = Node(self.nodes[nodeId])
			n.hide("_pipeline", self)
			return n
		return None

	def touch(self):
		self.lastUpdate = datetime.datetime.utcnow().isoformat()

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
		p.lastUpdate = None
		p.model = templateId
		
		for nodeDef in nodes:
			n = Node.build(**nodeDef)
			nodeId = nodeDef["id"]
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

	@staticmethod
	def build(id, type=NodeType.NODE, params={}, input=None, next=[], ready=None, before=None, after=None, **kwargs):
		n = Node({})
		n.id = id
		n.type = type
		n.params = copy.deepcopy(params)
		n.in_directive = input
		n.next = copy.deepcopy(next)
		n.ready_func = ready
		n.before_func = before
		n.after_func = after
		n.input = {}
		n.out = {}
		n.finished = False
		n.predecessors = []
		
		# Specific nodes
		if n.type == NodeType.ENTRY:
			n.api = kwargs["api"]
		elif n.type == NodeType.SERVICE:
			n.url = kwargs["url"]
		
		return n
	
	def ready(self):
		isReady = True
		if self.ready_func is None:
			for pred in self.predecessors:
				if not self._pipeline.node(pred).finished:
					isReady = False
					break
		
		# Call specific ready function
		else:
			locs = self.locals()
			# Inject modifiable object
			status = Context({})
			status.ready = isReady
			locs["status"] = status
			exec(self.ready_func, locs)
			isReady = status.ready

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
			exec(self.before_func, locs, globals())

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
		
		if self.type == NodeType.SERVICE:
			params = {"callback_url": self._pipeline._engine.route + "/processing", "task_id": taskId}
			if len(binaries) == 0:
				# Pure json service
				await self.client.post(self.url, params=params, json=self.input)
			else:
				# Multipart request with json and binaries
				binaries["data"] = json.dumps(jsonBody).encode("utf8")
				await self._pipeline._engine.client.post(self.url, params=params, files=binaries)
		else:
			for binaryKey in binaries:
				inIdentifier = str.join(".", [self.id, "input", binaryKey])
				outIdentifier = str.join(".", [self.id, "out", binaryKey])
				self._pipeline.binaries[outIdentifier] = self._pipeline.binaries[inIdentifier]
			await self._pipeline._engine.processTask(taskId, self.input)

	def after(self, result):
		self.out = result
		if self.after_func is not None:
			exec(self.after_func, self.locals(), globals())
	
	def locals(self):
		# So much sugar!!!
		loc = {"node": self, "pipeline": self._pipeline}
		for nodeId in self._pipeline.nodes:
			loc[nodeId] = self._pipeline.node(nodeId)
		return loc
