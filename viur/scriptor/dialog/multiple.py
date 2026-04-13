from viur.scriptor._utils import is_pyodide_context
import json
if is_pyodide_context():
    import js
    from viur.scriptor._utils import _wait_for_result

if is_pyodide_context():
    async def multiple(
        title: str,
        components: list[dict] | dict[str, dict],
        send_button_text: str,
        reuse: bool = False
    ):
        """
        Shows multiple input components in a single dialog and waits for the user to submit them.

        Each component is built by calling the corresponding ``Dialog``-method with
        ``in_multiple=True`` (e.g. ``await Dialog.text(..., in_multiple=True)``).
        The return value mirrors the structure of ``components``:
        a ``list`` if ``components`` is a list, or a ``dict`` with the same keys if it is a dict.

        :param title: heading displayed at the top of the dialog
        :param components: input component configs as a ``list[dict]`` or ``dict[str, dict]``,
            built with ``in_multiple=True`` on ``Dialog.text``, ``Dialog.number``,
            ``Dialog.select``, or ``Dialog.date``
        :param send_button_text: label of the submit button at the bottom of the dialog
        :param reuse: if ``True``, the component definitions are not re-sent to the browser;
            use this when showing the same dialog repeatedly in a loop
        :return: user inputs as a ``list`` or ``dict``, matching the structure of ``components``
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
        if isinstance(res, str):
            return json.loads(res)
        else:
            return res.to_py()

else:
    async def multiple(title: str, components: list, reuse: bool = False):
        return components
