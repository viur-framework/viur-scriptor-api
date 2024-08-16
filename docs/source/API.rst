API Reference
=============

.. autoclass:: viur.scriptor.file.File
    :members: from_string, from_bytes, from_table, get_filename, as_bytes, as_text, as_object_from_json,
              as_list_table, as_dict_table, open_dialog, download, get_size

.. autoclass:: viur.scriptor.requests.WebRequest
    :members: get, download, post, put, delete, request

.. autoclass:: viur.scriptor.requests.WebResponse
    :members: get_url, get_status_code, get_content

.. autoclass:: viur.scriptor.dialog.Dialog
    :members: print, alert, select, confirm, text, number, date, show_diff, table

.. autoclass:: viur.scriptor.progressbar.ProgressBar
    :members: set, unset

.. autoclass:: viur.scriptor.directory_handler.DirectoryHandler
    :members: open, list_files, open_file_for_writing, close_all, write_to_file, read_from_file, list_subdirs,
              get_subdirectory_handler

.. autoclass:: viur.scriptor.directory_handler.WritableFileFromDirectoryHandler
    :members: get_filename, write, close

.. autoclass:: viur.scriptor.logger.Logger
    :members: log, info, debug, error, critical, fatal, warn, warning, exception, setLevel

.. autoclass:: viur.scriptor.module.Modules
    :members: get_module, get_base_url, viur_request

.. autoclass:: viur.scriptor.module.ListModule
    :members: name, preview, structure, view, edit, list, add, delete

.. autoclass:: viur.scriptor.module.TreeModule
    :members: name, preview, structure, view, edit, list, add, delete, for_each, move, list_root_nodes

.. autoclass:: viur.scriptor.module.SingletonModule
    :members: name, preview, structure, view, edit

.. automodule:: viur.scriptor.utils
    :members: extract_items, map_extract_items
