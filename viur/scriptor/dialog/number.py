from viur.scriptor._utils import is_pyodide_context
import typing

if is_pyodide_context():
    import js
    from viur.scriptor._utils import _wait_for_result
else:
    import prompt_toolkit
    from ._validators import _ConvertableValidator
# todo placeholder
if is_pyodide_context():
    async def number(prompt: str = None, title: str = "Number Input", placeholder: str = None, image=None,
                     default_value: typing.Union[int, float] = None, in_multiple: bool = False):
        """
        prompts the user to input a number

        :param prompt: the prompt the user will be shown
        :param title: the title of the number-box
        :param placeholder: the placeholder-text to be displayed in the box while it is empty
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
            "image": image,
            "placeholder": placeholder,
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
    async def number(prompt: str = None, title: str = "Number Input", placeholder: str = None, image=None,
                     default_value: typing.Union[int, float] = None, in_multiple: bool = False):
        """
        prompts the user to input a number

        :param prompt: the prompt the user will be shown
        :param title: the title of the number-box
        :param placeholder: the placeholder-text to be displayed in the box while it is empty
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
            default=default_value or '',
            placeholder=placeholder,
        )
        try:
            return int(res)
        except ValueError:
            return float(res)
