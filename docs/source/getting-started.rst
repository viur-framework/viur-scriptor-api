.. scriptor documentation master file, created by
   sphinx-quickstart on Mon Jun  5 19:40:54 2023.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Getting Started
====================================

The Scriptor is built on Pyodide and interprets Python files as scripts. Each script has a "main" function, which is called once at the start, acting as the entry point for the script. The Scriptor provides additional modules for simplification. It includes interfaces for dialogues, networking, and logging.

Every newly created script always includes a default output with an alert dialog.

.. code-block:: python

    #### scriptor ####
    from scriptor import dialog

    async def main():
        await dialog.alert("Hello World")

The script showcases a simple component with the text "Hello world". This represents one type of dialog. The documentation will delve into various other types of dialogs as it progresses.

.. image:: images/01_Basic_Script.png

