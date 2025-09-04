from viur.scriptor._utils import is_pyodide_context
import json
if is_pyodide_context():
    import pyodide
    import js
    from viur.scriptor._utils import _wait_for_result
else:
    from .text import text
if is_pyodide_context():
    async def table(header: list[str], rows: list[list[str]], select: bool = None, multiselect: bool = None,
                    image=None):
        """
        displays a table

        :param header: the header of the table
        :param rows: the data of the tabel
        :param select: if True, the user can select a row
        :param multiselect: if True and select is True, the user can select multiple rows
        :param image: displays an image in the table-box
        :return: list of indices of selected items (if select is True)
        """
        assert not (multiselect is True and select is False), "You can't multiselect with disabled selection."
        if multiselect:
            select = True
        header = pyodide.ffi.to_js(header)
        rows = pyodide.ffi.to_js(rows)
        js.self.postMessage(type="table", header=header, rows=rows, select=select, multiple=multiselect,
                            image=image)
        if select:
            res = await _wait_for_result()
            res = json.loads(f"[{res}]")
            return res
else:
    async def table(header: list[str], rows: list[list[str]], select: bool = None, multiselect: bool = None,
                    image=None):
        """
        displays a table

        :param header: the header of the table
        :param rows: the data of the tabel
        :param select: if True, the user can select a row
        :param multiselect: if True and select is True, the user can select multiple rows
        :param image: displays an image in the table-box
        :return: list of indices of selected items (if select is True)
        """
        assert not (multiselect is True and select is False), "You can't multiselect with disabled selection."
        if multiselect:
            select = True
        if image:
            print(f"In the Browser, an image would have been shown here: {image}")
        if select:
            header = [''] + header
            rows = [[str(i)] + row for i, row in enumerate(rows)]
        column_widths = [len(i) for i in header]
        for row in rows:
            for idx, col in enumerate(row):
                w = len(col)
                if column_widths[idx] < w:
                    column_widths[idx] = w
        separator = '|'.join('-' * (w + 2) for w in column_widths)
        print('|'.join([' ' + c.ljust(column_widths[i] + 1) for i, c in enumerate(header)]))
        print(separator)
        num_rows = len(rows)
        for row in rows:
            print('|'.join([' ' + c.ljust(column_widths[i] + 1) for i, c in enumerate(row)]))
        if multiselect:
            selection = await text("Your selections (comma-separated ints): ")
            selection = json.loads(f"""[{selection}]""")
            assert isinstance(selection, list), "You need to input a json-list."
            assert all(isinstance(i, int) for i in selection), "All elements of the list must be ints."
            assert all(i < num_rows for i in selection), "You selected an invalid row."
            return selection
        else:
            selection = await text("Your selection: ")
            selection = json.loads(selection)
            assert isinstance(selection, int)
            return selection
