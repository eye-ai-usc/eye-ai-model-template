# Experiment Design Decisions

Decision log for the 2026-05-21 multi-persona e2e platform test.
Each persona appends entries in chronological order. Sections grow
top-to-bottom; do not insert above the Bootstrap entry.

---

## Bootstrap (Phase 0, 2026-05-21)

**What was created**

- Catalog `e2e-test-20260521` on `localhost`, catalog id **157**.
- CIFAR-10 domain schema via `load-cifar10`:
  - `Image` asset table — 500 rows, balanced 50 per class across all
    10 CIFAR-10 classes (airplane, automobile, bird, cat, deer, dog,
    frog, horse, ship, truck).
  - `Image_Class` vocabulary — 10 terms.
  - `Image_Classification` feature on `Image` (feature_table
    `Execution_Image_Image_Classification`) — 500 ground-truth
    feature values, one per image.
- **10 datasets** (out of 13 the script targets; 3 missing — see
  "Datasets the Curator inherits" below):
  - `86J` Complete (Complete + Labeled) — all 500 images
  - `86W` Split (parent of 874 + 87E)
  - `874` Training (Training + Labeled) — 250 images
  - `87E` Testing (Testing + Labeled) — 250 images
  - `87Y` Small split (sampled)
  - `886` Small training
  - `88G` Small testing
  - `B7Y` Labeled split (stratified 80/20 from training)
  - `B86` Labeled training (200 stratified samples of 874)
  - `B8G` Labeled testing (50 stratified samples of 874)
- Dev configs (`src/configs/dev/`) extended with
  `localhost_e2e_20260521` (catalog 157) and the 10 dataset names
  `*_e2e_20260521`.

**Invocation**

```
DERIVA_ML_ALLOW_DIRTY=true uv run load-cifar10 \
    --hostname localhost --create-catalog e2e-test-20260521 \
    --num-images 500
```

`--allow-dirty` was needed because Phase 0 had to patch four
template/library issues mid-bootstrap (see `findings/setup/`).

**Sibling versions at run-start**

- `deriva-ml`: v1.37.1 (ca593df1)
- `deriva-ml-mcp`: 976875e
- `deriva-mcp-core`: 376df57
- `deriva-skills`: 4f6af44
- `deriva-ml-skills`: v1.4.0 (9a3cfe9)

**Phase 0 findings (already captured)**

`findings/setup/01` through `findings/setup/05`. The five collectively
explain why `--allow-dirty` was needed and why one of the three
small_labeled splits failed to create:

1. `01-load-cifar10-check-auth-broken.md` — `DerivaML(check_auth=True)`
   no longer accepted; two call sites in `_cifar10_schema.py` patched.
2. `02-split-dataset-include-tables-must-list-anchor.md` —
   `include_tables=["Image_Classification"]` rejected by new
   denormalizer; must include the anchor table `"Image"`.
3. `03-include-tables-feature-name-vs-table-name.md` — even after
   adding `"Image"`, the *feature name* `"Image_Classification"` is
   not a table; must pass the feature-table name
   `"Execution_Image_Image_Classification"`.
4. `04-load-cifar10-not-idempotent-after-partial-failure.md` —
   `--phase datasets` re-runs after partial failure hit
   `UNIQUE constraint failed: Dataset_Image`.
5. `05-local-db-not-idempotent-on-second-denormalize.md` — second
   `split_dataset(...)` call against the same source dataset in one
   process raised `UNIQUE constraint failed: Dataset.RID` in local
   SQLite. This is the reason the small_labeled triplet is missing.

**Datasets the Curator inherits**

10 / 13 expected:
- ✓ Complete (`86J`), Split (`86W`), Training (`874`), Testing (`87E`)
- ✓ Small split (`87Y`), Small training (`886`), Small testing (`88G`)
- ✓ Stratified labeled split (`B7Y` parent, `B86` training,
  `B8G` testing)
- ✗ Small stratified labeled split — *missing because of finding 05*.
  This is a natural "Curator value-add" task: create a small stratified
  labeled split that downstream personas can use for quick training/eval
  iterations.

**Cross-channel verification status**

Direct deriva-ml inspection of catalog 157 confirmed (in this Phase 0):
- 500 Image rows, 500 Image_Classification feature values, balanced
  50-per-class distribution across all 10 classes.
- 10 datasets with correct types, descriptions, and split hierarchy.

The indirect channel (deriva MCP / skill tools) was not exercised in
Phase 0 because the orchestrator's MCP toolset does not include
deriva-ml MCP tools — verification will happen as part of each persona
arc with their own MCP-tool access.

---
