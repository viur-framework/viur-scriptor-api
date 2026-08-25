---
covers: [viur.scriptor.dialog.select.select]
status: accepted
---
## Seam
The base of every choice in scriptor - `confirm` is built on it. Options may be a dict
(label -> value) or a list/tuple (label used as value). The user picks labels; the
function returns the mapped **values**. Browser: `postMessage(type="select")`. CLI:
`simple_term_menu.TerminalMenu`.

## Rules
- Dict values must not be `None` - asserted in the browser branch.
- With `multiselect=False` a `default_value` list may hold exactly one entry.
- The return type follows `multiselect`: a single value, or a list of values. It is never
  the label unless label and value coincide.

## Traps
- `None` entries in a list/tuple are dropped silently, so the returned selection can refer
  to a different index than the one the caller counted.
- `default_value` is honoured in the browser only; the CLI menu always starts at the first
  entry. `show_values` is browser-only as well.
- The CLI branch echoes the raw menu index with a debug `print` on every call.
- Search inside the menu is disabled on the CLI when `multiselect` is set.

## See also
`confirm`, `multiple`, `../dialog`
