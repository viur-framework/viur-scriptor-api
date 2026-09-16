---
covers: [viur.scriptor._utils.clear_console, viur.scriptor._utils.prevent_close]
status: accepted
---
## Seam
Commands that change the script window itself rather than its content. Both are a bare
`js.self.postMessage(type=...)` with no `_wait_for_result()` behind it: the script keeps
running, the window reacts whenever it gets around to it. The `type` string is the whole
contract - the admin's Scriptor store (`vi-vue-components`, `store/scriptor.js`,
`handleMessage`) switches on it and owns the state that results.

## Rules
- A new window command is a dual-runtime `def` pair like every other one, see
  `runtime-split`. The CLI branch degrades to nothing or to a terminal equivalent, it
  never raises.
- Add the `type` to `handleMessage` in the admin **before** shipping the API function.
  Its `default` branch throws `Unknown event type`, so an unknown command does not fail
  silently, it breaks the window.
- Window state the script sets must be released by the window on `run_end` and on `err`,
  not only by the script. A script that crashes never gets to undo its own setting.
- Export the function in `__init__.py` **and** list it in `__all__`. Scripts see only what
  `from viur.scriptor import *` hands them.

## Traps
- Fire-and-forget: a returned `prevent_close()` means the message was posted, not that the
  window applied it. There is no acknowledgement and no way to read the flag back.
- `prevent_close` only guards the window's close button. Escape still minimizes and a
  click on the overlay is ignored outright - neither asks, because neither aborts.
- The protection dies with the run. Every new run starts unprotected, and `run_end`/`err`
  clear it, so a `prevent_close(False)` at the end of `main()` is tidiness, not a
  requirement.
- `clear_console(length)` is the number of entries that *survive*, not the number removed:
  the window truncates its message list to that length. The default `0` empties it.
- `clear_console` drops script output only. Installation and stdout lines from the
  environment live in a separate list in the store and stay visible.
- On the CLI `clear_console` shells out to `cls`/`clear` and ignores `length` entirely.

## Why not
Neither command uses the `Dialog` seam, although that is the other way to reach the
window: `Dialog` blocks on `_wait_for_result()` until the user answers, and both of these
have nothing to wait for. Making them blocking would stall a script on a window that is
not even open - a minimized window shows nothing and answers nothing.

## See also
`runtime-split`, `dialog`
