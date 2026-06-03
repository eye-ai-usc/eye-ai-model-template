"""DerivaML Connection Configuration.

Configuration Group: ``deriva_ml``

This group specifies which Deriva catalog to connect to.

The shipped ``default_deriva`` is a **placeholder** — it points at no catalog
in particular. Edit it for your environment, or override at the CLI:

    deriva-ml-run --host <hostname> --catalog <id> ...

For multi-environment work, register additional configs (one per host/catalog)
in ``src/configs/dev/deriva.py`` and select with
``deriva_ml=<name>``.
"""

from hydra_zen import store
from deriva_ml import DerivaMLConfig

deriva_store = store(group="deriva_ml")

# REQUIRED: ``default_deriva`` is used when no connection is specified.
# Points at the production EyeAI catalog. Override at the CLI with
# --host/--catalog, or select ``deriva_ml=localhost`` for local development.
deriva_store(
    DerivaMLConfig,
    name="default_deriva",
    hostname="www.eye-ai.org",
    catalog_id="eye-ai",
    zen_meta={
        "description": "Production EyeAI catalog at www.eye-ai.org."
    },
)

# Local development catalog. Select with ``deriva_ml=localhost``.
deriva_store(
    DerivaMLConfig,
    name="localhost",
    hostname="localhost",
    catalog_id=2,  # placeholder — set to your local catalog ID
    use_minid=False,
    zen_meta={
        "description": "Local development catalog on localhost."
    },
)
