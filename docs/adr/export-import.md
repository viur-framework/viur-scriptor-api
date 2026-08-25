---
covers: [viur.scriptor.export_import.import_from_table, viur.scriptor.export_import._generate_extraction_strategy, viur.scriptor.export_import._get_pre_extraction_converter, viur.scriptor.export_import.export_module, viur.scriptor.export_import.export_to_table]
status: accepted
---
## Seam
Bone type -> extractor factory. Import runs in two passes: **pre-extraction** folds the
flat table columns back into per-bone structures, **extraction** turns each bone value
into the flat params the backend's `edit`/`add` expects. A new bone type hooks into
`_generate_extraction_strategy`, plus `_get_pre_extraction_converter` when its column
layout differs. `export_import` is not re-exported from `viur.scriptor` - import it as
`viur.scriptor.export_import`.

## Rules
- The structure must be rendered by the `vi` renderer. `import_from_table` fetches it that
  way when `structure` is omitted; a json-rendered structure lacks the `multiple`,
  `languages` and `type` fields every strategy reads.
- A plain new bone type goes into `_extractable_with_default_strategy_types`, a family
  into `_extractable_with_default_strategy_type_prefixes`. The trailing dot in the
  prefixes is load-bearing: `"str."` must not match a bone type merely starting with
  `str`.
- An unknown bone type raises `NotImplementedError` while the strategy is built, before a
  single record is written. Keep it that way - silently skipping a bone loses data.
- The callbacks (`progress_callback`, `query_params_callback`, `server_result_callback`,
  `exception_callback`) are the sanctioned way to observe a run; `dry_run=True` performs
  everything except the write.

## Traps
- Per-record exceptions are swallowed into `exception_callback` and the run continues.
  Without that callback a half-failed import looks successful.
- `import_from_table` consumes the iterable: it pulls the first row to derive the base
  keys and chains it back. A generator handed in twice is empty the second time.
- `TreeModule` imports need `tree_skel_type`, and the exported `parententry` column is
  renamed to `node` by `_extractor_for_renamed_simple_bones`. Do not rename it yourself.
- The `dummy` fallback in the relational/record extractors yields the literal string
  `"NOT IMPLEMENTED"` as the bone value - it writes that into the database instead of
  raising.
- `export_module` collects all records in memory before building the file.
- `filter_module_structure_with_withelist` is misspelled but public; scripts depend on the
  name.

## See also
`module-parts`, `file`, `module`
