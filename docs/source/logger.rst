Logger
======
The logger provides, as the name suggests, methods for logging information. In the browser, this mainly means colored
messages, but it is important for scripts that get executed in the server-backend.
There's an already preconfigured instance under the name ``logger`` (all lower-case-letters).
The provided methods are ``log``, ``info``, ``debug``, ``error``, ``critical``, ``fatal``, ``warning``, ``warn``
(does the same as ``warning``) and ``exception``. Except for the ``exception``-method, all these log only the info you
provided. The ``exception``-method also logs the last error that occured in the script.

Also there is a ``setLevel``-method. The level set with this method supresses log-messages with a lower level,
i.e. if you set it to fatal or critcal, no errors, warnings, infos or debug-messages will be shown. The default level
is info, so no debug-messages are shown. The order is debug, info, warning (you cannot set to warn), error and
critical/fatal (these two are on the same level).

The last remaining method of the Logger is ``log``. It combines all the other methods and thus has an additional
parameter called ``level``. That means ``logger.info("message")`` does the same as ``logger.log("info", "message")``.

Here's an example to show you all of it (try it out in scriptor).

.. code-block:: python

    #### scriptor ####
    from viur.scriptor import *

    async def main():
        logger.setLevel("debug")

        logger.debug("this is a debug-message")
        logger.info("this is an info-message")
        logger.error("this is an error-message")
        logger.critical("this is a critical-message")
        logger.fatal("this is a fatal-message")
        logger.warn("this is a warn-message")
        logger.warning("this is a warning-message")
        logger.exception("this is an exception-message")

        logger.setLevel("critical")
        print("*** the loggers level was changed here ***")

        logger.debug("this is a debug-message")
        logger.info("this is an info-message")
        logger.error("this is an error-message")
        logger.critical("this is a critical-message")
        logger.fatal("this is a fatal-message")
        logger.warn("this is a warn-message")
        logger.warning("this is a warning-message")
        logger.exception("this is an exception-message")

