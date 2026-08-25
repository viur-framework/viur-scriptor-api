---
covers: [viur.scriptor.dialog.date.date]
status: accepted
---
## Seam
`postMessage(type="input", input_type="date")` in the browser, a prompt_toolkit prompt
with an ISO validator on the CLI. `use_time` switches between `datetime.date` and
`datetime.datetime`.

## Rules
- `default_value` may be a `datetime.date`, a `datetime.datetime` or an ISO string;
  anything else raises `ValueError` before the dialog is shown.

## Traps
- The browser returns either an ISO string or epoch **milliseconds**. The millisecond path
  is read as UTC and then has `tzinfo` stripped - the result is naive, not local time.
- The CLI branch validates with `datetime.datetime.fromisoformat` regardless of
  `use_time`, so a plain date is accepted for a datetime prompt and gets midnight.

## See also
`../dialog`, `number`
