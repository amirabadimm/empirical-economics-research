# Workspace Architecture

## Purpose

This workspace supports reproducible empirical economics projects. Commodity studies share a
common architecture. The Iran Energy Exchange is a separate top-level domain with its own source
register, package boundary, and data contracts.

## Layout

```text
empirical-economics-research/
├── commodity/{bitumen,copper,pellet,zinc}/
├── energy_exchange/
├── shared/ime_data/
├── reports/{copper,zinc}/
├── docs/
└── .venv/                         # local only; never versioned
```

Each commodity project may contain `src/<commodity>`, `data/{raw,interim,processed}`,
`notebooks`, `tests`, `logs`, `outputs`, and `docs`. The existing local `Finenv` directory is
ignored; new clones should use `.venv`.

The Energy Exchange domain uses `energy_exchange/src/energy_exchange` for reusable domain logic
and `energy_exchange/references` for source-document provenance. Its logic must remain separate
from `shared/ime_data`, which is specific to the Iran Mercantile Exchange.

## Execution model

Commands are run from the repository root. Examples:

```powershell
python .\commodity\bitumen\src\bitumen\collectors\certificate.py
python .\commodity\bitumen\src\bitumen\collectors\physical.py
python .\commodity\copper\src\copper\processing\build_physical_benchmark.py
```

Collectors own raw-data persistence. Processing scripts read raw data and write only interim or
processed outputs. Notebooks may explore and visualize data but must not mutate canonical raw files.

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

## Validation checkpoints

At each project's latest documented checkpoint:

| Project | Certificate rows | Physical rows | Positive physical trades |
|---|---:|---:|---:|
| Bitumen | 257 | 47,085 | 24,163 |
| Copper | 246 | 1,163 | 1,154 |
| Iron-ore pellet | 246 | 3,446 | 1,592 |
| Zinc | 246 | 6,178 | 3,428 |

Zinc was refreshed and extended on 2026-08-10 to 252 certificate rows and 6,235 broad physical
rows. Its processed pipeline contains a 554-day 99.97/99.98 benchmark, two direct bubble series,
a 178-day primary certificate bubble with 41 exact anchors, and regression sensitivity outputs.
See [STATUS.md](STATUS.md) for the current state.
