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
        # Ask the user if the program should proceed (interaction)
        ret = await Dialog.text("What's your name?")

        print("Your name is: "+ ret)

It's also possible to let the user input multiline-strings like this:

.. code-block:: python

    #### scriptor ####
    from viur.scriptor import *

    async def main():
        # Ask the user if the program should proceed (interaction)
        ret = await Dialog.text("What's your address?", multiline=True)

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



Date
~~~~
Often, documentation requires including information such as dates and times. To facilitate this, the Scriptor provides
the ability to input date values. Unlike other input types, this returns a datetime object.

.. code-block:: python

    #### scriptor ####
    from viur.scriptor import *

    async def main():
        date = await Dialog.date("When were you born?")
        print(f"You were born on {date}.")

In this example, the ``date`` variable is of type ``datetime.datetime``. Therefore, you can utilize all the functions
provided by the Python standard library's ``datetime``-module.

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