from viur.scriptor._utils import is_pyodide_context
if is_pyodide_context():

    import pyodide
    import js
    from viur.scriptor._utils import _wait_for_result
else:
    from simple_term_menu import TerminalMenu
if is_pyodide_context():
    async def select(
        options: dict[str, str] | list[str] | tuple[str],
        title: str = None, text: str = None,
        multiselect: bool = False, image=None,
        default_value: list[str] | str = None,
        in_multiple: bool = False,
        show_values: bool = False,
    ):
        """
        Gives the user a choice between different options.
        If multiselect is False, only one selection is allowed, otherwise the user can select multiple options.

        :param options: the selectable options
        :param title: the title on top of the select-box
        :param text: the text to be displayed
        :param multiselect: if True, multiple options can be selected, otherwise only one
        :param image: displays an image in the select-box
        :param default_value: The default value for the options.
        :param in_multiple: If true only the config of the Dialog is returned
        :param show_values: If true the values show in the select-box
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
                "default_value": default_value,
                "show_values": show_values,
            }
        js.self.postMessage(
            type="select",
            title=title,
            text=text,
            choices=pyodide.ffi.to_js(choices, dict_converter=js.Object.fromEntries),
            multiple=multiselect,
            image=image,
            default_value=default_value,
            show_values=show_values,
        )
        result = await _wait_for_result()
        if multiselect:
            return [choices[i] for i in (result)]
        else:
            return choices[result]
else:
    async def select(
        options: dict[str, str] | list[str] | tuple[str],
        title: str = None, text: str = None,
        multiselect: bool = False, image=None,
        default_value: list[str] | str = None,
        in_multiple: bool = False,
        show_values: bool = False,
    ):
        """
        Gives the user a choice between different options.
        If multiselect is False, only one selection is allowed, otherwise the user can select multiple options.

        :param options: the selectable options
        :param title: the title on top of the select-box
        :param text: the text to be displayed
        :param multiselect: if True, multiple options can be selected, otherwise only one
        :param image: displays an image in the select-box
        :param default_value: Just for testing purposes
        :param in_multiple: Just for testing purposes
        :param show_values: Just for testing purposes

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

