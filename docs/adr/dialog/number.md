---
covers: [viur.scriptor.dialog.number.number]
status: accepted
---
## Seam
`postMessage(type="input", input_type="number")` in the browser, a prompt_toolkit prompt
with a `float`-convertibility validator on the CLI.

## Rules
- `default_value` must be convertible with `float`, otherwise `ValueError` is raised
  before the dialog is shown. It is sent as a string.

## Traps
- The return types differ between contexts: the CLI branch converts to `int` when
  possible and falls back to `float`; the browser branch returns whatever the frontend
  sends, unconverted. Cast explicitly if the type matters.

## See also
`../dialog`, `text`, `date`
