from viur.scriptor._utils import is_pyodide_context
if is_pyodide_context():

    import pyodide
    import js
    from viur.scriptor._utils import _wait_for_result
else:
    import prompt_toolkit
    from ._validators import _StringNotEmptyValidator

if is_pyodide_context():

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
