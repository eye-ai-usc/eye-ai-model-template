# `split_dataset(include_tables=...)` now requires the anchor table

**Persona:** Phase 0 (bootstrap)
**Phase:** Catalog bootstrap — `load-cifar10` datasets phase
**Severity:** Blocker (blocks catalog bootstrap on `localhost`)
**Component:** deriva-ml-model-template (`src/scripts/_cifar10_datasets.py`) — drifted relative to deriva-ml denormalizer changes

## What happened

After the `check_auth` fix, asset upload completed and the datasets
phase started. `_cifar10_datasets.create_dataset_hierarchy` calls
`deriva_ml.dataset.split.split_dataset(...)` three times with
`element_table="Image"` and `include_tables=["Image_Classification"]`.
The new denormalizer rejects this:

```
deriva_ml.core.exceptions.DerivaMLDenormalizeUnrelatedAnchor:
Anchors of table(s) ['Image'] have no FK path to any table in
include_tables=['Image_Classification']. They would contribute
nothing to the output.
Options:
  • Remove these anchors from the anchor set.
  • Add ['Image'] (or a linking table) to include_tables.
  • Pass ignore_unrelated_anchors=True to silently drop them.
```

The library's own docstring example (deriva-ml `dataset/split.py`
lines 50, 63, 632, 647, 669, 695) now uses
`include_tables=["Image", "Image_Classification"]`. The template's
script was not updated.

## Reproduction

1. `cd /Users/carl/GitHub/DerivaML/deriva-ml-model-template`
2. With the `check_auth` patch from finding 01 applied:
   ```
   DERIVA_ML_ALLOW_DIRTY=true uv run load-cifar10 \
       --hostname localhost --catalog-id <freshly-created> --num-images 500
   ```
3. Wait through the asset-upload phase (~30s) — failure surfaces in
   the datasets phase at `_cifar10_datasets.py:317`.

## Impact on the persona's work

Blocker for catalog bootstrap, so blocker for the entire e2e test.
Routed around by changing the three call sites in
`_cifar10_datasets.py` to include `"Image"` in `include_tables`.

This is the second drift finding from the same script in a single
bootstrap run, which suggests `load-cifar10` is not exercised in CI
against the current sibling versions before each release. A smoke
job that bootstraps a fresh catalog against `main` of `deriva-ml`
would have caught both this and finding 01.

## Suggested classification

Bug + Doc gap. The denormalizer's exception message is actually
*good* (it lists exactly the fix options). But:

- The template needs to be updated for the new contract.
- It would help if `split_dataset` validated `include_tables` more
  proactively when `element_table` is given (i.e., the moment a
  caller passes `element_table="Image"` and "Image" isn't in
  `include_tables`, raise with the same helpful message
  *before* descending into the denormalizer call). The current
  failure surfaces deep in the denormalizer.
- Consider whether `split_dataset` should *auto-add* the
  `element_table` to `include_tables` when it's missing — the
  user is essentially saying "I know my anchor; please include
  what you need to honor it." Auto-add would shrink the surface
  area for this class of error. The trade-off is silent insertion
  of a table into a parameter the caller controlled, which
  surprises in the other direction.

## Notes for the fix-pass

- Three call sites in `_cifar10_datasets.py`: lines 326, 345, 358.
- After the fix, re-run the datasets phase against the same catalog
  (it's idempotent via `--phase datasets` per `load-cifar10 --help`)
  to confirm the rest of the hierarchy creates cleanly.
- This finding plus finding 01 should drive a tracking issue
  in the model-template repo titled "load-cifar10 drift vs current
  deriva-ml — add CI smoke job."
