from ._utils import is_pyodide_context

if is_pyodide_context():
    import js


class ProgressBar:
    if is_pyodide_context():
        @staticmethod
        def set(percent: int = 0, current_step: int = -1, total_steps: int = -1, text: str = ""):
            """
            displays a progressbar in the browser, prints progress-information in CLI

            :param percent: the percentage of the process that is complete (a value between 0 and 100)
            :param current_step: the number of completed steps
            :param total_steps: the number of total steps
            :param text: additional text to be displayed
            """
            js.self.postMessage(type="progressbar", total=percent, step=current_step, max_step=total_steps, txt=text)
    else:
        @staticmethod
        def set(percent: int = 0, current_step: int = -1, total_steps: int = -1, text: str = ""):
            """
            displays a progressbar in the browser, prints progress-information in CLI

            :param percent: the percentage of the process that is complete (a value between 0 and 100)
            :param current_step: the number of completed steps
            :param total_steps: the number of total steps
            :param text: additional text to be displayed
            """
            print(f"""Step {current_step}/{total_steps} ({percent}%): {text}""")

    if is_pyodide_context():
        @staticmethod
        def unset():
            """
            removes the progressbar, does nothing in CLI
            """
            js.self.postMessage(type="progressbar", total=100, step=-1, max_step=-1, txt="")
    else:
        @staticmethod
        def unset():
            """
            removes the progressbar, does nothing in CLI
            """
            pass
