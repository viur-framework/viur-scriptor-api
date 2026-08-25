---
covers: [viur.scriptor.dialog.print.print]
status: accepted
---
## Seam
The only dialog that is not async. Browser:
`postMessage(type="log", level="info")`. CLI: delegates to the builtin `print`, captured
as `_python_print` before the shadowing.

## Rules
- Inside the package, log through `Dialog.print` rather than the builtin - the browser has
  no stdout.

## Traps
- In the Pyodide context `viur/scriptor/__init__.py` rebinds the global name `print` to
  this function, so a script's plain `print` goes to the browser log. On the CLI the
  builtin stays in place. The `sep`, `end`, `file` and `flush` arguments are accepted but
  ignored in the browser branch.
- Everything is joined into one `str` and sent at level `info`; there is no way to raise
  the level here. Use `logger` for that.

## See also
`../dialog`, `../runtime-split`
