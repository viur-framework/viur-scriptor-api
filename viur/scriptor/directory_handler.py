from ._utils import is_pyodide_context

if is_pyodide_context():
    import pyodide
    import js
    from ._utils import bytes_to_blob, gather_async_iterator, _wait_for_result
else:
    import os
    import pathlib
    import prompt_toolkit
    from prompt_toolkit.completion import PathCompleter, FuzzyCompleter
    from prompt_toolkit.validation import Validator, ValidationError


    class DirectoryExistsOrShouldBeCreatedValidator(Validator):
        def validate(self, document):
            text = document.text
            if not os.path.isdir(text) and not text.endswith('!'):
                raise ValidationError(
                    message="This directory is not valid. If you want to try to create it, add an exclamation-mark (!) at the end.")


class WritableFileFromDirectoryHandler:
    def __init__(self, writable, parent, filename, file):
        self._file = file
        self._writable = writable
        self._parent = parent
        self._filename = filename
        self._closed = False

    def get_filename(self):
        """
        returns the name if the opened file

        :return: the name of the opened file
        """
        return self._filename

    if is_pyodide_context():
        async def write(self, data: bytes):
            """
            writes data to the opened file

            :param data: the data to write to the file
            """
            if self._closed:
                raise RuntimeError('This file is already closed.')
            assert isinstance(data, bytes), "data must be of type bytes"
            await self._writable.write(bytes_to_blob(data))
    else:
        async def write(self, data: bytes):
            """
            writes data to the opened file

            :param data: the data to write to the file
            """
            if self._closed:
                raise RuntimeError('This file is already closed.')
            assert isinstance(data, bytes), "data must be of type bytes"
            self._writable.write(data)

    if is_pyodide_context():
        async def close(self):
            """
            closes the file (data may not be persisted properly if the file isn't closed)
            """
            await self._writable.close()
            self._closed = True
            self._parent._opened_files.remove(self)
    else:
        async def close(self):
            """
            closes the file (data may not be persisted properly if the file isn't closed)
            """
            self._writable.close()
            self._closed = True
            self._parent._opened_files.remove(self)


class DirectoryHandler:
    if is_pyodide_context():
        def __init__(self, directory_handle):
            try:
                assert isinstance(directory_handle, pyodide.ffi.JsProxy)
                assert repr(directory_handle) == '[object FileSystemDirectoryHandle]'
            except AssertionError:
                raise ValueError("This class should be instantiated by it's .open()-method.")
            self._directory_handle = directory_handle
            self._name = directory_handle.name
            self._opened_files = []
            self._subdirectory_handlers = {}
    else:
        def __init__(self, directory_handle):
            try:
                assert isinstance(directory_handle, pathlib.Path)
                assert directory_handle.exists()
                assert directory_handle.is_dir()
            except AssertionError:
                raise ValueError("This class should be instantiated by it's .open()-method.")
            self._directory_handle = directory_handle
            self._name = str(directory_handle).split('/', -1)[-1]
            self._opened_files = []
            self._subdirectory_handlers = {}

    def __repr__(self):
        return f"""<{self.__class__.__name__} (directory name: "{self._name}")>"""

    @staticmethod
    def _check_filename(filename):
        return not any(i in filename for i in "/\\")

    if is_pyodide_context():
        @classmethod
        async def open(cls):
            """
            prompts the user to select a directory to work with.

            :return: a ``DirectoryHandler`` for the selected directory
            """
            js.self.postMessage(type="showDirectoryPicker")
            directory_handle = await _wait_for_result()
            if directory_handle == -1:
                raise RuntimeError("no directory has been opened")
            res = cls(directory_handle)
            return res
    else:
        @classmethod
        async def open(cls):
            """
            prompts the user to select a directory to work with.

            :return: a ``DirectoryHandler`` for the selected directory
            """
            dirname = await prompt_toolkit.PromptSession().prompt_async('Please enter a directory-name: ',
                                                                        completer=FuzzyCompleter(PathCompleter()),
                                                                        complete_while_typing=True,
                                                                        validator=DirectoryExistsOrShouldBeCreatedValidator())
            create = False
            if dirname.endswith('!'):
                dirname = dirname[:-1]
                create = True
            path = pathlib.Path(dirname).absolute()
            if create:
                path.mkdir(parents=True, exist_ok=True)
            res = cls(path)
            return res

    if is_pyodide_context():
        async def list_files(self):
            """
            lists the files in the selected directory

            :return: a ``list`` of all names of files present in the selected directory
            """
            entries = await gather_async_iterator(self._directory_handle.entries())
            files = [i[0] for i in entries if repr(i[1]) == "[object FileSystemFileHandle]"]
            return files
    else:
        async def list_files(self):
            """
            lists the files in the selected directory

            :return: a ``list`` of all names of files present in the selected directory
            """
            return [str(i).split('/', -1)[-1] for i in self._directory_handle.glob('*') if i.is_file()]

    if is_pyodide_context():
        async def list_subdirs(self):
            """
            lists the subdirectories in the selected directory

            :return: a ``list`` of all names of subdirectories present in the selected directory
            """
            entries = await gather_async_iterator(self._directory_handle.entries())
            files = [i[0] for i in entries if repr(i[1]) == "[object FileSystemDirectoryHandle]"]
            return files
    else:
        async def list_subdirs(self):
            """
            lists the subdirectories in the selected directory

            :return: a ``list`` of all names of subdirectories present in the selected directory
            """
            return [str(i).split('/', -1)[-1] for i in self._directory_handle.glob('*') if i.is_dir()]

    if is_pyodide_context():
        async def get_subdirectory_handler(self, dirname, create=False):
            """
            opens a subdirectory in a child-``DirectoryHandler``

            :param dirname: the name of the subdirectory that should be opened
            :param create: if set to true, the directory will be created if it doesn't already exist
            :return: ``DirectoryHandler`` for the subdirectory
            """
            try:
                return self._subdirectory_handlers[dirname]
            except KeyError:
                pass
            handle = None
            for k, v in await gather_async_iterator(self._directory_handle.entries()):
                if k == dirname:
                    handle = v
            if handle:
                if repr(handle) != "[object FileSystemDirectoryHandle]":
                    raise ValueError(f"""{dirname} is not a directory.""")
            else:
                if create:
                    handle = await self._directory_handle.getDirectoryHandle(dirname, create=create)
                else:
                    raise ValueError(f"""{dirname} does not exist.""")
            subdir_handler = DirectoryHandler(handle)
            self._subdirectory_handlers[dirname] = subdir_handler
            return subdir_handler

    else:
        async def get_subdirectory_handler(self, dirname, create=False):
            """
            opens a subdirectory in a child-``DirectoryHandler``

            :param dirname: the name of the subdirectory that should be opened
            :param create: if set to true, the directory will be created if it doesn't already exist
            :return: ``DirectoryHandler`` for the subdirectory
            """
            try:
                return self._subdirectory_handlers[dirname]
            except KeyError:
                pass
            subdir_path = self._directory_handle / dirname
            if create and not subdir_path.exists():
                subdir_path.mkdir()
            assert subdir_path.is_dir(), f"{subdir_path} is not a directory"
            subdir_handler = DirectoryHandler(subdir_path)
            self._subdirectory_handlers[dirname] = subdir_handler
            return subdir_handler

    if is_pyodide_context():
        async def open_file_for_writing(self, filename: str, create: bool = True, may_already_exist: bool = False):
            """
            opens a file from the selected directory for writing.
            (the content is completely replaced if the file already existed)

            :param filename: the name of the file to be written to
            :param create: if the file should be created if it doesn't already exist
            :param may_already_exist: if the file may already exist
            :return: a ``WritableFileFromDirectoryHandler`` representing the writable file
            """
            assert self._check_filename(filename), f"{filename} is not a valid filename"
            if not may_already_exist:
                if filename in (await self.list_files()):
                    raise ValueError(f"""A file with the name "{filename}" already exists.""")
            f = await self._directory_handle.getFileHandle(filename, create=create)
            wf = await f.createWritable()
            res = WritableFileFromDirectoryHandler(writable=wf, parent=self, filename=filename, file=f)
            self._opened_files.append(res)
            return res
    else:
        async def open_file_for_writing(self, filename: str, create: bool = True, may_already_exist: bool = False):
            """
            opens a file from the selected directory for writing.
            (the content is completely replaced if the file already existed)

            :param filename: the name of the file to be written to
            :param create: if the file should be created if it doesn't already exist, ignored in CLI.
            :param may_already_exist: if the file may already exist
            :return: a ``WritableFileFromDirectoryHandler`` representing the writable file
            """
            assert self._check_filename(filename), f"{filename} is not a valid filename"
            filepath = self._directory_handle / filename
            if not may_already_exist:
                assert not filepath.exists(), "This file already exists."
            fout = open(filepath, 'wb')
            res = WritableFileFromDirectoryHandler(writable=fout, parent=self, filename=filename, file=fout)
            self._opened_files.append(res)
            return res

    async def close_all(self):
        """
        closes all open ``WritableFileFromDirectoryHandler`` originating from this ``DirectoryHandler``
        and all of its child-DirectoryHandlers (after this, they can't be written to anymore)

        Intended to be called at the end of the script to make sure all files are correctly saved.
        """
        for open_file in self._opened_files:
            await open_file.close()
        for subdir_handler in self._subdirectory_handlers.values():
            await subdir_handler.close_all()

    if is_pyodide_context():
        async def write_to_file(self, data: bytes, filename: str, may_already_exist: bool = False):
            """
            writes data to a file in this directory

            :param data: the data that should be the new content of the file
            :param filename: the name of the file the data should be written to
            :param may_already_exist: if the file may already exist and should be replaced
            """
            assert self._check_filename(filename), f"{filename} is not a valid filename"
            f = await self.open_file_for_writing(filename=filename, may_already_exist=may_already_exist)
            await f.write(data=data)
            await f.close()
    else:
        async def write_to_file(self, data: bytes, filename: str, may_already_exist: bool = False):
            """
            writes data to a file in this directory

            :param data: the data that should be the new content of the file
            :param filename: the name of the file the data should be written to
            :param may_already_exist: if the file may already exist and should be replaced
            """
            assert self._check_filename(filename), f"{filename} is not a valid filename"
            filepath = self._directory_handle / filename
            if not may_already_exist:
                assert not filepath.exists(), "The file already exists"
            with open(filepath, 'wb') as fout:
                fout.write(data)

    if is_pyodide_context():
        async def read_from_file(self, filename: str, start: int = 0, end: int = None):
            """
            reads data from a file

            :param filename: the name of the file data should be read from
            :param start: the starting position in the file to read from
            :param end: the end position in the file to read to
            :return: the content of the file (or a part thereof) as bytes
            """
            assert self._check_filename(filename), f"{filename} is not a valid filename"
            f = await self._directory_handle.getFileHandle(filename, create=False)
            gf = await f.getFile()
            gfab = await gf.arrayBuffer()
            if start != 0 or end is not None:
                return gfab.slice(start, end).to_bytes()
            return gfab.to_bytes()
    else:
        async def read_from_file(self, filename: str, start: int = 0, end: int = None):
            """
            reads data from a file

            :param filename: the name of the file data should be read from
            :param start: the starting position in the file to read from
            :param end: the end position in the file to read to
            :return: the content of the file (or a part thereof) as bytes
            """
            assert self._check_filename(filename), f"{filename} is not a valid filename"
            with open(self._directory_handle / filename, 'rb') as fin:
                fin_len = fin.seek(0, 2)
                if start < 0:
                    start = fin_len + start
                if end is None:
                    end = fin_len
                elif end < 0:
                    end = fin_len + end
                fin.seek(start)
                data = fin.read(end - start)
            return data
