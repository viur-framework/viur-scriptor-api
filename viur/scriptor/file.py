import json
import chardet
import magic
from openpyxl.reader.excel import ExcelReader
from io import BytesIO, StringIO
import csv
from ._utils import list_table_to_dict_table, normalize_table, list_to_excel, list_to_csv, save_file
from .dialog import Dialog


class File:
    """
    Represents an opened file or data. Used to open files from the user or build files for the user to download.

    :param data: The ``bytes`` the file should contain.
    :param filename: The name the file should have.
    """

    _table_mimetypes = {
        'text/csv': 'csv',
        'text/plain': 'csv',  # tab-separated-values
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': 'xlsx'
    }

    def __init__(self, data: bytes, filename: str = None):
        assert isinstance(data, bytes)
        self._data = data
        self.filename = filename

    def __repr__(self):
        return f"""<{self.__class__.__name__} filename="{self.filename}", size={len(self._data)}>"""

    @classmethod
    def from_string(cls, text: str, filename: str = 'text.txt'):
        """
        creates a text-file from a string

        :param text: ``string``-content the file should have
        :param filename: name the file should have
        :return: ``File``-object
        """
        return File(data=text.encode('UTF-8'), filename=filename)

    @classmethod
    def from_bytes(cls, data: bytes, filename: str = 'bytes.bin'):
        """
        creates a binary file from ``bytes``

        :param data: ``bytes`` the file should contain
        :param filename: name the file should have
        :return: ``File``-object
        """
        return File(data=data, filename=filename)

    @classmethod
    async def from_url(cls, url: str, filename: str | None = None):
        """
        creates a binary file from ``bytes``
        :param url: ``str`` the url where the file can be downloaded from
        :param filename: name the file should have
        :return: ``File``-object
        """
        from . import modules
        response = await modules.viur_request('GET', url, raw=True)
        if filename is None:
            filename = response.filename
        return File(data=response.get_content(), filename=filename)

    @classmethod
    def from_table(cls, table: list[list[str, ...]] | list[dict[str, str]], header: list[str] = None,
                   filename: str = "table.xlsx", fill_empty: bool = False, auto_str: bool = False, csv_delimiter=','):
        """
        creates a CSV- or XLSX-file containing a single table

        :param table: table that should be saved: Either a ``list`` of ``list``\\ s or a ``list`` of ``dict``\\ s (one for each row)
        :param header: (optional) header of the table, if :data:`table` is a ``list`` of ``dict``\\ s, the header defines the order of columns
        :param filename: name the file should have
        :param fill_empty: if true, missing data is replaced by an empty ``string`` (this is primarily intended for testing and debugging)
        :param auto_str: if true, all keys and values are automatically converted to str
        :param csv_delimiter: the delimiter used to separate fields in csv-tables, ignored for xlsx
        :return: ``File``-object
        """
        file_suffix = filename.split('.')[-1]
        normalized_table = normalize_table(table, header=header, fill_empty=fill_empty, auto_str=auto_str)
        if file_suffix == "xlsx":
            data = list_to_excel(normalized_table)
        elif file_suffix == "csv":
            data = list_to_csv(normalized_table, delimiter=csv_delimiter).encode()
        else:
            raise ValueError("Only .csv and .xlsx are supported file extensions.")
        return File(data=data, filename=filename)

    def get_filename(self):
        """
        returns the name of the file

        :return: name of the file
        """
        return self.filename

    def get_size(self):
        """
        returns the size of the files data in bytes

        :return: the size of the files data in bytes
        """
        return len(self._data)

    def as_bytes(self):
        """
        returns the content of the file as ``bytes``

        :return: file-data
        """
        return self._data

    def as_text(self, encoding: str = None):
        """
        decodes the whole content of the file as a string and returns it

        :param encoding: (optional) if set, the content of the file is decoded using this encoding, otherwise the encoding is automatically guessed
        :return: content of the file as a ``string``
        """
        if encoding is None:
            encoding = self.guess_text_encoding()['encoding']
        return self._data.decode(encoding)

    def as_object_from_json(self):
        """
        parses JSON-data to a python-object representing the decoded data of the json-file, throws an exception if the file is not a valid JSON-file

        :return: python-object represented by the JSON-file
        """
        return json.loads(self._data)

    def _xls_data_to_list_table(self):
        bio = BytesIO(self._data)
        xls_reader = ExcelReader(bio, data_only=True)
        xls_reader.read()
        wb = xls_reader.wb
        ws = wb.active
        table = []
        for xlsrow in ws.rows:
            row = []
            for cell in xlsrow:
                row.append(cell.value)
            table.append(row)
        return table

    def _csv_data_to_list_table(self, delimiter=None):
        if delimiter:
            params = {'delimiter': delimiter}
        else:
            params = {}
        reader = csv.reader(StringIO(self.as_text()), **params)
        return list(reader)

    def as_list_table(self, csv_delimiter=None):
        """
        loads tabular data (i.e. a csv- or xlsx-file) as a ``list`` of ``list``\\ s

        :return: ``list`` of ``list``\\ s representing a table
        """
        try:
            detected_mime_type = self._table_mimetypes[self.detect_mime_type()]
        except KeyError:
            raise ValueError("The content of the file doesn't seem to be a table.")

        if detected_mime_type == "xlsx":
            return self._xls_data_to_list_table()
        elif detected_mime_type == "csv":
            if csv_delimiter:
                params = {'delimiter': csv_delimiter}
            else:
                params = {}
            return self._csv_data_to_list_table(**params)

    def as_dict_table(self, csv_delimiter=None):
        """
        loads tabular data (i.e. a csv- or xlsx-file) as a ``list`` of ``dict``\\ s

        :return: ``list`` of ``dict``\\ s representing a table
        """
        return list_table_to_dict_table(self.as_list_table(csv_delimiter=csv_delimiter))

    def detect_mime_type(self):
        """
        determines the mime-type from the files content

        :return: mime-type of the file
        """
        detected = magic.detect_from_content(self._data)
        return detected.mime_type

    def guess_text_encoding(self):
        """
        guesses the most likely encoding of the file

        :return: ``dict`` with the most probable encoding's name, probability and language if available
        """
        return chardet.detect(self._data)

    def get_all_text_encoding_guesses(self):
        """
        guesses the most likely encodings of the file

        :return: ``list`` of ``dict``\\ s with the most probable encodings and their name, probability and language if available
        """
        return chardet.detect_all(self._data)

    async def save_dialog(self, prompt: str = "Please select a file to save to:"):
        """
        asks the user where to save the file and saves it

        :param prompt: (optional) the prompt the user will read
        """
        await Dialog._save_file_dialog(prompt=prompt, data=self._data)

    @classmethod
    async def open_dialog(cls, prompt: str = "Please select a file to open:", types: list[dict] = []):
        """
        asks the user for a file to open
        :param prompt: (optional) the prompt the user will read
        :param types: Types of files
        Example:
        types= [
            {
                "description": "Images",
                "accept":{
                             "image/*": [".png", ".gif", ".jpeg", ".jpg"],
                         },
            }
        ]
        https://developer.mozilla.org/en-US/docs/Web/API/Window/showOpenFilePicker#examples
        :return: ``File``-object
        """
        return await Dialog._open_file_dialog(prompt=prompt, types=types)

    def download(self):
        """
        downloads the file to the users download-directory
        """
        save_file(data=self._data, filename=self.filename)
