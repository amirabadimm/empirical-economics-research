# Iran Cross-Asset Allocation

## Research question

How stable are hindsight-efficient allocations across Iranian gold, equities, Tehran residential housing, and fixed income, and what does that instability imply for a future forward-looking allocation framework?

This project is deliberately split into two parts. The completed component is a historical pilot used to build, audit, and test the four-asset dataset and allocation machinery. The intended final component is forward-looking and will require explicit expectations rather than realized historical returns.

## Assets and data

The four assets are:

- TGJU 18-karat gold;
- TEDPIX, the Tehran Stock Exchange total index;
- Tehran residential transaction prices per square metre;
- Etemad (`اعتماد`), an exchange-traded Iranian fixed-income fund.

The canonical monthly panel spans Solar Hijri 1395/01 through 1405/06, with the historical optimization sample beginning in 1396 because the housing series does not contain the 1394/12 level required to compute a 1395/01 return.

Daily traded assets use the final valid observation in each Jalali month. Returns are calculated only from adjacent month-end levels; missing observations remain missing rather than being forward-filled or replaced with zero.

## Four real estate funds and reconstructed returns

The single active notebook, `notebooks/iran_reits_cross_asset_analysis.ipynb`, covers Kelid, Danik, Arzesh Maskan, and Kakh. Its nine Plotly figures include six frequency-matched heatmaps: TEDPIX daily (1/3/6/12 months), weekly (1/3/6/12/24), and monthly (12/24/36); housing monthly (12/24/36); USD/IRR daily (1/3); and weekly REIT returns against USD/IRR returns 4/13/26 completed weeks earlier over a two-year sample. Housing is observed monthly, so no daily or weekly housing returns are invented. Every reported correlation needs at least five pairs, 70% coverage of its stated window, and nonconstant returns. The two-year cumulative comparison excludes Kakh because its history starts later. Daily, weekly, and monthly fund returns use compounded units times raw traded closes, never exchange-adjusted fund prices.

The two-year cumulative Plotly chart also has a dropdown for translucent month-end asset-mix bands for Arzesh Maskan or Danik. The right axis shows housing, fixed income, and the remainder (cash, equity, and other/receivables), summing to 100%; the left axis continues to show cumulative returns. The user-supplied Codal-derived 24-month workbook is retained as an immutable, ignored interim snapshot at `data/interim/codal_reit_asset_mix/REIT_Asset_Mix_24M.xlsx`. Run `python -m asset_allocation.build_reit_asset_mix` to validate it and rebuild the ignored `data/processed/analysis/reit_codal_asset_mix_monthly.csv` before executing the notebook. The 48 allocation observations run from 1403/07 to 1405/06; three rows carry source quality flags. Shading connects monthly observations for display only and does not imply weekly allocation observations or fund returns.

The allocation fills use explicitly low-alpha colors (about 5–7% opacity) so the cumulative-return lines remain legible.

Run `python -m asset_allocation.build_reit_assembly_reinvestment`, `python -m asset_allocation.build_reit_two_year_cumulative`, `python -m asset_allocation.build_reit_reinvested_correlations`, and `python -m asset_allocation.analyze_reit_usd_weekly_predictive` with `PYTHONPATH=src`, then execute the notebook. The approved-distribution ledger contains user-supplied Danik 1,800 IRR and Kelid 907 and 864 IRR events. Fractional units are bought at the first traded close on or after assembly, assuming immediate cash availability. Actual payment dates and complete payout histories remain unresolved. Arzesh Maskan and Kakh have no approved events in this ledger; their reconstructed paths equal traded-price paths without proving zero dividends. The separate payment-date audit is not mixed into this scenario.

The active weekly dollar-lead heatmap compares each fund's reconstructed weekly return with USD/IRR returns 4, 13, and 26 completed weeks earlier within the last 24 Jalali months; at least 74 paired weeks are required. The separate predictive model uses the fund's own prior weekly return, USD lags one and two, and TEDPIX's prior weekly return, requiring at least 52 complete weeks. Its table reports the unadjusted joint HAC/Newey-West p-value for the two USD coefficients and incremental in-sample R² against the same-date baseline without USD. Kakh has insufficient history for the two-year lead and predictive estimates. USD returns spanning its source-method change are excluded. These statistics do not establish causation or out-of-sample forecasting skill.

The housing overlay stays at observed monthly frequency and is a flagged Kilid listing-price proxy. See [`docs/HOUSING.md`](docs/HOUSING.md) and [`docs/REIT_DIVIDEND_AUDIT.md`](docs/REIT_DIVIDEND_AUDIT.md) for source limitations.

After the monthly REIT-return builder and four-asset housing panel are current, run `python -m asset_allocation.build_reit_requested_heatmaps`. It builds the six active grids in `data/processed/analysis/reit_requested_correlation_heatmaps.csv`. The 24-month same-month housing cells have 22 pairs for Arzesh Maskan (−0.064), 21 for Kelid (+0.094), and 22 for Danik (−0.178); Kakh has four and is suppressed. Arzesh Maskan and Danik lack REIT returns in 1405/01–02; Kelid also lacks 1403/07. Housing in this window is the flagged Kilid listing-price proxy. These descriptive correlations do not establish causation.

Generate the single table-first [LaTeX research report](reports/REIT_CROSS_ASSET_ANALYSIS.tex) with `python -m asset_allocation.build_reit_latex_report` after rebuilding the derivatives above. It includes the two-year cumulative comparison, all recorded distribution and reinvestment results, latest weekly and monthly fund returns, every cell of the six correlation grids with paired counts, the predictive-regression and coverage tables, and data-grounded conclusions. The generator reads processed tables only; it does not create HTML or modify canonical sources.

## Housing data integrity

A concise manager-facing companion is available at `reports/REIT_MANAGEMENT_BRIEF.tex`: key findings and qualifications first, followed by three supporting tables covering performance, asset allocation, and housing correlation. Rebuild with `python -m asset_allocation.build_reit_management_brief`; review its dated narrative whenever the research inputs change.

The expanded English REIT performance report (2026-10-08) also covers benchmark return gaps, relative ending wealth, calendar-day CAGR, observed weekly drawdowns, the two funds' complete asset-mix histories, management-attribution limits, full regression controls and fit, all two-year weekly/monthly returns, and the 80-cell coverage audit. It is a self-contained LaTeX source suitable for translation. Rebuild the asset-mix derivative before the report. Nominal underperformance and weak housing co-movement are documented separately from unproven causal claims about management.

Housing required the most substantial source audit. The project reconstructs the official CBI Tehran transaction-price series and keeps source adjudications in a reproducible override layer. Four material extraction or transcription values were checked against official reports and corrected with provenance retained downstream.

One malformed observation would otherwise have created an artificial approximately -99% / +13,000% monthly return pair. After source review and correction, the affected annual housing-volatility estimate falls from an obviously spurious level to an economically plausible range.

Official CBI coverage ends at 1403/05. A Kilid-based extension is chain-linked afterward and explicitly flagged as a secondary proxy rather than treated as an equivalent continuation. Common-period diagnostics show weak enough agreement that the source transition remains an analytical limitation.

Detailed evidence and decisions are documented in [`docs/HOUSING.md`](docs/HOUSING.md), [`docs/DATA_CONTRACT.md`](docs/DATA_CONTRACT.md), and [`config/housing_cbi_overrides.csv`](config/housing_cbi_overrides.csv).

## Historical pilot

The pilot separates two decisions that are often mixed together.

### Stage I — risky-sleeve composition

Stage I chooses long-only weights across gold, equity, and housing that maximize the annualized mean differential return over Etemad per unit of tracking error.

The portfolio is modeled as buy-and-hold within the year rather than mechanically rebalanced every month. Optimization uses deterministic multi-start search and is checked against corner portfolios, equal weights, and 25,000 random simplex portfolios.

### Stage II — risky exposure

Stage II holds the selected risky sleeve fixed and varies the share of wealth allocated to that sleeve versus Etemad under an explicit mean-variance objective and a grid of risk-aversion parameters.

This separates the question “what risky mix performed best?” from “how much risky exposure would the stated utility function choose?”

## Main finding

The central result is instability rather than a single permanent portfolio.

Across the historical periods analyzed, gold is the dominant risky asset in five periods, housing in four, and equity in one. Five of the ten Stage-I solutions place the entire risky sleeve in one asset.

This is an economically important finding: the hindsight-efficient risky composition is highly regime-dependent. The pilot therefore does **not** identify a stable all-weather allocation.

Fixed income outperforms the best available risky sleeve on the benchmark-relative criterion in 1400 and 1402, causing Stage II to select 100% fixed income in those years across the tested risk-aversion values. In some high-return years, the model instead selects full risky exposure even at high risk aversion because realized nominal return spreads are exceptionally large.

These are ex-post diagnostics, not forecasts or investor recommendations.

## Current status

The canonical four-asset level and return panels are complete, and the historical Stage-I and Stage-II pilot is implemented in [`notebooks/asset_allocation_analysis.ipynb`](notebooks/asset_allocation_analysis.ipynb).

A presentation-ready interpretation, exact result tables, limitations, and likely discussion questions are documented in [`reports/ASSET_ALLOCATION_ANALYSIS_REPORT.md`](reports/ASSET_ALLOCATION_ANALYSIS_REPORT.md). A typeset-ready version is available in [`reports/ASSET_ALLOCATION_ANALYSIS.tex`](reports/ASSET_ALLOCATION_ANALYSIS.tex).

The final forward-looking allocation has **not** been produced. It remains contingent on a documented expectation-building stage and a redesigned risk estimate using only information available at each allocation date.

## Reproduction

This project has its own dependency manifest and does not require sibling-project source code.

```bash
cd asset_allocation
python -m venv .venv
python -m pip install -e ".[test]"
python -m pytest -q
```

To rebuild the canonical monthly panel:

```bash
PYTHONPATH=src python -m asset_allocation.build_monthly_return_panel
```

On PowerShell, set `PYTHONPATH` for the current session before running the same module.

The builder writes:

- `data/processed/analysis/monthly_asset_levels.csv`;
- `data/processed/analysis/monthly_asset_returns.csv`;
- `data/processed/analysis/housing_data_quality_audit.csv`.

Project-owned raw histories and source evidence remain under `data/raw` and are excluded from Git.

## Project structure

- `config/` — selected assets, research scope, and source-adjudication rules;
- `src/asset_allocation/` — collectors, validation, and panel construction;
- `tests/` — project-specific validation;
- `data/raw/` — project-owned canonical histories and immutable source evidence;
- `data/interim/` and `data/processed/analysis/` — reproducible derived stages;
- `notebooks/` — historical pilot analysis;
- `reports/` — presentation-ready interpretation and tables;
- `docs/` — data contract, source decisions, workflow, and project status.

## Limitations

Housing is not observed with the same frequency or market microstructure as exchange-traded assets, so its measured monthly volatility is not directly comparable to continuously traded risk. The post-CBI housing extension is a proxy and contains an explicit source transition.

The historical pilot also estimates performance using realized returns, so it is inherently hindsight-based. The operational model must replace realized-return inputs with a documented forward-looking expectation process and must estimate risk from an information set available at the allocation date.

For detailed source and methodological decisions, see [`docs/WORKFLOW.md`](docs/WORKFLOW.md), [`docs/SOURCES.md`](docs/SOURCES.md), [`docs/FIXED_INCOME.md`](docs/FIXED_INCOME.md), and [`docs/INDEPENDENCE.md`](docs/INDEPENDENCE.md).
