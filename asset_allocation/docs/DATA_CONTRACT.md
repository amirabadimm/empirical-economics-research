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

Current persisted outputs are aligned valuations, returns, and coverage diagnostics. Stage I
weights and performance diagnostics are computed in the notebook but are not published as a
canonical result dataset. Stage II sensitivity outputs are also notebook-only diagnostics and
are not a canonical allocation dataset.

Official CBI Tehran housing PDFs are raw immutable evidence under
`data/raw/housing/cbi/reports/`. The extracted workbook is interim, not canonical raw or
curated output. Its citywide grain is one row per Jalali month; price unit is million IRR
per square metre. Required lineage fields include source PDF and provenance method.


The notebook's Stage I contract uses full years 1396-1404 plus 1405/01-05 YTD, with
gold/equity/housing as the risky
sleeve, Etemad as the investable benchmark, long-only risky weights summing to one, buy-and-hold
intra-year drift, and an annualized mean differential-return-to-tracking-error objective. It is
explicitly ex-post. Stage II keeps the Stage I composition fixed, searches the long-only risky
share on a 5,001-point grid, and reports mean-variance utility sensitivity for gamma values
0, 1, 2, 4, 6, 8, 10, 15, 20, 25, 30, 35, 40, 45, and 50. It does not define an
investor-specific policy. A parallel notebook-only specification estimates full-sample
annualized covariance once from the 113 aligned months in 1396–1405/05 and holds it fixed across
years. Its use of later observations in earlier-year risk estimates is explicitly ex-post.

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

## Removed fixed-income alternatives

Deposit-rate and اخزا sources are not part of the active data contract. Their datasets and
source-specific collectors were retired on 2026-09-09 after اعتماد
was selected as the sole fixed-income asset for the revised 1395/01–1405/05 window. The
decision and remaining distribution audit are documented in [FIXED_INCOME.md](FIXED_INCOME.md).
Immutable historical raw evidence remains frozen under its original path as required by
workspace policy, but it is not referenced by active configuration or processing.

## TSETMC TEDPIX source

Collector: src/asset_allocation/collectors/tsetmc_tedpix.py. Public endpoint:
Index/GetIndexB2History/32097828799138957. Canonical CSV:
data/raw/tse_total_index/tedpix_daily.csv; immutable API responses are archived at
data/raw/tse_total_index/tsetmc_snapshots/<sha256>.json.

The active equity derivative is part of the canonical panels built by
`src/asset_allocation/build_monthly_return_panel.py`. Each month uses the final valid official
TSETMC close and its actual Gregorian observation date. Returns are changes in the TEDPIX level,
treated as a total-return index subject to the documented index-definition audit.

Historical annual and TGJU stock-index files are inactive immutable evidence. They are not
referenced by active configuration or processing and must not be merged into this series.
## Canonical month-end levels and returns

`src/asset_allocation/build_monthly_return_panel.py` writes two long-form tables:

- `data/processed/analysis/monthly_asset_levels.csv`: 126 months from 1394/12 through 1405/05
  crossed with all four assets. Missing levels remain blank.
- `data/processed/analysis/monthly_asset_returns.csv`: 125 months from 1395/01 through 1405/05
  crossed with all four assets. Each valid return equals current month-end level divided by the
  preceding month-end level minus one.
- `data/processed/analysis/housing_data_quality_audit.csv`: one row per official CBI month,
  preserving normalized and original extracted levels, source PDF, provenance, verification
  evidence, quality flag, reconstructed return, and non-destructive extreme-return diagnostic.

The key is unique on `(jalali_period, asset_id)`. The files retain units, source observation
dates, source method, source path, return definition, quality flags, and missing reasons. Daily
gold and TEDPIX use the last valid observation in the Jalali month. اعتماد uses the final traded
observation. Housing uses CBI through 1403/05 and chain-linked Kilid afterward. No return is
zero-filled, forward-filled, or interpolated.

`config/housing_cbi_overrides.csv` is the reproducible adjudication layer. Each row records the
original extracted value, corrected or retained value, normalized unit, primary and verification
reports, evidence, reason, audit date, and quality flag. The builder refuses an override if its
recorded original no longer equals the workbook extraction.

The primary housing input is the CBI interim workbook with one Tehran-wide row per Jalali month,
price in million IRR/m², source PDF, provenance method and extraction method through 1403/05.
Kilid is converted from million toman/m² to million IRR/m² and multiplied by the boundary factor
`885 / 866`. It extends the panel from 1403/06 through 1405/05. Every secondary row retains its
raw level, factor, source path, regime, and the flag `secondary_proxy_low_overlap_similarity`.

## Portfolio-analysis status

The canonical monthly levels and returns are inputs, not recommendations. Stage I and Stage II
diagnostics are notebook outputs only and are not part of the persisted data contract. No single
Stage II sensitivity row is an authorized investor recommendation without a documented policy.
