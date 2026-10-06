# Workflow

The CBI-period housing levels were cross-checked against the independently curated
101-month CBI series in the separate Housing repository on 2026-09-19; all levels agree. This project
continues to generate its own four-asset panel and post-1403/05 Kilid extension. Refresh Kilid with `python -m asset_allocation.collectors.kilid_housing` before rebuilding the monthly panel; the collector archives exact responses, validates overlapping values, writes the canonical raw CSV atomically, and excludes the incomplete current month.

## Research objective

Build and validate a four-asset monthly-return panel from 1395/01/01 through 1405/06/31,
use a historical run to test the allocation algorithm, and then produce a forward-looking optimal
portfolio informed by an expert survey. The completed ex-post analysis is a pilot and data-building
stage; it is not the final purpose of the project.

The four assets are:
1. Fixed income: exchange-traded Iranian fixed-income funds (صندوق درآمد ثابت بورسی).
2. Gold: TGJU 18-karat gold / 750 (طلای 18 عیار).
3. Housing: Tehran apartment sale price per square metre.
4. Equities: Tehran Stock Exchange total index (شاخص کل بورس تهران).

## Mathematical specification

Stage I allocates the risky sleeve across gold, equity, and Tehran housing. Etemad is the
investable benchmark. For each complete year—and separately for 1405/01-06 YTD—positions are
bought once and held, and the model
maximizes `sqrt(12) * mean(risky_sleeve_return - benchmark_return) / sample_std(...)` subject to
nonnegative risky weights summing to one. This is an ex-post information-ratio-style statistic,
not a forecast or an unqualified Sharpe ratio.

Stage II chooses the total-wealth share assigned to the Stage I sleeve for an explicit
risk-aversion parameter. The notebook reports sensitivity over a documented parameter grid;
it does not infer an investor's risk preference from market history.

For the final project, completed expert-survey responses must be analyzed to estimate the experts'
expected asset-allocation distribution. Those views will supply forward-looking information to the
allocation process. The exact survey schema and mapping from responses to model inputs must be
documented after the survey is received; neither is inferred in the current historical notebook.

## Stage 1: collect fixed-income history first

Start with اعتمادآفرین پارسیان (ticker: اعتماد), reported as the first Iranian exchange-traded
fixed-income fund and reported to have begun activity on 1394/02/05. Verify its instrument
identity, first/last actual TSETMC trading observation, price history, NAV, distributions,
corporate actions, and gaps before calling that date the study start. AFRA/افران is a later
fund, with a reported activity start of 1398/11/21, so it is not the baseline candidate.

Initial collection on 2026-09-08 found a TSETMC reference/trading segment beginning
2015-03-14, including its first positive-trade row on 2015-03-15, followed by a 61-day gap to
2015-05-17. Preserve this finding as source evidence. Establish the usable return start only
after the listing-history and fund-distribution audit; do not bridge the gap by interpolation.

اعتماد is the sole fixed-income asset for 1395/01–1405/06. Deposit rates, اخزا and other
funds are not active inputs and must not be spliced into this series. Select the final
traded close in each Jalali month; exclude zero-volume reference rows. The return method
and rejected alternatives are recorded in [FIXED_INCOME.md](FIXED_INCOME.md).

اعتماد still needs its distribution, listing and corporate-action audit before calculated
closing-price changes can be described as total returns.

Collect distributions alongside fund prices/NAV. A quoted fund yield is not itself a realized
asset return: use a documented total-return construction or a verified close-price return when
there are no distributions.

Deliverable for this stage: source inventory, verified coverage and gaps, immutable evidence,
and validated source histories. No optimizer is needed at this stage.

## Stage 2: collect gold

Collect TGJU 18-karat / 750 history. Verify price per gram, currency (IRR versus toman), date
calendar, daily valuation field, duplicates, and first/last dates. Preserve source frequency.

For derived returns, select the final valid `price_close_irr_per_gram` observation in each Jalali
month. Do not average daily prices. Preserve the source observation date and compute adjacent
month-end price returns programmatically.

## Stage 3: collect housing

Preserve official CBI housing-report PDFs under `data/raw/housing/cbi/reports/`.
Keep ChatGPT-assisted extracted workbooks in `data/interim` until continuity,
duplicates, positivity, units, recomputed returns, source-file lineage and provenance
all pass validation. CBI observations take priority over every secondary housing source.

Never patch a housing level or return in the analysis notebook. Record source adjudications in
`config/housing_cbi_overrides.csv` with the original value, corrected value, unit, primary report,
verification report, evidence, reason, date, and quality flag. The builder must verify the
original value before applying the correction. Regenerate the level panel, return panel, and
housing quality audit together.

Use adjacent official reports to cross-check current-month levels against the previous-month
column in the following report and, where useful, the same-month-prior-year column. Treat large
changes as diagnostic flags only. Correct a level only after direct source review; otherwise
retain it with an unresolved or revision-disagreement flag.

Audit Kilid against CBI over 1402/06–1403/05. Because level and return agreement is weak, treat
Kilid as a secondary proxy, not an equivalent source. Keep CBI unchanged through 1403/05. Convert
Kilid from million toman/m² to million IRR/m², chain-link it at 1403/05 using `885 / 866`, and use
linked Kilid levels from 1403/06 onward. Preserve raw levels, link factor, source regime, and a
low-similarity flag on every Kilid-derived observation.

Collect average Tehran apartment sale price per square metre, prioritizing documented official
statistics. Preserve provider, geography, unit, reference period, publication date where known,
and methodological changes. Do not substitute construction costs, rent, or national prices.
Keep annual, quarterly, and monthly observations distinct. Never invent monthly housing prices
by expanding annual data for the main analysis.

## Stage 4: collect the stock-market index

Collect Tehran Stock Exchange index history from TSETMC and historical TSE reports. Keep price-only
TEPIX and the Price & Cash Return Index as separate definitions. Verify index identity, calendar,
historical methodology changes, and dividend treatment before selecting one source. Do not
substitute equal-weight or price-only indices silently. The index is a market proxy rather than a
directly tradable fund.

## Stage 5: build comparable periodic returns

Proposed reporting currency: IRR. Proposed analysis frequency: monthly, conditional on housing
coverage. Preserve Jalali labels and normalized Gregorian dates. Use a documented common
calendar and observation convention. Report missing/stale observations and exclusions; do not
silently forward-fill or replace missing returns with zero.

For price-only assets use P_t / P_(t-1) - 1. Fund returns must include distributions under a
specified reinvestment convention. Deposit-derived returns require an explicit accrual and
maturity rule; distinguish nominal quoted rates from effective annual rates. Housing price
returns exclude rent and carrying costs unless a later extension explicitly adds them. Record
index dividend treatment so the economic differences between proxies stay visible.

Fetch a preceding observation where available to compute the first return in 1384. A year of
annual price observations provides only one annual return, which is insufficient to estimate
within-year volatility/covariance. If monthly housing history is unavailable, revise the
estimation design explicitly rather than manufacture observations.

## Stage 6: portfolio methodology

Stage I is implemented in `notebooks/asset_allocation_analysis.ipynb` for 1396-1404 and the
six-month 1405 YTD period. Each solution is checked against corner
portfolios, equal weights, and 25,000 deterministic random simplex portfolios. Results are
reported as hindsight diagnostics and retain the 12-observation annual-sample limitation.

### Original year-specific volatility specification

For every candidate risky-sleeve weight vector, reconstruct the within-year buy-and-hold wealth
path and calculate monthly portfolio returns. Let the monthly differential from Etemad be
`d_m(w) = r_p,m(w) - r_b,m`. Stage I maximizes

```text
sqrt(12) * mean(d_m(w)) / sample_std(d_m(w))
```

subject to nonnegative risky weights summing to one. Both the numerator and tracking-error
denominator are estimated separately for each year. The selected weights and their risk estimates
are therefore allowed to change with the realized yearly sample.

### Stage II sensitivity workflow

Stage II keeps the Stage I risky composition fixed and performs a deterministic grid search over
5,001 risky-share values from zero to one. For every value in the complete sensitivity grid

```text
gamma = {0, 1, 2, 4, 6, 8, 10, 15, 20, 25, 30, 35, 40, 45, 50}
```

maximize realized mean-variance utility:

```text
U_y(alpha; gamma) = compounded_period_return_y(alpha)
                    - 0.5 * gamma * annualized_volatility_y(alpha)^2
```

The output is the full response curve `gamma -> alpha_y*(gamma)` for each year. Do not designate
any gamma as preferred, representative, or investor-specific. Treat every result as ex-post
sensitivity, not an investor policy.
Incomplete 1405 is optimized and reported strictly as a six-month YTD diagnostic, never as a
full-year result.

### Alternative sigma fixed over time

The notebook repeats both stages with one risk model estimated over the complete analysis sample.
Use all 114 aligned monthly observations in 1396–1405/06 to calculate

```text
Sigma_fixed = 12 * covariance(monthly asset returns)
Sigma_excess_fixed = 12 * covariance(risky asset returns - Etemad return)
```

The annualized volatility of total weights `x` is

```text
sigma_fixed(x) = sqrt(x' * Sigma_fixed * x)
```

and fixed Stage I tracking error is

```text
TE_fixed(w) = sqrt(w' * Sigma_excess_fixed * w)
```

Use covariance matrices rather than weighted standalone volatilities so cross-asset co-movement
and diversification remain represented. The resulting fixed annualized asset volatilities are
34.90% for gold, 40.83% for equity, 14.98% for housing, and 2.73% for fixed income.

In alternative Stage I, annual realized differential return continues to change by year, while
`TE_fixed(w)` does not. In alternative Stage II, yearly compounded returns continue to change,
while `sigma_fixed(x)` is used for every year. Run the same complete gamma grid and report the
entire sensitivity curve.

### Interpretation and cross-method checks

For both volatility definitions, confirm that risky exposure is weakly non-increasing as gamma
rises. Both methods select zero risky exposure throughout 1400 and 1402. The fixed-sigma method
de-risks earlier in 1396 and 1398, while retaining more high-gamma risky exposure in 1399, 1401,
1403, 1404, and 1405 YTD. These differences measure sensitivity to the risk definition; they do
not establish that either curve is an investor recommendation.

Because the fixed covariance matrices use the complete 1396–1405/06 sample, earlier-year risk
estimates include information from later observations. The second specification is therefore a
descriptive look-ahead comparison, not an investable backtest. A future investable extension must
estimate volatility using only information available before each allocation date, for example
with a rolling or expanding window.

## Stage 7: expert survey and forward-looking allocation

The final stage begins when the survey instrument and completed expert responses are available.
Preserve the original response export, document question meanings and coding, and derive an explicit
distribution of expert views across housing, gold, equity, and fixed income. Record how missing,
inconsistent, or incomplete responses are handled. Do not present expert weights or forecasts before
the survey evidence exists.

Redesign the risk model before calculating the final portfolio. The original pilot estimated
volatility separately inside each year, which uses too few observations and does not represent the
information set for a forward-looking decision. Estimate covariance from a documented trailing
window of recent years ending before the allocation date. Compare reasonable lookback lengths and,
if used, weighting or decay rules; select the specification through recorded diagnostics rather than
an arbitrary single year.

Combine the processed expert views with the revised trailing-risk estimate under a documented
optimization objective and constraints. Publish the resulting portfolio only after the survey
analysis, risk specification, and reproducible model run are complete. The final output must clearly
separate expert expectations, historical risk estimates, and optimizer decisions.

## Real estate funds: current four-fund workflow

The active English-language notebook is `notebooks/iran_reits_cross_asset_analysis.ipynb`. It covers Kelid, Danik, Arzesh Maskan, and Kakh. Eight funds remain in the immutable TSETMC source archive, but the active notebook displays only these four. If source prices or TEDPIX need refreshing, first run the documented incremental collectors `asset_allocation.collectors.tsetmc_reits` and `asset_allocation.collectors.tsetmc_tedpix`; validate the resulting raw coverage before rebuilding derivatives. Do not use exchange-adjusted fund prices for the current returns.

From `asset_allocation` with `PYTHONPATH=src`, run the following in order:

1. `python -m asset_allocation.build_reit_assembly_reinvestment`. Read `config/reit_approved_distributions.csv`, validate assembly dates and amounts, and buy fractional units at the first traded close on or after each assembly. The derived daily value is units times raw traded close. Kelid's two approved amounts and Danik's one amount are included. This assumes immediate cash availability; actual payment dates and other annual distributions remain under audit. Arzesh Maskan and Kakh have no recorded event, so their scenario currently equals traded-price change without establishing zero dividends.
2. `python -m asset_allocation.build_reit_two_year_cumulative` and `python -m asset_allocation.build_reit_reinvested_correlations`. The first builds the Friday-ending two-year comparison with USD/IRR and TEDPIX. The second builds derived weekly and monthly fund returns from the same reinvested-value path. Its older correlation grid remains a historical derivative and is not plotted in the active notebook.
3. `python -m asset_allocation.analyze_reit_usd_weekly_predictive`. Its 24-Jalali-month lag table compares each fund's weekly return with USD/IRR from the same or 1–4 prior completed weeks. A complete Friday grid makes a lag exactly one calendar week. All five coefficients for one fund use the same paired dates; at least 74 common weeks are required. USD returns across the shared FX source-method boundary remain missing. The regression uses fund lag 1, USD lags 1 and 2, and TEDPIX lag 1. It requires 52 complete weeks, reports the unadjusted HAC(4) joint p-value for the USD terms and incremental in-sample R² relative to a same-sample model without USD. Kakh does not yet meet the sample minimum. These statistics do not establish causation or out-of-sample prediction.
4. Refresh housing separately with `python -m asset_allocation.collectors.kilid_housing`, `python -m asset_allocation.build_monthly_return_panel`, and `python -m asset_allocation.build_housing_two_year_cumulative` when a new complete Kilid month is available. Housing stays at observed month ends and is a flagged chain-linked listing-price proxy, excluding rent and ownership costs.
5. Run `python -m asset_allocation.build_reit_requested_heatmaps` after both REIT weekly/monthly returns and the housing monthly panel are current. It writes 80 cells in `data/processed/analysis/reit_requested_correlation_heatmaps.csv`: four funds × six grids. TEDPIX uses daily 1/3/6/12-month, weekly 1/3/6/12/24-month, and monthly 12/24/36-month returns. USD/IRR uses daily same-day 1/3-month returns and weekly REIT returns against USD/IRR returns 4/13/26 completed weeks earlier over the last 24 Jalali months. Housing uses observed monthly 12/24/36-month returns; daily and weekly housing returns are unavailable and are never imputed. Pearson coefficients require at least five pairs, 70% of the stated window (74 weeks for the two-year dollar-lead sample), and variation in both returns. Kakh is retained in daily and weekly grids, with low-coverage long windows suppressed. Missing returns and the USD source-method boundary are not bridged.
6. Execute the notebook and check its nine Plotly figures: two cumulative comparisons, one predictive-regression table, and six heatmaps. The two-year cumulative comparison omits Kakh; the grids retain Kakh where its coverage qualifies. Each heatmap cell labels its actual paired count. No gaps are filled in processed data; lines may connect available observations visually.
7. Run `python -m asset_allocation.build_reit_latex_report` to generate the tracked `reports/REIT_CROSS_ASSET_ANALYSIS.tex` from validated derivatives. It contains cumulative-return, distribution, traded-versus-reinvested, six full correlation-grid, and predictive-regression tables plus conclusions that are recalculated from the processed data. It does not generate HTML, collect sources, or modify raw data. Inspect sample dates, suppression, and table labels before sharing. A local LaTeX engine may compile the source to PDF; no compiler is required to build the `.tex` file.

Historical-only derivatives include the earlier eight-fund traded-close panels, older same-period and day/week/month lag heatmaps, the standalone 24-month REIT–housing bar chart, exchange-adjusted-price comparison, and payment-date reinvestment audit. The active grids use custom reinvested returns. Preserve raw evidence and processed outputs. The separate payment-date ledger must not be combined with the assembly-date scenario, because that would count Kelid's 907 IRR distribution twice. See `docs/REIT_DIVIDEND_AUDIT.md` for unresolved payout coverage.

## Data governance and independent execution

Use project-local dependencies, project-relative paths, and explicit optional external inputs.
No sibling research-project imports or hard-coded workstation paths. Existing shared canonical
inputs retain their owner; the cumulative and fund-on-USD extensions read the shared FX series directly.

Collectors alone may refresh canonical raw CSVs through documented incremental, idempotent,
atomic writes. Preserve source responses byte-for-byte; never overwrite, delete, or extend
historical snapshots. Validate unique keys and reject conflicting records. Credentials come
only from the environment.

Derived data goes only to data/interim or data/processed/analysis. Numerical returns, weights,
coverage tables, and model diagnostics belong there. Notebooks go in `notebooks/`; presentation
artifacts should be created under `reports/` only when needed. Raw, snapshots, logs, caches, environments,
and bulk results stay out of Git. Update README, WORKFLOW, STATUS, and relevant contracts when
sources, schemas, paths, formulas, or stage status change.

### Canonical monthly return panel

Run `python -m asset_allocation.build_monthly_return_panel`. Daily assets use the final valid
observation in each Solar Hijri month; اعتماد requires a traded observation. Housing uses the
monthly CBI value. Build a complete month-by-asset grid, calculate returns only when adjacent
levels exist, and retain blank values plus explicit reasons otherwise. Never zero-fill,
forward-fill, or interpolate. Historical annual and TGJU equity alternatives remain inactive.
The primary housing input is the CBI monthly citywide series. Validate its 101 extracted
observations and provenance before publishing any processed return table. Kilid is retained
only to extend coverage after 1403/05 and requires an explicit boundary audit. Other secondary
and Esfand-only proxy workflows are retired and must not be regenerated.

### Portfolio analysis

Run the notebook only after rebuilding and testing the canonical panels. The notebook may read
the processed data but must not modify it. Preserve the distinction between the ex-post Stage I
and Stage II diagnostics and any future investable, out-of-sample allocation analysis.
The current notebook is the historical pilot. The future expert-informed model must be implemented
as a separate, reproducible stage so that its assumptions and outputs cannot be confused with the
ex-post results.
