# Energy Exchange Project Status

Last updated: 2026-08-23

## Current stage

Closed after feasibility assessment. No active collection or analysis.

## Completed

- Created a dedicated project boundary outside the commodity-exchange code.
- Established locations for immutable source documents, provenance records, notes, decisions,
  raw and derived data, notebooks, code, tests, and generated outputs.
- Defined the initial document-intake and data-governance workflow.
- Verified public access to physical-auction, electricity, certificate, salaf, and futures data.
- Documented an observed inventory of 21 certificate and 71 derivative symbols, with coverage and
  endpoint limitations in `docs/notes/MARKET_ACCESS_INVENTORY.md`.
- Inventoried all 66 source documents, assigned normalized English filenames, and organized them
  into eight role-based directories under `documents/` while preserving file contents and a full
  original-to-current filename manifest.
- Classified the corpus into eight analytical roles and assigned evidence-aware reading
  priorities in `docs/DOCUMENT_TAXONOMY.md`.
- Implemented an immutable, timestamped TSETMC collector for all 21 observed certificate symbols.
- Collected 7,070 daily certificate rows through 2026-08-22; 1,432 rows (20.25%) contain positive
  transaction count and volume.
- Published normalized daily and symbol-level activity tables, with the field contract and
  limitations documented in `docs/CERTIFICATE_DATA.md`.

## Terminal decision

The feasibility phase answered the research-selection question. Selected niches are active, but
the market-wide certificate registry is too sparse, concentrated, and heterogeneous for the
intended empirical project. Active development, further backfills, and recurring refreshes are
therefore stopped. The full rationale is recorded in
`docs/decisions/0001-close-certificate-research.md`.

There are no pending project actions. The retained corpus and code are archival. Any restart must
define a narrower research question and record a new decision before collecting more data.

## Data checkpoint

The first canonical dataset covers 21 certificate symbols and 7,070 daily rows through 2026-08-22.
Only 1,432 rows are actual traded days under the positive-count-and-volume rule. Read-only
reconnaissance found 71 derivative symbols; returned histories extend from 2016-02-09 for salaf
and 2023-05-31 for futures. Individually addressable physical auctions extend to 2013-07-31.
The immutable certificate snapshot and derived CSVs remain local under repository data policy;
the versioned collector reproduces them.
