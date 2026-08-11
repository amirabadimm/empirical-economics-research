# Workflow — IME warehouse and assessment fees

## Data flow

1. `collect_current.py` downloads the current official IME table, writes a
   content-addressed immutable HTML snapshot, then atomically refreshes the raw CSV.
2. `collect_wayback.py` stores an immutable CDX inventory of archived official pages.
3. Audited official notices are represented in `warehouse_fee_events.csv`; archived
   table observations are represented in `historical_page_observations.csv`.
4. `build_daily.py` validates those inputs, resolves same-day precedence in favour of
   exact official notices, carries each documented state forward, and atomically writes
   `warehouse_fees_daily.csv`.
5. Tests verify the output schema, `(date, commodity)` uniqueness, basic coverage, and
   known bitumen/pellet transitions.

```text
Official IME / Wayback
        │
        ▼
data/raw/warehouse_fees/       immutable source snapshots
        │
        ▼
data/interim/                  audited events and observations
        │
        ▼
build_daily.py
        │
        ▼
data/processed/warehouse_fees_daily.csv
```

## Interpretation

Tariffs are event data, not daily publications. A documented tariff is carried forward
until the next documented state. The builder never backfills dates before the first
officially recoverable record for a commodity.

An archived-page timestamp establishes only that a value was visible on that date. Such
boundaries are labelled `first_observed`; they are not presented as exact effective dates.
Unknown assessment fees remain blank and are labelled `not_recovered`. A numeric zero is
used only when the official evidence supports zero or no separate fixed fee.

## Storage policy

- Raw snapshots are immutable and never overwritten or transformed in place.
- The current raw CSV is refreshed only by its collector, using an atomic replacement.
- Derived files belong only in `data/interim` or `data/processed`.
- The canonical processed directory contains one consumer-facing CSV.
