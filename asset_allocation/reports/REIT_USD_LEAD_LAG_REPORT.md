# Iranian REITs and USD/IRR: returns and weekly lags

Data endpoint: 2026-10-02. Report generated: 2026-10-06 16:33 Asia/Tehran. Run `python -m asset_allocation.build_reit_usd_report` from this project to generate the [local interactive Plotly report](REIT_USD_LEAD_LAG_REPORT.html), or open the versioned [analysis notebook](../notebooks/iran_reits_cross_asset_analysis.ipynb) for its charts.

The four funds are Arzesh Maskan, Kelid, Danik, and Kakh. Returns use raw traded closes with fractional-unit reinvestment of the three approved distributions in the current ledger. This assumes immediate cash availability at assembly. Arzesh Maskan and Kakh have no recorded event; their displayed paths do not establish complete total return.

## Two-year cumulative comparison

| Asset | Baseline | Last observation | Observed points | Cumulative return |
| --- | --- | --- | --- | --- |
| TEDPIX | 2024-10-04 | 2026-10-02 | 105 weeks | +267.2% |
| USD/IRR | 2024-10-04 | 2026-10-02 | 104 weeks | +312.8% |
| Arzesh Maskan | 2024-10-04 | 2026-10-02 | 94 weeks | +156.8% |
| Kelid | 2024-10-04 | 2026-10-02 | 93 weeks | +97.9% |
| Danik | 2024-10-04 | 2026-10-02 | 94 weeks | +74.3% |
| Kakh | 2026-02-27 | 2026-10-02 | 23 weeks | +27.6% |
| Tehran housing | 2024-10-21 | 2026-09-22 | 24 months | +160.7% |

Housing is a monthly, chain-linked Kilid listing-price proxy. Kakh starts later than the other market series, so cumulative values do not all cover identical holding periods.

## Recorded reinvestments

| Fund | Assembly date | Purchase date | Cash IRR/unit | Purchase close IRR | Units after | Evidence |
| --- | --- | --- | --- | --- | --- | --- |
| Kelid | 2025-10-08 | 2025-10-11 | 907 | 10,380 | 1.087380 | user_supplied_and_manager_confirmed |
| Kelid | 2026-09-16 | 2026-09-19 | 864 | 16,461 | 1.144454 | user_supplied |
| Danik | 2025-08-18 | 2025-08-18 | 1,800 | 11,057 | 1.162793 | user_supplied |

## Weekly USD lag correlations

Each fund's lag 0–4 estimates use the same paired weeks. A dash means fewer than 74 common weeks or insufficient variation. USD returns crossing the source-method boundary are excluded.

| Fund | Common weeks | Lag 0 | Lag 1 | Lag 2 | Lag 3 | Lag 4 |
| --- | --- | --- | --- | --- | --- | --- |
| Arzesh Maskan | 84 | -0.091 | +0.233 | +0.190 | +0.143 | -0.032 |
| Kelid | 81 | -0.080 | +0.140 | +0.180 | +0.076 | -0.063 |
| Danik | 84 | -0.009 | +0.190 | +0.192 | +0.136 | -0.125 |
| Kakh | 16 | — | — | — | — | — |

## Conditional predictive regression

The weekly model includes REIT lag 1, USD lags 1 and 2, and TEDPIX lag 1. The joint USD test uses HAC(4); its FDR p-value adjusts across reportable funds. ΔR² is in-sample against a same-date model without USD. At least 52 complete weeks are required.

| Fund | Weeks | USD lag 1 beta | USD lag 2 beta | Joint p | FDR p | Delta in-sample R2 | Status |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Arzesh Maskan | 87 | +0.437 | +0.095 | 0.0020 | 0.0059 | +0.064 | Reported |
| Kelid | 84 | +0.187 | +0.007 | 0.0431 | 0.0431 | +0.036 | Reported |
| Danik | 87 | +0.283 | +0.180 | 0.0041 | 0.0062 | +0.053 | Reported |
| Kakh | 18 | — | — | — | — | — | Insufficient history |

These results are descriptive and in-sample. They do not establish causation or out-of-sample forecasting skill. Dividend histories and actual cash dates need further verification. See [the workflow](../docs/WORKFLOW.md) and [dividend audit](../docs/REIT_DIVIDEND_AUDIT.md).
