# Research Project Template

```text
<domain>/<name>/
├── README.md
├── AGENTS.md
├── src/<name>/{collectors,processing,analysis}/
├── data/raw/{physical,certificate}/
├── data/interim/
├── data/processed/{physical,certificate,bubble,analysis}/
├── notebooks/
├── tests/
├── logs/
├── outputs/{tables,figures,reports}/
└── docs/WORKFLOW.md
```

A collector writes only immutable snapshots and canonical raw data. Canonical raw files are
refreshed through documented atomic merges. Processing reads raw inputs and writes interim or
processed outputs. Physical and certificate source records remain separate; bubble outputs belong
only in `data/processed/bubble`. Analysis modules and notebooks must never mutate raw data.
Inputs shared by multiple projects belong under `shared/market_data` and `shared/data/raw`, not in
any individual project template.

Every public-facing project README should state the research question, economic motivation,
sources, sample coverage, measurement/identification strategy, main results, limitations,
reproduction commands, and data-availability conditions.

Documentation-first projects should also maintain a source register recording stable filename,
title, issuer, publication date, access date, origin, language, version, and notes. Original
source documents are immutable and interpretations belong in project notes or decision records.
