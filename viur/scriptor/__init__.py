from .requests import WebRequest, WebResponse
from .dialog import Dialog
from .file import File
from .logger import logger
from .module import Modules
from .http_errors import *
from ._utils import is_pyodide_context, is_pyodide_in_browser, gather_async_iterator, clear_console
from .utils import extract_items, map_extract_items
import os
from requests.exceptions import ConnectionError
from .directory_handler import DirectoryHandler
from .progressbar import ProgressBar

__version__ = '1.4.0'


def version():
    return __version__


modules = None
params = None

if is_pyodide_context():
    import config


    async def _init_modules():
        global modules
        global params
        try:
            import manager
            params = manager.params.to_py()
            if "__is_dev__" not in params:
                params["__is_dev__"] = True
        except ModuleNotFoundError:
            pass
        modules = Modules(config.BASE_URL, None, None)
        await modules.init()
        return True
else:
    async def _init_modules(base_url=None, username=None, password=None, login_skey=None, script_params=None):
        global modules, params
        assert not modules, "already initialized"
        params = script_params
        try:
            modules = Modules(base_url=base_url or os.environ.get('SCRIPTOR_TARGET', None),
                              username=username or os.environ.get('SCRIPTOR_USER', None),
                              password=password or os.environ.get('SCRIPTOR_PASSWORD', None),
                              login_skey=login_skey)
            await modules.init()
            return True
        except ConnectionError:
            print('Connection failed.')
            modules = None
            return False

__all__ = [
    'is_pyodide_context',
    'is_pyodide_in_browser',
    'WebRequest',
    'WebResponse',
    'DirectoryHandler',
    'Dialog',
    'File',
    'logger',
    'modules',
    'ConnectionError',
    'gather_async_iterator',
    'params',
    'extract_items',
    'map_extract_items',
    'ProgressBar',
    'version',
]

if is_pyodide_context():
    import traceback
    import pydoc
    from pyodide.ffi import JsException

    print = Dialog.print


    def help(thing):
        print(pydoc.render_doc(thing, renderer=pydoc._PlainTextDoc()))


    __all__.extend(['print', 'traceback', 'JsException', 'help'])
