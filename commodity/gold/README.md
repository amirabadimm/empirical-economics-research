# Gold research — Ayar NAV premium

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
- `data/processed/analysis/ayar_unmatched_prices.csv`: traded dates lacking exact NAV.
- `data/processed/analysis/ayar_nav_distribution.png`: histogram and percentile timeline.
- `outputs/ayar_nav_monitor.csv`: delivery view of the statistical table.
- `notebooks/01_ayar_nav.ipynb`: read-only interactive analysis.

Percentiles include the current observation and ties using <=. The initial rank
is 100; recent weights are `2 ** (-age_days / half_life_days)`. These are historical
ranks, not probabilities of reversal. Nothing is smoothed or made absolute.

See `docs/WORKFLOW.md` and `docs/STATUS.md`. Source data and bulk outputs are local,
ignored by Git; no raw evidence is removed by the pipeline.
