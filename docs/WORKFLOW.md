# Workspace Workflow

Gold's five-fund research phase was closed on 2026-10-03 against the September 29
data checkpoint. Its commands below remain the maintenance and audit procedure.

Mesghal NAV source rechecks use `commodity/gold/investigate_mesghal_nav.py`.
The script archives evidence and emits an audit, without publishing canonical
NAV. See [the gold workflow](../commodity/gold/docs/WORKFLOW.md).

## Gold Ayar source transition — 2026-09-29

For a server run, use `python commodity/gold/refresh.py --fund ayar --collect`.
It requests recent TSETMC prices and recent Fipiran NAV, then rebuilds Ayar's
bubble. Use `--collect --full` periodically for older source revisions. To
collect all five active funds, run `collect_daily.py` for bounded prices and
`collect_fipiran_nav.py` for recent NAV, then `build_two_years.py`. Initial
loads fetch complete history automatically; TSETMC comparison NAV is optional
through `collect_daily.py --comparison-nav` and uses a complete request.


Collect Ayar Fipiran historical NAV with `commodity/gold/collect_fipiran_nav.py --fund ayar`
before rebuilding its two-year analysis and bubble. The Mofid raw history remains
preserved as prior source evidence. September 29 collection/rebuild succeeded,
with 448/465 two-year matches and 1,928 bubble rows. The prior TSETMC selection is superseded.

For reliability verification run `commodity/gold/audit_nav_reliability.py --live`
then `commodity/gold/audit_manager_nav.py --live`; omit `--live` for archived replay.
These audits preserve canonical sources and produce per-date validation flags.

Reviewed: 2026-09-28.

Start with the [repository README](../README.md), [status index](STATUS.md), and the
affected project's README, workflow, status, and local `AGENTS.md`. The root
`pyproject.toml` defines the shared environment; Asset Allocation and Economic USD
document independent environments and data contracts.

## Inspect, collect, and rebuild

For Copper, Zinc, Pellet, Rebar, Bitumen, and Pista, run from the repository root:

```powershell
python -m shared.certificate_pipeline.refresh all --plan
python -m shared.certificate_pipeline.refresh copper --plan --collect
python -m shared.certificate_pipeline.refresh copper
python -m shared.certificate_pipeline.refresh copper --collect
```

`--plan` only inspects steps. Default execution rebuilds from local inputs;
`--collect` explicitly runs collectors first. `all` selects all six products.
Pista's Abtahi workbook remains a manual input. The engine stops on failure and exports
a project's delivery CSV only after its builders succeed; the run is not a transaction
across all datasets. See the [engine contract](../shared/certificate_pipeline/README.md).

Gold uses `python commodity/gold/collect_daily.py` for daily source collection
of Ayar, Tala, Kahroba, Ganj, and Gohar. The existing Ayar bubble workflow uses
`python commodity/gold/refresh.py`, optionally with `--collect` and `--full`;
Mesghal historical NAV remains unresolved and its older evidence is retained.
`python commodity/gold/collect_fipiran_nav.py` collects recent NAV
for all five, and `python commodity/gold/build_two_years.py`
builds exact-date two-year analysis tables without filling missing NAV.
Silver uses `python commodity/silver/refresh.py` for offline rebuilding after inputs exist;
its scaffold checkpoint contains no collected data. Follow project workflows for Warehouse
Fees, Codal, options, Asset Allocation, and Economic USD. The Energy Exchange study and
global Copper / COCHILCO research are closed, with source evidence preserved.

## Preserve ownership

Only documented collectors refresh canonical raw CSVs, incrementally, idempotently,
and atomically. Source snapshots are immutable. Complete IME physical responses go into
the shared content-addressed archive; historical local snapshots remain frozen.
Commodity consumers reference shared FX directly. Keep canonical physical and certificate
records independent. Write analytical derivatives only under `data/interim` or
`data/processed`, using the physical, certificate, bubble, and analysis domains.
Delivery copies and presentation artifacts belong in `outputs` or `reports`.

## Validate and document

Run checks appropriate to the change. Root CI uses `python -m ruff check .` and
`python -m pytest -q`; Pista requires `python -m pytest -q goods/pista/tests`.
Independent projects supply their own test commands. Documentation edits require
link/path validation and `git diff --check`; they do not require source collection.

Record source coverage separately from derived coverage, retaining comparability warnings
and pending research decisions. Software delivery does not approve an economic benchmark.
Update the affected project README, workflow, and status when sources, schemas, paths,
formulas, counts, or stages change, and reconcile the workspace summary. Date documentation
reviews separately from data refreshes and test runs.

Inspect the diff and stage intended files explicitly before committing. Raw data, snapshots,
credentials, environments, logs, caches, and bulk outputs must remain outside Git.
