# Workspace Architecture

## Purpose

This workspace supports reproducible empirical economics projects. Commodity studies share a
common architecture. The Iran Energy Exchange and Codal issuer research are separate top-level
domains with their own package boundaries and data contracts.

## Layout

```text
empirical-economics-research/
├── commodity/{bitumen,copper,pellet,zinc}/
├── energy_exchange/
├── codal/national_copper/
├── shared/ime_data/
├── shared/market_data/
├── reports/{copper,zinc}/
├── docs/
└── .venv/                         # local only; never versioned
```

Each commodity project may contain `src/<commodity>`, `data/raw/{physical,certificate}`,
`data/interim`, and `data/processed/{physical,certificate,bubble,analysis}`,
`notebooks`, `tests`, `logs`, `outputs`, and `docs`. The existing local `Finenv` directory is
ignored; new clones should use `.venv`.

The Energy Exchange domain uses `energy_exchange/src/energy_exchange` for reusable domain logic
and `energy_exchange/references` for source-document provenance. Its logic must remain separate
from `shared/ime_data`, which is specific to the Iran Mercantile Exchange.

The Codal domain uses one independent project per listed issuer under `codal/<company>/`. Codal
disclosure collection must remain separate from both `shared/ime_data` and the Energy Exchange
package. Reusable Codal logic should be extracted only after a stable source contract exists. The
first issuer project is `codal/national_copper`.

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

## Validation checkpoints

At each project's latest documented checkpoint:

| Project | Certificate rows | Physical rows | Positive physical trades |
|---|---:|---:|---:|
| Bitumen | 257 | 47,085 | 24,163 |
| Copper | 266 | 1,171 | 1,162 |
| Iron-ore pellet | 252 | 3,467 | 1,606 |
| Steel rebar | 268 | 31,532 | not yet standardized |
| Zinc | 256 | 6,235 | 3,462 |

Zinc was refreshed and extended on 2026-08-10 to 252 certificate rows and 6,235 broad physical
rows. Its processed pipeline contains a 554-day 99.97/99.98 benchmark, two direct bubble series,
a 178-day primary certificate bubble with 41 exact anchors, and regression sensitivity outputs.
See [STATUS.md](STATUS.md) for the current state.
