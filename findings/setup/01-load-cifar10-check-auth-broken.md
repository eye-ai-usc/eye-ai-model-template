# load-cifar10 passes removed `check_auth=True` to DerivaML constructor

**Persona:** Phase 0 (bootstrap)
**Phase:** Catalog bootstrap via `uv run load-cifar10 --create-catalog ...`
**Severity:** Blocker (blocks every fresh-catalog test run)
**Component:** deriva-ml-model-template (`src/scripts/_cifar10_schema.py`) — drifted relative to deriva-ml v1.36.x

## What happened

Running the canonical bootstrap command:

```
uv run load-cifar10 --hostname localhost --create-catalog e2e-test-20260521 --num-images 500
```

The catalog itself was successfully created on the server (id=153,
schema=`e2e-test-20260521`). But immediately after the
"CREATED NEW CATALOG" banner, the script crashed:

```
File ".../src/scripts/_cifar10_schema.py", line 113, in create_or_connect_catalog
    ml = DerivaML(
        hostname=args.hostname,
        catalog_id=str(catalog_id),
        domain_schemas={domain_schema},
        check_auth=True,
    )
TypeError: DerivaML.__init__() got an unexpected keyword argument 'check_auth'
```

Inspecting `DerivaML.__init__` confirms `check_auth` is not in the signature:

```
(hostname, catalog_id, domain_schemas=None, default_schema=None,
 project_name=None, cache_dir=None, working_dir=None,
 hydra_runtime_output_dir=None, ml_schema='deriva-ml',
 logging_level=30, deriva_logging_level=30, credential=None,
 s3_bucket=None, use_minid=None, clean_execution_dir=True,
 mode=<ConnectionMode.online: 'online'>)
```

So `check_auth=True` was either renamed, removed, or never accepted —
the template's `_cifar10_schema.py` has drifted relative to the
installed `deriva-ml` (current sibling tip `ca593df1`).

`check_auth=True` appears in two places in the file (lines 117 and 134
— create path and connect path).

## Reproduction

1. `cd /Users/carl/GitHub/DerivaML/deriva-ml-model-template`
2. `uv sync`
3. `uv run load-cifar10 --hostname localhost --create-catalog any-name --num-images 50`
4. Observe the same `TypeError` after the "CREATED NEW CATALOG" banner.

The catalog object on the server is created before the failure, so
re-runs leave orphan catalog entries on `localhost` that need cleanup.

## Impact on the persona's work

Blocker for the entire e2e platform test — no catalog can be
bootstrapped, so no persona can start. Routed around by patching the
two call sites to drop the unsupported kwarg (see "Notes for the
fix-pass" — Phase 0 applied the workaround so the test could proceed).

This is exactly the kind of cross-channel drift the test exists to
surface: the template's script implicitly assumes a `deriva-ml` API
that the current `main` of `deriva-ml` does not provide.

## Suggested classification

Bug. Template is out of sync with deriva-ml; either the template's
`check_auth=True` should be removed (if the validation it requested
is now unconditional / happened elsewhere) or the corresponding
parameter restored on `DerivaML.__init__` if some callers still need
to gate auth at construct time.

## Notes for the fix-pass

- Two call sites in `src/scripts/_cifar10_schema.py`: line 117
  (create-catalog branch) and line 134 (connect-to-existing-catalog
  branch). Both must change in lockstep.
- Likely the auth check is now performed unconditionally inside
  `DerivaML.__init__` (or by `get_credential`), making the kwarg
  redundant — but verify that assumption before deleting; check
  whether removing it accidentally suppresses an error that should
  surface.
- Consider a `tests/test_load_cifar10_smoke.py` (or similar) that just
  constructs `DerivaML(...)` with the template's expected kwargs, so
  this drift is caught at CI rather than during e2e runs.
- The orphan catalog 153 from the failed first run was reused for the
  successful Phase 0 retry (after the patch), so no orphan was left
  on the server in this case — but it's worth thinking about
  exception-handling around the create path so the catalog isn't
  created if `DerivaML(...)` will fail immediately after.
