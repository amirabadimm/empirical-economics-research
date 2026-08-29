# Commodity Data Architecture

Last updated: 2026-08-29

Every commodity project uses the same separation of source records and derived analysis:

```text
data/
  raw/
    physical/<commodity>_physical_raw.csv
    certificate/<commodity>_certificate_raw.csv
  interim/
  processed/
    physical/<approved physical tables>.csv
    certificate/<derived certificate-only tables>.csv
    bubble/<derived comparison and model tables>.csv
    analysis/<other derived analytical tables>.csv
```

The two canonical raw CSVs are independent source datasets. Collectors retain the full documented
commodity scope, including zero-trade observations, and may not apply a later analytical basket.
Snapshots are immutable. Filters, cleaning, aggregation, calendar alignment, and unit conversion
belong only in reproducible builders that write outside `data/raw`.

A bubble CSV is always derived and must live under `data/processed/bubble`. It may carry the
prices and source dates required to reconstruct its formula, but it is never the canonical store
for certificate or physical records. A project must be able to rebuild every bubble after reading
its separate canonical certificate CSV, canonical physical CSV, and any documented external
inputs. Notebooks never write or repair canonical raw data.

External market inputs used by more than one project have one workspace owner:

```text
shared/
  ime_data/                    # shared IME collector and snapshot ownership
  market_data/                 # shared FX/LME collector and validation logic
  market_analysis/             # shared analysis primitives and model engines
  data/raw/fx/usd_to_rial.csv  # single canonical USD/IRR series
  data/raw/ime/physical/       # content-addressed full-market IME responses
```

Commodity projects reference this canonical path directly. They must not seed, copy, or refresh
project-local FX files. The shared collector owns incremental refresh and immutable TGJU pages.

New complete IME physical responses are stored once by SHA-256 under
`shared/data/raw/ime/physical`. Commodity raw CSVs remain separate filtered canonical datasets.
Pre-consolidation project-local snapshots remain immutable evidence and rebuild inputs, but new
collection never extends those local archives.

Shared analysis owns only commodity-invariant mechanics. Product definitions, filters, units, and
benchmark choices remain explicit inside each commodity project.
