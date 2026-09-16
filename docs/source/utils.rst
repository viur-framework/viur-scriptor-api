Utilities
=========

extract_items and map_extract_items
-----------------------------------
A task scriptor is often used for is the extraction of data (most commonly into a table). ``extract_items`` and
``map_extract_items`` are aimed to ease the extraction of datapoints. They don't cover every use-case, but the most
common ones, and thus spare the developers of new scripts most of the repetitive work.
Since examples working with the database would need to be highly specific to the customers data, we'll use fictional
demo-data.

This example shows how to extract the first names of a user and the first names of all of their friends.
The demo-data contains two users, which are iterated over inside ``map_extract_items``. The mapping defines, what data
will be extracted from the given input-data and which name it will get in the result. The extraction of the first name
of the user is simple: As you would select the first_name from a dictionary with ``dictionary["first_name"]``, you have
to add ``"first_name"`` to the extractor-list. Similarly, you'd select the friends of a user with
``dictionary["friends"]``, which would be a ``list`` you'd need to iterate over. To signal to the extractor, that you
want to iterate it, you can write three dots (``...``) called ``Ellipsis`` in Python. The following selectors then get
applied to each element of the ``list``. The result of this is then printed. Afterwards a table-file is made from the
data, which is then converted to a list of lists representing the tables data, which is then shown in a
``Dialog.table``.

The ``join_with``-parameter defines how list-elements are concatenated. Setting it implies that all results are
converted to ``string``. Try removing it from the example code. You'll see, that the friends names aren't in a single
``string`` anymore, but in a ``list``. This will also lead to the ``Dialog.table`` raising an error. This is useful if
you want to modify the data before saving or displaying it.

.. code-block:: python

    #### scriptor ####
    from viur.scriptor import *

    async def main():
        demo_data = [
            {
                "first_name": "Peter",
                "last_name": "Jones",
                "friends": [
                    {"first_name": "Darrell", "last_name": "Bryant"},
                    {"first_name": "Julie", "last_name": "Brooks"},
                    {"first_name": "Erin", "last_name": "Jimenez"}
                ]
            },
            {
                "first_name": "Amy",
                "last_name": "Stephenson",
                "friends": [
                    {"first_name": "Christina", "last_name": "Allen"},
                    {"first_name": "Joel", "last_name": "Alvarez"},
                    {"first_name": "Melanie", "last_name": "Rivera"},
                    {"first_name": "Erica", "last_name": "Nicholson"},
                    {"first_name": "Roy", "last_name": "Weaver"}
                ]
            }
        ]
        mapping = {
            "First Name": ["first_name"],
            "Friends first Names": ["friends", ..., "first_name"]
        }
        extracted_data = map_extract_items(demo_data, mapping, join_with=", ")
        table_file = File.from_table(extracted_data)
        list_table_header, *list_table_data = table_file.as_list_table()
        await Dialog.table(list_table_header, list_table_data)


Note that ``map_extract_items`` recognises if you pass a ``list`` or a ``dict``. If you pass a ``list``, it will
automatically assume the mapping applies to the items of the ``list`` and iterate over it.

That means that
``extracted_data = map_extract_items(demo_data, mapping, join_with=", ")`` does the same as

.. code-block:: python

    extracted_data = []
    for user in demo_data:
        extracted_data.append(map_extract_items(user, mapping, join_with=", "))


If you want to extract more complex data, or want to transform the data, you need to iterate over the result of
``map_extract_items``. In this example, we'll do the same as before, but also extract the last names of the friends.
Note that we removed the ``join_with``-parameter, because we need the names as a ``list``.

.. code-block:: python

    #### scriptor ####
    from viur.scriptor import *

    async def main():
        demo_data = [
            {
                "first_name": "Peter",
                "last_name": "Jones",
                "friends": [
                    {"first_name": "Darrell", "last_name": "Bryant"},
                    {"first_name": "Julie", "last_name": "Brooks"},
                    {"first_name": "Erin", "last_name": "Jimenez"}
                ]
            },
            {
                "first_name": "Amy",
                "last_name": "Stephenson",
                "friends": [
                    {"first_name": "Christina", "last_name": "Allen"},
                    {"first_name": "Joel", "last_name": "Alvarez"},
                    {"first_name": "Melanie", "last_name": "Rivera"},
                    {"first_name": "Erica", "last_name": "Nicholson"},
                    {"first_name": "Roy", "last_name": "Weaver"}
                ]
            }
        ]
        mapping = {
            "First Name": ["first_name"],
            "friends_first_names": ["friends", ..., "first_name"],
            "friends_last_names": ["friends", ..., "last_name"]
        }
        extracted_data = []
        for row in map_extract_items(demo_data, mapping):
            row["Friends Names"] = ", ".join(f"""{first_name} {last_name}""" for
                                             first_name, last_name in
                                             zip(row["friends_first_names"],
                                                 row["friends_last_names"])
                                            )
            del row["friends_first_names"]
            del row["friends_last_names"]
            extracted_data.append(row)
        table_file = File.from_table(extracted_data)
        list_table_header, *list_table_data = table_file.as_list_table()
        await Dialog.table(list_table_header, list_table_data)


clear_console
-------------
Removes the output a script has produced so far from the script window. Pass a ``length`` to keep that many entries
and drop only what came after them, which is useful for a long-running loop that would otherwise fill the window with
its own progress output. On the CLI the terminal is cleared instead.

.. code-block:: python

    #### scriptor ####
    from viur.scriptor import *

    async def main():
        for i in range(100):
            clear_console()
            logger.info(f"step {i}")

prevent_close
-------------
Closing a script window aborts the script that runs in it right away. That is what you usually want, but a script
that writes files or edits entries should not be stopped halfway through by a stray click. ``prevent_close`` asks the
script window to confirm before aborting: the user is offered to minimize the window instead of closing it. Call it
with ``False`` once the critical part is over; at the end of the run the protection is dropped anyway.

Outside of the browser (the CLI) there is no script window, so calling it does nothing.

.. code-block:: python

    #### scriptor ####
    from viur.scriptor import *

    async def main():
        prevent_close()
        for entry in await modules.myModule.list():
            await modules.myModule.edit(entry, name="new name")
        prevent_close(False)
        logger.info("done")
