import traceback
import requests
from urllib.parse import urlencode as _urlencode
from .module_parts import BaseModule, ListModule, TreeModule, SingletonModule, Method
from .http_errors import get_exception_by_code,HTTPException
from ._utils import join_url
from .requests import WebRequest
from ._utils import is_pyodide_context, flatten_dict
from .dialog import Dialog
import json

if is_pyodide_context():
    from js import FormData
    from pyodide.ffi import JsProxy
else:
    from urllib3 import encode_multipart_formdata


class Modules:
    """
    used to retrieve modules from the viur-backend
    """

    def __init__(self, base_url: str, username: str, password: str, login_skey: str = None):
        self._base_url = base_url
        self._username = username
        self._password = password
        self._login_skey = login_skey
        self._session = None
        self._cookies = None
        self._modules = None

    def is_logged_in(self):
        return self._session is not None and self._cookies is not None

    if is_pyodide_context():

        async def init(self):
            resp = await self.viur_request("GET", "/config", renderer="vi")
            try:
                self._modules = resp["modules"]
            except KeyError:
                self._modules = []
    else:
        async def init(self):
            self._session = requests.sessions.Session()
            skey = self._session.get(self._base_url + "/json/skey")

            kwargs = {
                "data": {
                    "skey": skey.json(),
                    "name": self._username,
                    "password": self._password
                }
            }
            if self._login_skey:
                kwargs["headers"] = {"X-Scriptor": self._login_skey}

            response = self._session.post(self._base_url + "/vi/user/auth_userpassword/login?@vi-admin=true", **kwargs)

            Dialog.print(f"""LOGIN RESPONSE:\n{response.content = }""")

            if response.status_code == 200 and (b"""JSON(("OKAY"))""" in response.content or response.json() != "FAILURE"):
                Dialog.print("LOGIN SUCCESS")
                self._cookies = requests.sessions.cookiejar_from_dict(self._session.cookies.get_dict())
            else:
                Dialog.print("LOGIN FAILED")

            resp = await self.viur_request("GET", "/config", renderer="vi")
            try:
                self._modules = resp["modules"]
            except KeyError:
                self._modules = []

    async def logout(self):
        await self.viur_request("SECURE_POST", "/json/user/logout")
        self._session = None
        self._cookies = None
        self._modules = None
        Dialog.print("logout success")

    async def get_module(self, module_name: str):
        """
        gets a modules from the viur-backend

        :param module_name: the name of the module
        :return: the module, either a ``TreeModule``, a ``ListModule`` or a ``SingletonModule``
        """
        if module_name in ("__wrapped__",
                           "_repr_mimebundle_",
                           "_ipython_canary_method_should_not_exist_",
                           "_ipython_display_"):  # fixes iPython autocomplete and iPython-"repr"
            return None
        modules_resolver = {
            "tree": TreeModule,
            "hierarchy": TreeModule,
            "list": ListModule,
            "singleton": SingletonModule
        }

        details = self._modules.get(module_name,
                                    None)  # TODO? await self._viur_request("GET", module_name, None, renderer='vi')
        if details:
            module_type = None
            for key, value in modules_resolver.items():
                try:
                    _handler = details["handler"]
                except KeyError:
                    try:
                        _handler = details["action"]
                    except KeyError:
                        raise KeyError("details has no action and no handler")
                if _handler.startswith(key):
                    module_type = value
                    break

            # If the module has a registered type
            if module_type:

                # Ensure one instance of the module
                if "type" not in details:
                    details["type"] = module_type

                if "instance" not in details:
                    details["instance"] = details["type"](module_name, parent=self)
                    module: BaseModule = details["instance"]
                    try:
                        if "functions" in details or "methods" in details:
                            exposed_list = details.get("functions", details.get("methods"))
                            if isinstance(exposed_list, list):
                                exposed_list_iterator = exposed_list
                            elif isinstance(exposed_list, dict):
                                exposed_list_iterator = exposed_list.items()
                            else:
                                raise ValueError(
                                    f"""exposed_list should be of type dict or list, is {type(exposed_list)}""")
                            for exposed_name, data in exposed_list_iterator:
                                method = Method(
                                    exposed_name, module, data["accepts"],
                                    skey=data.get("skey", None),
                                    parent=True
                                )
                                details["instance"].register_route(exposed_name, method)
                    except:
                        Dialog.print(traceback.format_exc())

                return details["instance"]
        raise AttributeError(f"""No modules named "{module_name}" found.""")

    def get_base_url(self):
        """
        returns the base-url of the viur server

        :return: the base-url of the viur server
        """
        return self._base_url

    async def viur_request(self, method: str, url: str, params=None, renderer: str = None, raw: bool = False):
        """
        requests data from the viur server.

        :param method: one of "GET", "POST", "PUT", "DELETE", "PATCH" or "SECURE_POST"
        :param url: the url of the requested resource
        :param params: additional parameters
        :param renderer: the viur-renderer for the requested data
        :param raw: if true the raw response will be returned
        :return: the requested data renderd by the renderer
        """
        method = method.upper()
        if method not in ('GET', 'PUT', 'POST', 'DELETE', 'PATCH', 'SECURE_POST'):
            raise ValueError(
                f"""method not supported: "{method}", """
                """supported methods are GET, PUT, POST, DELETE, PATCH, SECURE_POST""")
        if method == "SECURE_POST":
            skey = await self.viur_request("GET", "/skey", renderer=renderer)
            if isinstance(params, dict):
                params["skey"] = skey
            elif isinstance(params, list):
                params.append(("skey", skey))
            else:
                params = {"skey": skey}
            method = "POST"

        if url and not any(url.startswith(prefix) for prefix in ('http://', 'https://', '//')):
            if not url.startswith("/"):
                url = "/" + url
            prefix = f"""/{renderer}""" if renderer else "/json"
            url = prefix + url
            url = join_url((self._base_url, url))

        data = None
        if params:
            if method == "GET":
                url += "?" + _urlencode(params)
            else:
                data = params
        kwargs = self._viur_request_kwargs_collector(data=(data if method != "GET" else None))

        response = await WebRequest.request(method, url, **kwargs)
        if raw:
            return response
        if response.get_status_code() < 200 or response.get_status_code() >= 300:
            responsedata = False
            try:
                responsedata = response.as_object_from_json()
            except:
                pass
            errormessage = f"""Request of type "{method}" for URL "{url}" returned with status-code {response.get_status_code()}"""
            if responsedata and all(key in responsedata for key in ["reason", "descr"]):
                errormessage = f"""{errormessage}\n\nreason: {responsedata["reason"]}\ndescription:\n{responsedata["descr"]}"""
            if exception := get_exception_by_code(response.get_status_code()):
                raise exception(errormessage,response)
            else:
                raise HTTPException(response.get_status_code(), "Http Error", errormessage,response)
        try:
            return response.as_object_from_json()
        except json.JSONDecodeError:
            return response.as_bytes()

    if is_pyodide_context():
        def _viur_request_kwargs_collector(self, data=None):
            from . import params
            kwargs = {
                "headers": {"Accept": "application/json, text/plain, */*"},

            }
            if params.get("__is_dev__"):
                kwargs["credentials"] = "include"
            if data:
                if isinstance(data, dict):
                    raw_fd = flatten_dict(data)
                elif isinstance(data, list):
                    raw_fd = data
                else:
                    raise ValueError(f"data must be a dict or FormData, but is {type(data)}")
                fd = FormData.new()
                for k, v in raw_fd:
                    fd.append(k, v)
                kwargs["body"] = fd
            return kwargs
    else:
        def _viur_request_kwargs_collector(self, data=None):
            kwargs = {
                "headers": {"Accept": "application/json, text/plain, */*"}
            }
            if self._cookies:
                kwargs["cookies"] = self._cookies
            else:
                raise RuntimeError("You need to log in.")
            if data:
                payload_data, payload_header = encode_multipart_formdata(data)
                kwargs["data"] = payload_data
                kwargs["headers"]["Content-Type"] = payload_header
            return kwargs

    def __repr__(self):
        if self._modules is None:
            module_list = "uninitialized"
        else:
            module_list = [i for i in self._modules if not i.startswith('_')]
        return f"""<{self.__class__.__name__}, modules: {module_list}>"""
