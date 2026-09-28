# Gold research — daily ETF histories and Ayar NAV premium

## Five-fund daily source collection (2026-09-28)

The active universe is Ayar (`ayar`), Lotus Gold (`tala`), Kahroba
(`kahroba`), Ganj (`ganj`), and Gohar (`gohar`). Zarvan began trading on
2024-12-02 and cannot cover the full two-year window. Mesghal's historical
NAV remains unresolved; its earlier files are retained as evidence. Run from
workspace root:

```powershell
E:/Work/.venv/Scripts/python.exe commodity/gold/collect_daily.py
```

`--fund` selects one fund. This collector retrieves full unadjusted TSETMC daily
trading histories into independent `data/raw/funds/<fund>/price.csv` files. It
also retrieves TSETMC `fund.stats[].navRed` historical redemption NAV for Tala,
Kahroba, Ganj, and Gohar into each fund's `nav.csv`. Ayar retains its existing official
Mofid raw redemption NAV; `collect_daily.py` refreshes only its price history.
For Ayar NAV refresh, use the existing `refresh.py --collect` workflow below.
An explicit `--fund mesghal` still refreshes its price evidence, but the default
five-fund collection excludes it.

Every successful response is archived by SHA256 before parsing. Canonical CSVs
are validated and atomically merged by date. A same-date exact duplicate in a
TSETMC NAV response is collapsed; conflicting same-date NAVs fail collection.
TSETMC's historical NAV is not established as equivalent to each manager's raw
NAV. Do not combine the five funds into one premium series without checking
source timing and NAV basis. See `docs/STATUS.md` for coverage and the Mesghal
identity conflict.

## Last two years of daily prices and redemption NAV

The 2024-09-28 through 2026-09-28 window is built with:

```powershell
E:/Work/.venv/Scripts/python.exe commodity/gold/collect_fipiran_nav.py
E:/Work/.venv/Scripts/python.exe commodity/gold/build_two_years.py --as-of 2026-09-28
```

Fipiran histories are separately archived in `nav_fipiran.csv` for Tala,
Kahroba, Ganj, and Gohar; the TSETMC `nav.csv` files remain independent. The two-year
processed files under `data/processed/analysis/<fund>_daily_price_nav_2y.csv`
select Mofid raw NAV for Ayar and Fipiran historical NAV for those four.
They left-join on exact trading dates, expose `nav_provider` and source hashes,
and leave missing NAV blank. Run `refresh.py --collect` to refresh Ayar's
manager NAV. `audit_coverage.py` prints a read-only raw coverage summary.
The current exact-date matches are 464/464 Ayar, 464/464 Tala, 463/464 Kahroba,
461/464 Ganj, and 463/463 Gohar. The old Mesghal processed table is superseded
and is no longer part of the active five. See `docs/STATUS.md` for missing dates.

Gold is a domain workspace, not a single-fund folder. Fund identity, official NAV
provider and statistical settings live in `config/funds.json`; source histories
are isolated by fund under `data/raw/funds/<fund>`. Future gold funds can add a
configuration or a provider-specific collector without changing statistical code.

## Delivered calculation

`100 * (unadjusted TSETMC closing price / same-date raw redemption NAV - 1)`.
Positive is a premium, negative a discount. Both prices are per unit in IRR.
No adjusted trading price, split-adjusted NAV, interpolation or carry-forward is used.
Only positive-volume, positive-trade-count dates enter the sample. This is an
ex-post daily comparison, not an intraday tradable NAV signal: the NAV valuation
date is known, but its historical publication timestamp is not supplied.

Prices: official TSETMC, InsCode `34144395039913458` (Ayar).
NAV: the fund manager's official [Ayar portal](https://ayar.mofidfund.com/nav),
fund/basket IDs 12/12, `NavReportType=Raw`, `redemptionNav` field.
This distinction matters: historical NAV is not claimed to come from TSETMC/SEO.
TSETMC's latest ETF NAV is not a historical series and is not backfilled into history.

## TSETMC NAV discovery (2026-09-27)

Read-only testing verified TSETMC historical daily Ayar redemption NAV through
`Fund/GetFundInDetail/11586` (`fund.stats[].navRed`) and latest intraday NAV for
Ayar and Ahram through `Fund/GetETFByInsCode/{InsCode}`. The existing collector
still uses Mofid for historical NAV. No TSETMC NAV collector or 30-minute scheduler
has been deployed. See [endpoint evidence and limitations](docs/TSETMC_NAV_API.md).

## Run from workspace root

```powershell
python commodity/gold/refresh.py --collect
python commodity/gold/refresh.py
```

The first downloads and rebuilds; the second rebuilds locally. `--full --collect`
reconciles all historical NAV dates. Normal NAV updates revisit 30 calendar days.
TSETMC returns full price history; it is merged by date, not blindly substituted.
All successful responses have immutable SHA256 snapshots and URL/timestamp metadata.
Collectors alone write canonical raw CSVs using validated, atomic merges.

## Outputs

- `data/processed/bubble/ayar_nav_bubble.csv`: canonical exact-date bubble.
- `data/processed/bubble/ayar_bubble_distribution.csv`: signed bubble plus expanding
  equal-weight and recent-weighted percentiles (90-calendar-day half-life).
- `outputs/ayar_nav_monitor.csv`: delivery view of the statistical table.
- `notebooks/01_ayar_nav.ipynb`: read-only interactive analysis.

Percentiles include the current observation and ties using <=. The initial rank
is 100; recent weights are `2 ** (-age_days / half_life_days)`. These are historical
ranks, not probabilities of reversal. Nothing is smoothed or made absolute.

See `docs/WORKFLOW.md` and `docs/STATUS.md`. Source data and bulk outputs are local,
ignored by Git; no raw evidence is removed by the pipeline.
