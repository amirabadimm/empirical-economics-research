# Planned data contract

The four-REIT assembly-date reinvestment scenario writes `data/processed/analysis/reit_assembly_reinvested_daily.csv` and its event audit, then `reit_reinvested_weekly_returns.csv` and `reit_reinvested_monthly_returns.csv`. The daily level is fractional units times raw traded close, with units increased at the first traded close on or after each approved assembly date. Older `reit_reinvested_correlations.csv` and `reit_usd_weekly_lag_correlations.csv` tables remain historical derivatives but are not active chart inputs. `reit_usd_weekly_predictive_regressions.csv` holds the REIT-lag-1/USD-lag-1-and-2/TEDPIX-lag-1 model, complete-case count, coefficients, unadjusted HAC(4) joint-test p-value, and same-sample baseline/full-model R². Fewer than 52 model rows are suppressed. These are derived analysis tables, not canonical raw sources or certified complete dividend total returns.

The active `reit_requested_correlation_heatmaps.csv` contains 80 fund/benchmark/frequency/window cells. Fields include `benchmark`, `frequency`, `fund`, `window_months`, `lag_months`, `lag_weeks`, `window_start`, `window_end`, `paired_observations`, `minimum_pairs`, `correlation`, and `status`. Six grids cover TEDPIX daily/weekly/monthly, housing monthly, USD/IRR daily, and weekly dollar-leading-REIT returns. Weekly dollar leads are 4, 13, and 26 completed Friday-ending weeks within a two-year sample. A coefficient needs at least five paired returns and 70% nominal-window coverage, plus nonconstant returns. Nominal coverage uses 20 sessions/month for daily, 52/12 weeks/month for weekly, and one observation/month for monthly; the two-year lead sample requires 74 pairs. Older `reit_housing_monthly_pairs.csv` and `reit_housing_monthly_correlation.csv` are retained historical derivatives and are not inputs to the active notebook or report. Housing is official CBI through 1403/05 and a flagged chain-linked Kilid listing-price extension afterward, available monthly only. No lag, fill, or interpolation is applied to housing.

The presentation generator `build_reit_latex_report` reads these derived tables and writes only `reports/REIT_CROSS_ASSET_ANALYSIS.tex`. It does not modify raw or processed datasets. The report contains 13 tables: cumulative returns, distribution events, traded-versus-reinvested returns, recent weekly and monthly returns, six complete correlation grids with paired counts and suppression markers, predictive regression, and grid coverage.

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
annualized covariance once from the 114 aligned months in 1396–1405/06 and holds it fixed across
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
was selected as the sole fixed-income asset for the revised 1395/01–1405/06 window. The
decision and remaining distribution audit are documented in [FIXED_INCOME.md](FIXED_INCOME.md).
Immutable historical raw evidence remains frozen under its original path as required by
workspace policy, but it is not referenced by active configuration or processing.

## Real estate fund comparison

Collector: `src/asset_allocation/collectors/tsetmc_reits.py`. TSETMC instrument search must yield one real-estate instrument per configured ticker. Its canonical manifest and per-instrument daily traded-price histories live in `data/raw/real_estate_funds/`; immutable API bytes are content-addressed in `snapshots/`. `src/asset_allocation/build_reit_correlation_panel.py` creates `data/processed/analysis/reit_tedpix_monthly_returns.csv`, keyed by `(jalali_period, asset_id)`. Missing adjacent-month prices imply missing returns. This derivative is independent of the four-asset canonical panel. Fund returns are market closing-price changes, with distributions and corporate actions unaudited.

`src/asset_allocation/analyze_reit_tedpix.py` writes `data/processed/analysis/reit_tedpix_trailing_windows.csv`, keyed by `(asset_id, window_months)`. Columns include the trailing start/end Jalali periods, actual paired observations, Pearson correlation, OLS intercept and slope on TEDPIX, R², and slope p-value. The most recent observed month is excluded as potentially incomplete. Undefined estimates are blank. A 48-month lookback may contain fewer than 48 paired returns for a recently listed fund.

`src/asset_allocation/analyze_reit_tedpix_weekly.py` writes `data/processed/analysis/reit_tedpix_weekly_returns.csv`, keyed by `(week_end_gregorian, asset_id)`, and `reit_tedpix_weekly_windows.csv`, keyed by `(asset_id, window_months)`. Its weekly close is the final valid observed daily close in a Saturday–Friday week. Weekly return is the ratio of adjacent weekly closes minus one; fund weeks require positive trading volume. The current unfinished week is excluded. The input lookback is 24 Jalali months plus a preceding-week buffer. Window results include 1, 3, 6, 12, and 24-month cutoffs, paired-week counts, Pearson correlation, OLS beta/intercept, R², and p-value. Undefined estimates remain blank.

`src/asset_allocation/analyze_reit_usd_weekly.py` reads `shared/data/raw/fx/usd_to_rial.csv` without copying it into project raw data. `data/processed/analysis/usd_irr_weekly_returns.csv` is keyed by `week_end_gregorian` and retains the IRR-per-USD level, weekly return, source observation date, current and prior price methods, method-change flag, and missing reason. A method-change return is blank. `reit_usd_weekly_windows.csv` is keyed by `(asset_id, window_months)` and contains 1, 3, 6, 12, and 24-month paired-week counts, source-method counts, Pearson correlation, and OLS fund-on-USD beta/intercept, R², and p-value. The weekly fund panel is read unchanged; TEDPIX is excluded from the USD regression universe.

`src/asset_allocation/analyze_reit_usd_lags.py` reads the shared canonical FX series and the three selected canonical fund raw histories without modifying either. `three_reit_usd_lag_pairs.csv` is keyed by `(fund, frequency, lag_periods, period)` for daily, Friday-ending weekly, and complete Jalali-month returns at zero and one lag. The one-day join requires the exact previous Gregorian date, the one-week join the previous Friday, and the one-month join the previous Jalali period; absent observations remain blank. Daily returns require consecutive observed sessions no more than five calendar days apart; weekly and monthly returns require adjacent periods. USD returns crossing a price-method boundary are blank. `three_reit_usd_lag_correlations.csv` is keyed by `(fund, frequency, lag_periods, window_months)` with trailing 1, 3, 6, 12, 24, and 48-Jalali-month windows, pair counts, source-method counts, and Pearson correlation when at least three nonconstant pairs exist. These are traded-price fund returns and are not verified dividend-reinvested returns.

`src/asset_allocation/collectors/tsetmc_reit_adjusted.py` archives immutable exchange member-chart responses under `data/raw/real_estate_funds/adjusted_price_snapshots/` for both adjustment modes. It validates matching dates and unadjusted closes against the canonical raw fund prices, then atomically writes the derived `data/processed/analysis/reit_adjusted_daily.csv`, keyed by `(source_date_gregorian, ins_code)`, with both closes, adjustment factor, and snapshot lineage. The adjustment feed changes Kelid, Danik, and Malek Atiyeh in the current two-year window; the other five have equal adjusted/unadjusted histories. The feed's exact dividend/corporate-action rules have not been independently audited.

`src/asset_allocation/build_reit_two_year_cumulative.py` writes `data/processed/analysis/reit_usd_tedpix_two_year_cumulative.csv`, keyed by `(week_end_gregorian, asset)`, and `reit_usd_tedpix_two_year_cumulative_summary.csv`, keyed by `asset`. It uses the last complete Friday and a cutoff 24 Jalali months earlier. Each fund's level comes from the validated exchange-adjusted daily table. Each asset's first observed weekly close on or after that cutoff is its baseline; later funds are not backfilled. Cumulative change equals observed weekly level divided by baseline level minus one. Missing weeks remain blank in the processed panel; only the Plotly line visually bridges gaps. The panel retains source observation dates, units, price method, return definition, and baseline week/level. The USD level spans two documented source methods. Monthly and weekly regression inputs remain unadjusted fund closes until their return definitions are separately revised.

`src/asset_allocation/build_housing_two_year_cumulative.py` reads the canonical processed monthly level panel and writes `data/processed/analysis/tehran_housing_two_year_cumulative.csv` plus `tehran_housing_two_year_cumulative_summary.csv`. Each observed Jalali month is dated at its Gregorian month end within the same 24-Jalali-month cutoff as the weekly chart. The first observed housing level is its baseline. Source method and quality flag are retained. Housing is neither converted to weekly observations nor carried past its last observed month.

`config/reit_cash_distributions.csv` is a source-verified payout ledger keyed by fund instrument and Gregorian payment date, with positive cash IRR per unit and a source URL. It currently contains one Kelid and one Malek Atiyeh payment; payout-history coverage is incomplete. `src/asset_allocation/build_reit_dividend_reinvestment.py` reads that ledger and the processed daily adjusted/unadjusted price comparison, writing `reit_price_adjustment_comparison.csv` and `reit_dividend_audit.csv` under processed analysis. For a verified payment it reinvests cash into fractional fund units at the first traded close on or after payment. Without a verified event, reinvested-value fields stay missing rather than being identified with price-only return. Even where events exist, the computed path represents known payments only until the full annual history is audited.

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

- `data/processed/analysis/monthly_asset_levels.csv`: 127 months from 1394/12 through 1405/06
  crossed with all four assets. Missing levels remain blank.
- `data/processed/analysis/monthly_asset_returns.csv`: 126 months from 1395/01 through 1405/06
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
`885 / 866`. It extends the panel from 1403/06 through 1405/06. Every secondary row retains its
raw level, factor, source path, regime, and the flag `secondary_proxy_low_overlap_similarity`.

`data/raw/housing/kilid/tehran_monthly.csv` is the canonical collector-owned Kilid source table, backed by immutable content-addressed page responses under `data/raw/housing/kilid/snapshots/`. The collector accepts only complete months, validates overlapping observations against the existing table, and atomically appends new months. As of the 2026-10-06 source refresh it contains 37 months through 1405/06; the incomplete 1405/07 page observation is excluded. The processed housing chart is a separate 24-point monthly series through 2026-09-22.

## Portfolio-analysis status

The canonical monthly levels and returns are inputs, not recommendations. Stage I and Stage II
diagnostics are notebook outputs only and are not part of the persisted data contract. No single
Stage II sensitivity row is an authorized investor recommendation without a documented policy.

The historical notebook is a pilot execution of the algorithm. The final project requires a
separate expert-survey input and forward-looking allocation output. Their schemas are intentionally
not invented before the survey instrument is received. When available, preserve the original survey
export as source evidence, define a processed response table and expert asset-view distribution, and
record the mapping from those views to the optimizer. The final risk input must be estimated from a
documented trailing window of recent years ending before the allocation date, not from the months
inside the year being predicted.
