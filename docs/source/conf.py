# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information
import os
import sys
import datetime
from importlib.util import spec_from_loader, module_from_spec

fake_ffi_module = module_from_spec(spec_from_loader('ffi', None))
fake_ffi_module.IN_BROWSER = True
fake_ffi_module.to_js = None
fake_ffi_module.JsException = None
fake_ffi_module.JsProxy = None
fake_pyodide_module = module_from_spec(spec_from_loader('pyodide', None))
fake_pyodide_module.ffi = fake_ffi_module
sys.modules['pyodide'] = fake_pyodide_module
sys.modules['pyodide.ffi'] = fake_ffi_module
fake_js_module = module_from_spec(spec_from_loader('js', None))
fake_js_module.FormData = None
sys.modules['js'] = fake_js_module
fake_manager_module = module_from_spec(spec_from_loader('manager', None))
sys.modules['manager'] = fake_manager_module
fake_config_module = module_from_spec(spec_from_loader('config', None))
sys.modules['config'] = fake_config_module

sys.path.append(os.path.abspath('../..'))

project = 'Scriptor'
author = 'Mausbrand Informationssysteme GmbH'
copyright = f"""{datetime.datetime.now().strftime("%Y")} {author}"""

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = ['sphinx.ext.autosummary', 'sphinx.ext.autodoc']  # 'autoapi.extension' for automatic api-doc
# html_show_sourcelink = False

templates_path = ['_templates']
exclude_patterns = []
# autoapi_dirs = ['../../viur/scriptor']
# autoapi_options = ['members', 'undoc-members', 'show-inheritance', 'show-module-summary']
# autoapi_dirs = ['../../src/viur-scriptor-api']

# autodoc_member_order = 'alphabetical'
# autodoc_member_order = 'groupwise'
autodoc_member_order = 'bysource'

# source_dir = os.path.abspath(autoapi_dirs[0])
# sys.path.insert(0, source_dir)

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']
