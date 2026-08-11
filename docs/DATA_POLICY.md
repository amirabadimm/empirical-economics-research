# Data Policy

## Data classes

- **Raw source snapshots:** complete source responses; immutable, append-only, and auditable.
- **Canonical raw CSV:** standardized raw view refreshed only by a documented incremental,
  idempotent, and atomic collector.
- **Interim:** temporary cleaning, alignment, or joins that are not final analytical outputs.
- **Processed:** derived datasets reproducible from raw inputs and versioned code.
- **Outputs:** tables, figures, and reports; never treated as source data.
- **Notebooks:** exploration and presentation; production logic belongs under `src`.
- **Logs:** execution and error records; never stored inside raw-data directories.

## Integrity requirements

Raw snapshots must never be deleted, rewritten, or silently transformed. Any migration must verify
file counts, sizes, and hashes. Units, source dates, trade dates, retrieval timestamps, and source
URLs must not be guessed or removed without documentation. Canonical refreshes must validate schema,
identity, uniqueness, calendar conversion, and economically relevant numeric constraints before an
atomic replacement.

## Version-control policy

Raw data, source snapshots, local environments, credentials, logs, caches, and bulk generated data
remain local by default. This protects source licensing, prevents accidental secret disclosure, and
keeps Git history focused on research logic. Small fixtures, code, tests, documentation, reports, and
selected reproducible figures may be versioned.

Processed CSVs are also excluded by default even when small. A processed dataset may be published
only after documenting its source licence, construction method, schema, version, and citation. See
the repository-level [DATA_AVAILABILITY.md](../DATA_AVAILABILITY.md).
