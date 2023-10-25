"""
Dialogs API.

This module provides several dialogs to be used for several user-interactions.

- alert: Show a modal message to be confirmed
- confirm: Show a Yes-No or Yes-No-Cancel dialog
- input: Input dialog with various types
- select: Select choice of several options, with multi-selection option.
"""

from .utils import is_pyodide_context

if is_pyodide_context():
    import js, pyodide
    from js import self as _self
    import manager
else:
    import asyncio
    import click
    import json
    _input = input

import time
import datetime
import math


async def wait():
    if is_pyodide_context():
        while manager.resultValue is None:
            await manager.sleep(250)
    else:
        await asyncio.sleep(250)

async def alert(text: str, image: str = "") -> None:
    """
    Provide a message and stop program execution until accepted.
    """
    if is_pyodide_context():
        _self.postMessage(type="alert", text=text, image=image)
        await wait()
        manager.reset()
        manager.resultValue = None
    else:
        click.pause("Press any key to continue")


async def confirm(text: str, *, title: str = "Confirm", allow_cancel: bool = False, image: str = "") -> bool | None:
    """
    Provide a Yes-No or Yes-No-Cancel-dialog.
    """
    if is_pyodide_context():
        _self.postMessage(type="confirm", title=title, text=text, cancel=allow_cancel, image=image)
        await wait()
        ret = manager.copyResult()
        manager.reset()
        manager.resultValue = None

        if ret < 0:
            return None
        elif ret == 0:
            return False

        ret = True

    else:
        ret = click.confirm(text, abort=allow_cancel)

    return ret


async def input(text: str, *, title: str = "Input", type: str = "input", use_time: bool = False, empty: bool = False, image: str = "") -> datetime.datetime|str|float|int:
    """
    Provide a dialog asking for some value.
    """

    if is_pyodide_context():
        _self.postMessage(type="input", title=title, text=text, input_type=type, use_time=use_time, empty=empty, image=image)
        await wait()
        tmp = manager.copyResult()
        manager.reset()
        manager.resultValue = None

        if type == "date":
            return datetime.datetime.fromtimestamp(math.floor(tmp/1000.0))

        return tmp
    else:
        # click.echo(title)  # not required
        ret = click.prompt(text)
        if type == "date":
            def validate_date(date_text):
                try:
                    return datetime.date.fromisoformat(date_text)
                except ValueError:
                    click.echo("Incorrect data format, should be YYYY-MM-DD")


                return None

            def validate_datetime(date_text):
                try:
                    return datetime.datetime.fromisoformat(date_text)
                except ValueError:
                    click.echo("Incorrect data format, should be YYYY-MM-DD HH:MM:SS")

                return None

            if use_time:
                while not validate_date(ret):
                    ret = click.prompt(text)
            else:
                while not validate_datetime(ret):
                    ret = click.prompt(text)

            return ret
        elif type == "number":
            def check_number(value: str):
                try:
                    r = float(value.replace("," "."))
                    return ret
                except:
                    try:
                        r = int(value)
                        return r
                    except:
                        return None
                return None
            while True:
                ret = check_number(ret)
                if ret is None:
                    click.echo("Enter a valid number.")
                    ret = click.prompt(text)
                else:
                    break

            return ret
        else:
            return ret

async def input_date(*args, **kwargs) -> datetime.datetime:
    """
        Provide a input asking for datetime value.
    """
    kwargs |= {"type": "date"}
    return await input(*args, **kwargs)

async def input_number(*args, **kwargs) -> int|float:
    kwargs |= {"type": "number"}
    return await input(*args, **kwargs)

async def input_string(*args, **kwargs) -> str:
    kwargs |= {"type": "string"}
    return await input(*args, **kwargs)

async def input_text(*args, **kwargs) -> str:
    kwargs |= {"type": "text"}
    return await input(*args, **kwargs)

input.date = input_date
input.number = input_number
input.text = input_text
input.string = input_string


async def select(text: str, choices: tuple[str] | list[str] | dict[str, str], *,
                 title: str = "Select", multiple: bool = False, image: str = "") -> str|list[str]:
    if isinstance(choices, (list, tuple)):
        if all([isinstance(k, (dict)) for k in choices]):
            # Image Mode
            choices = {str(k): {"text": str(k.get("text", "")), "image": str(k.get("image", "")) } for k in choices}
        else:
            choices = {str(k): str(k) for k in choices}
 
    if not isinstance(choices, dict):
        raise ValueError("'choices' must be either a list or a dict.")

    # Browser-mode
    if is_pyodide_context():
        choices = pyodide.ffi.to_js(choices, dict_converter=js.Object.fromEntries)

        _self.postMessage(type="select", title=title, text=text, choices=choices, multiple=multiple, image=image)
        await wait()

        ret = manager.resultValue
        if multiple:
            ret = ret.to_py()

        manager.reset()
        manager.resultValue = None

        return ret

    # CLI-mode
    maxkey = max([len(k) for k in choices])
    menu = [f"{k: <{maxkey}} - {v}" if k != v else str(v) for k, v in choices.items()]

    if not multiple:
        ret = click.prompt(
            "\n".join(menu) + "\n" + text,
            type=click.Choice(list(choices.keys()))
        )
    else:
        options = list(choices.keys())

        while True:
            ret = click.prompt("\n".join(menu) + "\n" + text + f" ({', '.join(options)})", type=str)
            ret = [c.strip() for c in ret.split(",")]
            if all([v in options for v in ret]):
                break

            click.echo(f"Invalid input entered. Allowed values: {options}")

    return ret

async def diffcmp(title: str, changes: list[list[str]], image: str = "") -> None:
    if is_pyodide_context():
        for i in range(len(changes)):
            changes[i] = pyodide.ffi.to_js(changes[i])

        _self.postMessage(type="diffcmp", title=title, changes=pyodide.ffi.to_js(changes), image=image)
    else:
        click.echo(title)

        for entry in changes:
            for i in range(len(entry)):
                if not isinstance(entry[i], str):
                    entry[i] = str(entry[i])

        ret = "\n".join([f"{e[0]}\t\t\t{e[1]} -> {e[2]}" for e in changes])
        click.echo(ret)

async def table(header: list[str], rows: list[list[str]], *, select=False, multiple=False, image: str = "") -> str|list[str]|None:
    if is_pyodide_context():
        for i in range(len(rows)):
            rows[i] = pyodide.ffi.to_js(rows[i])

        header = pyodide.ffi.to_js(header)
        rows = pyodide.ffi.to_js(rows)

        _self.postMessage(type="table", header=header, rows=rows, select=select, multiple=multiple, image=image)

        await wait()
        
        ret = manager.resultValue.to_py()
        ret = [rows[idx] for idx in ret]

        if not multiple:
            ret = ret[0] if ret else None

        manager.reset()
        manager.resultValue = None

        return ret

    column_widths = [max(len(header[i]), max(len(str(row[i])) for row in rows)) for i in range(len(header))]
    separator = "+".join(["-" * (width + 2) for width in column_widths])

    print(separator)
    print("|", end="")
    for i in range(len(header)):
        print(f" {header[i]:^{column_widths[i]}} |", end="")
    print("\n" + separator)

    for i in range(len(rows)):
        print("|", end="")
        for j in range(len(header)):
            print(f" {rows[i][j]:^{column_widths[j]}} |", end="")
        print("\n" + separator)

    if select:
        while True:
            if multiple:
                selected = _input("Select a multiple (example: [0, 1, 2] ...) ")
            else:
                selected = _input("Select a row (example: 1, 2, ...) ")
            try:
                if not multiple:
                    selected = int(selected)
                    if 0 <= selected < len(rows):
                        return rows[selected]
                    else:
                        print("Wrong input, try it again.")
                else:
                    selected = json.loads(selected)
                    if isinstance(selected, int):
                        if 0 <= selected < len(rows):
                            return rows[selected]
                    if not isinstance(selected, list):
                        print("Wrong input, try it again.")
                    else:
                        if any([not isinstance(e, int) for e in selected]):
                            print("Wrong input, try it again.")
                            continue
                        return [rows[e] for e in selected if e >= 0 and e < len(rows)]
            except ValueError:
                print("Wrong Input.")

    return None
