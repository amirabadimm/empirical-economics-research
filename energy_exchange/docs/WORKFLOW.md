# Energy Exchange Research Workflow

Last reviewed: 2026-08-23

## Objective and disposition

This workflow records the completed feasibility assessment of the Iran Energy Exchange. It mapped
public sources and market domains, organized the regulatory corpus, and implemented an auditable
certificate collector to determine whether a broader empirical project was justified. The answer
was negative at the market-wide level, and active research ended on 2026-08-23.

## Documentation intake

The initial IRENEX corpus retains its original contents under normalized English filenames in
eight role-based subdirectories of `documents/`. It is cataloged in
[`DOCUMENT_TAXONOMY.md`](DOCUMENT_TAXONOMY.md), and every original-to-current path is recorded in
[`../references/DOCUMENT_FILE_MANIFEST.tsv`](../references/DOCUMENT_FILE_MANIFEST.tsv). Secondary
classifications use tags; do not create duplicated source copies. For subsequent intake:

1. Save each newly acquired original file unchanged in `references/source_documents/` and record
   its acquired filename before assigning any normalized working filename.
2. Add one row to `references/SOURCE_REGISTER.md`, including provenance and access date.
3. Write interpretation or extracted structure in `docs/notes/`; do not modify the source file.
4. Record consequential scope, schema, or methodology choices in `docs/decisions/`.
5. Update this workflow, the project README, and `docs/STATUS.md` when the source set, schema,
   paths, formulas, observation counts, or project stage changes.

Classify each source by its primary analytical role and cross-cutting tags, not merely its file
type, publisher, or website section. Record amendment and implementation relationships explicitly.
Never infer that a document is current or superseded from its filename alone.

## Planned data lifecycle

- `data/raw`: immutable canonical files and source snapshots; collectors only.
- `data/interim`: normalized or joined reproducible tables.
- `data/processed`: analysis-ready outputs with documented definitions.
- `notebooks`: exploration and communication, never canonical data mutation.
- `outputs`: generated figures and presentation material.

Before a collector is introduced, its source contract must document endpoint or publication,
field meanings, units, identifiers, calendars, revisions, pagination, validation, and failure
behavior. Writes must be incremental, idempotent, and atomic.

## Public-market data checkpoint

Read-only reconnaissance on 2026-08-22 established public access to physical-auction lists and
details, electricity offers and selected trade feeds, certificate histories, and derivative
histories. The observed inventory contains 21 certificate symbols and 71 derivative symbols.
Certificate history begins on 2019-04-17, observed salaf history on 2016-02-09, observed futures
history on 2023-05-31, and individually addressable physical auctions on 2013-07-31. Full results,
limitations, and row counts are recorded in
[`notes/MARKET_ACCESS_INVENTORY.md`](notes/MARKET_ACCESS_INVENTORY.md).

## Collector sequence assessed

1. Build and validate a canonical instrument registry without downloading full histories.
2. Archive immutable instrument metadata and daily history responses for certificates.
3. The remaining proposed stages—derivatives, physical-auction backfill, electricity monitoring,
   normalization, and analytical tables—were cancelled after the certificate feasibility result.

Collectors must serialize requests or use low bounded concurrency. Transient failures require
bounded exponential backoff. Every run must retain a high-water mark and a failure manifest so an
interrupted refresh can resume without rewriting valid raw observations.

## Package boundary

Reusable energy-exchange logic belongs in `src/energy_exchange`. It must not be added to
`shared/ime_data`, which is reserved for Iran Mercantile Exchange logic. If multiple future
energy products need shared functionality, this package will provide that common layer and
product-specific wrappers will keep filters and settings explicit.

## Current workflow status

The workflow is complete and closed. The certificate collector produced one immutable snapshot on
2026-08-23 containing 21 symbols and 7,070 daily rows. Normalized and symbol-level activity outputs
were written to the interim and processed layers, and the source contract and limitations are in
`CERTIFICATE_DATA.md`. No collector is scheduled. Raw and derived data remain local; documents,
manifests, methodology, decision records, and reconstruction code remain versioned.

The terminal research-selection decision is recorded in
`decisions/0001-close-certificate-research.md`. A future restart requires a new explicit decision,
a narrowed scope, and a fresh review of endpoint stability, units, and liquidity.
