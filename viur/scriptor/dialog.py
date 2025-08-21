import datetime
import os
import typing
from email.policy import default

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
                raise ValidationError(message="Please enter a valid filename.")
            if not os.path.exists(text):
                raise ValidationError(message="A file with this name doesn't exist.")


    class _FileDoesntExistsOrShouldBeReplacedValidator(Validator):
        def validate(self, document):
            text = document.text
            if not text.strip():
                raise ValidationError(message="Please enter a filename.")
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
                    errormessage = "The format is not correct."
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
        async def raw_html(html: str, in_multiple: bool = False):
            """
            Shows preformatted html to the user.

            :param html: the preformatted html as a string
            :param in_multiple: If true only the config of the Dialog is returned
            """
            if in_multiple:
                return {
                    "type": "raw_html",
                    "html": html,
                }

            js.self.postMessage(type="raw_html", html=html)
            await _wait_for_result()
    else:
        @staticmethod
        async def raw_html(html: str, in_multiple: bool = False):
            """
            Shows preformatted html to the user.

            :param html: the preformatted html as a string
            :param in_multiple: just for testing purposes
            """
            print(html)

    if is_pyodide_context():
        @staticmethod
        async def _open_file_dialog(prompt=None, types=[]):
            js.self.postMessage(
                type="showOpenFilePicker",
                types=pyodide.ffi.to_js(types, dict_converter=js.Object.fromEntries)
            )
            res = await _wait_for_result()
            if res == -1:
                raise RuntimeError("The user has cancelled the dialog.")
            file = await res[0].getFile()
            bytes = (await file.arrayBuffer()).to_bytes()
            return _file.File.from_bytes(data=bytes, filename=file.name)
    else:
        @staticmethod
        async def _open_file_dialog(prompt=None,types=[]):
            if prompt is None:
                prompt = "Please enter a filename to open:"
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
                raise ValueError('Only strings and bytestrings can be saved.')

    if is_pyodide_context():
        @staticmethod
        async def select(options: dict[str, str] | list[str] | tuple[str], title: str = None, text: str = None,
                         multiselect: bool = False, image=None, default_value: list[str] | str = None,
                         in_multiple: bool = False):
            """
            Gives the user a choice between different options.
            If multiselect is False, only one selection is allowed, otherwise the user can select multiple options.

            :param options: the selectable options
            :param title: the title on top of the select-box
            :param text: the text to be displayed
            :param multiselect: if True, multiple options can be selected, otherwise only one
            :param image: displays an image in the select-box
            :param in_multiple: If true only the config of the Dialog is returned
            :param default_value: The default value for the options.
            :return: a ``tuple`` of the selected options
            """
            if isinstance(options, dict):
                assert all(value is not None for value in options.values()), "No value of a choices-dict may be None."
                choices = options
            elif isinstance(options, (list, tuple)):
                choices = {option: option for option in options if option is not None}
            else:
                raise ValueError("Only 'dict' or 'list' or 'tuple' can be options.'")

            if default_value:
                assert isinstance(default_value, (list, str)), "pre_selected must be a list or a string."
                if not multiselect:
                    if isinstance(default_value, list):
                        assert len(default_value) == 1, "Pre-selected can only have one option in not multiselect."

            title = title or "Select"
            text = text or ("Please select any options:" if multiselect else "Please select an option:")
            if in_multiple:
                return {
                    "type": "select",
                    "title": title,
                    "text": text,
                    "choices": choices,
                    "multiple": multiselect,
                    "image": image,
                    "default_value": default_value
                }
            js.self.postMessage(
                type="select",
                title=title,
                text=text,
                choices=pyodide.ffi.to_js(choices, dict_converter=js.Object.fromEntries),
                multiple=multiselect,
                image=image,
                default_value=default_value
            )
            if multiselect:
                return [choices[i] for i in (await _wait_for_result())]
            else:
                return choices[await _wait_for_result()]
    else:
        @staticmethod
        async def select(options: dict[str, str] | list[str] | tuple[str], title: str = None, text: str = None,
                         multiselect: bool = False, image=None, in_multiple: bool = False,
                         default_value: list[str] | str = None):
            """
            Gives the user a choice between different options.
            If multiselect is False, only one selection is allowed, otherwise the user can select multiple options.

            :param options: the selectable options
            :param title: the title on top of the select-box
            :param text: the text to be displayed
            :param multiselect: if True, multiple options can be selected, otherwise only one
            :param image: displays an image in the select-box
            :in_multiple: Just for testing purposes.
            :in_multiple: Just for testing purposes.
            :return: a ``tuple`` of the selected options
            """
            if isinstance(options, dict):
                keys = list(options.keys())
                choices = options
            elif isinstance(options, (list, tuple)):
                keys = options
                choices = {option: option for option in options if option is not None}
            else:
                raise ValueError("Only 'dict' or 'list' or 'tuple' can be options.'")
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
                return [choices[keys[selection]] for selection in menu_entry_index]
            else:
                return choices[keys[menu_entry_index]]

    @staticmethod
    async def confirm(text: str = None, title: str = None, yes: str = "Yes", no: str = "No"):
        """
        Asks the user to answer a Yes/No Question

        :param title: the title on top of the confirm-box
        :param text: the text to be displayed
        :param yes: (optional) the word for 'yes'
        :param no: (optional) the word for 'no'
        :return:
        """
        title = title or "Confirm"
        text = text or "OK?"
        return await Dialog.select(options={yes: yes, no: no}, title=title, text=text) == yes

    if is_pyodide_context():
        @staticmethod
        async def text(prompt: str = None, title: str = "Text Input", empty: bool = None, placeholder: str = None,
                       image=None, multiline=False, default_value: str = None, in_multiple: bool = False):
            """
            prompts the user to enter text

            :param prompt: the prompt the user will be shown
            :param title: the title of the textbox
            :param empty: allow the empty ``string`` as a valid result
            :param image: displays an image in the text-box
            :param placeholder: the placeholder-text to be displayed in the textbox while it is empty
            :param multiline: enables multiline-input
            :param default_value: optional default value
            :param in_multiple: If true only the config of the Dialog is returned
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
            if default_value:
                kwargs["default_value"] = str(default_value)
            if multiline:
                kwargs["input_type"] = "text"
            if in_multiple:
                return kwargs
            js.self.postMessage(**kwargs)
            return await _wait_for_result()
    else:
        @staticmethod
        async def text(prompt: str = None, title: str = "Text Input", empty: bool = None, placeholder: str = None,
                       image=None, multiline=False, default_value: str = None, in_multiple: bool = False):
            """
            prompts the user to enter text

            :param prompt: the prompt the user will be shown
            :param title: the title of the textbox
            :param empty: allow the empty ``string`` as a valid result
            :param image: displays an image in the text-box
            :param placeholder: the placeholder-text to be displayed in the textbox while it is empty
            :param multiline: enables multiline-input
            :param default_value: optional default value
            :param in_multiple: just for testing purposes
            :return: the text entered by the user
            """
            if title:
                print(title)
            if image:
                print(f"In the Browser, an image would have been shown here: {image}")
            if multiline:
                print("press [Esc] and then [Enter] to finish...")
            return await prompt_toolkit.PromptSession().prompt_async(
                "Please enter text: " if prompt is None else prompt,
                placeholder=placeholder,
                validator=None if empty else _StringNotEmptyValidator(),
                multiline=multiline,
                default=default_value or ''
            )

    if is_pyodide_context():
        @staticmethod
        async def number(prompt: str = None, title: str = "Number Input", image=None,
                         default_value: typing.Union[int, float] = None, in_multiple: bool = False):
            """
            prompts the user to input a number

            :param prompt: the prompt the user will be shown
            :param title: the title of the number-box
            :param number_type: the type of expected number
            :param image: displays an image in the number-box
            :param default_value: optional default value
            :param in_multiple: If true only the config of the Dialog is returned
            :return: the number the user entered
            """
            msg = {
                "type": "input",
                "title": title,
                "text": prompt,
                "input_type": 'number',
                "image": image
            }
            if default_value:
                try:
                    float(default_value)
                except ValueError:
                    raise ValueError("The default_value is not a valid number.")
                else:
                    msg["default_value"] = str(default_value)
            if in_multiple:
                return msg
            js.self.postMessage(**msg)
            return await _wait_for_result()
    else:
        @staticmethod
        async def number(prompt: str = None, title: str = "Number Input", image=None,
                         default_value: typing.Union[int, float] = None, in_multiple: bool = False):
            """
            prompts the user to input a number

            :param prompt: the prompt the user will be shown
            :param title: the title of the number-box
            :param number_type: the type of expected number
            :param image: displays an image in the number-box
            :param default_value: optional default value
            :param in_multiple: just for testing purposes
            :return: the number the user entered
            """
            if default_value:
                try:
                    float(default_value)
                except ValueError:
                    raise ValueError("The default_value is not a valid number.")
                else:
                    default_value = str(default_value)
            if title:
                print(title)
            if image:
                print(f"In the Browser, an image would have been shown here: {image}")
            if prompt is None:
                prompt = "Please enter a number: "
            validator = _ConvertableValidator(conversion_function=float, error_message="Please enter a number.")
            res = await prompt_toolkit.PromptSession().prompt_async(
                prompt,
                validator=validator,
                default=default_value or ''
            )
            try:
                return int(res)
            except ValueError:
                return float(res)

    if is_pyodide_context():
        @staticmethod
        async def date(prompt: str = None, use_time: bool = False, image=None,
                       default_value: typing.Union[str, datetime.date, datetime.datetime] = None):
            """
            prompts the user to input a date

            :param prompt: the prompt the user will be shown
            :param use_time: also input time in addition to the date
            :param image: displays an image in the date-box
            :param default_value: optional default value
            :return: the date entered by the user
            """
            msg = {
                "type": "input",
                "title": "Date input",
                "text": prompt,
                "input_type": "date",
                "use_time": use_time,
                "image": image
            }

            if default_value:
                if isinstance(default_value, str):
                    default_value = datetime.datetime.fromisoformat(default_value)
                if isinstance(default_value, datetime.date):  # is date or datetime
                    if use_time:
                        if not isinstance(default_value, datetime.datetime):  # is a date
                            default_value = datetime.datetime.fromisoformat(default_value.isoformat())
                    else:
                        if isinstance(default_value, datetime.datetime):
                            default_value = default_value.date()
                if not isinstance(default_value, datetime.date):
                    raise ValueError(
                        f"""The default_value must be a datetime.{"datetime" if use_time else "date"} or an ISO-string-representation of one.""")
                msg["default_value"] = default_value.isoformat()

            js.self.postMessage(**msg)
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
        async def date(prompt: str = None, use_time: bool = False, image=None,
                       default_value: typing.Union[str, datetime.date, datetime.datetime] = None):
            """
            prompts the user to input a date

            :param prompt: the prompt the user will be shown
            :param use_time: also input time in addition to the date
            :param image: displays an image in the date-box
            :param default_value: optional default value
            :return: the date entered by the user
            """
            if image:
                print(f"In the Browser, an image would have been shown here: {image}")
            validator = _ConvertableValidator(
                conversion_function=datetime.datetime.fromisoformat,
                error_message="Please enter a valid date."
            )
            if default_value:
                if isinstance(default_value, datetime.date):
                    default_value = default_value.isoformat()
                else:
                    try:
                        datetime.datetime.fromisoformat(default_value)
                    except ValueError:
                        raise ValueError(
                            f"""The default_value must be a datetime.{"datetime" if use_time else "date"} or an ISO-string-representation of one.""")

            prompt = prompt or "Please enter a date: "

            entered_date = await prompt_toolkit.PromptSession().prompt_async(
                prompt,
                validator=validator,
                default=default_value or ''
            )
            res = datetime.datetime.fromisoformat(entered_date)
            if not use_time:
                res = res.date()
            return res

    if is_pyodide_context():
        @staticmethod
        async def show_diff(title: str, diffs: list[tuple[str, str, str]], image=None):
            """
            shows a diff-view to the user

            :param title: the title of the diff-box
            :param diffs: the data to be shown
            :param image: displays an image in the diff-box
            """
            js.self.postMessage(type="diffcmp", title=title, changes=pyodide.ffi.to_js(diffs), image=image)
    else:
        @staticmethod
        async def show_diff(title: str, diffs: list[tuple[str, str, str]], image=None):
            """
            shows a diff-view to the user

            :param title: the title of the diff-box
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

    if is_pyodide_context():
        @staticmethod
        async def multiple(
            title: str,
            components: list[dict] | dict[str, dict],
            send_button_text: str,
            reuse: bool = False
        ):
            """
            :param title: the header of the component
            :param components: list of components
            :param send_button_text: the text of the button at the bottom of the dialog
            :param reuse: If True, the components are not sent to the JS.
            """
            msg = {
                "type": "multiple-dialog",
                "title": title,
                "buttonText": send_button_text,
                "components": json.dumps(components)
            }


            if not reuse:
                js.self.postMessage(**msg)
            res = await _wait_for_result()
            if isinstance(res,str):
                return json.loads(res)
            else:
                return res.to_py()

    else:
        @staticmethod
        async def multiple(title: str, components: list, reuse: bool = False):
            return components
