# `include_tables=` requires the feature *table* name, not the feature *name* — docstring misleads

**Persona:** Phase 0 (bootstrap)
**Phase:** Catalog bootstrap — datasets phase via `split_dataset`
**Severity:** High (blocks bootstrap *and* will mislead the Analyst when they exercise denormalize)
**Component:** deriva-ml (`dataset/split.py` docstrings, `local_db/denormalizer.py` error messages) + deriva-ml-model-template (`_cifar10_datasets.py`)

## What happened

After fixing finding 02 (adding `"Image"` to `include_tables`) and
upgrading the venv to `deriva-ml v1.37.1` (so the auto-default for
`row_per` is present — see finding for sibling-sync issue below), the
datasets phase failed with:

```
DerivaMLException: The table Image_Classification doesn't exist.
```

Direct catalog inspection (no MCP indirection):

```
schemas: ['public', 'WWW', 'deriva-ml', 'e2e-test-20260521']
domain tables: ['Dataset_Image', 'Execution_Image_Image_Classification',
                'Image', 'Image_Asset_Type', 'Image_Class',
                'Image_Execution']
find_features('Image') →
  Feature(target_table=Image, feature_name=Image_Classification,
          feature_table=Execution_Image_Image_Classification)
```

The catalog *has* an `Image_Classification` feature — but its
`feature_table` is `Execution_Image_Image_Classification`. There is
no table named `Image_Classification`.

The denormalizer's `name_to_table()` resolves literal table names, so
`include_tables=["Image", "Image_Classification"]` fails because the
second string is a *feature* name, not a *table* name.

But the **library's own docstring** for `split_dataset` (in
`deriva-ml/src/deriva_ml/dataset/split.py`) shows
`include_tables=["Image", "Image_Classification"]` and
`include_tables=["Image", "Execution_Image_Image_Classification"]` as
*two different examples* (lines 632, 647, 658, 669, 695) without
clarifying which one is appropriate for which case. Anyone reading
the docstring would reasonably default to the cleaner-looking
`["Image", "Image_Classification"]` example.

## Reproduction

1. Catalog 153 (`e2e-test-20260521`), `--phase datasets` after asset
   upload completed.
2. With `_cifar10_datasets.py:326` reading
   `include_tables=["Image", "Image_Classification"]`, run
   `DERIVA_ML_ALLOW_DIRTY=true uv run load-cifar10 --hostname localhost
   --catalog-id 153 --phase datasets`.
3. Observe failure at `denormalize_planner.py:1664` (`name_to_table`).

## Impact on the persona's work

Blocker for Phase 0 datasets phase. Phase 0 routed around by
patching to `["Image", "Execution_Image_Image_Classification"]`.
The same trap awaits the Analyst — denormalize is on their critical
path (§3.4), and the natural call shape "I want the Image_Classification
labels with each Image" leads to the same bad string.

## Suggested classification

Doc gap + library polish:

- The split.py docstring examples should make the distinction loud:
  `include_tables` takes **catalog table names**, not feature names.
  When you want a feature's columns in the denormalized output you
  pass the *feature table* (`Execution_<target>_<feature_name>`),
  not the feature name itself.
- `name_to_table`'s error message — "The table X doesn't exist" — is
  technically accurate but unhelpful when the caller meant a feature
  name. The denormalizer (which knows about features) could catch
  this and re-raise with: "X is a feature on table Y; pass its
  feature_table (Execution_Y_X) instead." That single message
  would have saved this Phase 0 investigation.

## Notes for the fix-pass

- Three sites in `_cifar10_datasets.py` (326, 345, 358) and one
  stratify column at line 56 (`STRATIFY_COLUMN`). The stratify
  column still uses dot notation
  `Image_Classification.Image_Class` — verify that the dot-notation
  side resolves through the feature name (catalog of stratify
  conventions implies it does, since dot notation is column-level
  syntax, but worth double-checking once the include_tables fix lands).
- Cross-link this finding to the docstring examples — picking one of
  the two example shapes as the canonical one and removing the other
  would shrink the trap.
- File a sibling issue against `deriva-ml-skills`'
  `dataset-lifecycle` skill: the denormalize section should call this
  out by example.
