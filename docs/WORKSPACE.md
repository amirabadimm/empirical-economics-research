# Workspace Architecture

Gold's five-fund research phase is closed at the September 29 data checkpoint;
the documented incremental collectors and quality audits remain available for
maintenance. The 2026-10-03 closeout did not refresh source data.

Reviewed: 2026-09-28. See [STATUS.md](STATUS.md) for current checkpoints and
[WORKFLOW.md](WORKFLOW.md) for execution and review steps. Gold and Silver have their own
commodity domains and entry points outside the six-product certificate engine.
Gold now has five-fund daily price collection for Ayar, Tala, Kahroba, Ganj,
and Gohar, independent historical NAV collectors, and a two-year analysis build
alongside its Ayar bubble refresh. Mesghal's 2026-09-29 live recheck verifies
identity but still yields no accepted historical NAV; its archived evidence and
reproducible investigation remain separate from the active panel.
The September 29 gold reliability audit adds manager corroboration and per-date
quality flags. Ayar now selects Fipiran (448/465 two-year matches; 1,928 bubble rows); Gohar has
material disputed NAV and a unit-count change requiring explicit treatment.
The workspace also includes independent Asset Allocation and Economic USD projects and
the Ahrom options pipeline.

## Certificate execution engine

`shared/certificate_pipeline/refresh.py` orchestrates all six certificate products using
their local `pipeline.json` manifests. Product filters and valuation builders remain local.
Legacy project launchers delegate to the engine. Offline rebuild, source refresh, and
read-only plan inspection are explicit modes. See `shared/certificate_pipeline/README.md`.

## Purpose

This workspace supports reproducible empirical economics projects. Commodity studies share a
common architecture. The Iran Energy Exchange and Codal issuer research are separate top-level
domains with their own package boundaries and data contracts.

## Layout

```text
empirical-economics-research/
├── commodity/{bitumen,copper,gold,pellet,rebar,silver,warehouse_fees,zinc}/
├── goods/pista/
├── asset_allocation/
├── economic_usd/
├── options/
├── energy_exchange/
├── codal/national_copper/
├── shared/ime_data/
├── shared/market_data/
├── shared/certificate_pipeline/
├── shared/market_analysis/
├── shared/notebook_tools/
├── reports/{copper,zinc}/
├── docs/
└── .venv/                         # local only; never versioned
```

Shared infrastructure also includes `shared/market_analysis` and the content-addressed
`shared/data/raw/ime/physical` source archive. Full-market IME responses are stored once there;
commodity projects own only their filtered canonical physical CSVs and explicit scopes. Generic
I/O, as-of matching, and model selection are shared while research assumptions remain local.

Active commodity notebooks use the read-only helpers in `shared/notebook_tools`. Their common
dashboard contract covers source audit, physical/certificate activity and price panels, physical
goods composition, and visualization of existing validated bubble outputs. A notebook must never
create a missing bubble merely to satisfy the presentation pattern.

Each commodity project may contain `src/<commodity>`, `data/raw/{physical,certificate}`,
`data/interim`, and `data/processed/{physical,certificate,bubble,analysis}`,
`notebooks`, `tests`, `logs`, `outputs`, and `docs`. The existing local `Finenv` directory is
ignored. The workstation uses sibling `../Finenv`; new clones can use an isolated `.venv`.

The Energy Exchange domain uses `energy_exchange/src/energy_exchange` for reusable domain logic
and `energy_exchange/references` for source-document provenance. Its logic must remain separate
from `shared/ime_data`, which is specific to the Iran Mercantile Exchange.

The Codal domain uses one independent project per listed issuer under `codal/<company>/`. Codal
disclosure collection must remain separate from both `shared/ime_data` and the Energy Exchange
package. Reusable Codal logic should be extracted only after a stable source contract exists. The
first issuer project is `codal/national_copper`.

The `economic_usd/` domain is an independent macroeconomic data project. It retains its own raw and processed inputs and does not depend on the Housing or commodity project directory structures.

Power BI certificate/physical delivery files are project-local under `outputs/power_bi/<product>_certificate_physical_comparison.csv`. Analytical benchmark and valuation tables stay in `data/processed`; presentation CSVs stay in `outputs`. Each product with a comparison has a local `refresh_powerbi.cmd` and `refresh_powerbi.py`; no combined cross-product Power BI table is maintained. The launcher rebuilds from current local raw inputs, so source collectors must run first when new market data is required. Bitumen and pistachio retain their unapproved/provisional status labels.

The delivery schema is consistent across projects. `premium_discount_pct` equals
`100 * (certificate_price_irr_per_kg / physical_price_irr_per_kg - 1)`;
`comparability_status` and `physical_price_method` preserve research limitations.
Power BI users should filter those fields before comparing products. Certificate
volume remains in each source's units and must not be pooled across products.

## Execution model

Commands are run from the repository root. Examples:

```powershell
python .\commodity\bitumen\src\bitumen\collectors\certificate.py
python .\commodity\bitumen\src\bitumen\collectors\physical.py
python .\commodity\copper\src\copper\processing\build_physical_benchmark.py
```

Collectors own raw-data persistence. Processing scripts read raw data and write only interim or
processed outputs. Bubble/model tables belong under `processed/bubble`, never beside canonical
source records. Notebooks may explore and visualize data but must not mutate canonical raw files.
Cross-commodity inputs have one canonical owner under `shared/data/raw`; commodity-local copies
are prohibited.

## Architecture history

- 2026-08-03: the legacy `Cert` layer was replaced by independent commodity projects while raw
  files and snapshots were preserved unchanged.
- 2026-08-09: commodity projects moved from `projects/` to `commodity/`; shared collectors,
  reports, and raw data retained their content and provenance.
- 2026-08-11: public-facing metadata was reframed as a broader empirical-economics research
  portfolio capable of supporting energy and other applied-economics domains.
- 2026-08-22: the Iran Energy Exchange became a dedicated top-level project for documentation
  intake and domain mapping; the separately maintained housing project was removed from this
  workspace.
- 2026-08-24: a separate Codal domain was created, beginning with the National Iranian Copper
  Industries Company issuer project.
- 2026-08-29: commodity canonical physical and certificate CSVs were reaffirmed as independent
  raw datasets; physical, certificate-only, bubble/model, and other analysis outputs moved into
  separate processed-domain directories. Builders, notebooks, tests, and reports were migrated.
- 2026-08-29: duplicate Copper and Zinc USD/IRR ownership was consolidated into one shared TGJU
  collector and canonical series under `shared/market_data` and `shared/data/raw/fx`.

## Historical validation checkpoint (2026-09-19)

These counts describe the historical checkpoint, not current coverage:

| Project | Certificate rows | Physical rows | Positive physical trades |
|---|---:|---:|---:|
| Bitumen | 286 | 47,191 | 24,201 |
| Copper | 286 | 1,174 | 1,165 |
| Iron-ore pellet | 286 | 3,588 | 1,706 |
| Steel rebar | 286 | 31,953 | 16,968 |
| Zinc | 286 | 6,398 | 3,581 |

See [STATUS.md](STATUS.md) and each project's status for subsequent refreshes and current
research stages. Copper and Zinc each have 206 primary comparison dates through 2026-09-20
at their latest documented production checkpoints.
