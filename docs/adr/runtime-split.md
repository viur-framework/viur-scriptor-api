---
covers: [viur.scriptor._utils.is_pyodide_context, viur.scriptor._utils.is_pyodide_in_browser, viur.scriptor._utils._wait_for_result, viur.scriptor._utils.save_file]
status: accepted
---
## Seam
`is_pyodide_context()` decides at **import time** which of two definitions of a name
survives. Everything that behaves differently in the browser and on the CLI is written as
two module-level `def`s under `if is_pyodide_context(): ... else: ...`, never as one
function with a runtime branch. That is the hook point for a new dual-runtime function.

## Rules
- Both branches keep the identical signature and docstring. The browser branch is the
  contract; the CLI branch may only degrade (print a note instead of showing an image),
  never take different arguments.
- Never import `js`, `pyodide` or `manager` unguarded at module top level - the CLI has
  none of them.
- `_wait_for_result` exists **only** in the Pyodide branch of `_utils`. Import it inside
  the `if is_pyodide_context():` block, or every CLI import of that module breaks.
- CLI-only dependencies (`prompt_toolkit`, `simple_term_menu`) must sit behind the same
  guard as the `def` that uses them; they are not in the Pyodide wheel set.

## Traps
- `is_pyodide_context()` is not "am I in a browser". It is true whenever `pyodide`, `js`
  and `manager` import. The browser question is `is_pyodide_in_browser()`.
- Detection runs once when `_utils` is imported. Nothing can flip it afterwards, and there
  is no way to exercise the CLI branch inside a Pyodide worker.
- `_wait_for_result()` treats the result `"__exit__"` as a stop signal and calls
  `sys.exit(0)`. Do not wrap awaits on it in a bare `except:` - that swallows the abort.
- `js.self.postMessage` is fire-and-forget. Posting a dialog is not the same as the user
  having answered; only `_wait_for_result()` blocks.
- `save_file` in the CLI branch writes into `SCRIPTOR_DEFAULT_SAVE_DIRECTORY` (default
  `~/Scriptor_Downloads`) and appends `_001`, `_002`, ... instead of overwriting.

## Why not
One function with an inner `if` would be shorter, but the CLI-only imports could then not
be guarded together with the code that needs them.

## See also
`dialog`, `module`
