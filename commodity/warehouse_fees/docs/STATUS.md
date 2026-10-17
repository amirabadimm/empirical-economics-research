# Status

## Validation isolation — 2026-10-17

The historical-cutoff panel test now uses temporary copies of its inputs and a
temporary processed-output path. It can no longer overwrite the live research
panel. Both data-dependent fee tests skip when local inputs are absent. The root
suite passed 86 tests and 233 subtests. This was a validation-code change, not a
tariff refresh; the October 13 source/output checkpoint below remains current.
## Live refresh checkpoint (2026-10-13)

The current official fee table was collected (12 assets), and the Wayback inventory contains 110 unique page records. The daily panel rebuilt to 32,794 rows for 21 commodities through 2026-10-13. Historical tariff boundaries retain their documented quality flags; the archive inventory is evidence, not a newly audited tariff event.

Last verified build: 2026-09-19.

- Canonical output: `data/processed/warehouse_fees_daily.csv`
- Rows: 32,290
- Commodities: 21
- Overall date range: 2016-10-29 through 2026-09-19
- Key uniqueness: `(date, commodity)`
- Current official table: 12 assets captured on 2026-09-19
- Exact official storage-fee events: 43
- Archived official-table observations: 30 across 16 commodities/assets
- Earliest exact event: copper cathode, 2022-01-01
- Earliest archived observation: feed barley and grain corn, 2016-10-29
- Bitumen 60/70: zero storage fee from 2025-10-20
- Iron-ore pellet: 2 rial/kg/day from 2025-10-20; 3 rial/kg/day from 2026-04-11

## Known limitation

The IME public archive does not reliably expose every historical opening or tariff-change
notice. Accordingly, the panel contains all currently recovered and documented official
states, but is not claimed to be a complete historical census. Boundary-quality columns
make this limitation explicit instead of inventing dates or zero values.
