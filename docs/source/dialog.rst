Dialogs
=======

Dialogs are a crucial component for interacting with the user. The scriptor provides a variety of dialogue types,
including alerts, confirmations, inputs, selects, comparisons of changed data, and tables.


Print
-----
The simplest way to interact with a user is to show them text. This is done with the ``print`` function.
Since this function is used very often, you can call it directly, in spite of it being a member of ``Dialog``.
(Note that print doesn't need to be awaited.)

.. code-block:: python

    #### scriptor ####
    from viur.scriptor import *

    async def main():
        Dialog.print("Hello World")
        print("This works, too!")


Alert
-----
When an ``alert`` is triggered, a message is displayed, and the script waits until the 'OK' button is clicked.

.. code-block:: python

    #### scriptor ####
    from viur.scriptor import *

    async def main():
        await Dialog.alert("Hello World")
        print("done")


Confirm
-------
A ``confirm``-element is a component that represents a simple yes/no dialog. It allows the user to confirm an action
or cancel it. After the user interacts with the ``confirm``-element, it returns one of two values:
``True`` or ``False``.

Here is a simple example where the user is prompted using a ``confirm``-element to determine whether the program should
continue or be stopped.

.. code-block:: python
    
    #### scriptor ####
    from viur.scriptor import *

    async def main():
        # Ask the user if the program should proceed (interaction)
        ret = await Dialog.confirm("Should we proceed?")

        # ret can be True or False (Yes/No)
        
        if not ret:
            print("Stop!") # We will print an output for debug
            return # will stop the whole program

        # Done!
        print("Done!")


Select
------
The ``select``-element is the generalized version of the ``confirm``-element. As the name suggests, you can prompt the
user with a selection of elements you provide.

.. code-block:: python

    #### scriptor ####
    from viur.scriptor import *

    async def main():
        selections = ["Option A", "Option B", "Option C"]
        ret = await Dialog.select(selections)
        print(f"""you selected {ret}""")

The return value will be the name of the selected element. Multiselect is also supported:

.. code-block:: python

    #### scriptor ####
    from viur.scriptor import *

    async def main():
        selections = ["Option A", "Option B", "Option C"]
        ret = await Dialog.select(selections, multiselect=True)
        print(f"""you selected {ret}""")


The return-value will be a list of the selected elements. You can also specify the return-values for the different
selections. This works with and without multiselect:


.. code-block:: python

    #### scriptor ####
    from viur.scriptor import *

    async def main():
        selections = {
            "Option A": 1,
            "Option B": 2,
            "Option C": 3,
        }
        ret = await Dialog.select(selections)
        print(f"""you selected {ret}""")


.. code-block:: python

    #### scriptor ####
    from viur.scriptor import *

    async def main():
        selections = {
            "Option A": 1,
            "Option B": 2,
            "Option C": 3,
        }
        ret = await Dialog.select(selections, multiselect=True)
        print(f"""you selected {ret}""")


Data-input
----------
Input-elements are used to get data from the user.

Text
~~~~
A ``text``-element is another type that expects user input in the form of strings, or multi-line strings. It provides
a way for users to enter and submit data.

.. code-block:: python

    #### scriptor ####
    from viur.scriptor import *

    async def main():
        ret = await Dialog.text("What's your name?")

        print("Your name is: "+ ret)

It's also possible to let the user input multiline-strings like this:

.. code-block:: python

    #### scriptor ####
    from viur.scriptor import *

    async def main():
        ret = await Dialog.text("What's your address?", multiline=True)

        print("Your address is:\n"+ ret)


Additionaly, there's an option to provide a default value to the user:

.. code-block:: python

    #### scriptor ####
    from viur.scriptor import *

    async def main():
        ret = await Dialog.text("What's your name?", default_value="Mausbrand")

        print("Your name is: "+ ret)

        ret = await Dialog.text("What's your address?", multiline=True,
            default_value="Mausbrand Informationssysteme GmbH\nSpeicherstraße 33\n44147 Dortmund")

        print("Your address is:\n"+ ret)


Numbers
~~~~~~~
Another input type is a ``number``, where the number can be either an integer or a floating-point number. For example, if
the value "1.5" is given as an input, the output will be a ``float`` variable. However, if the number is an integer, the
output type will be returned as ``int``.


.. code-block:: python

    #### scriptor ####
    from viur.scriptor import *

    async def main():
        age = await Dialog.number("How old are you?")
        print(f"You are {age} years old.")


As with ``text``, you can provide a default value:

.. code-block:: python

    #### scriptor ####
    from viur.scriptor import *

    async def main():
        age = await Dialog.number("How old are you?", default_value=20)
        print(f"You are {age} years old.")


Date
~~~~
Often, documentation requires including information such as dates and times. To facilitate this, the Scriptor provides
the ability to input date values. Unlike other input types, this returns a ``date``- or ``datetime``-object.

.. code-block:: python

    #### scriptor ####
    from viur.scriptor import *

    async def main():
        date = await Dialog.date("When were you born?")
        print(f"You were born on {date}.")


In this example, the ``date`` variable is of type ``datetime.date``. Therefore, you can utilize all the functions
provided by the Python standard library's ``datetime``-module. If you want the user to input a time as well, you need
to use the ``use_time``-parameter:

.. code-block:: python

    #### scriptor ####
    from viur.scriptor import *

    async def main():
        date = await Dialog.date("When were you born?", use_time=True)
        print(f"You were born on {date}.")


This example will ask for a date and a time and therefore return a ``datetime.datetime``-object.


| Similar to ``text`` and ``number``, there's an option for a default value. In this case, there are several
  format-options:
| The ``default_value`` can be a ``datetime.date``, a ``datetime.datetime`` or an ISO-format-date-string like
  ``"2024-12-24"`` or ``"2024-12-24 23:59:59"``. The behaviour depends on if ``use_time`` is set to ``True`` or not.
| If it is, ``datetime`` and an ISO-string with a time will work as expected, a ``date`` or an ISO-string without time
  will produce a ``default_value`` on that date at midnight.
| If it is not, ``date`` and an ISO-string without time will work as expected. If ``default_value`` is a ``datetime``
  or an ISO-string with a time, the time is simply ignored.


Diff
----
Somethimes, when data has to be changed in the database, the user needs to confirm this first. Of course, you should
use a ``Dialog.confirm`` to do this, but you might want to show the user the data that changed first.
This is what ``show_diff`` is for. With it, you can show the names of changed fields, their old and their new values.

.. code-block:: python

    #### scriptor ####
    from viur.scriptor import *

    async def main():
        await Dialog.show_diff(
            title="Here's what changed:",
            diffs=[
                ("name", "John", "Bob"),
                ("age", 37, 38)
            ]
        )


Raw HTML
--------
``Dialog.raw_html`` renders arbitrary HTML in the Scriptor output area. This is useful for
displaying formatted content — highlighted text, links, images, or structured layouts — that
would be awkward to express with plain text.

.. note::
   ``Dialog.raw_html`` is only available in the browser context (Pyodide). In the CLI it
   prints the raw HTML string to stdout.

``raw_html`` must be awaited. It shows the HTML and then waits for the user to click a
continue button before the script proceeds.

.. code-block:: python

    #### scriptor ####
    from viur.scriptor import *

    async def main():
        await Dialog.raw_html("<h2>Summary</h2><p>Everything went <b>OK</b>.</p>")


It also supports ``in_multiple=True``, so it can be embedded inside a ``Dialog.multiple``
to show a static HTML label or description above other input fields:

.. code-block:: python

    #### scriptor ####
    from viur.scriptor import *

    async def main():
        components = {
            "info":  await Dialog.raw_html("<b>Please fill in your contact details:</b>", in_multiple=True),
            "name":  await Dialog.text("Name", in_multiple=True),
            "email": await Dialog.text("E-Mail", in_multiple=True),
        }
        result = await Dialog.multiple(
            title="Contact",
            components=components,
            send_button_text="Submit"
        )
        print(result["name"], result["email"])


Table
-----
The last remaining Dialog-type is the ``table``. It is used to show tabular data, but can also be used to select rows.
This example shows how to display a simple table:

.. code-block:: python

    #### scriptor ####
    from viur.scriptor import *

    async def main():
        tbl_head = ["Name", "Age"]
        tbl_data = [
            ["John", 37],
            ["Bob", 38]
        ]
        await Dialog.table(tbl_head, tbl_data)


This example shows how to show the same table, but let the user pick a line.

.. code-block:: python

    #### scriptor ####
    from viur.scriptor import *

    async def main():
        tbl_head = ["Name", "Age"]
        tbl_data = [
            ["John", 37],
            ["Bob", 38]
        ]
        result = await Dialog.table(tbl_head, tbl_data, select=True)
        print(f"you selected row {result}")


There is also an option to select multiple rows:

.. code-block:: python

    #### scriptor ####
    from viur.scriptor import *

    async def main():
        tbl_head = ["Name", "Age"]
        tbl_data = [
            ["John", 37],
            ["Bob", 38]
        ]
        result = await Dialog.table(tbl_head, tbl_data, select=True, multiselect=True)
        print(f"you selected row {result}")


Multiple
--------
``Dialog.multiple`` combines several input components into a single dialog. The user sees all
fields at once and confirms everything with one button — instead of having to click through
several dialogs one after another.

Each component is built by calling the corresponding ``Dialog``-method with ``in_multiple=True``.
This returns the component's configuration dict instead of showing it. These dicts are then
collected into a list or a named dict and passed to ``Dialog.multiple``.

.. note::
   ``Dialog.multiple`` is only available in the browser context (Pyodide). In the CLI it
   immediately returns the components unchanged without waiting for user input.

Basic example (list of components)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
When ``components`` is a **list**, the return value is a list of the user's inputs in the
same order.

.. code-block:: python

    #### scriptor ####
    from viur.scriptor import *

    async def main():
        components = [
            await Dialog.text("First name", in_multiple=True),
            await Dialog.text("Last name", in_multiple=True),
            await Dialog.number("Age", in_multiple=True),
        ]
        results = await Dialog.multiple(
            title="Enter your details",
            components=components,
            send_button_text="Submit"
        )
        first_name, last_name, age = results
        print(f"{first_name} {last_name}, age {age}")


Named components (dict)
~~~~~~~~~~~~~~~~~~~~~~~
When ``components`` is a **dict**, the return value is a dict with the same keys — which makes
it easier to access individual fields by name.

.. code-block:: python

    #### scriptor ####
    from viur.scriptor import *

    async def main():
        components = {
            "name":     await Dialog.text("Name", in_multiple=True),
            "category": await Dialog.select(["A", "B", "C"], in_multiple=True),
            "date":     await Dialog.date("Date", in_multiple=True),
        }
        results = await Dialog.multiple(
            title="New entry",
            components=components,
            send_button_text="Create"
        )
        print(results["name"])
        print(results["category"])
        print(results["date"])


Reusing a dialog (``reuse=True``)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
If you want to show the same dialog again — for example in a loop to collect several entries —
you can pass ``reuse=True`` for all calls after the first. This skips re-sending the component
definitions to the browser and only waits for the next submission.

.. code-block:: python

    #### scriptor ####
    from viur.scriptor import *

    async def main():
        components = {
            "article": await Dialog.text("Article number", in_multiple=True),
            "amount":  await Dialog.number("Amount", in_multiple=True),
        }
        entries = []
        first = True
        while True:
            results = await Dialog.multiple(
                title="Scan article",
                components=components,
                send_button_text="Add",
                reuse=not first
            )
            first = False
            entries.append(results)
            if not await Dialog.confirm("Add another article?"):
                break
        print(entries)