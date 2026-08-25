---
covers: [viur.scriptor.dialog.open_file._open_file_dialog, viur.scriptor.dialog.open_file._FileExistsValidator]
status: accepted
---
## Seam
Private. The public entry is `File.open_dialog`, which forwards here. Browser:
`showOpenFilePicker` via `postMessage`, result wrapped with `File.from_bytes`. CLI: a
path prompt with completion and an existence validator, read with `open(..., 'rb')`.

## Rules
- Call `File.open_dialog`, not this function. It is prefixed with `_` because the `File`
  detour is what keeps both branches returning a `File`.
- `types` follows the browser `showOpenFilePicker` format
  (`[{"description": ..., "accept": {...}}]`).

## Traps
- A cancelled browser picker raises `RuntimeError("The user has cancelled the dialog.")`;
  the CLI branch has no cancel path at all.
- `types` is ignored on the CLI, `prompt` is ignored in the browser. Neither is an error.
- The CLI branch reads the whole file into memory before returning.

## See also
`../file`, `save-file`, `../dialog`
