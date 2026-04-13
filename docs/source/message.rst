Message
=======

The ``Message`` class sends toast-style notifications to the user. Unlike ``Dialog.print``, which
appends text to the output area, a message appears as a brief overlay notification — similar to a
system notification. In the CLI context it is printed to stdout.

The ``send``-method is **not** a coroutine and does not need to be awaited.

Parameters
----------

``type``
    Controls the appearance of the notification. Supported values:

    - ``"success"`` (default) — green, signals a successful operation
    - ``"warning"`` — yellow, signals a non-critical issue
    - ``"error"`` — red, signals a failure
    - ``"info"`` — neutral, for general information

``title``
    A short heading shown above the message text.

``text``
    The main body of the notification.

Examples
--------

Simple success message after completing an operation:

.. code-block:: python

    #### scriptor ####
    from viur.scriptor import *

    async def main():
        # ... do some work ...
        Message.send(type="success", title="Done", text="All records have been updated.")


Warning the user without interrupting the script:

.. code-block:: python

    #### scriptor ####
    from viur.scriptor import *

    async def main():
        skipped = 3
        if skipped:
            Message.send(
                type="warning",
                title="Skipped entries",
                text=f"{skipped} records could not be processed and were skipped."
            )


Signalling an error:

.. code-block:: python

    #### scriptor ####
    from viur.scriptor import *

    async def main():
        try:
            result = await modules.get_module("mymodule")
        except Exception as e:
            Message.send(type="error", title="Module not found", text=str(e))
            return
