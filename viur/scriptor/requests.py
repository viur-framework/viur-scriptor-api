import requests
from .file import File
from ._utils import is_pyodide_context

if is_pyodide_context():
    import js
    from pyodide.ffi import to_js


class WebRequest:
    """
    provides methods to request data from HTTP-Servers
    """

    @classmethod
    async def get(cls, url, params=None, headers=None, **kwargs):
        """
        handles HTTP-GET-requests

        :param url: the URL of the endpoint
        :param params: parameters of the request (for the query string)
        :param headers: HTTP-headers to send with the request
        :param kwargs: additional parametrs
        :return: ``WebResponse``
        """
        return await cls.request(method='GET', url=url, params=params, headers=headers, **kwargs)

    @classmethod
    async def download(cls, url, **kwargs):
        """
        convenience-method for simple HTTP-GET-Reuests that don't need parameters or headers

        :param url: the URL of the endpoint
        :param kwargs: additional parameters
        :return: ``WebResponse``
        """
        return await cls.get(url=url, **kwargs)

    @classmethod
    async def post(cls, url, data, params=None, headers=None, **kwargs):
        """
        handles HTTP-POST-requests

        :param url: the URL of the endpoint
        :param data: the data to send to the endpoint
        :param params: parameters of the request
        :param headers: HTTP-headers to send with the request
        :param kwargs: additional parametrs
        :return: ``WebResponse``
        """
        return await cls.request(method='POST', url=url, data=data, params=params, headers=headers, **kwargs)

    @classmethod
    async def put(cls, url, data, params=None, headers=None, **kwargs):
        """
        handles HTTP-PUT-requests

        :param url: the URL of the endpoint
        :param data: the data to send to the endpoint
        :param params: parameters of the request
        :param headers: HTTP-headers to send with the request
        :param kwargs: additional parametrs
        :return: ``WebResponse``
        """
        return await cls.request(method='PUT', url=url, data=data, params=params, headers=headers, **kwargs)

    @classmethod
    async def delete(cls, url, params, data, headers, **kwargs):
        """
        handles HTTP-DELETE-requests

        :param url: the URL of the endpoint
        :param data: the data to send to the endpoint
        :param parameters: parameters of the request
        :param headers: HTTP-headers to send with the request
        :param kwargs: additional parametrs
        :return: ``WebResponse``
        """
        return await cls.request(method='DELETE', url=url, params=params, data=data, headers=headers, **kwargs)

    if is_pyodide_context():
        @classmethod
        async def request(cls, method: str, url, **kwargs):
            """
            handles general HTTP-requests

            :param method: the method to use (GET, PUT, POST or DELETE)
            :param url: the URL of the endpoint
            :param kwargs: additional parameters
            :return: ``WebResponse``
            """
            mup = method.upper()
            assert mup in ("GET", "POST", "PUT", "DELETE"), "invalid method: only GET, POST, PUT and DELETE are allowed"
            params = {"method": mup}
            params.update(kwargs)
            if "headers" in params:
                params["headers"] = to_js(params["headers"])
            res = await js.fetch(url, **params)
            content = (await res.arrayBuffer()).to_bytes()
            return WebResponse(url=url, http_status_code=res.status, content=content)

    else:
        @classmethod
        async def request(cls, method: str, url, **kwargs):
            """
            handles general HTTP-requests

            :param method: the method to use (GET, PUT, POST or DELETE)
            :param url: the URL of the endpoint
            :param kwargs: additional parameters
            :return: ``WebResponse``
            """
            mup = method.upper()
            assert mup in ("GET", "POST", "PUT", "DELETE"), "invalid method: only GET, POST, PUT and DELETE are allowed"
            res = requests.request(method=mup, url=url, **kwargs)
            return WebResponse(url=url, http_status_code=res.status_code, content=res.content)


class WebResponse(File):
    """
    represents the result of a ``WebRequest``, can have the requested content or information about errors.
    """

    def __init__(self, url, http_status_code, content):
        super().__init__(content, url.rsplit('/', 1)[-1].split('?', 1)[0])
        self._url = url
        self._http_status_code = http_status_code

    def __repr__(self):
        return f"""<{self.__class__.__name__} filename="{self.filename}", status_code={self._http_status_code}, """ \
               f"""size={len(self._data)}>"""

    def get_url(self):
        """
        returns the url that was requested

        :return: the url that was requested
        """
        return self._url

    def get_status_code(self):
        """
        returns the HTTP-status-code returned from the server

        :return: the HTTP-status-code
        """
        return self._http_status_code

    def get_content(self):
        """
        returns the content of the HTTP-response

        :return: the content of the HTTP-response
        """
        return self._data
