# Gold workflow

## Implemented daily pipeline

1. Resolve fund identity from `config/funds.json` (Ayar official TSETMC symbol).
2. Fetch official TSETMC unadjusted daily history and the manager's raw NAV history.
3. Archive response bytes before parsing; keep content-addressed evidence immutable.
4. Validate unique dates and values; merge updates by date and atomically publish
   independent `price.csv` and `nav.csv`. Historical NAV revisions outside the
   trailing 30-day window require an explicit `--full` reconciliation.
5. Select traded price days and inner-join NAV on exact dates. Report unmatched
   dates separately; do not fill them. Use closing price and redemption NAV in IRR.
6. Build the premium and shared signed-distribution/expanding-percentile outputs.
7. Read those products from the notebook. The notebook does not collect or write raw.

Extension boundary: new funds need explicit identity, units and NAV basis. Do not
assume every provider has the same schema or that all funds are comparable. Add
collectors under `src/gold/collectors`; keep calculations under `processing`.
This ETF price/NAV analysis is independent of IME physical commodity benchmarks.

Atomic publication is per CSV, not a transaction over the whole dataset. A failed
collection/rebuild must be resolved before declaring a new checkpoint complete.

## Tested TSETMC NAV extension (not integrated)

[TSETMC_NAV_API.md](TSETMC_NAV_API.md) records the 2026-09-27 endpoint tests:
historical Ayar NAV uses fund registration number 11586 and `fund.stats[].navRed`;
latest NAV uses the trading InsCode and `etf.pRedTran`. These identifiers and
schemas must remain distinct. Historical coverage can lag the latest summary.

A future 30-minute collector must retain immutable responses and individual UTC
retrieval records, preserve source timestamps, validate freshness and alignment,
and log failures. Source timezone, valuation-time semantics, and repeated-sample
policy remain to be established. Daily history is not historical intraday NAV.
Existing Mofid raw history must not be overwritten or relabelled as TSETMC data.
