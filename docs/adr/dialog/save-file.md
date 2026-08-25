---
covers: [viur.scriptor.dialog.save_file._save_file_dialog, viur.scriptor.dialog._validators._FileDoesntExistsOrShouldBeReplacedValidator]
status: accepted
---
## Seam
Private. The public entries are `File.save_dialog` (ask the user where) and
`File.download` (write without asking). Browser: `showSaveFilePicker` plus a writable
stream, `bytes` go through `bytes_to_blob`. CLI: a path prompt, then `open(...)`.

## Rules
- Accepts `str` or `bytes` only; anything else raises `ValueError` on the CLI and an
  assertion in the browser.

## Traps
- The CLI overwrite protection is a trailing `!` on the filename, which is stripped before
  writing. A user who does not know that cannot overwrite an existing file.
- The `prompt` argument reaches the CLI branch only; the browser picker ignores it.
- A cancelled browser picker raises `RuntimeError`.

## See also
`../file`, `open-file`, `../dialog`
