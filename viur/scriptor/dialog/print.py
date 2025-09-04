from viur.scriptor._utils import is_pyodide_context

if is_pyodide_context():
    import js

_python_print = print

if is_pyodide_context():
    def print(*args, sep=' ', end='\n', file=None, flush=False):
        """
        displays Text

        :param args: ``string`` / ``object``\\ s that should be displayed.
        :param sep: ``string`` inserted between values, default a space.
        :param end: ``string`` appended after the last value, default a newline. ignored in browser.
        :param file: a file-like object (stream); defaults to the current sys.stdout. ignored in browser.
        :param flush: whether to forcibly flush the stream. ignored in browser.
        """
        js.self.postMessage(type="log", text=sep.join(str(t) for t in args), level="info")
else:
    def print(*args, sep=' ', end='\n', file=None, flush=False):
        """
        displays Text

        :param args: ``string`` / ``object``\\ s that should be displayed.
        :param sep: `string` inserted between values, default a space.
        :param end: `string` appended after the last value, default a newline. ignored in browser.
        :param file: a file-like object (stream); defaults to the current sys.stdout. ignored in browser.
        :param flush: whether to forcibly flush the stream. ignored in browser.
        """
        _python_print(*args, sep=sep, end=end, file=file, flush=flush)
