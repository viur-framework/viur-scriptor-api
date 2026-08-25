---
covers: [viur.scriptor.dialog.alert.alert]
status: accepted
---
## Seam
Blocking notice. Browser: `postMessage(type="alert")` then `_wait_for_result()`. CLI:
`print` plus `input("Please press <Enter> to continue...")`.

## Rules
- Use `alert` only when the script must not continue before the user acknowledged. For a
  message that just informs, use `Message.send` (browser toast) or `Dialog.print`.

## Traps
- Returns `None` in both branches. A dismissed and a confirmed alert are indistinguishable.
- Has no `in_multiple`, so it cannot be embedded in `Dialog.multiple`.

## See also
`../dialog`, `raw-html`
