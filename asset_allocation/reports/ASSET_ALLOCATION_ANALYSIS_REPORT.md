# Iran Cross-Asset Allocation: Complete Analysis and Interpretation

Updated: 2026-09-12

## Executive summary

This study compares four Iranian assets—18-karat gold, TEDPIX, Tehran residential housing,
and the Etemad fixed-income ETF—using monthly observations from Solar Hijri 1395/01 through
1405/05. The optimization sample begins in 1396 because housing lacks the 1394/12 level needed
to calculate its 1395/01 return. Years 1396–1404 contain 12 aligned observations; 1405 is a
five-month year-to-date diagnostic through Mordad.

The central result is not one permanent portfolio. The hindsight-efficient risky allocation
changes sharply across regimes. Gold dominates five periods, housing four, and equity one.
Five of the ten Stage I solutions are 100% in one risky asset. This instability is itself an
important finding: the historical winner was highly regime-specific, and the analysis does not
identify a stable all-weather allocation.

Fixed income beat the best available risky sleeve on the benchmark-relative criterion in 1400
and 1402. Stage II therefore selects 100% fixed income in those years for every tested risk-
aversion value. In several high-return years it selects 100% risky exposure even for high risk
aversion because realized nominal return spreads were exceptionally large. These are ex-post
diagnostics, not forecasts or recommended portfolios.

## Research question and analytical structure

The work separates two decisions that are often incorrectly combined:

1. **Stage I — composition:** What mix of gold, equity, and housing produced the best realized
   return relative to Etemad per unit of tracking error?
2. **Stage II — exposure:** Given that risky mix and an explicit risk-aversion coefficient, how
   much total wealth would hindsight utility allocate to the risky sleeve versus fixed income?

This separation makes the result interpretable. Stage I answers *what was most efficient inside
the risky sleeve*. Stage II answers *how much of that sleeve would maximize the stated utility*.

## Data construction and governance

The analysis uses one canonical processed panel. Raw source snapshots remain immutable, and the
notebook reads but does not edit source or processed data.

| Asset | Active source and monthly convention | Return interpretation |
|---|---|---|
| Gold | TGJU 18-karat gold; final valid close in each Jalali month; IRR per gram | Price appreciation |
| Equity | Official TSETMC TEDPIX history; final valid monthly close | Total-return-index level change, subject to the documented index-definition audit |
| Housing | CBI Tehran average transaction price through 1403/05; chain-linked Kilid thereafter | Price appreciation only; excludes rent and ownership costs |
| Fixed income | Etemad ETF; final traded close in each Jalali month | Market-price return; historical distribution/corporate-action policy remains provisional |

The processed level panel has 126 months from 1394/12 through 1405/05 crossed with four assets.
The return panel has 125 months from 1395/01 through 1405/05 crossed with four assets. Returns
are calculated only from adjacent month-end levels. Missing values are retained; there is no
forward filling, interpolation, smoothing, or replacement with zero.

## Housing integrity work

Housing required the most important data-quality intervention. Four transcription or extraction
values were adjudicated against official CBI reports through the reproducible override layer:

| Month | Extracted level | Verified level | Treatment |
|---|---:|---:|---|
| 1396/12 | 48.987 | 57.591 | Corrected using the current official report; adjacent revision disagreement disclosed |
| 1397/01 | 55.220 | 55.280 | Corrected from agreeing official reports |
| 1397/04 | 91.728 | 69.728 | Corrected from agreeing official reports |
| 1397/07 | 0.6811 | 86.109 | Corrected after visual review of the damaged RTL PDF text layer |

Levels are million IRR per square metre. The malformed 1397/07 value created an artificial
approximately −99%/+13,000% return pair. Correcting Mehr alone reduced 1397 annualized housing
volatility from 13,379.56% to 46.12%; applying all verified corrections reduced it to 14.08%.
Corrected 1397 compounded housing appreciation is 91.72%.

CBI ends at 1403/05. Kilid is converted from million toman to million IRR and chain-linked at
that boundary using `885 / 866 = 1.021939953811`. This avoids an artificial level jump but does
not make the two sources equivalent: overlap level MAPE is 10.97%, maximum level gap is 19.61%,
monthly-return correlation is 0.288, and return MAE is 2.29 percentage points. Consequently,
1403 contains a source transition and 1404–1405 are Kilid-proxy periods.

## Asset-level realized results

All figures below are nominal and in percent. Return is compounded over the year; volatility is
the sample standard deviation of monthly returns multiplied by the square root of 12.

| Year | Gold return / vol. | Equity return / vol. | Housing return / vol. | Fixed income return / vol. |
|---:|---:|---:|---:|---:|
| 1396 | 32.92 / 13.05 | 24.68 / 9.87 | 26.09 / 8.68 | 23.91 / 1.41 |
| 1397 | 180.34 / 57.00 | 85.54 / 39.86 | 91.72 / 14.08 | 22.26 / 0.89 |
| 1398 | 40.18 / 18.85 | 187.08 / 20.59 | 41.55 / 15.75 | 22.85 / 1.60 |
| 1399 | 80.14 / 43.64 | 154.96 / 81.08 | 93.71 / 17.14 | 21.56 / 7.38 |
| 1400 | 13.60 / 19.02 | 4.55 / 26.35 | 16.00 / 8.40 | 20.98 / 0.52 |
| 1401 | 114.14 / 28.86 | 43.39 / 35.89 | 85.77 / 15.79 | 23.42 / 0.30 |
| 1402 | 23.21 / 22.30 | 11.97 / 27.55 | 24.83 / 14.73 | 26.17 / 0.32 |
| 1403 | 149.24 / 34.33 | 23.46 / 26.03 | 15.07 / 5.99 | 31.56 / 0.53 |
| 1404 | 117.52 / 45.54 | 37.04 / 43.15 | 37.84 / 9.02 | 34.95 / 0.76 |

Three patterns matter for presentation. First, fixed income has much lower measured volatility
than all risky assets. Second, the identity of the highest-return risky asset changes materially.
Third, housing's low measured volatility partly reflects transaction averaging, illiquidity, and
source construction; it is not directly comparable to continuously traded risk.

## Stage I methodology

For initial risky weights `w`, the model simulates a buy-and-hold wealth path. It does not reset
weights monthly. Monthly portfolio return is compared with the contemporaneous Etemad return,
and Stage I maximizes:

`sqrt(12) × mean(portfolio return − benchmark return) / sample standard deviation(portfolio return − benchmark return)`

Constraints are long-only weights between zero and one that sum to one. The solver uses equal
weights, all corner portfolios, and 30 deterministic random starting points. Each selected result
is then compared with corners, equal weights, and 25,000 random simplex portfolios. Every selected
score met or exceeded the best sampled score within numerical tolerance.

## Stage I results and interpretation

| Year | Initial gold | Initial equity | Initial housing | Risky return | Benchmark return | Tracking error | Score |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 1396 | 84.37% | 0.00% | 15.63% | 31.85% | 23.91% | 11.75% | 0.59 |
| 1397 | 4.40% | 0.00% | 95.60% | 95.62% | 22.26% | 13.86% | 3.58 |
| 1398 | 0.00% | 100.00% | 0.00% | 187.08% | 22.85% | 21.51% | 4.24 |
| 1399 | 0.00% | 1.35% | 98.65% | 94.54% | 21.56% | 17.84% | 2.79 |
| 1400 | 100.00% | 0.00% | 0.00% | 13.60% | 20.98% | 18.80% | −0.25 |
| 1401 | 23.71% | 0.00% | 76.29% | 92.50% | 23.42% | 15.61% | 3.02 |
| 1402 | 100.00% | 0.00% | 0.00% | 23.21% | 26.17% | 22.35% | −0.01 |
| 1403 | 100.00% | 0.00% | 0.00% | 149.24% | 31.56% | 34.13% | 2.11 |
| 1404 | 100.00% | 0.00% | 0.00% | 117.52% | 34.95% | 45.37% | 1.31 |
| 1405 YTD | 15.56% | 10.87% | 73.57% | 58.52% | 14.89% | 17.53% | 4.74 |

Year-by-year reading:

- **1396:** a diversified gold–housing mix modestly beat Etemad. The 0.59 score is positive but
  much weaker than the strong-opportunity years.
- **1397:** housing received 95.60% despite gold's larger raw return because housing delivered a
  much smoother realized path. This illustrates that Stage I rewards return relative to tracking
  error, not raw return alone.
- **1398:** equity was both the dominant return winner and the optimal corner portfolio.
- **1399:** housing dominated because its 93.71% return came with far lower measured volatility
  than equity's 154.96% return and 81.08% volatility.
- **1400:** no risky asset beat fixed income on return. Gold was merely the least unfavorable
  risky sleeve under the Stage I relative-efficiency objective; the negative score matters more
  than the 100% gold label.
- **1401:** housing and gold combined, with housing dominant, balancing housing's smoother path
  against gold's higher return.
- **1402:** the score is approximately zero and negative. The risky opportunity set offered no
  meaningful realized advantage over Etemad.
- **1403 and 1404:** gold was the clear ex-post winner. Confidence in comparisons involving
  housing is reduced by the 1403 source transition and Kilid-only housing data in 1404.
- **1405 YTD:** the model selected a three-asset mix dominated by housing. This uses only five
  observations and must not be described as a full-year result.

## Stage II methodology

Stage II fixes each year's Stage I risky composition. It searches 5,001 possible risky shares,
`alpha`, from zero to one. The rest is placed in Etemad. For each risk-aversion value
`gamma ∈ {0, 1, 2, 4, 6, 8, 10, 15, 20, 25, 30, 35, 40, 45, 50}`, it maximizes:

`utility = compounded period return − 0.5 × gamma × annualized volatility²`

Like Stage I, the total portfolio is buy-and-hold within the period. Stage II changes total risk
exposure, not the relative composition inside the risky sleeve.

## Stage II results and interpretation

Optimal risky allocation (`alpha`) in percent:

| Year | γ=0 | γ=1 | γ=2 | γ=4 | γ=6 | γ=8 | γ=10 | γ=15 |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1396 | 100.00 | 100.00 | 100.00 | 100.00 | 97.32 | 76.18 | 62.94 | 44.56 |
| 1397 | 100.00 | 100.00 | 100.00 | 100.00 | 100.00 | 100.00 | 100.00 | 100.00 |
| 1398 | 100.00 | 100.00 | 100.00 | 100.00 | 100.00 | 100.00 | 100.00 | 100.00 |
| 1399 | 100.00 | 100.00 | 100.00 | 100.00 | 100.00 | 100.00 | 100.00 | 100.00 |
| 1400 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 |
| 1401 | 100.00 | 100.00 | 100.00 | 100.00 | 100.00 | 100.00 | 100.00 | 100.00 |
| 1402 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 |
| 1403 | 100.00 | 100.00 | 100.00 | 100.00 | 100.00 | 100.00 | 100.00 | 70.16 |
| 1404 | 100.00 | 100.00 | 100.00 | 100.00 | 69.64 | 45.54 | 33.24 | 19.56 |
| 1405 YTD | 100.00 | 100.00 | 100.00 | 100.00 | 100.00 | 100.00 | 100.00 | 97.72 |

At the notebook's illustrative `gamma = 4`, the total portfolio equals the Stage I sleeve in
1396–1399, 1401, and 1403–1405 YTD. It is 100% fixed income in 1400 and 1402. This should not be
presented as a recommended risk setting; gamma 4 is one sensitivity point.

The boundary-heavy pattern has a straightforward explanation. Iranian nominal asset returns in
several years were very large relative to annualized variance, so the specified utility still
favored full risky exposure. In 1400 and 1402 the risky sleeve's return was below fixed income,
so both return and risk favored the benchmark. Interior diversification appears most clearly in
1396 and 1404 as gamma rises. The model is therefore sensitive to realized regimes and to the
chosen utility scale.

## What can and cannot be concluded

Supported conclusions:

- Historical risky-asset leadership changed substantially across years.
- Housing sometimes improved benchmark-relative efficiency because its measured monthly path was
  smoother, after correcting source errors.
- Fixed income was the superior total allocation in the weak risky years 1400 and 1402 under the
  stated ex-post utility.
- A higher gamma weakly reduces optimal risky exposure; it never increases it in the computed grid.
- Numerical checks support the reported Stage I optima relative to a large random comparison set.

Unsupported conclusions:

- That any displayed weight was knowable at the start of its year.
- That 100% allocations are suitable for a real investor.
- That housing volatility is economically equivalent to traded-asset volatility.
- That nominal returns represent gains in purchasing power; inflation is not deducted.
- That gamma 4, or any other gamma, represents the audience's risk preference.
- That five-month 1405 YTD behavior predicts the complete year.

## Methodological limitations

1. Every full year contains only 12 monthly observations; 1405 contains five. Estimated
   volatility, tracking error, and optimal weights are statistically fragile.
2. All optimization is in-sample and uses realized returns. It is vulnerable to hindsight bias
   and cannot establish out-of-sample performance.
3. Returns are nominal IRR returns. Inflation, real purchasing power, and currency depreciation
   are not separately modeled.
4. Housing is an average transaction price, not a constant-quality repeat-sales index. It omits
   rent, vacancy, maintenance, taxes, transaction costs, leverage, and illiquidity.
5. TEDPIX is an index, not a directly investable fund. Tracking error, fees, and implementation
   constraints are omitted.
6. Etemad is an investable benchmark, not a risk-free rate. Its historical distribution and
   corporate-action policy still requires final verification.
7. Housing changes from CBI to a weakly similar chain-linked Kilid proxy after 1403/05.
8. Stage II combines compounded period return with annualized monthly variance. For 1405 YTD,
   the return horizon is five months while volatility is annualized, so its utility is not fully
   horizon-consistent with the full-year rows.
9. Long-only constraints, no rebalancing, and no transaction costs simplify implementation.

## Presentation storyline

Recommended sequence for a presentation:

1. **Question:** separate risky-sleeve composition from total risk exposure.
2. **Data credibility:** show the immutable source chain and the housing correction example.
3. **Asset regimes:** use the return–volatility chart to show changing leadership.
4. **Stage I:** explain the information-ratio-style objective and show the stacked weights.
5. **Main finding:** emphasize instability and the negative-score years, not only winners.
6. **Stage II:** show the gamma sensitivity chart and heatmap; explain why results reach boundaries.
7. **Close:** describe this as a historical diagnostic framework that now needs out-of-sample
   testing, real-return adjustment, and an investor-specific risk policy.

Suggested closing sentence:

> The analysis does not reveal one timeless Iranian portfolio; it reveals that the ex-post
> efficient allocation changed sharply by regime, and that credible portfolio decisions require
> both clean data and an explicit risk preference.

## Likely questions and concise answers

**Why is fixed income the benchmark instead of a risk-free rate?**
Etemad is an investable local alternative. The objective is therefore benchmark-relative and is
described as information-ratio-style, not as a conventional Sharpe ratio.

**Why does the optimizer often choose 100% of one asset?**
The sample is short, the model is long-only, and some realized return differences are very large.
Boundary solutions are mathematically valid but demonstrate instability rather than certainty.

**Why can housing receive a large weight when it is illiquid?**
The model observes a smooth monthly transaction-price series but does not penalize illiquidity or
transaction costs. This is a known limitation, so the weight is a historical statistical result,
not an implementable recommendation.

**Why is 1405 separate?**
Only five months are available. It is included as YTD evidence and never treated as a full year.

**How was optimization checked?**
The selected Stage I result was compared with corner portfolios, equal weights, and 25,000
deterministic random portfolios per period. All selected scores were at least as high as the best
sampled alternative within numerical tolerance.

## Reproduction and verified status

From `asset_allocation/`, rebuild the derived panels, run the tests, and execute the notebook:

```powershell
$env:PYTHONPATH = "src"
python -m asset_allocation.build_monthly_return_panel
python -m pytest -q
python -m jupyter execute --inplace notebooks/asset_allocation_analysis.ipynb
```

The notebook also ends with an alternative fixed-volatility analysis. That specification uses
all 113 aligned months to estimate one annualized covariance matrix, then reuses it in every
year. Fixed annualized asset volatility is 35.03% for gold, 40.76% for equity, 15.04% for
housing, and 2.74% for fixed income. At gamma 4, its Stage II result differs most visibly in
1396: 33.76% risky and 66.24% fixed income, compared with 100% risky under year-specific
volatility. The full-sample method is more stable but contains look-ahead information.

The final notebook contains 57 cells, including 33 executed code cells, with zero error outputs.
The project test suite passes all eight tests.
