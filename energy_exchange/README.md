# Iran Energy Exchange Research

This project is the documentation and research home for work related to the Iran Energy
Exchange (بورس انرژی ایران). It is intentionally separate from `commodity/` and
`shared/ime_data`, because energy-exchange sources, market structure, instruments, and
collection rules differ from those of the Iran Mercantile Exchange.

## Project conclusion

This project is closed after its feasibility assessment. The 2026-08-23 certificate snapshot
contains 21 symbols and 7,070 daily rows, but only 1,432 rows (20.25%) contain actual trades.
Activity is concentrated in renewable-production, capacity, and selected gas/electricity-saving
symbols; the broader registry is too sparse and concentrated for the intended market-wide
empirical project. No recurring collection or further Energy Exchange analysis is planned.

The evidence and reproducible collector are retained so this conclusion can be audited. See
`docs/CERTIFICATE_DATA.md` for the data contract and
`docs/decisions/0001-close-certificate-research.md` for the terminal decision.

## Where to add material

- The initial 66-document IRENEX corpus is held under `documents/` using normalized English
  filenames and eight role-based directories. Preserve file contents and record every rename or
  move in `references/DOCUMENT_FILE_MANIFEST.tsv`.
- For new acquisitions, use `references/source_documents/`. Preserve the original filename and do
  not overwrite an existing file; add a dated or versioned copy instead.
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
│   ├── DOCUMENT_TAXONOMY.md      Conceptual catalog of the document corpus
│   ├── decisions/                Architecture and methodology decisions
│   ├── notes/                    Working domain notes and document summaries
│   ├── STATUS.md                 Current stage and next actions
│   └── WORKFLOW.md               Data and research lifecycle
├── notebooks/                    Exploratory and analytical notebooks
├── outputs/                      Generated figures and presentation artifacts
├── documents/                    Role-based initial IRENEX document corpus
├── references/
│   ├── source_documents/         Original regulations, manuals, and references
│   ├── DOCUMENT_FILE_MANIFEST.tsv Original-to-professional filename mapping
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

The 66-document conceptual catalog and reading priorities are documented in
[`docs/DOCUMENT_TAXONOMY.md`](docs/DOCUMENT_TAXONOMY.md). It classifies sources by their role in
understanding the exchange rather than by file type or website structure.

The empirical access inventory, symbol counts, date coverage, and limitations are documented in
[`docs/notes/MARKET_ACCESS_INVENTORY.md`](docs/notes/MARKET_ACCESS_INVENTORY.md). A reusable prompt
for integrating these findings into external documentation is available in
[`docs/DOCUMENTATION_PROMPT.md`](docs/DOCUMENTATION_PROMPT.md).
