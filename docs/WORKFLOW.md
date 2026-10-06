# Workspace Workflow

## Asset Allocation: active four-fund notebook

Use `asset_allocation/notebooks/iran_reits_cross_asset_analysis.ipynb` for Kelid, Danik, Arzesh Maskan, and Kakh. With `PYTHONPATH=src` from `asset_allocation`, run `python -m asset_allocation.build_reit_assembly_reinvestment`, `python -m asset_allocation.build_reit_two_year_cumulative`, `python -m asset_allocation.build_reit_reinvested_correlations`, and `python -m asset_allocation.analyze_reit_usd_weekly_predictive` in that order. If a new complete housing month is available, run the Kilid collector, four-asset monthly panel builder, and housing two-year cumulative builder. Then run `python -m asset_allocation.analyze_reit_housing_monthly` before executing the notebook and report generator. Source collectors alone refresh canonical raw data; derivatives remain under `data/processed/analysis`.

REIT returns use compounded fractional units and raw traded closes. The approved-distribution ledger assumes immediate reinvestment at the first traded close on or after assembly; actual cash dates and missing payments remain unresolved. The notebook has five Plotly figures, including a common-sample 0–4-week USD lag curve, a two-lag predictive regression with HAC(4) joint tests and FDR-adjusted p-values, and a no-lag monthly correlation with Tehran housing. Kakh stays in return plots but lacks enough paired observations for these estimates. Earlier three-fund heatmaps and exchange-adjusted fund charts are historical derivatives, not the active workflow. See [the project workflow](../asset_allocation/docs/WORKFLOW.md) for run order, sample rules, and limitations.

To publish a local research artifact after these derivatives are current, run `python -m asset_allocation.build_reit_usd_report` from `asset_allocation` with `PYTHONPATH=src`. The self-contained interactive HTML is regenerated under `reports/`; the companion Markdown summary is versioned. This step reads processed tables only.

Gold's five-minute and daily/weekly systemd refresh units are versioned under
`commodity/gold/db`. Live readings replace an expiring cache; permanent source
collection and PostgreSQL daily loading remain separate scheduled jobs.
All three timers are enabled: live every five minutes only 12:00-18:00 Tehran,
daily source/DB refresh at 23:30 Tehran, weekly full reconciliation Sunday 03:30.

Gold database deployment and refresh are documented in
[the project database workflow](../commodity/gold/db/README.md). Git transfers
code and schema; raw CSVs and immutable snapshots require separate secure transfer.
The production checkout uses `/opt/empirical-economics-research` on a private deployment host;
the first database load and repeat-load verification succeeded on 2026-10-03.

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

```bash
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

Root CI runs `python -m ruff check .`, the root pytest suite, the dedicated Pista tests,
and the network-free Asset Allocation collector tests. Independent projects with local-data
contracts document additional validation commands in their own READMEs.
Documentation edits require link/path validation and `git diff --check`; they do not require
source collection.

Record source coverage separately from derived coverage, retaining comparability warnings
and pending research decisions. Software delivery does not approve an economic benchmark.
Update the affected project README, workflow, and status when sources, schemas, paths,
formulas, counts, or stages change, and reconcile the workspace summary. Date documentation
reviews separately from data refreshes and test runs.

Inspect the diff and stage intended files explicitly before committing. Raw data, snapshots,
credentials, environments, logs, caches, and bulk outputs must remain outside Git.
