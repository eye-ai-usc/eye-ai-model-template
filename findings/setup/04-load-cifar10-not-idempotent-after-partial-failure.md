# `load-cifar10 --phase datasets` is not idempotent after partial failure

**Persona:** Phase 0 (bootstrap)
**Phase:** Catalog bootstrap — datasets phase re-run after fixing earlier finding
**Severity:** Medium (workable, but cost: lose the catalog and start over)
**Component:** deriva-ml-model-template (`src/scripts/_cifar10_datasets.py`) and/or deriva-ml (`Dataset.add_dataset_members`)

## What happened

After fixing findings 01–03 (`check_auth`, `include_tables` anchor,
include_tables feature-table name + row_per), the datasets phase
finally got far enough to call `split_dataset(...)` successfully. The
split selection logic ran, but the actual member-insertion into
`Dataset_Image` raised:

```
sqlalchemy.exc.IntegrityError: UNIQUE constraint failed:
Dataset_Image.Dataset, Dataset_Image.Image
[SQL: INSERT INTO "e2e-test-20260521"."Dataset_Image" ...]
```

Catalog 153 had already accumulated Dataset_Image rows from an
earlier (now-aborted) partial datasets-phase run. The current run
tried to insert the same (Dataset, Image) pairs again.

`load-cifar10 --help` advertises `--phase datasets` as a separate
phase ("'schema' is idempotent; 'images' uploads + features;
'datasets' creates the hierarchy"). The wording stops short of
claiming `datasets` itself is idempotent — but in a development
workflow where fixing prior findings *requires* re-running this
phase, the lack of idempotency turns every retry into a
"throw the catalog away" operation.

## Reproduction

1. Start a bootstrap that gets through asset upload but fails
   somewhere inside `create_dataset_hierarchy`.
2. Fix the cause of the failure.
3. Re-run with `--phase datasets`.
4. Observe `IntegrityError` on `Dataset_Image` if any
   `split_dataset` call partially populated the membership.

## Impact on the persona's work

Phase 0 ended up creating, partially populating, and abandoning
catalog 153 across several retry attempts. Each fix-and-rerun cycle
would otherwise require a fresh `--create-catalog` (and orphan the
prior one on the server). Routed around in this Phase 0 by deleting
catalog 153 and starting with a fresh catalog after collecting these
findings.

## Suggested classification

Bug (template script) and/or library polish. Two complementary
fixes:

1. **Script-level guard:** before adding members to a dataset that
   already has them, either check membership and skip duplicates, or
   delete-and-rewrite the membership. The "delete and rewrite"
   variant is safer when partition cardinalities have changed
   between runs.
2. **Library-level support:** `add_dataset_members` could grow an
   `on_conflict` parameter (`"error"` default, `"skip"`, `"replace"`)
   and surface it through `split_dataset`. The current default-error
   behaviour is correct as a default; what's missing is a clean way
   to opt into idempotency during script development.

## Notes for the fix-pass

- The `splits` dict (`labeled`, `small_labeled`, etc.) is the natural
  place to add an "is this already done?" check — if all expected
  dataset RIDs are present and populated, skip. The challenge: dataset
  RIDs are catalog-state-derived, not script-derived, so the check
  has to walk the catalog by *name* of the registered dataset_type.
- An alternative: make `load-cifar10 --phase datasets` always start
  by dropping any prior `e2e-test-*` datasets (whose name matches the
  current run) before recreating them. Heavy-handed but unambiguous.
- Worth noting that the test plan's Phase 0 procedure (`§6.2`)
  *does* anticipate this — step 1 already requires asking the user
  for delete-and-reuse confirmation when a prior catalog at the same
  name exists. So the workflow accommodates the lack of idempotency
  at the catalog level; what's friction-y is having to take that
  decision *inside* a single bootstrap attempt after a recoverable
  failure.
