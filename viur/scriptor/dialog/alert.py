from viur.scriptor._utils import is_pyodide_context

if is_pyodide_context():
    import js
    from viur.scriptor._utils import _wait_for_result



if is_pyodide_context():
    async def alert(text: str, image=None):
        """
        Shows a message to the user and blocks until it is confirmed.

        :param text: The message to be displayed
        :param image: displays an image in the alert-box
        """
        js.self.postMessage(type="alert", text=text, image=image)
        await _wait_for_result()
else:
    async def alert(text: str, image=None):
        """
        Shows a message to the user and blocks until it is confirmed.

        :param text: The message to be displayed
        :param image: displays an image in the alert-box
        """
        print(text)
        if image:
            print(f"In the Browser, an image would have been shown here: {image}")
        input("Please press <Enter> to continue...")
