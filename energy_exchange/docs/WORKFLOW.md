# Energy Exchange Research Workflow

Last reviewed: 2026-08-22

## Objective

Build a source-grounded map of the Iran Energy Exchange before implementing collection or
analysis. The initial scope is institutional structure, markets, boards, instruments, contract
specifications, trading lifecycle, settlement, delivery, participants, and published data.

## Documentation intake

1. Save each original file unchanged in `references/source_documents/`.
2. Add one row to `references/SOURCE_REGISTER.md`, including provenance and access date.
3. Write interpretation or extracted structure in `docs/notes/`; do not modify the source file.
4. Record consequential scope, schema, or methodology choices in `docs/decisions/`.
5. Update this workflow, the project README, and `docs/STATUS.md` when the source set, schema,
   paths, formulas, observation counts, or project stage changes.

## Planned data lifecycle

- `data/raw`: immutable canonical files and source snapshots; collectors only.
- `data/interim`: normalized or joined reproducible tables.
- `data/processed`: analysis-ready outputs with documented definitions.
- `notebooks`: exploration and communication, never canonical data mutation.
- `outputs`: generated figures and presentation material.

Before a collector is introduced, its source contract must document endpoint or publication,
field meanings, units, identifiers, calendars, revisions, pagination, validation, and failure
behavior. Writes must be incremental, idempotent, and atomic.

## Package boundary

Reusable energy-exchange logic belongs in `src/energy_exchange`. It must not be added to
`shared/ime_data`, which is reserved for Iran Mercantile Exchange logic. If multiple future
energy products need shared functionality, this package will provide that common layer and
product-specific wrappers will keep filters and settings explicit.

## Current workflow status

Only the project skeleton and documentation intake process exist. No source documents have yet
been registered, and no collection or analytical pipeline is approved.
