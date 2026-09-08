# Planned data contract

`config/assets.csv` registers the four selected assets. Blank source fields are unverified; all assets remain disabled until source validation.

| Field | Meaning |
|---|---|
| asset_id | Stable unique identifier |
| label | Human-readable name |
| asset_class | Explicit research grouping |
| currency | Quotation currency; distinguish IRR and toman |
| price_unit | Quantity represented by the price |
| source_path | Project-relative canonical input path or explicitly configured external input |
| date_column | Source observation-date column |
| price_column | Source valuation column |
| calendar | Source calendar, e.g. Gregorian or Jalali |
| return_basis | Explicit price-only or total-return definition |
| enabled | true or false; enable only reviewed assets |

Planned normalized-history grain: one row per Gregorian ISO date and asset ID, with positive
finite valuation and retained source path/date, units, currency, and return basis. This is
derived data and must never replace raw sources. Instruments requiring different return
methods must be identified by their adapters.

Planned outputs are aligned valuations, returns, coverage diagnostics, weights, and portfolio
performance. Exact numerical schemas and formulas will be versioned with implementation.


Yearly optimization contract: one output row per eligible Solar Hijri year, with four weights, expected return, covariance-based portfolio volatility, return/volatility ratio, sample window and count, fixed-income proxy regimes, and solver diagnostics. The current year is explicitly year-to-date. Source fund distributions and deposit terms must support return construction. The objective does not subtract a risk-free rate. See WORKFLOW.md for formulas and unresolved constraints.

## TSETMC fixed-income source: اعتماد

Collector: `src/asset_allocation/collectors/tsetmc_fixed_income.py`.
Public endpoint: `ClosingPrice/GetClosingPriceDailyList/66818022341772870/0`.
Canonical CSV: `data/raw/fixed_income/etf/etemad.csv`. Immutable source responses:
`data/raw/fixed_income/etf/tsetmc_snapshots/<sha256>.json`.

The source's `dEven` is Gregorian `YYYYMMDD`; the canonical CSV stores it as an ISO date.
`pClosing` is the daily closing price in IRR. `has_trade` identifies positive trade count and
volume. Zero-volume reference rows are preserved as source evidence and must not be silently
used as realizable returns. TSETMC closing prices alone are not yet a final total-return series;
distribution treatment remains to be audited.

## Bank-deposit source: World Bank annual deposit interest rate

Collector: `src/asset_allocation/collectors/bank_deposit_world_bank.py`. Public endpoint: World
Bank indicator `FR.INR.DPST` for Iran (`IRN`). Canonical CSV:
`data/raw/fixed_income/bank_deposits/world_bank_deposit_interest_rate_annual.csv`. Immutable
source responses: `data/raw/fixed_income/bank_deposits/world_bank_snapshots/<sha256>.json`.

Each row is the provider's annual percentage observation, with its Gregorian source year. World
Bank identifies this as an IMF/IFS series that can cover demand, time, or savings deposits and
uses country-specific averaging. It is not a verified quoted rate for a particular Iranian bank
term or a realized fund return. It remains separate from ETF and اخزا data until a proxy regime
and accrual rule are specified.

## Iranian one-year term-deposit policy schedule

Collector: `src/asset_allocation/collectors/iranian_term_deposit_schedule.py`. Canonical CSV:
`data/raw/fixed_income/bank_deposits/iranian_one_year_term_deposit_policy_schedule.csv`.
Downloaded source pages are archived byte-for-byte under
`data/raw/fixed_income/bank_deposits/iranian_source_snapshots/<sha256>.html`.

Rows are effective-dated published policy events for one-year deposits. They retain rate type,
policy status, source publisher and URL, publication date, and transcription note. This is a
schedule of announced rates, not actual bank-by-bank paid yields; unknown intervals remain absent.

## Canonical bank-deposit source: CBI annual one-year rate

Collector: cbi_one_year_deposit_rate.py. Canonical CSV:
data/raw/fixed_income/bank_deposits/cbi_one_year_deposit_rate_annual.csv. Official reference:
https://cbi.ir/simplelist/1515.aspx.

This is the selected source for 1384–1396. The one_year_rate_text_percent field preserves the CBI
table entry and selected_one_year_rate_percent is the series used for analysis. When CBI gives an
interval, the selected value is the upper endpoint, as directed by the user. The table was
transcribed from the official CBI material supplied by the user because CBI blocks automated
retrieval; its URL and that extraction basis are retained in every row.
