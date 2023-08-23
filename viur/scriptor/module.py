from .viur import viur
from .network import Request
from .viur import viur
from .utils import is_pyodide_context
if is_pyodide_context():
	from js import console

import inspect
import traceback
import copy


def create_and_compile_function(function_name, function_code):
	# Define the function code as a string
	code = f'''
async def {function_name}(*args, **kwargs):
{function_code}
'''

	# Compile the code using the built-in `compile()` function
	compiled_code = compile(code, filename='<string>', mode='exec')

	# Execute the compiled code using `exec()` to define the function
	exec(compiled_code)

	# Return the created function
	return eval(function_name)

class BaseModule(object):
	def __init__(self, name: str):
		self._name = name
		self._routes = {}

	@property
	def name(self) -> str:
		return self._name

	@name.setter
	def name(self, value: str):
		self._name = value

	def register_route(self, callback: callable, name: str = None, *args, **kwargs):
		_name = name if name is not None else callback.__name__
		_func = getattr(self, _name, None)
		if _func:
			if is_pyodide_context():
				console.warn(f"There is already a function for {_name}")
			return

		if is_pyodide_context():
			console.log(f"Register route name {_name}")

		self._routes[_name] = {"function": callback,"instance": None, "args": args, "kwargs": kwargs}

	async def register_routes(self, route: object):
		functions = inspect.getmembers(route.__class__, predicate=inspect.isfunction)
		for name, func in functions:
			if is_pyodide_context():
				console.log(f"Register route name {name}")

			if name.startswith("__"):
				continue

			if is_pyodide_context():
				console.log(f"Register route {name} -> {func}")
			async def wrap(*args, **kwargs):
				return await func(self._routes[name]["instance"], *args, **kwargs)

			self._routes[name] = {
				"function": wrap,
				"instance": route,
			}

	def __getattr__(self, name: str):
		if ret := self._routes.get(name, None):
			return ret["function"]
		return self.__getattribute__(name)


	async def preview(self, params: dict = None, group: str = "", **kwargs):
		return await viur.preview(module=self._name, params=params, group=group, **kwargs)

	async def structure(self, group: str = "", **kwargs):
		return await viur.structure(module=self._name, group=group, **kwargs)

	async def view(self, key: str, group: str = "", **kwargs) -> dict:
		return await viur.view(module=self._name, key=key, group=group, **kwargs)

class SingletonModule(BaseModule):
	async def edit(self, params: dict = None, group: str = "", **kwargs):
		return await viur.edit(module=self._name, params=params, group=group, **kwargs)

class ExtendedModule(BaseModule):
	async def edit(self, key: str, params: dict = None, group: str = "", **kwargs):
		return await viur.edit(module=self._name, key=key, params=params, group=group, **kwargs)

	def list(self, params: dict = None, group: str = '', **kwargs) -> viur.list:
		return viur.list(module=self._name, params=params, group=group, **kwargs)

	async def add(self, params: dict = None, group: str = "", **kwargs):
		return await viur.add(module=self._name, params=params, group=group, **kwargs)

	async def delete(self, key: str, params: dict = None, group: str = "", **kwargs):
		return await viur.delete(module=self._name, key=key, params=params, group=group, **kwargs)


class ListModule(ExtendedModule):
	async def for_each(self, callback: callable, params: dict = None, **kwargs):
		async for entry in self.list(params=params, **kwargs):
			await callback(entry)

class TreeModule(ExtendedModule):
	async def edit(self, group: str, key: str, params: dict = None, **kwargs):
		return await super().edit(group=group, key=key, params=params, **kwargs)

	def list(self, group: str, params: dict = None, **kwargs) -> viur.list:
		return super().list(group=group, params=params, **kwargs)

	async def add(self, group: str, params: dict = None, **kwargs):
		return await super().add(group=group, params=params, **kwargs)

	async def view(self, group: str, key: str, **kwargs) -> dict:
		return await super().view(group=group, key=key, **kwargs)

	async def preview(self, group: str, params: dict = None, **kwargs):
		return await super().preview(params=params, group=group, **kwargs)
	

	async def list_root_nodes(self, **kwargs):
		return await viur.request.get(f"/{self.name}/listRootNodes", **kwargs)

	async def delete(self, group: str, key: str, params: dict = None, **kwargs):
		return await super().delete(group=group, key=key, params=params, **kwargs)

	async def move(self, key: str, parentNode: str, **kwargs):
		return await viur.request.secure_post(f"/{self.name}/move", params={
			"key": key,
			"parentNode": parentNode
		}, **kwargs)

	async def for_each(self, callback: callable, root_node_key: str = None, params: dict = None, **kwargs):
		##
		async def download(key: str, group: str|list[str] = ['node', 'leaf']):
			if isinstance(group, list):
				for grp in group:
					await download(key, grp)
				return
			
			_params = {"parententry": key}
			if params:
				_params.update(params)


			async for entry in self.list(group, _params, **kwargs):
				await callback(group, entry)
				# Check if this is a node
				if group == "node":
					await download(entry["key"])

		if root_node_key:
			root_nodes = [root_node_key]
		else:
			root_nodes = await self.list_root_nodes(**kwargs)
	
		for root_node in root_nodes:
			await download(root_node["key"])


def __getattr__(attr):
	#console.log("Calling __getattr__")
	modules_resolver = {
		"tree": TreeModule, 
		"list": ListModule,
		"singleton": SingletonModule
	}

	details = viur.modules.get(attr, None)
	if details:
		module_type = None
		for key, value in modules_resolver.items():
			if details["handler"].startswith(key):
				module_type = value
				break

		
		# If the module has a registered type
		if module_type:

			# Ensure one instance of the module
			if not ("type" in details):
				details["type"] = module_type

			if not ("instance" in details):	
				details["instance"] = details["type"](attr)
				try:
					if "functions" in details or "methods" in details:
						_methods = details.get("functions", details.get("methods"))
						for f in _methods:
							code = f"""
	route = f"/{attr}/{f['name']}"
	result = None
	methods = {f["method"]}
	_method = "GET"
	if methods == ["POST"]:
		_method = "POST"
	secure_method: bool = kwargs.get("scriptor_request_secure", {f['skey']})
	method: str = kwargs.get("scriptor_request_method", _method).upper()
	renderer: str = kwargs.get("scriptor_request_renderer", '')
	console.log("route renderer", kwargs)

	if "scriptor_request_method" in kwargs:
		kwargs.pop("scriptor_request_method")
	if "scriptor_request_secure" in kwargs:
		kwargs.pop("scriptor_request_secure")	
	if "scriptor_request_renderer" in kwargs:
		kwargs.pop("scriptor_request_renderer")
	#console.log("route callback", route)
	if method == "POST":
		if secure_method is None:
			## Bruteforce method try skey method.. and after a normal post..
			try:
				params = copy.deepcopy(kwargs)
				result = await viur.request.secure_post(route, *args, params=params, renderer=renderer)
				if result["status"] != 200:
					result = await viur.request.post(route, *args, params=kwargs, renderer=renderer)
			except:
				result = await viur.request.post(route, *args, params=kwargs, renderer=renderer)
		else:
			# New version
			if secure_method:
				result = await viur.request.secure_post(route, *args, params=kwargs, renderer=renderer)
			else:
				result = await viur.request.post(route, *args, params=kwargs, renderer=renderer)
	elif method == "GET":
		result = await viur.request.get(route, *args, params=kwargs, renderer=renderer)
	elif method == "DELETE":
		result = await viur.request.delete(route, *args, params=kwargs, renderer=renderer)
	elif method == "PATCH":
		result = await viur.request.patch(route, *args, params=kwargs, renderer=renderer)
	elif method == "PUT":
		result = await viur.request.put(route, *args, params=kwargs, renderer=renderer)
	return result"""
							callback = create_and_compile_function(f"callback_{attr}_{f['name']}", code)
							callback.__doc__ = f["docs"]
							details["instance"].register_route(callback, f["name"])
				except:
					if is_pyodide_context():
						console.error(traceback.format_exc())
					else:
						print(traceback.format_exc())
			return details["instance"]

	return super(__import__(__name__).__class__).__getattr__(attr)