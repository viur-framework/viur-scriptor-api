import traceback

from ._utils import is_pyodide_context

if is_pyodide_context():
    import js


    class Logger:
        """
        The logger for the pyodide-context that logs to the browser.
        """
        _levels = {
            'notset': 0,
            'debug': 10,
            'info': 20,
            'warning': 30,
            'error': 40,
            'critical': 50,
            'fatal': 50
        }

        _level_map = {
            'critical': 'error',
            'fatal': 'error'
        }

        def __init__(self, name="scriptor"):
            self._level = 'info'

        def log(self, level: str, msg: str, *args, **kwargs):
            """
            logs a message with the given log-level

            :param level: log-level (debug, info, warning, error, critical or fatal)
            :param msg: the message to be logged
            :param args: additional arguments. ignored in browser.
            :param kwargs: additional keyword-arguments. ignored in browser.
            """
            if not isinstance(msg, str):
                msg = str(msg)
            if kwargs.get('exc_info', False):
                if msg:
                    msg += '\n'
                msg += traceback.format_exc()
            if self._levels[self._level] <= self._levels[level.lower()]:
                js.self.postMessage(type="log", text=msg, level=self._level_map.get(level, level))

        def info(self, msg: str, *args, **kwargs):
            """
            logs a message with the log level 'info'

            :param msg: the message to be logged
            :param args: additional arguments. ignored in browser.
            :param kwargs: additional keyword-arguments. ignored in browser.
            """
            self.log("info", msg=msg, *args, **kwargs)

        def debug(self, msg: str, *args, **kwargs):
            """
            logs a message with the log level 'debug'

            :param msg: the message to be logged
            :param args: additional arguments. ignored in browser.
            :param kwargs: additional keyword-arguments. ignored in browser.
            """
            self.log("debug", msg=msg, *args, **kwargs)

        def error(self, msg: str, *args, **kwargs):
            """
            logs a message with the log level 'error'

            :param msg: the message to be logged
            :param args: additional arguments. ignored in browser.
            :param kwargs: additional keyword-arguments. ignored in browser.
            """
            self.log("error", msg=msg, *args, **kwargs)

        def critical(self, msg: str, *args, **kwargs):
            """
            logs a message with the log level 'critical'

            :param msg: the message to be logged
            :param args: additional arguments. ignored in browser.
            :param kwargs: additional keyword-arguments. ignored in browser.
            """
            self.log("critical", msg=msg, *args, **kwargs)

        def fatal(self, msg: str, *args, **kwargs):
            """
            logs a message with the log level 'fatal'

            :param msg: the message to be logged
            :param args: additional arguments. ignored in browser.
            :param kwargs: additional keyword-arguments. ignored in browser.
            """
            self.log("fatal", msg=msg, *args, **kwargs)

        def warn(self, msg: str, *args, **kwargs):
            """
            logs a message with the log level 'warning'

            :param msg: the message to be logged
            :param args: additional arguments. ignored in browser.
            :param kwargs: additional keyword-arguments. ignored in browser.
            """
            self.log("warning", msg=msg, *args, **kwargs)

        def warning(self, msg: str, *args, **kwargs):
            """
            logs a message with the log level 'warning'

            :param msg: the message to be logged
            :param args: additional arguments. ignored in browser.
            :param kwargs: additional keyword-arguments. ignored in browser.
            """
            self.log("warning", msg=msg, *args, **kwargs)

        def exception(self, msg: str, *args, exc_info: bool = True, **kwargs):
            """
            logs a message with the log level 'fatal'.

            the exc_info-argument is ignored in the browser.

            :param msg: the message to be logged
            :param args: additional arguments. ignored in browser.
            :param exc_info: if true, exception information will be logged. ignored in browser.
            :param kwargs: additional keyword-arguments. ignored in browser.
            """
            self.log("fatal", msg=msg, exc_info=exc_info, *args, **kwargs)

        def setLevel(self, level: str):
            """
            sets the minimal level of log-messages to be printed.

            :param level: the minimal level of log-messages that should be printed.
            """
            self._level = level.lower()

else:
    import logging


    class Logger(logging.Logger):
        """
        A preconfigured Logger.
        """

        def __init__(self, name="scriptor"):
            super().__init__(name=name, level=logging.INFO)

logger = Logger()
