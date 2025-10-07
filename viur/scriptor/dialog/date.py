from viur.scriptor._utils import is_pyodide_context
import typing
import datetime

if is_pyodide_context():

    import pyodide
    import js
    from viur.scriptor._utils import _wait_for_result
else:
    import prompt_toolkit
    from ._validators import _ConvertableValidator

if is_pyodide_context():
    async def date(
        prompt: str = None,
        use_time: bool = False,
        image=None,
        default_value: typing.Union[str, datetime.date, datetime.datetime] = None,
        in_multiple: bool = False
    ):
        """
        prompts the user to input a date

        :param prompt: the prompt the user will be shown
        :param use_time: also input time in addition to the date
        :param image: displays an image in the date-box
        :param default_value: optional default value
        :param in_multiple: If true only the config of the Dialog is returned
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
        if in_multiple:
            return msg
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
    async def date(
        prompt: str = None,
        use_time: bool = False,
        image=None,
        default_value: typing.Union[str, datetime.date, datetime.datetime] = None,
        in_multiple: bool = False
    ):
        """
        prompts the user to input a date

        :param prompt: the prompt the user will be shown
        :param use_time: also input time in addition to the date
        :param image: displays an image in the date-box
        :param default_value: optional default value
        :param in_multiple: just for testing purposes
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
