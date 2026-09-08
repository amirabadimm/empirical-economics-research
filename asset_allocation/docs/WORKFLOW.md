# Workflow

## Research objective

Estimate the best four-asset weight basket for each Solar Hijri year, targeting history from
1384/01/01 through the latest verified observation in 1405. Collect the inputs step by step
before implementing optimization.

The four assets are:
1. Fixed income: exchange-traded Iranian fixed-income funds (صندوق درآمد ثابت بورسی).
2. Gold: TGJU 18-karat gold / 750 (طلای 18 عیار).
3. Housing: Tehran apartment sale price per square metre.
4. Equities: Tehran Stock Exchange total index (شاخص کل بورس تهران).

## Mathematical specification

For year y, let mu_y be the vector of estimated expected periodic returns and Sigma_y the
covariance matrix of those same aligned asset returns. The portfolio objective is:

```text
maximize_w   (w.T @ mu_y) / sqrt(w.T @ Sigma_y @ w)
subject to   sum(w) = 1
```

This is expected return divided by portfolio volatility, with no risk-free-rate subtraction.
Fixed income is one of the four weighted assets. It is not a separate subtraction from the
objective. Portfolio volatility includes cross-asset covariance; sum(w_i * sigma_i) is not
portfolio standard deviation and would omit diversification effects.

The sum-to-one constraint is user-confirmed. Nonnegative weights (no short selling) are a
proposed additional constraint, not yet confirmed. Resolve short selling, leverage, and any
weight caps before implementing a solver. Do not silently add constraints.

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

After the اعتماد audit, inventory active and expired/renamed exchange-traded fixed-income
instruments only if the audit establishes a missing period or an unresolvable return-definition
problem. Record historical fund type: a fund's inception date may precede its exchange listing
or a type change. Do not select funds by future returns or only by survival to the present.

Collect ETF, اخزا, and bank-deposit histories separately before deciding the fixed-income proxy.
Never splice them into a single series by default: any later combination needs an explicit
proxy-regime specification, switch dates, return/accrual method, and sensitivity reporting.
The World Bank annual bank-deposit series is an initial partial source (2003–2016); collect a
term-specific Iranian bank-rate schedule for later years as separate evidence.

### Selected fixed-income regimes

The selected continuous fixed-income proxy is CBI's annual one-year term-deposit rate for Solar
Hijri 1384–1395, followed by اعتماد from 1396/01/01 through the latest verified observation in
1405. For CBI interval observations, use the maximum value. This switch is a research design
choice, not a claim that deposits and ETF units are identical investments.

Do not compute a synthetic jump return at the switch. Each annual result uses the regime assigned
to that year. Bank-deposit observations need a documented nominal-rate accrual convention; اعتماد
needs its distribution, listing, and price-gap audit before its return series is released.

Collect distributions alongside fund prices/NAV. A quoted fund yield is not itself a realized
asset return: use a documented total-return construction or a verified close-price return when
there are no distributions.

Deliverable for this stage: source inventory, verified coverage and gaps, immutable evidence,
and validated source histories. No optimizer is needed at this stage.

## Stage 2: collect gold

Collect TGJU 18-karat / 750 history. Verify price per gram, currency (IRR versus toman), date
calendar, daily valuation field, duplicates, and first/last dates. Preserve source frequency.

## Stage 3: collect housing

Collect average Tehran apartment sale price per square metre, prioritizing documented official
statistics. Preserve provider, geography, unit, reference period, publication date where known,
and methodological changes. Do not substitute construction costs, rent, or national prices.
Keep annual, quarterly, and monthly observations distinct. Never invent monthly housing prices
by expanding annual data for the main analysis.

## Stage 4: collect the stock-market index

Collect Tehran Stock Exchange total-index history, starting with TSETMC. Verify index identity,
calendar, historical methodology changes, and dividend treatment. Do not substitute equal-weight
or price-only indices silently. The index is a market proxy rather than a directly tradable fund.

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

## Stage 6: yearly optimization, after collection and validation

Primary interpretation: a retrospective best basket for each year. Estimate mu_y by arithmetic
mean and Sigma_y by sample covariance of aligned periodic returns within year y. Report these
as in-sample historical optima, not weights that were knowable at the start of that year.

With monthly inputs, a full year supplies at most 12 returns, so estimates are uncertain.
Record sample size, matrix conditioning, and weight sensitivity. Reject undefined ratios with
zero/near-zero portfolio volatility and flag singular or insufficient-data cases; do not claim
an optimum from a failed solver. Confirm sample sufficiency and numerical policy before coding.
Use the same periodic units in numerator and denominator. Any annualization must be explicit.

For incomplete 1405, label results year-to-date through the actual data cutoff. Never present
partial-year results as a completed-year optimum. Produce one row per eligible year with four
weights, expected return, portfolio volatility, objective value, sample dates/count, source
regimes, and solver diagnostics. An equal-weight basket is the comparison baseline.

If a forward-looking strategy is later requested, estimate weights using only prior data and
apply them to subsequent returns, with explicit lookback, rebalancing, weight drift, and costs.
That is a separate evaluation from the retrospective yearly optimization.

## Data governance and independent execution

Use project-local dependencies, project-relative paths, and explicit optional external inputs.
No sibling research-project imports or hard-coded workstation paths. Existing shared canonical
inputs retain their owner; this scope does not require an FX series.

Collectors alone may refresh canonical raw CSVs through documented incremental, idempotent,
atomic writes. Preserve source responses byte-for-byte; never overwrite, delete, or extend
historical snapshots. Validate unique keys and reject conflicting records. Credentials come
only from the environment.

Derived data goes only to data/interim or data/processed/analysis. Numerical returns, weights,
coverage tables, and model diagnostics belong there. Notebooks go in notebooks, logs in logs,
and presentation artifacts in outputs or reports. Raw, snapshots, logs, caches, environments,
and bulk results stay out of Git. Update README, WORKFLOW, STATUS, and relevant contracts when
sources, schemas, paths, formulas, or stage status change.
