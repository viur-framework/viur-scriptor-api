---
covers: [viur.scriptor.http_errors.HTTPException, viur.scriptor.http_errors.get_exception_by_code]
status: accepted
---
## Seam
`Modules.viur_request` maps a non-2xx status to a class via `get_exception_by_code` and
falls back to a bare `HTTPException`. Every instance carries the raw `response` (a
`WebResponse`, hence a `File`) alongside `status`, `name` and `descr`.

## Rules
- A new status needs both a subclass and an entry in the `get_exception_by_code` dict.
  The dict is the registry, not the class hierarchy.
- Subclass `__init__` takes `(descr, response)` only; status and name are fixed in the
  `super()` call. `viur_request` relies on that shape.
- Catch `HTTPException` for "any HTTP failure" and read `status`/`response` for the
  details.

## Traps
- `http_errors.NotImplemented` shadows the builtin `NotImplemented` inside the
  `viur.scriptor` namespace, because `__init__.py` does `from .http_errors import *` and
  `http_errors` defines no `__all__`. `from viur.scriptor import *` is unaffected - its
  `__all__` does not list it - but `viur.scriptor.NotImplemented` is the exception class.
- `str(exc)` is the description only; the status code is not part of the message.
- No 3xx is mapped, so a redirect that reaches the check raises a plain `HTTPException`.
- `response` is `None` whenever an exception is raised outside `viur_request`.

## See also
`module`, `file`
