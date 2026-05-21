"""Localhost catalog 1407 dataset RIDs (cifar10_e2e schema, 200 images).

Loaded by `load-cifar10 --hostname localhost --create-catalog cifar10_e2e --num-images 200`.

These configs register names with a `_localhost` suffix that point at the
RIDs in catalog 1407. Select one at the CLI:

    uv run deriva-ml-run --host localhost --catalog 1407 \\
        +experiment=cifar10_quick datasets=cifar10_small_labeled_split_localhost \\
        dry_run=true

The default `datasets.py` configs still point at the seeded demo catalog (6)
RIDs (28DM, 28HJ, etc.) which do not exist in this catalog.
"""

from hydra_zen import store
from deriva_ml.dataset import DatasetSpecConfig
from deriva_ml.execution import with_description

datasets_store = store(group="datasets")

# -----------------------------------------------------------------------------
# Full datasets (200 images total, 100 train + 100 test)
# -----------------------------------------------------------------------------

datasets_store(
    with_description(
        [DatasetSpecConfig(rid="60A", version="0.2.0")],
        "Complete CIFAR-10 dataset on localhost catalog 1407 (200 images).",
    ),
    name="cifar10_complete_localhost",
)

datasets_store(
    with_description(
        [DatasetSpecConfig(rid="60M", version="0.4.0")],
        "Split dataset on localhost 1407 (100 train + 100 test, test unlabeled).",
    ),
    name="cifar10_split_localhost",
)

datasets_store(
    with_description(
        [DatasetSpecConfig(rid="60W", version="0.4.0")],
        "Training partition on localhost 1407 (100 labeled images).",
    ),
    name="cifar10_training_localhost",
)

datasets_store(
    with_description(
        [DatasetSpecConfig(rid="616", version="0.4.0")],
        "Testing partition on localhost 1407 (100 unlabeled images).",
    ),
    name="cifar10_testing_localhost",
)

# -----------------------------------------------------------------------------
# Small datasets (alias of full at this scale)
# -----------------------------------------------------------------------------

datasets_store(
    with_description(
        [DatasetSpecConfig(rid="61T", version="0.4.0")],
        "Small split on localhost 1407.",
    ),
    name="cifar10_small_split_localhost",
)

datasets_store(
    with_description(
        [DatasetSpecConfig(rid="622", version="0.4.0")],
        "Small training set on localhost 1407.",
    ),
    name="cifar10_small_training_localhost",
)

datasets_store(
    with_description(
        [DatasetSpecConfig(rid="62C", version="0.4.0")],
        "Small testing set on localhost 1407.",
    ),
    name="cifar10_small_testing_localhost",
)

# -----------------------------------------------------------------------------
# Labeled split datasets (both partitions labeled, full catalog scale)
# -----------------------------------------------------------------------------

datasets_store(
    with_description(
        [DatasetSpecConfig(rid="7AG", version="0.4.0")],
        "Labeled split on localhost 1407 (both partitions labeled).",
    ),
    name="cifar10_labeled_split_localhost",
)

datasets_store(
    with_description(
        [DatasetSpecConfig(rid="7AR", version="0.4.0")],
        "Labeled training partition on localhost 1407.",
    ),
    name="cifar10_labeled_training_localhost",
)

datasets_store(
    with_description(
        [DatasetSpecConfig(rid="7B2", version="0.4.0")],
        "Labeled testing partition on localhost 1407.",
    ),
    name="cifar10_labeled_testing_localhost",
)

# -----------------------------------------------------------------------------
# Small labeled datasets (alias of full labeled at this scale)
# -----------------------------------------------------------------------------

datasets_store(
    with_description(
        [DatasetSpecConfig(rid="7KE", version="0.4.0")],
        "Small labeled split on localhost 1407.",
    ),
    name="cifar10_small_labeled_split_localhost",
)

datasets_store(
    with_description(
        [DatasetSpecConfig(rid="7KP", version="0.4.0")],
        "Small labeled training set on localhost 1407.",
    ),
    name="cifar10_small_labeled_training_localhost",
)

datasets_store(
    with_description(
        [DatasetSpecConfig(rid="7M0", version="0.4.0")],
        "Small labeled testing set on localhost 1407.",
    ),
    name="cifar10_small_labeled_testing_localhost",
)

# -----------------------------------------------------------------------------
# E2E-2026-05-21 datasets (catalog 157, e2e-test-20260521 schema, 500 images)
# Created by Phase 0 of the multi-persona e2e test
# (docs/test-plans/2026-05-20-e2e-multipersona.md).
# -----------------------------------------------------------------------------

# Top-level datasets

datasets_store(
    with_description(
        [DatasetSpecConfig(rid="86J", version="0.1.0")],
        "Complete CIFAR-10 dataset on localhost 157 (500 images, all labeled).",
    ),
    name="cifar10_complete_e2e_20260521",
)

datasets_store(
    with_description(
        [DatasetSpecConfig(rid="86W", version="0.1.0")],
        "Train/Test split (parent) on localhost 157.",
    ),
    name="cifar10_split_e2e_20260521",
)

datasets_store(
    with_description(
        [DatasetSpecConfig(rid="874", version="0.1.0")],
        "Training partition on localhost 157 (250 labeled images).",
    ),
    name="cifar10_training_e2e_20260521",
)

datasets_store(
    with_description(
        [DatasetSpecConfig(rid="87E", version="0.1.0")],
        "Testing partition on localhost 157 (250 labeled images).",
    ),
    name="cifar10_testing_e2e_20260521",
)

# Small (sampled) datasets — both partitions ~500 each at this scale

datasets_store(
    with_description(
        [DatasetSpecConfig(rid="87Y", version="0.1.0")],
        "Small split on localhost 157 (sampled).",
    ),
    name="cifar10_small_split_e2e_20260521",
)

datasets_store(
    with_description(
        [DatasetSpecConfig(rid="886", version="0.1.0")],
        "Small training set on localhost 157.",
    ),
    name="cifar10_small_training_e2e_20260521",
)

datasets_store(
    with_description(
        [DatasetSpecConfig(rid="88G", version="0.1.0")],
        "Small testing set on localhost 157.",
    ),
    name="cifar10_small_testing_e2e_20260521",
)

# Stratified labeled split (B7Y parent, B86 training=200, B8G testing=50)

datasets_store(
    with_description(
        [DatasetSpecConfig(rid="B7Y", version="0.1.0")],
        "Stratified labeled split (80/20) on localhost 157 — both sides labeled.",
    ),
    name="cifar10_labeled_split_e2e_20260521",
)

datasets_store(
    with_description(
        [DatasetSpecConfig(rid="B86", version="0.1.0")],
        "Labeled training partition on localhost 157 (200 stratified samples).",
    ),
    name="cifar10_labeled_training_e2e_20260521",
)

datasets_store(
    with_description(
        [DatasetSpecConfig(rid="B8G", version="0.1.0")],
        "Labeled testing partition on localhost 157 (50 stratified samples).",
    ),
    name="cifar10_labeled_testing_e2e_20260521",
)

