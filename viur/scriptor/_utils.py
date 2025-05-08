import os
from io import StringIO, BytesIO
import openpyxl
from csv import writer as CSVWriter
from zipfile import ZipFile, ZIP_DEFLATED
import datetime
from openpyxl.writer.excel import ExcelWriter
from collections import Counter
import pathlib

__pyodide_context = False
__pyodide_in_browser = False
try:
    import pyodide
    import js
    import manager

    __pyodide_context = True
    __pyodide_in_browser = pyodide.ffi.IN_BROWSER
except ModuleNotFoundError:
    pass


def is_pyodide_context():
    return __pyodide_context


def is_pyodide_in_browser():
    return __pyodide_in_browser


if is_pyodide_context():
    async def _wait_for_result():
        while manager.resultValue is None:
            await manager.sleep(250)
        res = manager.resultValue
        if res == "__exit__":
            import sys
            sys.exit(0)
        manager.reset()
        manager.resultValue = None
        return res


def get_table_type(tbl, check_length=False, check_str=True):
    try:
        assert isinstance(tbl, list), "The outer container of the table must be a list."
        assert tbl, "The table is empty."
        if isinstance(tbl[0], dict):
            expected_length = len(tbl[0])
            for i in tbl:
                assert isinstance(i, dict), "Some, but not all rows of the table are dicts."
                assert not check_length or (len(i) == expected_length), "At least one dict doesn't have enough values."
                if check_str:
                    for key, value in i.items():
                        assert isinstance(key, str), "All keys must be of type str."
                        assert isinstance(value, str), "All values must be of type str."
            return 'dict'
        elif isinstance(tbl[0], list):
            expected_length = len(tbl[0])
            for i in tbl:
                assert isinstance(i, list), "Some, but not all rows of the table are lists."
                assert not check_length or (len(i) == expected_length), "At least one list doesn't have enough values."
                if check_str:
                    for j in i:
                        assert isinstance(j, str), "All elements of a row-list must be of type str."
            return 'list'
    except AssertionError as ae:
        raise ValueError(ae.args[0])


def normalize_table(table, header=None, fill_empty=False, auto_str=False):
    table_type = get_table_type(table, check_length=not fill_empty, check_str=not auto_str)
    if table_type == "dict":
        table = stringify(table, max_depth=2)
        if header is None:
            header = generate_dict_table_header(dicts=table)
        else:
            header = stringify(header, max_depth=1)
        return list(table_dict_to_list_style_generator(table, header, fill_empty=fill_empty))
    elif table_type == "list":
        if header:
            header = stringify(header, max_depth=1)
        table = stringify(table, max_depth=2)
        if not fill_empty:
            if header:
                return [header] + table
            else:
                return table
        if header is None:
            header, *table = table
        header_len = len(header)
        return [extend_list(row, header_len, '') for row in [header] + table]
    else:
        raise ValueError(f"""Tables must be of type list[dict[str,str]] or list[list[str]].""")


def table_dict_to_list_style_generator(data, header, fill_empty=False):
    yield header
    empty_string = ''
    if fill_empty:
        for d in data:
            yield [d.get(i, empty_string) for i in header]
    else:
        for d in data:
            yield [d[i] for i in header]


def list_to_csv(data, header=None, delimiter=','):
    sio = StringIO()
    writer = CSVWriter(sio, delimiter=delimiter)
    if header:
        writer.writerow(header)
    writer.writerows(data)
    return sio.getvalue()


def list_to_excel(data):
    workbook = openpyxl.Workbook()
    sheet = workbook.active
    for d in data:
        sheet.append(d)
    bio = BytesIO()
    archive = ZipFile(bio, 'w', ZIP_DEFLATED, allowZip64=True)
    workbook.properties.modified = datetime.datetime.utcnow()
    writer = ExcelWriter(workbook, archive)
    writer.save()
    bio.seek(0)
    return bio.getvalue()


def list_table_to_dict_table(list_table, header=None):
    if header is None:
        header, *list_table = list_table
    return [dict(zip(header, row)) for row in list_table]


def join_url(parts):
    return '/'.join(part.strip('/') for part in parts if part is not None)


if not is_pyodide_context():
    def _get_scriptor_default_save_directroy():
        if "SCRIPTOR_DEFAULT_SAVE_DIRECTORY" in os.environ:
            p = pathlib.Path(os.environ["SCRIPTOR_DEFAULT_SAVE_DIRECTORY"])
        else:
            p = pathlib.Path.home() / 'Scriptor_Downloads'
            print(f"""Warning: No default directory for saving files set. You can define in the """
                  f"""environment-variable SCRIPTOR_DEFAULT_SAVE_DIRECTORY. Your files will be saved in {str(p)}.""")
        if not p.exists():
            p.mkdir(parents=True, exist_ok=True)
        if p.is_dir():
            return p
        else:
            raise ValueError(f"""The path "{str(p)}" is not valid.""")

if is_pyodide_context():
    def save_file(data: bytes, filename: str = "file.bin"):
        js.self.postMessage(
            type="download",
            blob=js.Blob.new(
                [js.Uint8Array.new(data).buffer],
                {type: 'application/octet-stream'}
            ),
            filename=filename
        )
else:
    def save_file(data: bytes, filename: str = "file.bin"):
        scriptor_default_save_directroy = _get_scriptor_default_save_directroy()
        if '.' in filename:
            filename_prefix, filename_extension = filename.rsplit('.', 1)
            filename_extension = f""".{filename_extension}"""
        else:
            filename_prefix = filename
            filename_extension = ''
        full_file_path = scriptor_default_save_directroy / filename
        exists_count = 0
        while full_file_path.exists():
            exists_count += 1
            full_file_path = (scriptor_default_save_directroy /
                              f"""{filename_prefix}_{str(exists_count).zfill(3)}{filename_extension}""")
        assert not full_file_path.exists()
        with open(full_file_path, 'wb') as fout:
            fout.write(data)
        print(f"""Saved a file in "{str(full_file_path)}".""")


def extend_list(l, target_length, filler):
    len_l = len(l)
    if len_l == target_length:
        return l
    assert len_l <= target_length
    return l + ([filler] * (target_length - len_l))


def generate_dict_table_header(dicts: list):
    assert isinstance(dicts, list)
    assert all(isinstance(d, dict) for d in dicts)
    key_lists = [list(d.keys()) for d in dicts]
    header = []
    while key_lists:
        candidates = []
        for ks in key_lists:
            k = ks[0]
            if k not in candidates:
                candidates.append(k)
        counter = Counter(candidates)
        next_header_item = counter.most_common()[0][0]
        header.append(next_header_item)
        for ks in key_lists:
            try:
                ks.remove(next_header_item)
            except ValueError:
                pass
        key_lists = [l for l in key_lists if l]
    return header


def stringify(data, max_depth=None):
    if max_depth or max_depth is None:
        if max_depth is not None:
            max_depth -= 1
        if isinstance(data, list):
            res = []
            for i in data:
                if isinstance(i, (list, tuple, dict)):
                    res.append(stringify(i, max_depth=max_depth))
                else:
                    res.append(str(i))
            return res
        elif isinstance(data, dict):
            res = {}
            for i in data.keys():
                if isinstance(data[i], (list, tuple, dict)):
                    res[str(i)] = stringify(data[i], max_depth=max_depth)
                else:
                    res[str(i)] = str(data[i])
            return res
    return str(data)


def flatten_dict(data, none_value="", prefix=None):
    if isinstance(data, list):
        if any(isinstance(entry, dict) for entry in data):
            if not all(isinstance(entry, dict) for entry in data):
                raise ValueError("Inconsistent data in List, dicts and other types are mixed.")
        if not data:
            yield prefix, none_value
        for index, value in enumerate(data):
            if prefix is not None:
                yield from flatten_dict(value, none_value=none_value, prefix=f"""{prefix}.{index}""")
            else:
                yield from flatten_dict(value, none_value=none_value, prefix=f"""{index}""")
    elif isinstance(data, dict):
        for key, value in data.items():
            if prefix is not None:
                yield from flatten_dict(value, none_value=none_value, prefix=f"""{prefix}.{key}""")
            else:
                yield from flatten_dict(value, none_value=none_value, prefix=f"""{key}""")
    else:
        if data is None:
            data = none_value
        yield prefix, data


async def gather_async_iterator(async_iterator):
    """
    a helper function to get a list from an asynchronous itrator without using async for

    :param async_iterator: the iterator of which the content should be returned
    :return: a list of the content of the iterator
    """

    async def gai_internal(async_iterator):
        res = []
        async for i in async_iterator:
            res.append(i)
        return res

    result = await gai_internal(async_iterator)
    return result


if is_pyodide_context():
    def bytes_to_blob(b: bytes):
        length = len(b)
        buffer = js.eval(f"new Uint8Array({length})")
        for index, value in enumerate(b):
            buffer[index] = value
        buffer.__len__ = lambda: length
        buffer.buffer.__len__ = lambda: length
        blob = js.Blob.new([buffer.buffer], {type: 'application/octet-stream'})
        return blob

if is_pyodide_context():
    def clear_console(length=0):
        """
            A helper function to clear console output.
            :param length: the length of the console output
            :return: None
        """
        js.self.postMessage(
            type="clear",
            length=length
        )
else:
    def clear_console(length=0):
        os.system('cls' if os.name == 'nt' else 'clear')

