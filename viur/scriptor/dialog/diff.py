from viur.scriptor._utils import is_pyodide_context

if is_pyodide_context():
    import pyodide
    import js
if is_pyodide_context():
    async def show_diff(title: str, diffs: list[tuple[str, str, str]], image=None):
        """
        shows a diff-view to the user

        :param title: the title of the diff-box
        :param diffs: the data to be shown
        :param image: displays an image in the diff-box
        """
        js.self.postMessage(type="diffcmp", title=title, changes=pyodide.ffi.to_js(diffs), image=image)
else:
    async def show_diff(title: str, diffs: list[tuple[str, str, str]], image=None):
        """
        shows a diff-view to the user

        :param title: the title of the diff-box
        :param diffs: the data to be shown
        :param image: displays an image in the diff-box
        """
        print(title)
        if image:
            print(f"In the Browser, an image would have been shown here: {image}")
        print('=' * len(title))
        for key, old, new in diffs:
            print(f"""{key}: {old} -> {new}""")
        print('')
