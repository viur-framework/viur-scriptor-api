from viur.scriptor._utils import is_pyodide_context

if is_pyodide_context():
    import js


class Message:
    if is_pyodide_context():
        @staticmethod
        def send(type: str = "success", title: str = "", text: str = "", ):
            """
            Shows a message to the user.
            :param type: The type of message to send.
            :param title: The title of message to be displayed
            :param text: The message to be displayed
            """
            js.self.postMessage(type="system-message", _type=type, title=title, text=text)
    else:
        @staticmethod
        def send(type: str = "success", title: str = "", text: str = "", ):
            """
            Shows a message to the user.
            :param type: The type of message to send.
            :param title: The title of message to be displayed
            :param text: The message to be displayed
            """

            print(f"type={type}, title={title}, text={text}")
