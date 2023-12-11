import json

from urllib.parse import urlencode as _urlencode
from .utils import is_pyodide_context
from abc import abstractmethod

if is_pyodide_context():
	from js import console, fetch, FormData
	from pyodide.ffi import to_js
	from config import BASE_URL
else:
	import requests
	from requests.sessions import cookiejar_from_dict

from .logger import Logging as logging
import traceback


class Request:
	COOKIES = {}

	def __init__(self, method: str, url: str, credentials: bool = False, headers: dict = None,
				 data: dict = None) -> None:
		self._status = None
		self._result = None

		self._method = method.upper()
		self._data = None
		self._credentials = credentials

		if data:
			if method == "GET":
				url += "?" + _urlencode(data)
			else:
				if is_pyodide_context():
					self._data = FormData.new()
					for k, v in data.items():
						for val in self.to_form_value(k,v):
							self._data.append(val[0], val[1])

				else:
					self._data = data

		self._headers = headers
		self._url = url
		self._response = None

	def flat(self, val):
		res = []
		for v in val:
			if isinstance(v, list):
				res.extend(self.flat(v))
			else:
				res.append(v)
		return res

	def to_form_value(self, bone_name, val):
		def to_form_value_intern(bone_name_intern, val_intern):
			res = []
			if isinstance(val_intern, list):
				if any([isinstance(entry, dict) for entry in val_intern]):
					for idx, entry in enumerate(val_intern):
						res += to_form_value_intern(bone_name + "." + str(idx), entry)
				else:
					for v in val_intern:
						res.append(to_form_value_intern(bone_name, v))

			elif isinstance(val_intern, dict):
				for k, v in val_intern.items():
					if bone_name_intern:
						res.append(to_form_value_intern(f"{bone_name_intern}.{k}", v))
					else:
						res.append(to_form_value_intern(k, v))
			else:
				if val_intern is None:
					val_intern = ""
				if bone_name_intern:
					res.append((bone_name, val_intern))

			return res

		return self.flat(to_form_value_intern(bone_name, val))

	async def perform(self):
		if is_pyodide_context():
			options = {"method": self._method}

			if self._headers:
				options.update({"headers": to_js(self._headers)})

			if self._data:
				options.update({"body": to_js(self._data)})

			if self._credentials:
				options.update({"credentials": 'include'})

			self._response = await fetch(self._url, **options)
			self._status = self._response.status
		else:
			kwargs = {"headers": self._headers}
			if self._method == "POST":
				kwargs.update({"data": self._data})

			try:
				if self._credentials:
					kwargs.update({"cookies": self.COOKIES})
			except AttributeError:
				Logging.error("You need to set an cookie.")

			self._response = requests.request(self._method, self._url, **kwargs)
			self._status = self._response.status_code

	async def json(self):
		if not self._response:
			return None

		if is_pyodide_context():
			_text = await self._response.text()
			try:
				ret = json.loads(_text)
			except:
				# Logging.error(traceback.format_exc())
				ret = _text
			return ret

		return self._response.json()

	async def text(self):
		if is_pyodide_context():
			return await self._response.text()

		return self._response.text

	async def blob(self):
		if is_pyodide_context():
			return await self._response.blob()

		return self._response.content

	@staticmethod
	async def get(*args, **kwargs):
		_request = Request("GET", *args, **kwargs)
		await _request.perform()
		return _request

	@staticmethod
	async def post(*args, **kwargs):
		_request = Request("POST", *args, **kwargs)
		await _request.perform()

		return _request

	@staticmethod
	async def put(*args, **kwargs):
		_request = Request("PUT", *args, **kwargs)
		await _request.perform()

		return _request

	@staticmethod
	async def delete(*args, **kwargs):
		_request = Request("DELETE", *args, **kwargs)
		await _request.perform()

		return _request

	@staticmethod
	async def patch(*args, **kwargs):
		_request = Request("PATCH", *args, **kwargs)
		await _request.perform()

		return _request
