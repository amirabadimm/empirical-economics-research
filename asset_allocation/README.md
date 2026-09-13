# Iran Cross-Asset Allocation

Study historical allocation across Tehran residential housing prices per square metre,
TGJU 18-karat gold (750), an exchange-traded Iranian fixed-income fund, and the Tehran Stock
Exchange total index.

The primary housing corpus contains 87 official CBI Tehran transaction-market reports.
Raw PDFs are preserved under `data/raw/housing/cbi/reports/`; the reconstructed monthly
workbook remains in `data/interim` and is validated through a reproducible audit and
source-adjudication layer.

The fixed-income asset is اعتمادآفرین پارسیان (ticker: اعتماد). Competing deposit-rate
and اخزا proxies were evaluated and retired after the research window changed to
1395/01–1405/05. See the [fixed-income decision](docs/FIXED_INCOME.md).

## Current stage

Four assets are registered, and the canonical month-end level and monthly-return panels have
been built. The analysis notebook implements a source-audited, ex-post Stage I allocation of
gold, equity, and housing relative to the Etemad fixed-income benchmark for 1396-1404 and
the five-month 1405 YTD period. Stage II now reports an ex-post mean-variance sensitivity
analysis over an explicit grid of risk-aversion values; it is diagnostic and is not an
investor-specific recommendation: `notebooks/asset_allocation_analysis.ipynb`.

The notebook ends with a parallel alternative specification requested for comparison. It
estimates one covariance matrix from all aligned months in 1396–1405/05 and holds that risk
model fixed across yearly optimizations, while yearly realized returns continue to vary.

A presentation-ready account of the complete workflow, exact result tables, interpretation,
limitations, suggested storyline, and likely questions is available in
[`reports/ASSET_ALLOCATION_ANALYSIS_REPORT.md`](reports/ASSET_ALLOCATION_ANALYSIS_REPORT.md).
The same analysis is also available as a typeset-ready LaTeX document:
[`reports/ASSET_ALLOCATION_ANALYSIS.tex`](reports/ASSET_ALLOCATION_ANALYSIS.tex).

## Independent setup

Run from this project directory. This project has its own dependency manifest and no sibling
project imports or required workspace data paths. Create an environment here:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e ".[test]"
```

The manifest prepares the research environment. Documented collectors refresh canonical raw
market histories, while the panel builder validates and transforms those inputs. Optional
external datasets must never require another project's source code.
Existing shared canonical datasets remain under their current owner; independence does not
require duplicating or modifying them. No FX input is currently required by the chosen scope.

Verify the installation and data pipeline with:

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

## Research objective and collection sequence

The completed data objective is a canonical monthly-return history for all four assets from
1395/01 through 1405/05. Stage I maximizes the annualized mean differential return of a
buy-and-hold risky sleeve over Etemad divided by the sample volatility of that differential,
subject to long-only risky weights summing to one. Results are historical hindsight diagnostics,
not forecasts. Treat the 1405/01–1405/05 optimization strictly as a YTD diagnostic, not a
full-year result.

Collect and validate one asset at a time:
1. Fixed income: اعتماد only.
2. TGJU 18-karat gold.
3. Tehran apartment sale price per square metre.
4. Tehran Stock Exchange total index, starting with TSETMC.

Fund distributions must be included where applicable, housing appreciation excludes rent, and
annual yields must not be used directly as monthly returns. Report actual aligned coverage
before any future model is estimated.

The fixed-income collector uses the public TSETMC closing-price API for `اعتماد`
(`66818022341772870`) and archives each raw JSON response before atomically refreshing the
canonical CSV. Run it from this project directory with:

```powershell
$env:PYTHONPATH = 'src'
python -m asset_allocation.collectors.tsetmc_fixed_income
```

## Layout

- `config/`: selected assets and research scope; paths are project-relative unless explicitly external.
- `src/asset_allocation/` and `tests/`: collectors, validation, transformation, and tests.
- `data/raw/`: project-owned canonical histories and immutable snapshots.
- `data/interim/` and `data/processed/analysis/`: derived inputs and approved analytical tables.
- `notebooks/`: the presentation-ready research notebook.

See [workflow](docs/WORKFLOW.md), [data contract](docs/DATA_CONTRACT.md), and
[source register](docs/SOURCES.md), and [independence audit](docs/INDEPENDENCE.md).


## Canonical monthly asset panel

After collecting the authoritative daily sources, build Solar Hijri month-end levels and returns:

```powershell
$env:PYTHONPATH = 'src'
python -m asset_allocation.build_monthly_return_panel
```

The builder writes `data/processed/analysis/monthly_asset_levels.csv` and
`data/processed/analysis/monthly_asset_returns.csv`, plus the CBI-only diagnostic table
`housing_data_quality_audit.csv`. Daily assets use the last valid observation
within each Jalali month; اعتماد additionally requires `has_trade=true`. Returns are calculated
from adjacent month-end levels and missing values remain blank with an explicit reason.

CBI extraction adjudications are tracked in `config/housing_cbi_overrides.csv`. The builder
verifies each recorded original value before applying a source-cited correction, so workbook
changes cannot silently invalidate an override. The original extracted value, official report,
verification report, audit note, provenance method, and quality flag remain visible downstream.

No standalone portfolio-result CSV is authoritative. Stage I is executed transparently inside
the notebook and includes deterministic multi-start optimization plus comparison with corner,
equal-weight, and 25,000 random portfolios. Stage II keeps each Stage I risky sleeve fixed and
searches the long-only risky share on a deterministic grid for several risk-aversion values.

## TGJU 18-karat gold collector

Collect the daily price series with:

```powershell
$env:PYTHONPATH = 'src'
python -m asset_allocation.collectors.tgju_gold_18k
```
Housing uses official CBI monthly values through 1403/05 and an explicitly flagged, chain-linked
Kilid extension afterward. The common-period audit found weak agreement, so the extension is a
secondary proxy rather than an equivalent continuation; see [housing](docs/HOUSING.md).
