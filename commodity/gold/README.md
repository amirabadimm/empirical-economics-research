# Gold research — daily ETF histories and Ayar NAV premium

The five-fund [PostgreSQL schema and loader](db/README.md) are prepared for a
server database. They store daily prices, Fipiran redemption NAV, exact-date
bubbles, expanding historical percentiles and deciles. Deployed on 2026-10-03
to the server's existing PostgreSQL 17 `investment` database; 8,202 bubbles
loaded from the saved September 29 histories at initial deployment. The first
October 3 server daily refresh increased this to 8,213 bubbles. The five-minute
disposable monitor and daily refresh units are enabled; the workflow describes the four
daily reference distributions and cache retention.
Live polling is restricted to 12:00-18:00 Tehran; each moment has one-year,
six-month, two-year (2024 onward), and 90-day-half-life full-history deciles.

Research checkpoint closed 2026-10-03 using the September 29 collected data.
The five-fund panels and Ayar bubble are available. Residual NAV gaps and Gohar
disagreements are retained as quality flags for interpretation, not blockers.
No new data collection or notebook execution is claimed by this closeout.

## NAV reliability checkpoint (2026-09-29)

The [live source and manager audit](docs/NAV_RELIABILITY.md) corroborates all saved
Tala, Kahroba, and Ganj Fipiran observations on shared two-year dates. Kahroba has
one missing trading NAV; Ganj has three. Gohar has three manager disagreements,
including a material September 9 traded-date conflict, and an 80-fold unit-count
change on September 27. Use the per-date `validation_status` in
`data/processed/analysis/nav_reliability/trading_date_validation.csv` when reviewing
these observations. Coverage alone does not establish correctness.

## Mesghal historical NAV recheck (2026-09-29)

Live Fipiran identity is verified: registration 11899, group 2, symbol مثقال,
InsCode 32469128621155736. Its historical chart again returned HTTP 200 with `[]`.
TSETMC's fund-detail response was labelled نقرات and was rejected; only a current
Mesghal ETF NAV was obtained. No historical Mesghal NAV dataset was published.
See [the archived evidence and technical report](docs/MESGHAL_NAV_VALIDATION.md)
and `investigate_mesghal_nav.py` for reproduction. The active universe remains unchanged.

## Ayar NAV source transition (2026-09-29)

Ayar selects Fipiran `getfundchart` (registration 11586, group 0), mapping
`cancelNav` to redemption NAV in IRR. Run `collect_fipiran_nav.py --fund ayar`.
The collector archived and published 2,997 unique dates, 2018-06-20 through
2026-09-26, in `data/raw/funds/ayar/nav_fipiran.csv` on September 29.
The rebuilt two-year table has 448/465 matches (17 missing); the full-history
bubble has 1,928 observations. The saved TSETMC comparison agrees on all 337
shared traded dates in the two-year window. Provider agreement is not independent
portfolio valuation. Prior Mofid and TSETMC source files remain separate evidence.
This selection supersedes the earlier TSETMC-based build today.

## Five-fund daily source collection (2026-09-28)

The active universe is Ayar (`ayar`), Lotus Gold (`tala`), Kahroba
(`kahroba`), Ganj (`ganj`), and Gohar (`gohar`). Zarvan began trading on
2024-12-02 and cannot cover the full two-year window. Mesghal's historical
NAV remains unresolved; its earlier files are retained as evidence. Run from
workspace root:

```powershell
E:/Work/.venv/Scripts/python.exe commodity/gold/collect_daily.py
```

`--fund` selects one fund. Routine runs request the latest 30 TSETMC trading
rows and merge them into each `price.csv`. Initial loads and `--full` fetch
complete price history. Add `--comparison-nav` to fetch complete TSETMC
fund-detail NAV into separate comparison files (`nav_tsetmc.csv` for Ayar,
`nav.csv` for the others). Ayar's Mofid `nav.csv` remains prior evidence.
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

Fipiran histories are separately archived in `nav_fipiran.csv` for Ayar, Tala,
Kahroba, Ganj, and Gohar; the TSETMC `nav.csv` files remain independent. The two-year
processed files under `data/processed/analysis/<fund>_daily_price_nav_2y.csv`
select Fipiran historical NAV for all five.
They left-join on exact trading dates, expose `nav_provider` and source hashes,
and leave missing NAV blank. Run `refresh.py --collect` to refresh Ayar's
Fipiran NAV. `audit_coverage.py` prints a read-only raw coverage summary.
The latest September 29 rebuild has 448/465 Ayar, 465/465 Tala, 464/465 Kahroba,
462/465 Ganj, and 464/464 Gohar. The old Mesghal processed table is superseded
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
Ayar NAV: Fipiran `getfundchart?regno=11586&groupId=0&showAll=true`, `cancelNav`.
The former Mofid raw history is frozen evidence. TSETMC's historical adjustment
basis and publication vintages remain unverified; the source is recorded explicitly.
TSETMC's latest ETF NAV is not a historical series and is not backfilled into history.

## TSETMC NAV discovery (2026-09-27)

Read-only testing verified TSETMC historical daily Ayar redemption NAV through
`Fund/GetFundInDetail/11586` (`fund.stats[].navRed`) and latest intraday NAV for
Ayar and Ahram through `Fund/GetETFByInsCode/{InsCode}`. TSETMC historical Ayar
collection is now integrated. No 30-minute scheduler has been deployed.
See [endpoint evidence and limitations](docs/TSETMC_NAV_API.md).

## Run from workspace root

```powershell
python commodity/gold/refresh.py --collect
python commodity/gold/refresh.py
```

The first downloads recent Fipiran NAV and 30 TSETMC price rows, then rebuilds;
the second rebuilds locally. Initial loads automatically fetch full history.
Run `--collect --full` periodically to capture older revisions. Short responses
must cover the last saved date or collection stops and requires `--full`. Fipiran's
`showAll=false` returned 342 Ayar dates on September 29; `showAll=true` returned
2,997. Tested date filters did not narrow this response further. The separate
TSETMC fund-detail comparison requires a complete request when selected.
All successful responses have immutable SHA256 snapshots and URL/timestamp metadata.
Collectors alone write canonical raw CSVs using validated, atomic merges.

## Outputs

- `data/processed/bubble/ayar_nav_bubble.csv`: exact-date Fipiran NAV bubble, with incomplete historical coverage.
- `data/processed/bubble/ayar_bubble_distribution.csv`: signed bubble plus expanding
  equal-weight and recent-weighted percentiles (90-calendar-day half-life).
- `outputs/ayar_nav_monitor.csv`: delivery view of the statistical table.
- `notebooks/01_ayar_nav.ipynb`: read-only interactive analysis.

Percentiles include the current observation and ties using <=. The initial rank
is 100; recent weights are `2 ** (-age_days / half_life_days)`. These are historical
ranks, not probabilities of reversal. Nothing is smoothed or made absolute.

See `docs/WORKFLOW.md` and `docs/STATUS.md`. Source data and bulk outputs are local,
ignored by Git; no raw evidence is removed by the pipeline.
