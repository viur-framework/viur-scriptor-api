from ._utils import join_url
import typing


class BaseModule:
    def __init__(self, name: str, parent):
        super().__init__()
        self._name = name
        self._routes = {}
        self._parent = parent

    def __repr__(self):
        return f"""<{self.__class__.__name__} "{self._name}">"""

    @property
    def name(self) -> str:
        """
        returns the name of the database-model

        :return: the name of the database-model
        """
        return self._name

    @name.setter
    def name(self, value: str):
        self._name = value

    def register_route(self, name: str, method: object):
        self._routes[name] = method

    @staticmethod
    def _build_url(action: str, url: str, module: str, group: str = "", key: str = "", skel_type: str = ""):
        _url = url
        if not _url:
            if not module:
                raise ValueError("You need to set an url or use the module parameter.")
            _url = [module, action]
            if skel_type:
                _url.append(skel_type)
            if group:
                _url.append(group)
            if key:
                _url.append(key)
        return join_url(_url)

    def __getattr__(self, name: str):
        if ret := self._routes.get(name, None):
            return ret
        raise AttributeError(f"""'{self.__class__.__name__}' object hast no attribute '{name}'""")

    async def preview(self, params: dict = None, group: str = "", skel_type: str = "", **kwargs):
        _url = kwargs.get('url', '')
        _renderer = kwargs.get('renderer', '')
        url = self._build_url(action="preview", url=_url, module=self._name, group=group, skel_type=skel_type)
        return await self._parent.viur_request("SECURE_POST", url, params, renderer=_renderer)

    async def structure(self, group: str = "", skel_type: str = "", **kwargs):
        if 'url' in kwargs:
            _url = kwargs['url']
            del kwargs['url']
        else:
            _url = ''
        url = self._build_url(action="structure", url=_url, module=self._name, group=group, skel_type=skel_type)
        return await self._parent.viur_request("GET", url, **kwargs)

    async def view(self, key: str, group: str = "", skel_type: str = "", **kwargs) -> dict:
        if 'url' in kwargs:
            _url = kwargs['url']
            del kwargs['url']
        else:
            _url = ''
        url = self._build_url(action="view", url=_url, module=self._name, group=group, key=key, skel_type=skel_type)
        res = await self._parent.viur_request("GET", url, **kwargs)
        if res:
            return res['values']
        else:
            return res

    async def edit(self, key: str = "", params: dict = None, group: str = "", skel_type: str = "", **kwargs):
        _url = kwargs.get('url', '')
        _renderer = kwargs.get('renderer', '')
        url = self._build_url(action="edit", url=_url, module=self._name, group=group, key=key, skel_type=skel_type)
        return await self._parent.viur_request("SECURE_POST", url, params=params, renderer=_renderer)

    async def add_or_edit(self, key: str = "", params: dict = None, group: str = "", skel_type: str = "", **kwargs):
        _url = kwargs.get('url', '')
        _renderer = kwargs.get('renderer', '')
        url = self._build_url(action="add_or_edit", url=_url, module=self._name, group=group, key=key,
                              skel_type=skel_type)
        return await self._parent.viur_request("SECURE_POST", url, params=params, renderer=_renderer)


class SingletonModule(BaseModule):
    """
    This class is not meant to be instantiated by the user. It is returned by ``module`` for modules of type
    "singleton".
    """

    def edit(self, params: dict = None, **kwargs):  # without key
        """
        saves changes to a record in the database

        :param params: parameters to pass to the database
        :param kwargs: additional keyword-arguments
        :return: the edited database-record with structure- and error-information
        """
        return super().edit(module=self._name, params=params, **kwargs)

    def add_or_edit(self, params: dict = None, **kwargs):  # without key
        """
        saves changes to a record in the database or create it if it does not exist

        :param params: parameters to pass to the database
        :param kwargs: additional keyword-arguments
        :return: the edited database-record with structure- and error-information
        """
        return super().add_or_edit(module=self._name, params=params, **kwargs)

    async def preview(self, params: dict = None, **kwargs):
        """
        acts like add or edit, returns the same result, but doesn't save data to the database

        :param params: parameters to pass to the database
        :param kwargs: additional keyword-arguments
        :return: the database-record that would have been created with structure- and error-information
        """
        return await super().preview(params=params, **kwargs)

    async def structure(self, **kwargs):
        """
        returns the structure of the database-model

        :param kwargs: additional keyword-arguments
        :return: the structure of the database model
        """
        return await super().structure(**kwargs)

    async def view(self, key: str, **kwargs) -> dict:
        """
        retrieves a single record from the database

        :param key: the key of the databse record
        :param kwargs: additional keyword-arguments
        :return: the retrieved record
        """
        return await super().view(key=key, **kwargs)


class ExtendedModule(BaseModule):
    async def list(self, params: dict = None, group: str = "", skel_type: str = "", limit: int = None, **kwargs):
        if not params:
            params = {}

        _url = kwargs.get('url', '')
        _renderer = kwargs.get('renderer', '')

        if not _url:
            _url = [self._name, "list"]
            if skel_type:
                _url.append(skel_type)
            if group:
                _url.append(group)
            _url = join_url(_url)

        batch = []
        cursor = None
        fetched = False

        counter = 0
        while True:
            for i in batch:
                yield i
                counter += 1
                if limit and counter >= limit:
                    return
            if fetched and not cursor:
                return
            if cursor:
                params["cursor"] = cursor
            ret = await self._parent.viur_request("GET", _url, params, _renderer)
            fetched = True
            if not ret:
                return
            batch = ret['skellist']
            # batch.reverse()
            cursor = ret['cursor']
            if not batch:
                cursor = None

    async def add(self, params: dict = None, group: str = "", skel_type: str = "", **kwargs):
        _url = kwargs.get('url', '')
        _renderer = kwargs.get('renderer', '')
        url = self._build_url(action='add', url=_url, module=self._name, group=group, skel_type=skel_type)
        return await self._parent.viur_request("SECURE_POST", url=url, params=params, renderer=_renderer)

    async def delete(self, key: str, params: dict = None, **kwargs):
        """
        deletes a record from the database

        :param key: the key of the record that will be deleted
        :param params: parameters to pass to the database
        :param kwargs: additional keyword-arguments
        :return: ``True`` if the deletion was successful, otherwise raises an exception
        """
        _url = kwargs.get('url', '')
        _renderer = kwargs.get('renderer', '')
        url = self._build_url(action='delete', url=_url, module=self._name, key=key)
        return (await self._parent.viur_request("SECURE_POST", url=url, params=params, renderer=_renderer)) == "OKAY"


class ListModule(ExtendedModule):
    """
    This class is not meant to be instantiated by the user. It is returned by ``module`` for any modules that have
    multiple independent records.
    """

    async def preview(self, params: dict = None, group: str = "", **kwargs):
        """
        acts like add or edit, returns the same result, but doesn't save data to the database

        :param params: parameters to pass to the database
        :param group: the group
        :param kwargs: additional keyword-arguments
        :return: the database-record that would have been created with structure- and error-information
        """
        return await super().preview(params=params, group=group, **kwargs)

    async def structure(self, group: str = "", **kwargs):
        """
        returns the structure of the database-model

        :param group: applies group-specific modifiers to the structure
        :param kwargs: additional keyword-arguments
        :return: the structure of the database model
        """
        return await super().structure(group=group, **kwargs)

    async def view(self, key: str, group: str = "", **kwargs) -> dict:
        """
        retrieves a single record from the database

        :param key: the key of the databse record
        :param group: filters result to only contain records belonging to that group and applies group-specific
            modifiers
        :param kwargs: additional keyword-arguments
        :return: the retrieved record
        """
        return await super().view(key=key, group=group, **kwargs)

    async def edit(self, key: str = "", params: dict = None, group: str = "", **kwargs):
        """
        writes changes to a database-record

        :param key: the key of the record to be edited
        :param params: parameters to pass to the database
        :param group: applied group-specific modifiers to the model
        :param kwargs: additional keyword-arguments
        :return: the edited database-record with structure- and error-information
        """
        return await super().edit(key=key, params=params, group=group, **kwargs)

    async def add_or_edit(self, key: str = "", params: dict = None, group: str = "", **kwargs):
        """
        writes changes to a database-record or creates it, if it does not exist

        :param key: the key of the record to be edited
        :param params: parameters to pass to the database
        :param group: applied group-specific modifiers to the model
        :param kwargs: additional keyword-arguments
        :return: the edited database-record with structure- and error-information
        """
        return await super().add_or_edit(key=key, params=params, group=group, **kwargs)

    async def list(self, params: dict = None, group: str = "", limit: int = None, **kwargs):
        """
        retrieves multiple records from the database (all if called without parameters)

        :param params: parameters to pass to the database
        :param group: the group the records belong to
        :param limit: maximum amount of entries that should be fetched.
            Note: The amount of entries per request/batch must be specified as "limit" in the params.
        :param kwargs: additional keyword-arguments
        :return: an asynchronous generator yielding the retrieved records
        """
        async for i in super().list(params=params, group=group, limit=limit, **kwargs):
            yield i

    async def add(self, params: dict = None, group: str = "", **kwargs):
        """
        adds a record to the database

        :param params: parameters to pass to the database
        :param group: the group the records belong to
        :param kwargs: additional keyword-arguments
        :return: the new record
        """
        return await super().add(params=params, group=group, **kwargs)


class TreeModule(ExtendedModule):
    """
    This class is not meant to be instantiated by the user. It is returned by ``module`` for modules that have records
    in a tree-structure.
    """

    async def list_root_nodes(self, **kwargs):
        """
        return all root nodes (nodes without a parent)

        :param kwargs: additional keyword-arguments
        :return: list of dicts with the root-nodes names and keys
        """
        return await self._parent.viur_request("GET", f"/{self.name}/listRootNodes", **kwargs)

    async def move(self, key: str, parentNode: str, **kwargs):
        """
        moves a node to a new parent

        :param key: the key of the record that will be moved
        :param parentNode: the new parent the record will be moved to
        :param kwargs: additional keyword-arguments
        :return: the edited database-record with structure- and error-information
        """
        return await self._parent.viur_request("SECURE_POST", f"/{self.name}/move", params={
            "key": key,
            "parentNode": parentNode
        }, **kwargs)

    async def for_each(self, callback: callable, root_node_key: str = None, params: dict = None, **kwargs):  # FIXME
        """
        retrieves records from the database, then calls a callback function on each of them

        :param callback: the function to call on each retrieved record (parameters are ``skel_type`` and ``entry``,
            both as keyword-arguments, callback may be sync or async)
        :param root_node_key: the key of the root-node of which you want to iterate all children
        :param params: parameters to pass to the database
        :param kwargs: additional keyword-arguments
        """

        async def download(key: str, skel_type: str | tuple[str, str] = ("node", "leaf")):
            if isinstance(skel_type, tuple):
                for skelt in skel_type:
                    await download(key, skelt)
                return

            _params = {"parententry": key}
            if params:
                _params.update(params)

            async for entry in self.list(skel_type=skel_type, params=_params, **kwargs):
                cb = callback(skel_type=skel_type, entry=entry)
                if isinstance(cb, typing.Coroutine):
                    await cb
                # Check if this is a node
                if skel_type == "node":
                    await download(entry["key"])

        if root_node_key:
            root_nodes = [{"key": root_node_key}]
        else:
            root_nodes = self.list_root_nodes(**kwargs)

        for root_node in root_nodes:
            await download(root_node["key"])

    async def preview(self, params: dict = None, skel_type: str = "", **kwargs):
        """
        acts like add or edit, returns the same result, but doesn't save data to the database

        :param params: parameters to pass to the database
        :param skel_type: the skel_type of the record (either "node" or "leaf")
        :param kwargs: additional keyword-arguments
        :return: the database-record that would have been created with structure- and error-information
        """
        return await super().preview(params=params, skel_type=skel_type, **kwargs)

    async def structure(self, skel_type: str = "", **kwargs):
        """
        returns the structure of the database-model

        :param kwargs: additional keyword-arguments
        :param skel_type: the skel_type (either "node" or "leaf")
        :return: the structure of the database model
        """
        return await super().structure(skel_type=skel_type, **kwargs)

    async def view(self, key: str, skel_type: str = "", **kwargs) -> dict:
        """
        retrieves a single record from the database

        :param key: the key of the databse record
        :param skel_type: the skel_type of the record (either "node" or "leaf")
        :param kwargs: additional keyword-arguments
        :return: the retrieved record
        """
        return await super().view(key=key, skel_type=skel_type, **kwargs)

    async def edit(self, key: str = "", params: dict = None, skel_type: str = "", **kwargs):
        """
        writes changes to a database-record

        :param key: the key of the record to be edited
        :param params: parameters to pass to the database
        :param skel_type: the skel_type of the record (either "node" or "leaf")
        :param kwargs: additional keyword-arguments
        :return: the edited database-record with structure- and error-information
        """
        return await super().edit(key=key, params=params, skel_type=skel_type, **kwargs)

    async def list(self, params: dict = None, skel_type: str = "", limit: int = None, **kwargs):
        """
        retrieves multiple records from the database (all if called without parameters)

        :param params: parameters to pass to the database
        :param skel_type: the skel_type of the record (either "node" or "leaf")
        :param limit: maximum amount of entries that should be fetched.
            Note: The amount of entries per request/batch must be specified as "limit" in the params.
        :param kwargs: additional keyword-arguments
        :return: an asynchronous generator yielding the retrieved records
        """
        async for i in super().list(params=params, skel_type=skel_type, limit=limit, **kwargs):
            yield i

    async def add(self, params: dict = None, skel_type: str = "", **kwargs):
        """
        adds a record to the database

        :param params: parameters to pass to the database
        :param skel_type: the skel_type of the record (either "node" or "leaf")
        :param kwargs: additional keyword-arguments
        :return: the new record
        """
        return await super().add(params=params, skel_type=skel_type, **kwargs)


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
                self._attr = {
                    option.lower(): Method(name, module, [option.lower()], skey, False)
                    for option in methods
                }

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
        if not self.is_supporting_multiple_methods():
            method = self.methods[0]

        if self.support_method(method):
            if self._attr:
                if method.lower() in self._attr:
                    return await self._attr[method.lower()](*args, **kwargs)

        renderer = kwargs.get("scriptor_renderer", "json")
        if "scriptor_renderer" in kwargs:
            kwargs.pop("scriptor_renderer")

        result = None
        method = method.upper()
        if method == "POST":
            if self._skey:
                result = await self._module._parent.viur_request("SECURE_POST", route, params=kwargs,
                                                                 renderer=renderer)
            else:
                result = await self._module._parent.viur_request("POST", route, *args, params=kwargs,
                                                                 renderer=renderer)
        else:
            if method in ("GET", "DELETE", "PATCH", "PUT"):
                result = await self._module._parent.viur_request(method, route, *args, params=kwargs,
                                                                 renderer=renderer)
        return result

    def __getattr__(self, name: str):
        if self._attr:
            if name in self._attr:
                return self._attr[name]
        raise AttributeError(f"""'{self.__class__.__name__}' object hast no attribute '{name}'""")
