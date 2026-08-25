---
covers: [viur.scriptor.module_parts.BaseModule, viur.scriptor.module_parts.ExtendedModule, viur.scriptor.module_parts.ListModule, viur.scriptor.module_parts.TreeModule, viur.scriptor.module_parts.SingletonModule, viur.scriptor.module_parts.Method, viur.scriptor.module_parts.BaseModule.__getattr__, viur.scriptor.module_parts.ExtendedModule.list]
status: accepted
---
## Seam
Module objects are never built by hand. `Modules.get_module` picks the class from the
backend's `handler` string (`tree`/`hierarchy` -> `TreeModule`, `list` -> `ListModule`,
`singleton` -> `SingletonModule`) and wraps every server-side `@exposed` method in a
`Method`, registered with `register_route`. Those methods are reachable only through
`BaseModule.__getattr__`.

## Rules
- Never instantiate `ListModule`/`TreeModule`/`SingletonModule` yourself; without
  `parent` they cannot request anything.
- A new shared operation belongs in `BaseModule` (all three types) or `ExtendedModule`
  (list and tree only). Adding it to `ListModule` and `TreeModule` separately is how the
  duplicated wrapper methods came about.
- The subclass overrides exist to narrow the signature, not to add behaviour:
  `SingletonModule` without `key`, `TreeModule` with `skel_type`, `ListModule` with
  `group`. Keep that split - a `ListModule` must not expose `skel_type`.
- `list()` is an async generator: `async for`, or `gather_async_iterator`. `await
  module.list()` yields the generator object, not data.
- The batch size per request is `params["limit"]`. The `limit` argument only caps how
  many entries are yielded overall.

## Traps
- `BaseModule.__getattr__` raises `AttributeError` for anything not in `_routes`. A
  mistyped exposed-method name therefore looks like a Python attribute error and never
  reaches the server.
- `Method.__call__` sends every **keyword** argument as request params. Positional
  arguments land in `viur_request`'s `params` slot and are almost never what you want.
- `scriptor_renderer` is the one kwarg that is popped instead of sent.
- A `Method` with several verbs defaults to GET and re-dispatches through `_attr`; pick
  explicitly with `module.my_method.post(...)`.
- `TreeModule.for_each` does not `await list_root_nodes()`. Called without
  `root_node_key` it iterates a coroutine and fails - always pass `root_node_key`.
- `_cursor` lives on the shared module instance, so two concurrent `list()` runs on the
  same module overwrite each other's cursor.

## See also
`module`, `export-import`
