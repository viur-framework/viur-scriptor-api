from .writer import MemoryWriter, FilePickerWriter
from .utils import is_pyodide_context

if is_pyodide_context():
	from js import console

import csv
import json

from .logger import Logging as logging


class MemoryCsvWriter(MemoryWriter):
	"""
	Writer for CSV exports
	"""

	DEFAULT_FILE_NAME = "export.csv"

	def __init__(self, *args, delimiter=";", formatter: callable = None):
		super().__init__()
		self._content.write("\ufeff")  # excel needs this for right utf-8 decoding
		if args:
			self._writer = csv.DictWriter(
				self._content,
				fieldnames=args,
				extrasaction="ignore",
				delimiter=delimiter,
				dialect="excel",
				quoting=csv.QUOTE_ALL
			)
			self._writer.writeheader()
		else:
			self._writer = csv.writer(
				self._content,
				delimiter=delimiter,
				dialect="excel",
				quoting=csv.QUOTE_ALL
			)

		self._formatter: callable = formatter

	@property
	def writer(self):
		return self._writer

	@writer.setter
	def writer(self, writer: csv.DictWriter):
		self._writer = writer

	def fmt(self, value):
		if self._formatter:
			ret = self._formatter(value)
			if ret is not None:
				return ret

		if isinstance(value, list):
			ret = ", ".join([self.fmt(v) for v in value])
			return ret
		elif isinstance(value, dict):
			return json.dumps(value, sort_keys=True)

		return str(value)

	async def write(self, values: object):
		if isinstance(values, dict):
			assert isinstance(self._writer, csv.DictWriter)
			self._writer.writerow({k: self.fmt(v) for k, v in values.items() if k in self._writer.fieldnames})
			self._line_count += 1
		elif isinstance(values, list):
			if isinstance(self._writer, csv.DictWriter):
				for row in values:
					self.write(row)
			else:
				self._writer.writerow([self.fmt(v) for v in values])
				self._line_count += 1
		else:
			raise NotImplementedError(f"Don't know what to do with {repr(values)}")


	def __str__(self):
		return self._content.getvalue()

class FileSystemCsvWriter(FilePickerWriter):
	"""
	Writer for CSV exports
	"""

	DEFAULT_FILE_NAME = "export.csv"

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self._columns = []
		self._writer: MemoryWriter = None
		self._delimiter = ";"
		self._formatter = None
	
	def set_formatter(self, formatter: callable):
		self._formatter = formatter

	def set_columns(self, columns: list[str]):
		self._columns = columns
	
	def set_delimiter(self, delimiter: str):
		self._delimiter = delimiter

	async def flush(self):
		if self._writer is None:
			return

		content = str(self._writer)
		if content:
			## Flushing the header
			await super().write(content)

	
		self._writer.clear()

	async def __aenter__(self):
		self._writer = MemoryCsvWriter(*self._columns, delimiter=self._delimiter, formatter=self._formatter)
		await super().__aenter__()

	async def __aexit__(self, *args):
		await self.flush()
		await super().__aexit__(*args)

	async def write(self, values: object, should_flush: bool = False):
		if self._writer is not None:
			await self._writer.write(values)

		if should_flush:
			await self.flush()
