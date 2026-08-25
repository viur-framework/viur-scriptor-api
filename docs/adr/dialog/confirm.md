---
covers: [viur.scriptor.dialog.confirm.confirm]
status: accepted
---
## Seam
The only dialog with no runtime branch of its own: it builds a two-option `select` and
compares the result against the `yes` label. Change `select` and you change `confirm`.

## Rules
- `yes` and `no` must be distinct non-empty strings. They are used as both key and value
  of the options dict, so equal labels collapse to one option and `None` is rejected by
  `select`.

## Traps
- The return value is `result == yes`, so a frontend that returns anything unexpected
  reads as "No" rather than raising.

## See also
`select`, `../dialog`
