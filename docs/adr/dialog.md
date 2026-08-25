---
covers: [viur.scriptor.dialog.Dialog]
status: accepted
---
## Seam
`Dialog` is a flat facade: one module per dialog under `viur/scriptor/dialog/`, one
function of the same name inside it, imported in `dialog/__init__.py` and bound as a
class attribute. A new dialog is a new module, one import line and one line in the class
body - nothing else registers it.

## Rules
- Dialog functions are `async` in both branches, even where the CLI branch would not need
  it: the browser branch always awaits `_wait_for_result()`.
- Every dialog that renders a box takes `image=None`, and `in_multiple=False` if it may
  appear inside `Dialog.multiple`. With `in_multiple=True` it returns its config dict
  instead of posting it.
- The `type` string in `js.self.postMessage` is the contract with the scriptor frontend.
  A new type that the frontend does not handle hangs the script forever in
  `_wait_for_result()`.
- Never call `js.self.postMessage` outside a dialog module (`message`, `progressbar` and
  `logger` are the pre-existing exceptions, each owning its own message type).

## Traps
- `Dialog.diff` is the **module** `viur.scriptor.dialog.diff`, not the function
  `show_diff`: `from .diff import show_diff` binds the submodule as `diff` in the package
  namespace, and `diff = diff` in the class body picks that up. `Dialog.diff(...)` raises
  `TypeError: 'module' object is not callable`. Call
  `viur.scriptor.dialog.diff.show_diff` instead. `Dialog.multiple` escapes the same trap
  only because the imported name equals the module name and overwrites it.
- `print` is shadowed: `viur/scriptor/__init__.py` rebinds it to `Dialog.print` in the
  Pyodide context only. In CLI scripts `print` stays the builtin.
- CLI branches block the whole process on `input()` or prompt_toolkit. No dialog anywhere
  has a timeout.

## See also
`runtime-split`, `dialog/select`, `dialog/multiple`, `dialog/table`
