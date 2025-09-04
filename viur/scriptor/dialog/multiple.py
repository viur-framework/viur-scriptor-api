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
        if isinstance(res, str):
            return json.loads(res)
        else:
            return res.to_py()

else:
    async def multiple(title: str, components: list, reuse: bool = False):
        return components
