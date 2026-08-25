---
covers: [viur.scriptor.dialog.table.table]
status: accepted
---
## Seam
Displays a table and optionally lets the user pick rows.
Browser: `postMessage(type="table")`, selection read back through `_wait_for_result()`.
CLI: a hand-formatted ASCII table plus a `Dialog.text` prompt for the indices.

## Rules
- `multiselect=True` implies `select=True`; the combination with `select=False` is
  rejected by an assertion.
- Cells must already be strings - the CLI branch measures them with `len()` and the
  browser branch hands them to the frontend unconverted. Use `File.from_table`'s
  `auto_str` route or `_utils.stringify` beforehand.

## Traps
- Return types differ: browser returns a list of indices when `select` is set and `None`
  otherwise; the CLI returns a list for `multiselect` but a bare `int` for single select.
- The CLI selection is parsed with `json.loads` and checked by assertions - malformed
  input raises `AssertionError` instead of re-prompting.
- The CLI adds an index column to `header` and `rows` when selecting, so the row data the
  user sees is not identical to what was passed in.

## See also
`../dialog`, `text`, `../file`
