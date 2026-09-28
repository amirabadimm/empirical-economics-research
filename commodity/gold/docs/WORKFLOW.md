# Gold workflow

## Five-fund daily data collection

Run `E:/Work/.venv/Scripts/python.exe commodity/gold/collect_daily.py` from the
workspace root. The active universe is Ayar, Tala, Kahroba, Ganj, and Gohar.
`--fund <key>` limits collection to one fund; Mesghal remains available for
explicit price-only evidence refresh. The full TSETMC unadjusted
daily trading response is archived and merged by date into each fund's
`data/raw/funds/<key>/price.csv`. For Tala, Kahroba, Ganj, and Gohar, the corresponding
registered fund's `Fund/GetFundInDetail/{regNo}` response is archived and its
`stats[].navRed` is merged into an independent `nav.csv`. The collector checks
the returned fund name and rejects conflicting NAV rows on one date.

Ayar's NAV remains manager-sourced through the existing collector. Mesghal has
no validated historical NAV source yet; no other fund's NAV may fill it. TSETMC
historical NAV can lag the trading history. Track price and NAV coverage
separately and use exact-date joins for any later comparisons. Ganj's older NAV
history predates its currently available trading history and its gold strategy;
do not use pre-gold NAV rows as gold-fund observations.

For fuller historical NAV, run `collect_fipiran_nav.py` for Tala, Kahroba,
Ganj, and Gohar. It stores `nav_fipiran.csv` and immutable response snapshots beside
the independent TSETMC NAV history. Then run `build_two_years.py --as-of
YYYY-MM-DD` to produce one analysis table per fund from the prior two calendar
years. The build uses Mofid raw NAV for Ayar, Fipiran historical NAV for the
four funds. It writes only under
`data/processed/analysis` and never changes raw data. Exact-date unmatched
sessions remain explicit nulls. Use `audit_coverage.py` for raw-only coverage;
the selected two-year output's `nav_available` column is the analysis coverage
measure.

The Fipiran collector verifies registration number, group, and name against
its live fund directory. If that request fails, it may use an existing
SHA256-verified archived directory response containing the same identity;
the NAV chart itself is still fetched live and archived. Gohar has 463/463
exact-date matches in the 2024-09-28 through 2026-09-28 build. Zarvan's
first TSETMC price date is 2024-12-02, so it is ineligible for that full window.

## Implemented daily pipeline

1. Resolve fund identity from `config/funds.json` (Ayar official TSETMC symbol).
2. Fetch official TSETMC unadjusted daily history and the manager's raw NAV history.
3. Archive response bytes before parsing; keep content-addressed evidence immutable.
4. Validate unique dates and values; merge updates by date and atomically publish
   independent `price.csv` and `nav.csv`. Historical NAV revisions outside the
   trailing 30-day window require an explicit `--full` reconciliation.
5. Select traded price days and inner-join NAV on exact dates. Use closing price
   and redemption NAV in IRR. The two-year analysis table exposes any missing
   NAV as null through `nav_available`; no separate unmatched CSV is produced.
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
