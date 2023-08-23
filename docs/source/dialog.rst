.. scriptor documentation master file, created by
   sphinx-quickstart on Mon Jun  5 19:40:54 2023.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Dialogues
====================================

Dialogues are a crucial component for interacting with the user. The scriptor provides a variety of dialogue types, including alerts, confirm, inputs, select, diffcompare, and table.

Alert
----------
When an alert is triggered, a message is displayed, and the script proceeds only after the 'OK' button is clicked. This functionality is comparable to an alert in JavaScript.

.. code-block:: python

    #### scriptor ####
    from scriptor import dialog

    async def main():
        await dialog.alert("Hello World")

An alert is generated in this example, displaying the text "Hello World".

.. autofunction:: scriptor.dialog.alert

Confirm
----------
A Confirm element is a component that represents a simple yes/no/cancel dialog. It allows the user to confirm an action or cancel it. After the user interacts with the Confirm element, it returns one of the values: True, False, or None.

Here is a simple example where the user is prompted using a Confirm element to determine whether the program should continue or be stopped.

.. code-block:: python
    
    #### scriptor ####
    from scriptor.dialog import confirm

    async def main():
        # Ask the user if the program should proceed (interaction)
        ret = await confirm("Should we proceed?")

        # ret can be True or False (Yes/No)
        
        if not ret:
            print("Stop!") # We will print an output for debug
            return # will stop the whole program

        # Done!
        print("Done!")

.. autofunction:: scriptor.dialog.confirm

Input
----------
An Input is another type that expects user input in the form of numbers, dates, strings, or multi-line strings. It provides a way for users to enter and submit data.
The inputs in Scriptor are similar to inputs in an HTML context.

.. autofunction:: scriptor.dialog.input

Number
~~~~~~~~~~~~~

The simplest input type is a number, where the number can be either an integer or a floating-point number. For example, if the value "1.5" is given as an input, the output will be a float variable. However, if the number is an integer, the output type will be returned as 'int'.

A simple example that asks for the age.

.. code-block:: python

    #### scriptor ####
    from scriptor.dialog import input

    async def main():
        age = await input.number("How old are you?")
        print(f"You are {age} years old.")

Properties

.. autofunction:: scriptor.dialog.input.number

Date
~~~~~~~~~~~~~
Often, documentation requires including information such as dates and times. To facilitate this, the Scriptor provides the ability to input date values. Unlike other input types, the Scriptor returns a datetime object.

.. code-block:: python

    #### scriptor ####
    from scriptor.dialog import input

    async def main():
        date = await input.date("When were you born?")
        print(f"You were born on {date}.")

In this example, the 'date' variable is of type 'datetime.datetime'. Therefore, you can utilize all the functions provided by the Python standard library's 'datetime' module.

Properties

.. autofunction:: scriptor.dialog.input.date

Strings
~~~~~~~~~~~~~
The Scriptor also supports input fields in the form of strings. Input strings allow the receiving of one-line texts. Here is a simple example to ask for a name:

.. code-block:: python

    #### scriptor ####
    from scriptor.dialog import input

    async def main():
        name = await input.name("What is your name?")
        print(f"Hello {name}.")


.. autofunction:: scriptor.dialog.input.string

Text
~~~~~~~~~~~~~
Not only single-line strings are possible, but also multi-line strings. The designated type for this purpose is the 'input.text' type. With this type, it is possible to receive multi-line strings.

.. code-block:: python

    #### scriptor ####
    from scriptor.dialog import input

    async def main():
        story = await input.text("Tell me a story about you")
        print(story)


.. autofunction:: scriptor.dialog.input.text