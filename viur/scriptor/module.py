from .viur import viur
from .network import Request
from .viur import viur
from .utils import is_pyodide_context
if is_pyodide_context():
    from js import console

import inspect
import traceback
import copy


class BaseModule:
    def __init__(self, name: str):
        super().__init__()
        self._name = name
        self._routes = {}

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value: str):
        self._name = value

    def register_route(self, name: str, method: object):
        self._routes |= {
            name: method
        }

    def __getattr__(self, name: str):
        if ret := self._routes.get(name, None):
            return ret
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


class Method:
    def __init__(self, name: str, module: BaseModule, methods: list[str] | None = None,
                 skey: str = None, parent: bool = True):
        if methods is None:
            methods = []
        self._name: str = name
        self._methods: list[str] = [method for method in methods if method != "HEAD"]

        self._module: BaseModule = module
        self._skey = skey  # supports skey?
        self._parent = parent

        self._attr = None
        if methods:
            if parent:
                self._attr = {option.lower(): Method(name, module, [option.lower()], skey, False) for option in methods }

    @property
    def methods(self):
        return [method.lower() for method in self._methods]

    @property
    def name(self):
        return self._name

    def support_method(self, name: str) -> bool:
        return name.lower() in self.methods

    def is_supporting_multiple_methods(self):
        return len(self.methods) > 1

    async def __call__(self, *args, **kwargs):
        route = f"/{self._module.name}/{self._name}"
        method = "GET"
        if not self.is_supporting_multiple_methods(): ## Multiple options
            method = self.methods[0]

        if self.support_method(method):
            if self._attr:
                if method.lower() in self._attr:
                    return await self._attr[method.lower()](*args, **kwargs)

        renderer = kwargs.get("scriptor_renderer", "json")
        if "scriptor_renderer" in kwargs:
            kwargs.pop("scriptor_renderer")

        result = None
        match method.upper():
            case "POST":
                if self._skey:
                    result = await viur.request.secure_post(route, params=kwargs, renderer=renderer)
                else:
                    result = await viur.request.post(route, *args, params=kwargs, renderer=renderer)
            case "GET":
                result = await viur.request.get(route, *args, params=kwargs, renderer=renderer)
            case "DELETE":
                result = await viur.request.delete(route, *args, params=kwargs, renderer=renderer)
            case "PATCH":
                result = await viur.request.patch(route, *args, params=kwargs, renderer=renderer)
            case "PUT":
                result = await viur.request.put(route, *args, params=kwargs, renderer=renderer)

        return result

    def __getattr__(self, name: str):
        if self._attr:
            if name in self._attr:
                return self._attr[name]
        return self.__getattribute__(name)


def __getattr__(attr: str):
    #console.log("Calling __getattr__")
    modules_resolver = {
        "tree": TreeModule,
        "hierarchy": TreeModule,
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
                details["instance"]  = details["type"](attr)
                module: BaseModule = details["instance"]
                try:
                    if "functions" in details or "methods" in details:
                        exposed_list = details.get("functions", details.get("methods"))
                        for exposed_name, data in exposed_list.items():
                            method = Method(
                                exposed_name, module, data["accepts"],
                                skey=data.get("skey", None),
                                parent=True
                            )
                            details["instance"].register_route(exposed_name, method)
                except:
                    if is_pyodide_context():
                        console.error(traceback.format_exc())
                    else:
                        print(traceback.format_exc())

            return details["instance"]

    return super(__import__(__name__).__class__).__getattr__(attr)
