Export & Import
===============

The ``export_import`` module provides functions to export data from ViUR modules into files
(CSV, Excel, JSON) and to import data back from such files. It handles the conversion between
ViUR's internal data format and flat table representations automatically — including relational
bones, translated bones, and multiple-values.

.. note::
   The export/import functions are **not** included in ``from viur.scriptor import *``.
   Import them explicitly:

   .. code-block:: python

       from viur.scriptor.export_import import export_module, import_from_table


Exporting
---------

export_module
~~~~~~~~~~~~~
The simplest way to export a module. Fetches all records automatically and returns a ``File``
object in the format determined by the filename extension (``.json``, ``.xlsx``, or ``.csv``).

.. code-block:: python

    #### scriptor ####
    from viur.scriptor import *
    from viur.scriptor.export_import import export_module

    async def main():
        file = await export_module("article", filename="article.xlsx")
        file.download()


CSV with a custom delimiter (useful for European Excel installations that expect ``;``):

.. code-block:: python

    #### scriptor ####
    from viur.scriptor import *
    from viur.scriptor.export_import import export_module

    async def main():
        file = await export_module("article", filename="article.csv", csv_delimiter=";")
        file.download()


export_to_csv / export_to_excel / export_to_json
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Use these functions when you already have the data and structure — for example when you want
to filter or transform records before exporting, or when you only want to export a subset of
entries.

The workflow is always the same:

1. Get the module and its structure
2. Collect the records you want to export
3. Call the matching export function

.. code-block:: python

    #### scriptor ####
    from viur.scriptor import *
    from viur.scriptor.export_import import export_to_excel

    async def main():
        article = await modules.get_module("article")
        structure = await article.structure()

        # Only export articles that are marked as active
        data = []
        async for entry in article.list(params={"active": True}):
            data.append(entry)

        file = export_to_excel(data, structure, filename="active_articles.xlsx")
        file.download()


The same pattern works for ``export_to_csv`` and ``export_to_json``:

.. code-block:: python

    #### scriptor ####
    from viur.scriptor import *
    from viur.scriptor.export_import import export_to_csv, export_to_json

    async def main():
        article = await modules.get_module("article")
        structure = await article.structure()
        data = [entry async for entry in article.list()]

        export_to_csv(data, structure, filename="articles.csv").download()
        export_to_json(data, structure, filename="articles.json").download()


Restricting exported fields
~~~~~~~~~~~~~~~~~~~~~~~~~~~
By default all bones are exported. Use ``filter_module_structure_with_whitelist`` to keep only
specific fields, or ``filter_module_structure_with_blacklist`` to remove specific fields.

.. code-block:: python

    #### scriptor ####
    from viur.scriptor import *
    from viur.scriptor.export_import import (
        export_to_excel,
        filter_module_structure_with_withelist,
        filter_module_structure_with_blacklist,
    )

    async def main():
        article = await modules.get_module("article")
        structure = await article.structure()
        data = [entry async for entry in article.list()]

        # Only export key, name and price
        filtered = filter_module_structure_with_withelist(structure, ["key", "name", "price"])
        export_to_excel(data, filtered, filename="articles_slim.xlsx").download()

        # Export everything except internal fields
        filtered2 = filter_module_structure_with_blacklist(structure, ["viurCurrentSeoKeys", "viurTags"])
        export_to_excel(data, filtered2, filename="articles_clean.xlsx").download()


Importing
---------

import_from_table
~~~~~~~~~~~~~~~~~
Imports records from a table (e.g. a previously exported CSV or Excel file) back into a ViUR
module. Each row is written to the module using the configured write mode.

The simplest case — re-importing an exported file to update existing records:

.. code-block:: python

    #### scriptor ####
    from viur.scriptor import *
    from viur.scriptor.export_import import import_from_table

    async def main():
        file = await File.open_dialog()
        table = file.as_dict_table()

        article = await modules.get_module("article")
        await import_from_table(table, article)


Write modes
^^^^^^^^^^^
The ``add_or_edit_mode`` parameter controls what happens for each row:

- ``"edit"`` *(default)* — updates existing records; each row must contain a ``key`` column
- ``"add"`` — always creates a new record, ignoring any ``key`` column
- ``"add_or_edit"`` — creates a new record if no ``key`` is present, otherwise updates

.. code-block:: python

    #### scriptor ####
    from viur.scriptor import *
    from viur.scriptor.export_import import import_from_table

    async def main():
        file = await File.open_dialog()
        article = await modules.get_module("article")

        await import_from_table(
            file.as_dict_table(),
            article,
            add_or_edit_mode="add"  # always create new records
        )


Tracking progress and errors
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
For large imports use the callback parameters to track progress and handle errors without
stopping the entire script:

.. code-block:: python

    #### scriptor ####
    from viur.scriptor import *
    from viur.scriptor.export_import import import_from_table

    async def main():
        file = await File.open_dialog()
        article = await modules.get_module("article")
        errors = []

        def on_progress(index, total):
            ProgressBar.set(
                percent=int(index / total * 100),
                current_step=index,
                total_steps=total
            )

        def on_error(exc, params):
            errors.append({"error": str(exc), "params": params})

        await import_from_table(
            file.as_dict_table(),
            article,
            progress_callback=on_progress,
            exception_callback=on_error,
        )

        ProgressBar.unset()
        if errors:
            print(f"{len(errors)} rows failed:")
            for e in errors:
                print(e)
        else:
            print("Import complete.")


Dry run
^^^^^^^
Pass ``dry_run=True`` to process and validate the data without writing anything to the
database. Useful for checking that the file format is correct before running the real import.

.. code-block:: python

    #### scriptor ####
    from viur.scriptor import *
    from viur.scriptor.export_import import import_from_table

    async def main():
        file = await File.open_dialog()
        article = await modules.get_module("article")

        await import_from_table(
            file.as_dict_table(),
            article,
            dry_run=True
        )
        print("Dry run finished — nothing was written to the database.")
