# Workflow

## Research objective

Build and validate a four-asset monthly-return panel from 1395/01/01 through 1405/05/31,
then perform an ex-post Stage I risky-sleeve allocation analysis for complete CBI years.

The four assets are:
1. Fixed income: exchange-traded Iranian fixed-income funds (صندوق درآمد ثابت بورسی).
2. Gold: TGJU 18-karat gold / 750 (طلای 18 عیار).
3. Housing: Tehran apartment sale price per square metre.
4. Equities: Tehran Stock Exchange total index (شاخص کل بورس تهران).

## Mathematical specification

Stage I allocates the risky sleeve across gold, equity, and Tehran housing. Etemad is the
investable benchmark. For each complete year—and separately for 1405/01-05 YTD—positions are
bought once and held, and the model
maximizes `sqrt(12) * mean(risky_sleeve_return - benchmark_return) / sample_std(...)` subject to
nonnegative risky weights summing to one. This is an ex-post information-ratio-style statistic,
not a forecast or an unqualified Sharpe ratio.

Stage II chooses the total-wealth share assigned to the Stage I sleeve for an explicit
risk-aversion parameter. The notebook reports sensitivity over a documented parameter grid;
it does not infer an investor's risk preference from market history.

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

اعتماد is the sole fixed-income asset for 1395/01–1405/05. Deposit rates, اخزا and other
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
five-month 1405 YTD period. Each solution is checked against corner
portfolios, equal weights, and 25,000 deterministic random simplex portfolios. Results are
reported as hindsight diagnostics and retain the 12-observation annual-sample limitation.

Stage II keeps the Stage I risky composition fixed and performs a deterministic grid search over
the risky share from zero to one. For each documented risk-aversion value, it maximizes realized
mean-variance utility, defined as period compounded return minus one-half gamma times annualized
monthly variance. Treat every result as ex-post sensitivity, not an investor-specific policy.
Incomplete 1405 is optimized and reported strictly as a five-month YTD diagnostic, never as a
full-year result.

The notebook also contains an alternative fixed-volatility specification. It estimates the
annualized asset covariance matrix and risky-minus-fixed-income covariance matrix once from all
113 aligned monthly observations in 1396–1405/05. These matrices are held fixed across yearly
optimizations. Yearly returns remain realized, period-specific inputs. Because the risk model uses
the complete sample, this alternative is a descriptive look-ahead comparison and not an
investable backtest.

## Data governance and independent execution

Use project-local dependencies, project-relative paths, and explicit optional external inputs.
No sibling research-project imports or hard-coded workstation paths. Existing shared canonical
inputs retain their owner; this scope does not require an FX series.

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
