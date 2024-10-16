import datetime
import os
from ._utils import is_pyodide_context
import json

if is_pyodide_context():
    import pyodide
    import js
    from ._utils import _wait_for_result, bytes_to_blob

else:
    import prompt_toolkit
    from prompt_toolkit.completion import PathCompleter, FuzzyCompleter
    from prompt_toolkit.validation import Validator, ValidationError
    from simple_term_menu import TerminalMenu
from . import file as _file

_python_print = print

if not is_pyodide_context():
    class _FileExistsValidator(Validator):

        def validate(self, document):
            text = document.text
            if not text.strip():
                raise ValidationError(message="Bitte geben sie einen Dateinamen ein.")
            if not os.path.exists(text):
                raise ValidationError(message="Eine Datei mit diesem Namen existiert nicht.")


    class _FileDoesntExistsOrShouldBeReplacedValidator(Validator):
        def validate(self, document):
            text = document.text
            if not text.strip():
                raise ValidationError(message="Bitte geben sie einen Dateinamen ein.")
            if os.path.exists(text) and not text.endswith('!'):
                raise ValidationError(
                    message="This file already exists. If you want to replace it, add an exclamation-mark (!) at the end.")


    class _ConvertableValidator(Validator):
        def __init__(self, conversion_function, error_message=None):
            super().__init__()
            self._conversion_function = conversion_function
            self._errormessage = error_message

        def validate(self, document):
            text = document.text
            try:
                self._conversion_function(text)
            except Exception:
                if self._errormessage is None:
                    errormessage = "Das Format stimmt nicht."
                else:
                    errormessage = self._errormessage
                raise ValidationError(message=errormessage)


    class _StringNotEmptyValidator(Validator):
        def validate(self, document):
            if not document.text:
                raise ValidationError(message="You need to enter text. An empty string is not allowed.")


class Dialog:
    if is_pyodide_context():
        @staticmethod
        def print(*args, sep=' ', end='\n', file=None, flush=False):
            """
            displays Text

            :param args: ``string`` / ``object``\\ s that should be displayed.
            :param sep: ``string`` inserted between values, default a space.
            :param end: ``string`` appended after the last value, default a newline. ignored in browser.
            :param file: a file-like object (stream); defaults to the current sys.stdout. ignored in browser.
            :param flush: whether to forcibly flush the stream. ignored in browser.
            """
            js.self.postMessage(type="log", text=sep.join(str(t) for t in args), level="info")
    else:
        @staticmethod
        def print(*args, sep=' ', end='\n', file=None, flush=False):
            """
            displays Text

            :param args: ``string`` / ``object``\\ s that should be displayed.
            :param sep: `string` inserted between values, default a space.
            :param end: `string` appended after the last value, default a newline. ignored in browser.
            :param file: a file-like object (stream); defaults to the current sys.stdout. ignored in browser.
            :param flush: whether to forcibly flush the stream. ignored in browser.
            """
            _python_print(*args, sep=sep, end=end, file=file, flush=flush)

    if is_pyodide_context():
        @staticmethod
        async def alert(text: str, image=None):
            """
            Shows a message to the user and blocks until it is confirmed.

            :param text: The message to be displayed
            :param image: displays an image in the alert-box
            """
            js.self.postMessage(type="alert", text=text, image=image)
            await _wait_for_result()
    else:
        @staticmethod
        async def alert(text: str, image=None):
            """
            Shows a message to the user and blocks until it is confirmed.

            :param text: The message to be displayed
            :param image: displays an image in the alert-box
            """
            print(text)
            if image:
                print(f"In the Browser, an image would have been shown here: {image}")
            input("Please press <Enter> to continue...")

    if is_pyodide_context():
        @staticmethod
        async def _open_file_dialog(prompt=None):
            js.self.postMessage(type="showOpenFilePicker")
            res = await _wait_for_result()
            if res == -1:
                raise RuntimeError("The user has cancelled the dialog.")
            file = await res[0].getFile()
            bytes = (await file.arrayBuffer()).to_bytes()
            return _file.File.from_bytes(data=bytes, filename=file.name)
    else:
        @staticmethod
        async def _open_file_dialog(prompt=None):
            if prompt is None:
                prompt = "Bitte geben sie eine Datei zum öffnen an:"
            prompt += ' '
            filename = await prompt_toolkit.PromptSession().prompt_async(prompt,
                                                                         completer=FuzzyCompleter(PathCompleter()),
                                                                         complete_while_typing=True,
                                                                         validator=_FileExistsValidator())
            with open(filename, 'rb') as fin:
                data = fin.read()
            return _file.File(data=data, filename=filename)

    if is_pyodide_context():
        @staticmethod
        async def _save_file_dialog(data, prompt):
            assert isinstance(data, (str, bytes)), "data must be of type str or bytes"
            js.self.postMessage(type="showSaveFilePicker")
            res = await _wait_for_result()
            if res == -1:
                raise RuntimeError("The user has cancelled the dialog.")
            w = await res.createWritable()
            if isinstance(data, str):
                await w.write(data)
            elif isinstance(data, bytes):
                await w.write(bytes_to_blob(data))
            await w.close()

    else:
        @staticmethod
        async def _save_file_dialog(data, prompt):
            validator = _FileDoesntExistsOrShouldBeReplacedValidator()
            filename = await prompt_toolkit.PromptSession().prompt_async(prompt,
                                                                         completer=FuzzyCompleter(PathCompleter()),
                                                                         complete_while_typing=True,
                                                                         validator=validator)
            if filename.endswith('!'):
                filename = filename[:-1]
            if isinstance(data, str):
                with open(filename, 'w') as fout:
                    fout.write(data)
            elif isinstance(data, bytes):
                with open(filename, 'wb') as fout:
                    fout.write(data)
            else:
                raise ValueError('Nur Strings und Bytestrings können gespeichert werden.')

    if is_pyodide_context():
        @staticmethod
        async def select(options: dict[str, str] | list[str] | tuple[str], title: str = None, text: str = None,
                         multiselect: bool = False, image=None):
            """
            Gives the user a choice between different options.
            If multiselect is False, only one selection is allowed, otherwise the user can select multiple options.

            :param options: the selectable options
            :param multiselect: if True, multiple options can be selected, otherwise only one
            :param image: displays an image in the select-box
            :return: a ``tuple`` of the selected options
            """
            if isinstance(options, dict):
                assert all(i is not None for i in options.values()), "No value of a choices-dict may be None."
                choices = options
            elif isinstance(options, (list, tuple)):
                choices = {i: i for i in options if
                           i is not None}
            title = title or "Select"
            text = text or ("Please select any options:" if multiselect else "Please select an option:")
            js.self.postMessage(
                type="select",
                title=title,
                text=text,
                choices=pyodide.ffi.to_js(choices, dict_converter=js.Object.fromEntries),
                multiple=multiselect,
                image=image
            )
            if multiselect:
                return [choices[i] for i in (await _wait_for_result())]
            else:
                return choices[await _wait_for_result()]
    else:
        @staticmethod
        async def select(options: dict[str, str] | list[str] | tuple[str], title: str = None, text: str = None,
                         multiselect: bool = False, image=None):
            """
            Gives the user a choice between different options.
            If multiselect is False, only one selection is allowed, otherwise the user can select multiple options.

            :param options: the selectable options
            :param multiselect: if True, multiple options can be selected, otherwise only one
            :param image: displays an image in the select-box
            :return: a ``tuple`` of the selected options
            """
            assert isinstance(options, dict)
            keys = list(options.keys())
            title = title or "Select"
            text = text or ("Please select any options:" if multiselect else "Please select an option:")
            print(title)
            print(text)
            if image:
                print(f"In the Browser, an image would have been shown here: {image}")
            terminal_menu = TerminalMenu(
                keys,
                multi_select=multiselect,
                show_multi_select_hint=multiselect,
                search_key=False if multiselect else None  # disable search on multiselect
            )
            menu_entry_index = terminal_menu.show()
            print(f"""{menu_entry_index = }""")
            if multiselect:
                return [options[keys[selection]] for selection in menu_entry_index]
            else:
                return options[keys[menu_entry_index]]

    @staticmethod
    async def confirm(text: str = None, title: str = None, yes: str = "Yes", no: str = "No"):
        """
        Asks the user to answer a Yes/No Question

        :param yes: (optional) the word for 'yes'
        :param no: (optinoal) the word for 'no'
        :return:
        """
        title = title or "Confirm"
        text = text or "OK?"
        return await Dialog.select(options={yes: yes, no: no}, title=title, text=text) == yes

    if is_pyodide_context():
        @staticmethod
        async def text(prompt: str = None, title: str = "Text Input", empty: bool = None, placeholder: str = None,
                       image=None, multiline=False):
            """
            prompts the user to enter text

            :param prompt: the prompt the user will be shown
            :param title: the title of the textbox
            :param empty: allow the empty ``string`` as a valid result
            :param image: displays an image in the text-box
            :param placeholder: the placehodler-text to be displayed in the textbox while it is empty
            :param multiline: enables multiline-input
            :return: the text entered by the user
            """
            kwargs = {
                "type": "input",
                "title": title,
                "text": prompt,
                "empty": empty,
                "image": image,
                "placeholder": placeholder,
            }
            if multiline:
                kwargs["input_type"] = "text"
            js.self.postMessage(**kwargs)
            return await _wait_for_result()
    else:
        @staticmethod
        async def text(prompt: str = None, title: str = "Text Input", empty: bool = None, placeholder: str = None,
                       image=None, multiline=False):
            """
            prompts the user to enter text

            :param prompt: the prompt the user will be shown
            :param title: the title of the textbox
            :param empty: allow the empty ``string`` as a valid result
            :param image: displays an image in the text-box
            :param placeholder: the placehodler-text to be displayed in the textbox while it is empty
            :param multiline: enables multiline-input
            :return: the text entered by the user
            """
            if title:
                print(title)
            if image:
                print(f"In the Browser, an image would have been shown here: {image}")
            if prompt is None:
                prompt = "Bitte geben sie Text ein:"
            if multiline:
                print("press [Esc] and then [Enter] to finish...")
            return await prompt_toolkit.PromptSession().prompt_async(
                prompt,
                placeholder=placeholder,
                validator=None if empty else _StringNotEmptyValidator(),
                multiline=multiline
            )

    if is_pyodide_context():
        @staticmethod
        async def number(prompt: str = None, title: str = "Number Input", image=None):
            """
            prompts the user to input a number

            :param prompt: the prompt the user will be shown
            :param title: the title of the textbox
            :param number_type: the type of expected number
            :param image: displays an image in the number-box
            :return: the number the user endered
            """
            js.self.postMessage(
                type="input",
                title=title,
                text=prompt,
                input_type='number',
                image=image
            )
            return await _wait_for_result()
    else:
        @staticmethod
        async def number(prompt: str = None, title: str = "Number Input", image=None):
            """
            prompts the user to input a number

            :param prompt: the prompt the user will be shown
            :param title: the title of the textbox
            :param number_type: the type of expected number
            :param image: displays an image in the number-box
            :return: the number the user endered
            """
            if title:
                print(title)
            if image:
                print(f"In the Browser, an image would have been shown here: {image}")
            if prompt is None:
                prompt = "Bitte geben eine Zahl ein:"
            validator = _ConvertableValidator(conversion_function=float, error_message="Bitte geben sie eine Zahl ein.")
            res = await prompt_toolkit.PromptSession().prompt_async(prompt, validator=validator)
            try:
                return int(res)
            except ValueError:
                return float(res)

    if is_pyodide_context():
        @staticmethod
        async def date(prompt: str = None, use_time: bool = False, image=None):
            """
            prompts the user to input a date

            :param prompt: the prompt the user will be shown
            :param use_time: also input time in addition to the date
            :param image: displays an image in the date-box
            :return: the date entered by the user
            """
            js.self.postMessage(
                type="input",
                title="Date input",
                text=prompt,
                input_type="date",
                use_time=use_time,
                image=image
            )
            timestamp = await _wait_for_result()
            try:
                if use_time:
                    return datetime.datetime.fromisoformat(timestamp)
                else:
                    return datetime.date.fromisoformat(timestamp)
            except ValueError:
                pass
            if use_time:
                res = datetime.datetime.fromtimestamp(timestamp / 1000, tz=datetime.timezone.utc).replace(tzinfo=None)
            else:
                res = datetime.date.fromtimestamp(timestamp / 1000)
            return res
    else:
        @staticmethod
        async def date(prompt: str = None, use_time: bool = False, image=None):
            """
            prompts the user to input a date

            :param prompt: the prompt the user will be shown
            :param use_time: also input time in addition to the date
            :param image: displays an image in the date-box
            :return: the date entered by the user
            """
            if image:
                print(f"In the Browser, an image would have been shown here: {image}")
            if prompt is None:
                prompt = "Bitte geben sie ein Datum ein:"
            validator = _ConvertableValidator(
                conversion_function=datetime.datetime.fromisoformat,
                error_message="Bitte geben sie ein gütliges Datum ein."
            )
            entered_date = await prompt_toolkit.PromptSession().prompt_async(prompt, validator=validator)
            res = datetime.datetime.fromisoformat(entered_date)
            if not use_time:
                res = datetime.date.fromtimestamp(res.timestamp())
            return res

    if is_pyodide_context():
        @staticmethod
        async def show_diff(title: str, diffs: list[tuple[str, str, str]], image=None):
            """
            shows a diff-view to the user

            :param title: the title of the box
            :param diffs: the data to be shown
            :param image: displays an image in the diff-box
            """
            js.self.postMessage(type="diffcmp", title=title, changes=pyodide.ffi.to_js(diffs), image=image)
    else:
        @staticmethod
        async def show_diff(title: str, diffs: list[tuple[str, str, str]], image=None):
            """
            shows a diff-view to the user

            :param title: the title of the box
            :param diffs: the data to be shown
            :param image: displays an image in the diff-box
            """
            print(title)
            if image:
                print(f"In the Browser, an image would have been shown here: {image}")
            print('=' * len(title))
            for key, old, new in diffs:
                print(f"""{key}: {old} -> {new}""")
            print('')

    if is_pyodide_context():
        @staticmethod
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
        @staticmethod
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
                selection = await Dialog.text("Your selections (comma-separated ints): ")
                selection = json.loads(f"""[{selection}]""")
                assert isinstance(selection, list), "You need to input a json-list."
                assert all(isinstance(i, int) for i in selection), "All elements of the list must be ints."
                assert all(i < num_rows for i in selection), "You selected an invalid row."
                return selection
            else:
                selection = await Dialog.text("Your selection: ")
                selection = json.loads(selection)
                assert isinstance(selection, int)
                return selection
