Files
=====
Files, in general, are for storing data. In Scriptor, there is a set of typical tasks where files are involved. The
``File``-Class provies several methods to do those tasks easily and efficiently.


.. note::
    In the first examples, we'll use the download()-method of Files to make your browser download it.
    This will be explained later in this document.

Creating Files from Data
------------------------

from_string
~~~~~~~~~~~
This method is used to create a File from a string (aka. a text-file).

.. code-block:: python

    #### scriptor ####
    from viur.scriptor import *

    async def main():
        file = File.from_string("Hello World", "hello_world.txt")
        file.download()
        print("Please check your downloads. You should have a new file called hello_world.txt")


from_bytes
~~~~~~~~~~
Similar to the ``from_string``-Method, this method creates a File from bytes. This is usually useful for working with
files like xlsx, zip, pdf, etc. (Also there are extra convenience-methods for handling tables.)

.. code-block:: python

    #### scriptor ####
    from viur.scriptor import *

    async def main():
        file = File.from_bytes(b"Hello World", "hello_world.txt")
        file.download()
        print("Please check your downloads. You should have a new file called hello_world.txt")


from_table
~~~~~~~~~~
This method can handle two different representations of tables and create a xlsx- or csv-file from them.
Tables can either be defined as lists of dicts or lists of lists. In the case of dicts, the keys from the dict must
match the headers of the table. If no header is specified explicitly, it is automatically generated from the
dictinaries' keys. In case of a list of lists, the first list in the outer list is considered the header if no header
is defined explicitly.

.. code-block:: python

    #### scriptor ####
    from viur.scriptor import *

    async def main():
        tbl_head = ["Name", "Age"]
        tbl_data = [
            ["John", "37"],
            ["Bob", "38"]
        ]
        file = File.from_table(tbl_data, tbl_head, filename="simple_table.xlsx")
        file.download()
        print("Please check your downloads."
              " You should have a new file called simple_table.xlsx")


.. code-block:: python

    #### scriptor ####
    from viur.scriptor import *

    async def main():
        tbl = [
            {"Name": "John", "Age": "37"},
            {"Name": "Bob", "Age": "38"}
        ]
        file = File.from_table(tbl, filename="simple_table2.xlsx")
        file.download()
        print("Please check your downloads."
              " You should have a new file called simple_table2.xlsx")


As you may have noticed, in this example, the ages are defined as strings. This is because tables generally consists of
strings only. If you have other types in your data, they can be converted automatically, but you need to explicitly
enable this functionality by setting ``auto_str`` to ``True``.

.. code-block:: python

    #### scriptor ####
    from viur.scriptor import *

    async def main():
        tbl_head = ["Name", "Age"]
        tbl_data = [
            ["John", 37],
            ["Bob", 38]
        ]
        file = File.from_table(
            tbl_data,
            tbl_head,
            filename="simple_table3.xlsx",
            auto_str=True
        )
        file.download()
        print("Please check your downloads."
              " You should have a new file called simple_table3.xlsx")


Sometimes, especially while developing a new script, you may have incomplete data, that you want to save anyway, just
to see what it looks like. To achieve this, you just have to set ``fill_empty`` to ``True``.

.. code-block:: python

    #### scriptor ####
    from viur.scriptor import *

    async def main():
        tbl_head = ["Name", "Age"]
        tbl_data = [
            ["John", 37],
            ["Bob"]  # missing age
        ]
        file = File.from_table(
            tbl_data,
            tbl_head,
            filename="simple_table3.xlsx",
            fill_empty=True,
            auto_str=True
        )
        file.download()
        print("Please check your downloads."
              " You should have a new file called simple_table3.xlsx")


Besides xlsx, csv is supported. You can just change the file-name and it will automatically generate the right format.

.. code-block:: python

    #### scriptor ####
    from viur.scriptor import *

    async def main():
        tbl_head = ["Name", "Age"]
        tbl_data = [
            ["John", 37],
            ["Bob"]  # missing age
        ]
        file = File.from_table(
            tbl_data,
            tbl_head,
            filename="simple_table4.csv",
            fill_empty=True,
            auto_str=True
        )
        file.download()
        print("Please check your downloads."
              " You should have a new file called simple_table4.csv")


The default delimiter is a comma (,), but sometimes, especially for Excel in europe, you might want to use a semicolon
(;). This is simply achieved by passing it as the parameter ``csv_delimiter`` (if you pass it while generating xlsx,
it is ignored).

.. code-block:: python

    #### scriptor ####
    from viur.scriptor import *

    async def main():
        tbl_head = ["Name", "Age"]
        tbl_data = [
            ["John", 37],
            ["Bob"]  # missing age
        ]
        file = File.from_table(
            tbl_data,
            tbl_head,
            filename="simple_table5.csv",
            fill_empty=True,
            auto_str=True,
            csv_delimiter=";"
        )
        file.download()
        print("Please check your downloads."
              " You should have a new file called simple_table5.csv")


Getting information about the File
----------------------------------

get_filename
~~~~~~~~~~~~
The ``get_filename``-method returns, as the name suggests, the name of the file.

.. code-block:: python

    #### scriptor ####
    from viur.scriptor import *

    async def main():
        file = File.from_string("Hello World", "hello_world.txt")
        filename = file.get_filename()
        print(f"The File you just created has the name {filename}")


get_size
~~~~~~~~
The ``get_size``-method returns the size of the file in bytes.

.. code-block:: python

    #### scriptor ####
    from viur.scriptor import *

    async def main():
        file = File.from_string("Hello World", "hello_world.txt")
        filesize = file.get_size()
        print(f"The File has a size of {filesize} bytes.")

Using Data from a File
----------------------

Files can also be user-input (this is explained later, we use demo-data in the following examples). In that case, you
want to get data from the file. Files from user-input usually contain text or tabular data, so there are extra methods
for handling those easily.

as_bytes
~~~~~~~~
The ``as_bytes``-method returns the complete data of the file as a ``bytestring``.

.. code-block:: python

    #### scriptor ####
    from viur.scriptor import *

    async def main():
        file = File.from_string("Hello World", "hello_world.txt")
        content = file.as_bytes()
        print(content)


as_text
~~~~~~~
The ``as_text``-method return the complete data of the file as a decoded ``string``, if possible. If not, it raises an
error.

.. code-block:: python

    #### scriptor ####
    from viur.scriptor import *

    async def main():
        file = File.from_string("Hello World", "hello_world.txt")
        content = file.as_text()
        print(content)


as_object_from_json
~~~~~~~~~~~~~~~~~~~
If the file the user provided is a json-file, this method will convert it to a python-object.

.. code-block:: python

    #### scriptor ####
    from viur.scriptor import *

    async def main():
        file = File.from_string("""
            {"key": "value", "a_list_of_ints": [1,2,3,4], "a_float_value": 1.23}
        """, "demo.json")
        content = file.as_object_from_json()
        print(content)


as_list_table and as_dict_table
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Mostly, user-provided data comes in the form of tables. These can be loaded as the aforementioned two representations:
a list of dicts or a list of lists.

.. code-block:: python

    #### scriptor ####
    from viur.scriptor import *

    async def main():
        tbl_head = ["Name", "Age"]
        tbl_data = [
            ["John", "37"],
            ["Bob", "38"]
        ]
        file = File.from_table(tbl_data, tbl_head, filename="simple_table.xlsx")
        print(file.as_list_table())
        print(file.as_dict_table())


Getting the file to and from your PC.
-------------------------------------

download
~~~~~~~~
The ``download``-method provides the simplest way to get data from scriptor to your PC. As you have seen from the
earlier examples, it just triggers a download so your browser saves the file or asks for where to save it (depending
on your browsers settings).

.. code-block:: python

    #### scriptor ####
    from viur.scriptor import *

    async def main():
        file = File.from_string("Hello World", "hello_world.txt")
        file.download()
        print("Please check your downloads. You should have a new file called hello_world.txt")


If you try to download more than one file in the same script, your browser may ask you if you want to allow the
website (scriptor) to do this. You can try it out with this code:


.. code-block:: python

    #### scriptor ####
    from viur.scriptor import *

    async def main():
        File.from_string("Hello World", "download1.txt").download()
        File.from_string("Hello World", "download2.txt").download()
        File.from_string("Hello World", "download3.txt").download()


open_dialog
~~~~~~~~~~~
The ``open_dialog`` prompts the user to select a file from their PC. The data from the selected file will get loaded
into scriptor. The file itself remains as it is. If the user cancels the dialog, an error will be raised and the script
stops (unless you handle the error differently).

.. code-block:: python

    #### scriptor ####
    from viur.scriptor import *

    async def main():
        print("Please select a simple text-file.")
        textfile = await File.open_dialog()
        print(textfile.as_text())


save_dialog
~~~~~~~~~~~
The ``save_dialog`` is the counterpart to the open_dialog and provides an alternative to the download-method. The user
is prompted to save the file. They can choose to select an existing file, which will then get overwritten, or a new
filename that doesn't exist yet, which will then be created. This also means that the file can be saved with a
different name than defined in your code. As with the ``open_dialog``, if the user cancels the dialog, an error will be
raised.


.. code-block:: python

    #### scriptor ####
    from viur.scriptor import *

    async def main():
        print("Please select where to save the test-file")
        testfile = File.from_string("Hello World", "save_test.txt")
        await testfile.save_dialog()


