from viur.scriptor._utils import is_pyodide_context
import viur.scriptor.file as _file

if is_pyodide_context():

    import pyodide
    import js
    from viur.scriptor._utils import _wait_for_result
else:
    import os
    import prompt_toolkit
    from prompt_toolkit.completion import PathCompleter, FuzzyCompleter
    from prompt_toolkit.validation import Validator, ValidationError


    class _FileExistsValidator(Validator):

        def validate(self, document):
            text = document.text
            if not text.strip():
                raise ValidationError(message="Please enter a valid filename.")
            if not os.path.exists(text):
                raise ValidationError(message="A file with this name doesn't exist.")

if is_pyodide_context():

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

    async def _open_file_dialog(prompt=None, types=[]):
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
