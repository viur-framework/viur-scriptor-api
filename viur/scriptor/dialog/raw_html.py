from viur.scriptor._utils import is_pyodide_context

if is_pyodide_context():
    import js
    from viur.scriptor._utils import _wait_for_result

if is_pyodide_context():

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

    async def raw_html(html: str, in_multiple: bool = False):
        """
        Shows preformatted html to the user.

        :param html: the preformatted html as a string
        :param in_multiple: just for testing purposes
        """
        print(html)
