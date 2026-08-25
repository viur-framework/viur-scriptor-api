---
covers: [viur.scriptor.dialog.diff.show_diff]
status: accepted
---
## Seam
The function is called `show_diff`, not `diff`. Browser:
`postMessage(type="diffcmp")`. CLI: prints `key: old -> new` per entry.

## Rules
- `diffs` is a list of `(key, old, new)` triples. The browser side renders them as given;
  no formatting happens here.

## Traps
- `Dialog.diff` is the module, not this function - see `../dialog`. Import
  `viur.scriptor.dialog.diff.show_diff` directly.
- Unlike `alert`, the browser branch does **not** await `_wait_for_result()`. The script
  runs on while the diff is still displayed.

## See also
`../dialog`
