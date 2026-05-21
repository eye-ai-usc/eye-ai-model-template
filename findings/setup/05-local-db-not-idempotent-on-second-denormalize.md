# `_populate_from_catalog_inner` not idempotent — second denormalize of same dataset in one session

**Persona:** Phase 0 (bootstrap)
**Phase:** Catalog bootstrap — second `split_dataset()` call against the same source dataset
**Severity:** High (library-level; blocks any workflow that calls denormalize twice for the same dataset in one process)
**Component:** deriva-ml (`local_db/denormalize.py:458` → `local_db/denormalize.py:487` → `paged_fetcher.py:217`)

## What happened

After fixing findings 01–04, a fresh `load-cifar10` against a brand
new catalog (no prior local cache) created:

- Schema, vocab, feature ✓
- 500 image assets uploaded ✓
- Ground-truth `Image_Classification` feature values ✓
- `Complete`/`Split`/`Training`/`Testing` datasets ✓
- `Small_Training`/`Small_Testing` random samples ✓
- First `split_dataset(...)` for the labeled split (`B7Y` parent,
  `B86` training, `B8G` testing) ✓ — denormalize ran, dataframe was
  produced, members were inserted.

Then the second `split_dataset(...)` call (`small_labeled`, also
sourced from the same `training` dataset RID `874`) failed during its
own denormalize step with:

```
sqlite3.IntegrityError: UNIQUE constraint failed: Dataset.RID
[SQL: INSERT INTO "deriva-ml"."Dataset" ("RID", "RCT", "RMT", "RCB",
       "RMB", "Description", "Deleted", "Version")
       VALUES (?, ?, ?, ?, ?, ?, ?, ?)]
[parameters: ('874', ..., 'CIFAR-10 training set with 50,000 labeled
              images', ...)]
```

The traceback chain:

```
_cifar10_datasets.py:351  split_dataset(...)
  dataset/split.py:820     source_ds.get_denormalized_as_dataframe(...)
    dataset/dataset.py:1613 Denormalizer(...).as_dataframe(...)
      local_db/denormalizer.py:426
        local_db/denormalize.py:_denormalize_impl
          local_db/denormalize.py:458 _populate_from_catalog
            local_db/denormalize.py:487 fetch_by_rids(table="deriva-ml:Dataset", ...)
              local_db/paged_fetcher.py:217 _insert_rows
                ↳ INSERT into Dataset RID=874  ← already exists from prior call
```

The local SQLite cache for catalog 157 (its workspace under
`~/.deriva-ml/localhost/157/`) was populated with RID 874 the first
time the parent training dataset was denormalized. The second call
within the *same process* tries to re-populate it instead of either
(a) skipping it because it's already there, or (b) using upsert /
`INSERT OR REPLACE`.

This is purely a within-session issue — the local-db idempotency
between sessions appears to be different (the file persists, but a
fresh DerivaML instance would presumably check `working` state on
init). The two calls happen in the same process, against the same
`DerivaML` object, sharing one workspace.

## Reproduction

1. Fresh catalog with the `_cifar10_schema.py` and
   `_cifar10_datasets.py` fixes from findings 01–04 applied.
2. `DERIVA_ML_ALLOW_DIRTY=true uv run load-cifar10 --hostname localhost
   --create-catalog any-name --num-images 500`.
3. After the first `split_dataset(...)` completes (look for `B7Y`,
   `B86`, `B8G` RIDs assigned to `labeled_split` /
   `labeled_training` / `labeled_testing`), the second call against
   the same source dataset (`training`, RID `874`) raises
   `IntegrityError: UNIQUE constraint failed: Dataset.RID`.

A minimal repro (no `load-cifar10`):

```python
from deriva_ml import DerivaML
ml = DerivaML(hostname="localhost", catalog_id="157",
              domain_schemas={"e2e-test-20260521"})
src = ml.lookup_dataset("874")
src.get_denormalized_as_dataframe(
    ["Image", "Execution_Image_Image_Classification"],
    row_per="Execution_Image_Image_Classification",
)  # works
src.get_denormalized_as_dataframe(
    ["Image", "Execution_Image_Image_Classification"],
    row_per="Execution_Image_Image_Classification",
)  # fails: UNIQUE constraint Dataset.RID
```

## Impact on the persona's work

Blocked `small_labeled` dataset creation in Phase 0. Phase 0 ended
with 10 datasets present out of 13 expected. The missing slot
(`small_labeled_split`/`_training`/`_testing`) was left for the
Curator persona to create or skip — turning a Phase 0 blocker into a
Curator opportunity in keeping with §6 ("add value on top of the
bootstrap").

Also relevant to: anyone running multiple training experiments in
one process against the same dataset RID. The denormalizer caches
behave like a first-call-wins state machine — subsequent calls
explode rather than reusing.

## Suggested classification

Bug (library, `deriva-ml`). The local-db population path needs
either:

- **Upsert semantics:** `INSERT OR REPLACE INTO Dataset` (and the
  same for any other tables the inner populate hits). Simple and
  correct.
- **Skip-if-present:** check existence before INSERT (or wrap in a
  per-row `try/except IntegrityError`). Less efficient but easier to
  audit.
- **Session-level state tracking:** `Denormalizer` remembers which
  dataset RIDs have already been hydrated this session and short-
  circuits the populate call. Cleanest but largest change.

## Notes for the fix-pass

- The repro above is the minimum failing test. A regression test
  that calls `get_denormalized_as_dataframe` twice on the same
  dataset in one process and asserts both calls return non-empty
  DataFrames would cover this.
- Worth checking whether *single*-call denormalize against a dataset
  whose local-db file already has rows from a prior session works
  correctly — if it does (because of some "is already populated"
  short-circuit at the outer level), then the second-call bug is
  inside a path that bypasses that check. If it doesn't, this is a
  symptom of a deeper "populate is never idempotent" issue.
- Pair with finding 04: both are about the local layer not coping
  with re-entry. May share a root cause.
