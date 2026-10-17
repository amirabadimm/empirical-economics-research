# Silver workflow

## First source collection (2026-10-13)

First live certificate collection produced 307 rows through 2026-10-12, including 228 traded rows. The full official physical archive was collected and replayed from 235 immutable monthly snapshots. The corrected filter excludes vehicle colors; it found zero silver-bar or silver-shot physical rows. Consequently the strict physical benchmark and certificate/physical diagnostic cannot be built. This is source coverage, not an approved economic valuation. The combined Silver and Warehouse Fees test run passed 6 tests.

1. The certificate wrapper selects only the governed IME silver contract.
2. The physical wrapper retains a broad silver-related subset of complete IME
   responses. Comparable-product selection occurs only in processing.
3. The physical builder selects 999.9 silver bars, IRR/kg, cash or cash-matching,
   with positive executed price and quantity, then calculates a daily VWAP.
4. The comparison converts certificate settlement from IRR/g to IRR/kg and joins
   on the exact Jalali date. Missing dates remain missing; no interpolation occurs.
5. Premium is `100 * (certificate IRR/kg / physical IRR/kg - 1)`.
6. The distribution builder publishes observed points only.

Storage follows workspace policy: canonical inputs under `data/raw/{physical,
certificate}`, physical derivatives under `data/processed/physical`, comparisons
under `data/processed/bubble`, and other analysis under `data/processed/analysis`.
Complete IME physical responses remain owned by `shared/data/raw/ime/physical`.

Before promoting the diagnostic to fair value, verify physical specifications, VAT,
delivery and warehouse costs, lot size, purity, and reported-price comparability.
Builders reject missing columns, duplicate dates, unsupported units, non-positive
prices, and empty exact-date overlap. Derived files are written atomically.
