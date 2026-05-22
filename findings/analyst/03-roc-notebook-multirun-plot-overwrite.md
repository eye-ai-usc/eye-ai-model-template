# `roc_analysis.ipynb` overwrites per-experiment plots when multiple runs share a `model_config`

**Persona:** Analyst
**Phase:** ROC analysis after a hyperparameter sweep
**Severity:** High (silent data loss; user sees one plot for N runs)
**Component:** deriva-ml-model-template (`notebooks/roc_analysis.ipynb` cells 18, 22; cell 20 also affected)

## What happened

The ROC analysis notebook compares two or more model executions by
loading their prediction-probability CSVs as assets and producing
per-experiment ROC curves and confusion-matrix JPEGs as output
assets of the analysis execution.

The per-experiment asset filename is keyed only on `exp['name']`:

```python
# notebooks/roc_analysis.ipynb cell 18
exp_name = exp.get('name', exp['asset_rid']).replace(' ', '_')
roc_path = execution.asset_file_path(
    MLAsset.execution_asset, f"roc_curves_{exp_name}.jpg", ExecAssetType.output_file
)
fig.savefig(roc_path, ...)

# notebooks/roc_analysis.ipynb cell 22
cm_path = execution.asset_file_path(
    MLAsset.execution_asset, f"confusion_matrix_{exp_name}.jpg", ExecAssetType.output_file
)
fig.savefig(cm_path, ...)
```

`exp['name']` is set from `Experiment.name`, which resolves to
`config_choices["model_config"]` (deriva-ml
`src/deriva_ml/experiment/experiment.py:194`). When the analyst points
the notebook at a *sweep* of one model — e.g. the bundled
`roc_lr_sweep` config that loads four `cifar10_quick` executions
varying only `learning_rate` — every loaded experiment has the same
`name` (`"cifar10_quick"`).

Result: each of the four sweep cells writes `roc_curves_cifar10_quick.jpg`
and `confusion_matrix_cifar10_quick.jpg` over the previous cell's
file. The catalog ends up with one ROC JPEG and one confusion-matrix
JPEG for four distinct runs. There is no error, no warning — the
user sees a single plot and concludes the sweep produced a single
result.

The CSV metrics table (cell 24) survives the collision because each
sweep cell is a separate row in the in-memory DataFrame, but the
visual artifacts collapse.

## Reproduction

1. After running an lr-sweep multirun
   (`uv run deriva-ml-run +experiment=cifar10_lr_sweep`), capture the
   four `prediction_probabilities.csv` asset RIDs.
2. Configure `src/configs/roc_analysis.py` (or use the bundled
   `roc_lr_sweep`) with all four asset RIDs.
3. Run `uv run deriva-ml-run-notebook notebooks/roc_analysis.ipynb
   assets=roc_lr_sweep`.
4. Inspect the analysis execution's output assets: only one
   `roc_curves_*.jpg` and one `confusion_matrix_*.jpg` exist
   (overwriting was silent).

## Impact on the persona's work

The Analyst persona's whole reason to run the ROC notebook against a
sweep is to *compare runs*. Three quarters of the comparison plots
are lost. The cross-experiment plot in cell 20
(`plt.show()` only — never saved as an asset) is the one visual that
*would* survive multirun, but it lives only in the notebook's
display output, not in the catalog. After upload-execution-outputs
runs and the analysis is shared by RID, the comparison is gone too.

## Cells affected

| Cell | What it does | Bug |
|---|---|---|
| 18 | Save per-experiment ROC JPEG | Filename keyed only on `exp_name` — collides when `model_config` repeats across sweep cells. |
| 20 | Cross-experiment micro-AUC comparison plot | `plt.show()` only; never saved as an asset. The most informative artifact for a sweep is the one that doesn't get persisted. |
| 22 | Save per-experiment confusion-matrix JPEG | Same collision as cell 18. |
| 24 | Save `roc_metrics.csv` | OK — the per-row `Experiment` field doesn't disambiguate, but `Execution_RID` is preserved. Adding an `Asset_RID` column would close the loop. |

## Suggested classification

Notebook bug, contained inside the model-template repo. No platform
fix needed. The notebook output-asset naming scheme needs to include
an identifier that is guaranteed unique per *loaded* experiment, not
just per *Hydra model_config*.

## Notes for the fix-pass

**Disambiguator choice:** the right primary key is `exp['asset_rid']`
— the prediction CSV's RID. It is short, guaranteed unique, available
on every experiment cell, and the resulting filename
(`roc_curves_cifar10_quick_<asset_rid>.jpg`) gives auditors a clean
link back to the input artifact.

A reasonable secondary disambiguator is the *producing*
execution_rid (`exp['experiment'].execution_rid`); use it if the
preferred semantics is "this artifact is *about* that run." For this
fix, asset_rid is enough — the notebook already prints both RIDs in
the loaded-experiments markdown summary so traceability is preserved.

Concrete patch:

- Cell 18: `f"roc_curves_{exp_name}_{exp['asset_rid']}.jpg"`.
- Cell 22: `f"confusion_matrix_{exp_name}_{exp['asset_rid']}.jpg"`.
- Cell 20: save the comparison figure as an asset too. The natural
  name is `roc_comparison_<analysis_execution_rid>.jpg`, since the
  comparison is an artifact of the analysis run itself (there's only
  one per execution).
- Cell 24: append an `Asset_RID` column to `metrics_df` so the CSV
  carries the same disambiguator the JPEGs do.

After this change the analysis execution emits 2N+2 image assets
(N per-experiment ROC, N per-experiment confusion matrix, one
comparison ROC, one metrics CSV) for N loaded experiments, and the
filenames are stable across re-runs against the same input asset
set (idempotent — re-running just overwrites the same files with
fresh bytes).
