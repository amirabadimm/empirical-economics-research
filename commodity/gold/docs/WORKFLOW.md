# Gold workflow

Live and scheduled daily refresh code is in `db/run_server.py`, with versioned
`db/gold-*.service` and `db/gold-*.timer` units. Live readings use last price/current
redemption NAV and compare only with completed daily bubbles: rolling one year,
rolling six months, full history weighted with a 90-day half-life, and a rolling
two-year reference bounded to 2024 onward. Polls run only 12:00-18:00 Tehran. They replace
the previous cache rows and expire after 24 hours; they never become daily history.
See [database deployment instructions](../db/README.md).

For database setup and refresh after collection, see [the PostgreSQL workflow](../db/README.md).
The database loader reads canonical CSVs and writes only to PostgreSQL; it never
edits raw files. The first server deployment succeeded on 2026-10-03 at
`/opt/empirical-economics-research`, using the existing Docker PostgreSQL database.
Pull code updates through Git, run the documented collectors when a market refresh
is needed, then load PostgreSQL. The daily timer runs at 23:30 Tehran and weekly
full reconciliation runs Sunday at 03:30 Tehran.

The five-fund research build is closed at the September 29 data checkpoint.
Refresh commands below remain available for maintenance; source gaps and Gohar
disagreements are recorded in `NAV_RELIABILITY.md` and its per-date audit output.

## Source reliability audit

Run `audit_nav_reliability.py --live`, then `audit_manager_nav.py --live`, from
the gold project path (or prefix both with `commodity/gold/` from workspace root).
These archive live source evidence and write derived comparisons only. Omit
`--live` to replay the most recent archived requests. Use
`data/processed/analysis/nav_reliability/trading_date_validation.csv` to distinguish
manager agreement, provider-only agreement, disputed values and missing NAV.
See [the September 29 reliability report](NAV_RELIABILITY.md) for source coverage,
manager endpoint mappings, Gohar's unit change, and unresolved discrepancies.

## Mesghal source investigation

Run `E:/Work/.venv/Scripts/python.exe -B commodity/gold/investigate_mesghal_nav.py`
from workspace root to verify the live Fipiran identity, request its historical
chart, and cross-check TSETMC and the listed manager website. Each response is
archived before parsing under `data/raw/funds/mesghal/snapshots/nav_investigation`;
the audit report is written under `data/processed/analysis`. This investigation
does not write canonical NAV or prices. Only verified, nonempty history may be
integrated through a collector. On 2026-09-29 the chart returned `[]` and TSETMC
history failed the fund-identity check. See [the report](MESGHAL_NAV_VALIDATION.md).

## Ayar NAV source transition — 2026-09-29

Run `collect_fipiran_nav.py --fund ayar` to collect Fipiran redemption NAV into
`data/raw/funds/ayar/nav_fipiran.csv` (registration 11586, group 0, `cancelNav`).
Then run `build_two_years.py --as-of 2026-09-28` and `refresh.py --fund ayar`.
`refresh.py --fund ayar --collect` refreshes recent TSETMC prices and Fipiran NAV.
Use `--collect --full` for an initial load or periodic older-revision check.
The September 29 build has 448/465 two-year matches and 1,928 full-history bubble
rows. Missing dates remain blank. The former Mofid `nav.csv` and independent
TSETMC `nav_tsetmc.csv` are preserved; neither is an Ayar analysis fallback.

## Five-fund daily data collection

Run `E:/Work/.venv/Scripts/python.exe commodity/gold/collect_daily.py` from the
workspace root. The active universe is Ayar, Tala, Kahroba, Ganj, and Gohar.
`--fund <key>` limits collection to one fund; Mesghal remains available for
explicit price-only evidence refresh. Routine TSETMC requests return the latest
30 unadjusted trading rows; initial loads and `--full` return complete history.
Responses are archived and merged into each fund's `price.csv`. Add
`--comparison-nav` to fetch complete TSETMC fund-detail NAV into its separate
comparison file. This endpoint has no verified bounded history option.

Ayar's selected NAV comes from Fipiran in `nav_fipiran.csv`; `collect_daily.py --comparison-nav` can refresh its separate TSETMC comparison. Mesghal has
no validated historical NAV source yet; no other fund's NAV may fill it. TSETMC
historical NAV can lag the trading history. Track price and NAV coverage
separately and use exact-date joins for any later comparisons. Ganj's older NAV
history predates its currently available trading history and its gold strategy;
do not use pre-gold NAV rows as gold-fund observations.

For fuller historical NAV, run `collect_fipiran_nav.py` for Ayar, Tala, Kahroba,
Ganj, and Gohar. It stores `nav_fipiran.csv` and immutable response snapshots beside
the independent TSETMC NAV history. Routine runs use `showAll=false` (342 Ayar
dates on September 29). Initial loads and `--full` use `showAll=true`; run full
mode periodically for older revisions. Then run `build_two_years.py --as-of
YYYY-MM-DD` to produce one analysis table per fund from the prior two calendar
years. The build selects Fipiran historical NAV for all five funds. It writes only under
`data/processed/analysis` and never changes raw data. Exact-date unmatched
sessions remain explicit nulls. Use `audit_coverage.py` for raw-only coverage;
the selected two-year output's `nav_available` column is the analysis coverage
measure.

The Fipiran collector verifies registration number, group, and name against
its live fund directory. If that request fails, it may use an existing
SHA256-verified archived directory response containing the same identity;
the NAV chart itself is still fetched live and archived. Gohar has 464/464
exact-date matches in the 2024-09-28 through 2026-09-28 build. Zarvan's
first TSETMC price date is 2024-12-02, so it is ineligible for that full window.

## Implemented daily pipeline

1. Resolve fund identity from `config/funds.json` (Ayar official TSETMC symbol).
2. Fetch official TSETMC unadjusted daily prices and provider-specific historical NAV.
3. Archive response bytes before parsing; keep content-addressed evidence immutable.
4. Validate unique dates and values; merge updates by date and atomically publish
   independent price/NAV files. All five selected funds use `nav_fipiran.csv`.
   TSETMC comparison files (`nav_tsetmc.csv` for Ayar, `nav.csv` for the others)
   stay independent.
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

## Historical TSETMC NAV and future intraday extension

[TSETMC_NAV_API.md](TSETMC_NAV_API.md) records the 2026-09-27 endpoint tests:
historical Ayar NAV uses fund registration number 11586 and `fund.stats[].navRed`;
latest NAV uses the trading InsCode and `etf.pRedTran`. These identifiers and
schemas must remain distinct. Historical coverage can lag the latest summary.

A future 30-minute collector must retain immutable responses and individual UTC
retrieval records, preserve source timestamps, validate freshness and alignment,
and log failures. Source timezone, valuation-time semantics, and repeated-sample
policy remain to be established. Daily history is not historical intraday NAV.
Existing Mofid raw history must not be overwritten or relabelled as TSETMC data.
