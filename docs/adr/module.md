---
covers: [viur.scriptor.module.Modules, viur.scriptor.module.Modules.viur_request, viur.scriptor.module.Modules.get_module, viur.scriptor.requests.WebRequest]
status: accepted
---
## Seam
`Modules.viur_request` is the only door to a ViUR backend. `module_parts`, `File.upload`
and `export_import` all go through it. New backend interaction hooks in here or on top of
it - never with a raw `WebRequest.request` against the ViUR host, because that skips skey
handling, renderer prefixing and the status-to-exception mapping.

## Rules
- Every write uses the pseudo-method `"SECURE_POST"`. It is not an HTTP verb:
  `viur_request` fetches `/skey` first, injects it into `params` and then sends a POST.
  A plain `"POST"` on a write route is rejected by the core.
- Do not prefix the url with a renderer. `viur_request` prepends `/{renderer}` or
  `/json`; passing `"/vi/..."` together with `renderer="vi"` yields `/vi/vi/...`.
- Do not construct `Modules` in a script. `viur.scriptor.modules` is the initialised
  singleton, filled by `_init_modules()`. A second instance is a second session.
- Failure is an exception, not a return value: any non-2xx raises the mapped
  `http_errors` class. Do not inspect the return value for error dicts.
- `raw=True` skips both the error mapping and the JSON decode and hands back the
  `WebResponse`. Use it only when you want the bytes (`File.from_url` does).

## Traps
- The Pyodide branch never logs in; it rides on the browser session cookie. `_session`
  stays `None` there, so `is_logged_in()` is permanently `False` in the browser. Do not
  gate script logic on it.
- In the CLI branch a request without cookies raises
  `RuntimeError("You need to log in.")` from the kwargs collector - not an HTTP 401.
- `get_module` returns `None` (not an error) for four iPython-internal names. A wrapper
  that reads `None` as "module missing" misreports.
- `get_module` caches the instance inside the backend's module dict, so repeated calls
  hand back the same object, including its `_cursor` state.
- Absolute urls (`http://`, `https://`, `//`) bypass base url and renderer completely.
- `Modules.init()` in the CLI branch prints the raw login response through
  `Dialog.print`. Keep credentials out of shared terminal logs.

## See also
`module-parts`, `file`, `http-errors`, `runtime-split`
