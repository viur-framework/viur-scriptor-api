---
covers: [viur.scriptor.dialog.multiple.multiple, viur.scriptor.dialog.select.select, viur.scriptor.dialog.text.text, viur.scriptor.dialog.number.number, viur.scriptor.dialog.date.date]
status: accepted
---
## Seam

`Dialog.multiple` (`viur.scriptor.dialog.multiple.multiple`) shows several
input fields in ONE dialog with one submit button. Prefer it over a chain of
single dialogs whenever a script asks for more than one related value - a
setup or configuration step: one submit instead of one dialog round-trip per
field, and the user sees and corrects the whole block before sending.

Build each field by calling the component dialog with `in_multiple=True` -
`Dialog.text`, `Dialog.number`, `Dialog.select` and `Dialog.date` then return
their component config instead of showing anything. Pass the configs as a
`dict[str, dict]` keyed by field name; the answers come back as a dict with
the same keys (a `list` mirrors as a `list`). `reuse=True` skips re-sending
the definitions when the identical dialog is shown again in a loop.

## Rules

- Browser only. In CLI mode (`viur script run`) `multiple` is a stub that
  returns `components` unchanged, and its signature does not even have
  `send_button_text`. Branch on `is_pyodide_context()` and ask the same
  fields as sequential single dialogs there.
- The frontend must implement the `multiple-dialog` message type. Verified
  live with the scriptor bundled in vi-admin 4.14.8 (2026-08-25).

## Traps

- A select inside `multiple` answers with the LABEL (the key of the choices
  dict). A standalone `Dialog.select` answers with the VALUE: `select` maps
  `choices[result]` itself, while `multiple` passes the frontend answer
  through unexamined. Map labels back to values in the script - or accept
  both, if one evaluation serves the block path and the CLI path.
- Pre-selecting a select works by LABEL, not by value: the frontend compares
  `default_value` against the keys of `choices`. Passing the value selects
  nothing (measured 2026-08-25).
- In the standalone browser select, `default_value` must be a string, not a
  list: unlike `choices` it is not converted with `pyodide.ffi.to_js`, and a
  list aborts the `postMessage` with `DataCloneError` (measured 2026-08-25).
- The docstrings of `text`, `number` and `date` call `in_multiple` "just for
  testing purposes". It is not: it is the only way to build components for
  `Dialog.multiple`.
- The passthrough also skips per-component post-processing: a standalone
  `Dialog.date` converts the frontend timestamp to `datetime`; inside
  `multiple` the raw frontend value arrives.
