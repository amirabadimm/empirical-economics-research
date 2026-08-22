# Iran Energy Exchange Research

This project is the documentation and research home for work related to the Iran Energy
Exchange (بورس انرژی ایران). It is intentionally separate from `commodity/` and
`shared/ime_data`, because energy-exchange sources, market structure, instruments, and
collection rules differ from those of the Iran Mercantile Exchange.

## Current stage

The project is in the documentation-intake and domain-mapping stage. No data source, schema,
collector, or analytical methodology has been approved yet.

## Where to add material

- Put original documents in `references/source_documents/`. Preserve the original filename and
  do not overwrite an existing file; add a dated or versioned copy instead.
- Record source metadata in `references/SOURCE_REGISTER.md` whenever a document is added.
- Put working summaries and terminology notes in `docs/notes/`.
- Record durable decisions in `docs/decisions/` rather than burying them in notebooks.
- Do not place credentials, tokens, or passwords anywhere in the project.

## Structure

```text
energy_exchange/
├── config/                       Non-secret project configuration
├── data/
│   ├── raw/                      Immutable canonical source data (local only)
│   ├── interim/                  Reproducible intermediate data (local only)
│   └── processed/                Reproducible analytical data (local only)
├── docs/
│   ├── decisions/                Architecture and methodology decisions
│   ├── notes/                    Working domain notes and document summaries
│   ├── STATUS.md                 Current stage and next actions
│   └── WORKFLOW.md               Data and research lifecycle
├── notebooks/                    Exploratory and analytical notebooks
├── outputs/                      Generated figures and presentation artifacts
├── references/
│   ├── source_documents/         Original regulations, manuals, and references
│   └── SOURCE_REGISTER.md        Provenance catalog for source documents
├── src/energy_exchange/          Energy-exchange-specific Python package
└── tests/                        Network-free tests
```

## Operating principles

Original documents and raw source snapshots are immutable. Automated collection must be
documented, incremental, idempotent, and atomic. Derived files belong only in `data/interim`
or `data/processed`. Generated outputs belong in `outputs/`. Any future credentials must be
read from environment variables.

See [`docs/WORKFLOW.md`](docs/WORKFLOW.md) for the intake workflow and
[`docs/STATUS.md`](docs/STATUS.md) for the current checkpoint.
