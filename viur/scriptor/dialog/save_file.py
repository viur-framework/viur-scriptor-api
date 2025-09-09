from viur.scriptor._utils import is_pyodide_context

if is_pyodide_context():
    import js
    from viur.scriptor._utils import _wait_for_result, bytes_to_blob
else:
    import prompt_toolkit
    from prompt_toolkit.completion import PathCompleter, FuzzyCompleter
    from ._validators import _FileDoesntExistsOrShouldBeReplacedValidator



if is_pyodide_context():
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
