DirectoryHandler
================
The ``DirectoryHandler`` is a class with which you can open directories on your PC. You can read, write and list files
as well as subdirectories.

.. warning::
    The ``write_to_file``-method replaces the content of the file you selected (if it already existed). The
    ``open_file_for_writing``-method will also clear the content of any existing selected file before writing. Be
    careful not no open files for writing if you still need their current content.

.. note::
    Some of the following examples need specific files to exist in the directory you open. Ideally, you'd create an
    empty directory and execute the examples in order. The earlier examples show how to create files and will create
    the files the latter examples need.

open
----
The ``open``-method prompts the user to open a directory. If it's the first time that directory is opened since your
scriptor-session started, you'll get asked for permissions by the browser. (see next example)

list_files and list_subdirs
---------------------------
The ``list_files``- and ``list_subdirs``-methods return a list of all files and a list of all directorys in the selected
directory respectively. (see next example)

write_to_file
-------------
The ``write_to_file``-method writes binary data to a file. If the file already exists it will raise an error, unless you
passed ``may_already_exist`` as True. If you did, it will completely replace the files content.
(see ``open_file_for_writing`` example)


.. code-block:: python

    #### scriptor ####
    from viur.scriptor import *

    async def main():
        my_dir = await DirectoryHandler.open()
        files_in_dir = await my_dir.list_files()
        subdirs_in_dir = await my_dir.list_subdirs()
        print(f"""These files are in the directory you selected: {files_in_dir}""")
        print(f"""These subfolders are in the directory you selected: {subdirs_in_dir}""")
        if "test.bin" in files_in_dir:
            print("test.bin already exists")
        else:
            await my_dir.write_to_file(b"This is a test-file!", "test.bin")
            print("created test.bin")


open_file_for_writing
---------------------
The ``open_file_for_writing``-method is intended to be used if the data can't be written in one step, i.e. if it's too
big for your computers memory. It returns a ``WritableFileFromDirectoryHandler``, which allows you to write data piece
by piece. (``WritableFileFromDirectoryHandler``-objects need to be explicitly closed, otherwise data will not be
persisted correctly. It has a ``close``-method, and there's a ``close_all``-method in the ``DirectoryHandler``. Both
will get explained later in this document, as well as the ``read_from_file``-method.)

.. code-block:: python

    #### scriptor ####
    from viur.scriptor import *

    async def main():
        my_dir = await DirectoryHandler.open()
        files_in_dir = await my_dir.list_files()
        subdirs_in_dir = await my_dir.list_subdirs()
        writable = await my_dir.open_file_for_writing(
            "writable_test.bin",
            may_already_exist=True
        )
        await writable.write(b"Hello ")
        await writable.write(b"World!\n")
        await my_dir.close_all()
        print("Please try to open the writable_test.bin that just got created in a text-editor."
              " Here's a preview of it's content:")
        print(await my_dir.read_from_file("writable_test.bin"))


close_all
---------
The ``close_all``-method closes all file-handles originating from this ``DirectoryHandler`` or any of it's children
(subdirectories, see below). Files need to be explicitly closed to guarantee all data has been written properly.
This only applies to files opened with ``open_file_for_writing``. If you use the ``write_to_file``-method, the file will
be closed automatically after the data has been written.

get_subdirectory_handler
------------------------
The ``get_subdirectory_handler``-method creates a new ``DirectoryHandler`` for a subdirectory. This ``DirectoryHandler``
works exactly the same way as the one creating it, just on a subdirectory. Also the root-``DirectoryHandler`` keeps
a reference to it, so ``close_all`` only needs to be called on the root-``DirectoryHandler``.

.. code-block:: python

    #### scriptor ####
    from viur.scriptor import *

    async def main():
        my_dir = await DirectoryHandler.open()
        subdir = await my_dir.get_subdirectory_handler("new_subdir", create=True)
        await subdir.write_to_file(b"data", "filename.txt")
        await my_dir.close_all()
        print("Inside the directory you picked, there should now be a new"
              " subdirectory called new_subdir.")
        print("Inside it, you should find a file called filename.txt")


read_from_file
--------------
The ``read_from_file``-method reads data from a file. You can either read the whole file, or pass a ``start``- and/or
``end``-parameter to read only a part of the file. (If you haven't, pleas execute the first example-script from this
document. The test.bin created by it is expected to be in the directory we're using in this example.)

.. code-block:: python

    #### scriptor ####
    from viur.scriptor import *

    async def main():
        my_dir = await DirectoryHandler.open()
        complete_content = await my_dir.read_from_file("test.bin")
        print("complete file content: ", complete_content)
        print("number of bytes in the file: ", len(complete_content))
        first_four = await my_dir.read_from_file("test.bin", end=4)
        print("first four bytes: ", first_four)
        five_to_fifteen = await my_dir.read_from_file("test.bin", start=5, end=15)
        print("bytes 5 to 15: ", five_to_fifteen)
        last_five = await my_dir.read_from_file("test.bin", start=-5)
        print("the lasst 5 bytes: ", last_five)

