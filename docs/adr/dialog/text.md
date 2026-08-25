---
covers: [viur.scriptor.dialog.text.text, viur.scriptor.dialog._validators._StringNotEmptyValidator]
status: accepted
---
## Seam
The generic string input, and the fallback the CLI `table` selection uses.
Browser: `postMessage(type="input")`, with `input_type="text"` added for `multiline`.
CLI: prompt_toolkit with `_StringNotEmptyValidator` unless `empty` is truthy.

## Rules
- `empty=True` is the only way to accept an empty string; the default rejects it on the
  CLI.
- `default_value` is stringified before it is sent.

## Traps
- The empty-string rule is enforced on the CLI only. The browser branch forwards `empty`
  to the frontend and trusts it.
- `multiline` on the CLI needs `[Esc]` then `[Enter]` to submit; the hint is printed, but
  only when `multiline` is set.
- `placeholder` reaches prompt_toolkit as-is and is not part of the result.

## See also
`../dialog`, `number`, `table`
