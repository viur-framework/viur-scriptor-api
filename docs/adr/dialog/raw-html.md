---
covers: [viur.scriptor.dialog.raw_html.raw_html]
status: accepted
---
## Seam
Sends an HTML string to the frontend for unescaped rendering
(`postMessage(type="raw_html")`). The CLI branch prints the markup verbatim.

## Rules
- **Never pass unsanitised data here.** Backend content, user input and anything read
  from a file end up in the browser DOM as markup. Build the string from literals and
  escape everything interpolated into it.

## Traps
- The CLI branch does not await a result, the browser branch does - a script that pauses
  in the browser runs straight through on the CLI.

## See also
`../dialog`, `multiple`
