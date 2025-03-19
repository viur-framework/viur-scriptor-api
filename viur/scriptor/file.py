import json
import zipfile
import chardet
import magic
import typing as t
from openpyxl.reader.excel import ExcelReader
from io import BytesIO, StringIO
import csv
from ._utils import list_table_to_dict_table, normalize_table, list_to_excel, list_to_csv, save_file
from .dialog import Dialog


class FileBase:
    def __init__(self, data: bytes | BytesIO, filename: str = None):
        assert isinstance(data, (bytes, BytesIO))
        assert isinstance(filename, str)
        self._data = data
        self.filename = filename

    def __repr__(self):
        return f"""<{self.__class__.__name__} filename="{self.filename}", size={len(self._data)}>"""

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
        return len(self._data.getvalue() if isinstance(self._data, BytesIO) else self._data)

    def as_bytes(self):
        """
        returns the content of the file as ``bytes``

        :return: file-data
        """
        return self._data.getvalue() if isinstance(self._data, BytesIO) else self._data

    def as_text(self, encoding: str = None):
        """
        decodes the whole content of the file as a string and returns it

        :param encoding: (optional) if set, the content of the file is decoded using this encoding, otherwise the
        encoding is automatically guessed
        :return: content of the file as a ``string``
        """
        data = self._data.getvalue() if isinstance(self._data, BytesIO) else self._data
        if encoding is None:
            encoding = self.guess_text_encoding()['encoding']
        return data.decode(encoding)

    async def save_dialog(self, prompt: str = "Please select a file to save to:"):
        """
        asks the user where to save the file and saves it

        :param prompt: (optional) the prompt the user will read
        """
        data = self._data.getvalue() if isinstance(self._data, BytesIO) else self._data
        await Dialog._save_file_dialog(prompt=prompt, data=data)

    @classmethod
    async def open_dialog(cls, prompt: str = "Please select a file to open:"):
        """
        asks the user for a file to open

        :param prompt: (optional) the prompt the user will read
        :return: ``File``-object
        """
        return await Dialog._open_file_dialog(prompt=prompt)

    def download(self):
        data = self._data.getvalue() if isinstance(self._data, BytesIO) else self._data
        save_file(data = data, filename = self.filename)


class File(FileBase):
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
        super().__init__(data,filename)

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
            data = list_to_csv(normalized_table, delimiter=csv_delimiter).encode('UTF-8')
        else:
            raise ValueError("Only .csv and .xlsx are supported file extensions.")
        return File(data=data, filename=filename)

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


class ZipFile(FileBase):
    def __init__(self, filename: str, mode: t.Literal['r', 'w', 'x', 'a'] = 'a'):
        super().__init__(BytesIO(), filename)
        self.mode = mode

    def add(self, file: File):
        """
        Adds a file to the zip archive
        """
        with self.zip_file as zip_file:
           zip_file.writestr(file.get_filename(), file.as_text())

    @property
    def zip_file(self):
        """
        Create an instance form a zipfile.ZipFile with the contents of self._data and return it
        :return: zipfile.ZipFile instance
        """
        return zipfile.ZipFile(self._data, self.mode, zipfile.ZIP_DEFLATED)

    def infolist(self):
        """
        Proxy function for ``zipfile.ZipFile.infolist``
        """
        return self.zip_file.infolist()

    def namelist(self):
        """
        Proxy function for ``zipfile.ZipFile.namelist``
        """
        return self.zip_file.namelist()

    def printdir(self):
        """
        Proxy function for ``zipfile.ZipFile.namelist``
        """
        return self.zip_file.printdir()
