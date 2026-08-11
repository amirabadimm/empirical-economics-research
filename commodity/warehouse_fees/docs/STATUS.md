# Status

Last verified build: 2026-08-11.

- Canonical output: `data/processed/warehouse_fees_daily.csv`
- Rows: 31,471
- Commodities: 21
- Overall date range: 2016-10-29 through 2026-08-11
- Key uniqueness: `(date, commodity)`
- Current official table: 11 assets captured on 2026-08-11
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
