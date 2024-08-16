Getting Started
===============

The Scriptor is built on Pyodide and interprets Python files as scripts. Each script has a "main" function, which is
called once at the start, acting as the entry point for the script. The Scriptor provides additional modules for
simplification. It includes functions and classes for dialogs, database-access, file-access, networking, and logging.

Every newly created script always includes a default output with an alert dialog.

.. code-block:: python

    #### scriptor ####
    from viur.scriptor import *

    async def main():
        print("Hello World")


The script showcases a simple ``print`` with the text "Hello World". The documentation will explain various other
ways of interacting with users as it progresses. Most functionality explained in this documentation has code-examples.
All code-examples given in this documentation can be directly copied into an empty scriptor-script to try them out.


Default import from viur.scriptor
---------------------------------

The functions and classes provided by scriptor are usually imported with ``from viur.scriptor import *``.
This imports the commonly used members directly into your scripts namespace.
That means you don't need to write the full name that you see in the API-doc. Here's a table of readily imported
functions, methods and classes:

.. list-table:: scriptor tools
   :widths: 50 150
   :header-rows: 1

   * - name
     - purpose
   * - ``is_pyodide_context``
     - determining if the script is running in a pyodide-interpreter
   * - ``is_pyodide_in_browser``
     - determining if the script is running in a browser
   * - ``WebRequest`` and ``WebResponse``
     - retrieving data from http(s)-servers
   * - ``DirectoryHandler``
     - working with directories and files in them
   * - ``Dialog``
     - intracting with the user
   * - ``File``
     - working with data, getting files from and to the user
   * - ``logger``
     - logging information
   * - ``modules``
     - accessing database modules
   * - ``extract_items`` and ``map_extract_items``
     - extracting datapoints from a larger data-structure
   * - ``ProgressBar``
     - showing progress to the user
   * - ``print``
     - showing text to the user
   * - ``help``
     - printing information about a python-object

Also imported are ``traceback``, ``ConnectionError`` and ``JsException`` for handling exceptions, and ``params``,
which contains parameters for the script.
