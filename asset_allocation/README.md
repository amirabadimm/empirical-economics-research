# Iran Cross-Asset Allocation

Study historical allocation across Tehran residential housing prices per square metre,
TGJU 18-karat gold (750), an exchange-traded Iranian fixed-income fund, and the Tehran Stock
Exchange total index.

The primary housing corpus contains 87 official CBI Tehran transaction-market reports.
Raw PDFs are preserved under `data/raw/housing/cbi/reports/`; the reconstructed monthly
workbook remains in `data/interim` pending independent validation.

The fixed-income asset is اعتمادآفرین پارسیان (ticker: اعتماد). Competing deposit-rate
and اخزا proxies were evaluated and retired after the research window changed to
1395/01–1405/05. See the [fixed-income decision](docs/FIXED_INCOME.md).

## Current stage

Four assets are registered, and the canonical month-end level and monthly-return panels have
been built. Earlier portfolio-optimization results were removed because the risk-adjusted
objective requires a new specification. The analysis notebook now audits the retained inputs
only: `analysis/asset_allocation_analysis.ipynb`.

## Independent setup

Run from this project directory. This project has its own dependency manifest and no sibling
project imports or required workspace data paths. Create an environment here:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

The manifest prepares the research environment; there is no executable analysis command yet.
Source adapters will collect from documented providers or accept explicit external input
paths. An optional external dataset must never require another project's source code.
Existing shared canonical datasets remain under their current owner; independence does not
require duplicating or modifying them. No FX input is currently required by the chosen scope.

## Research objective and collection sequence

The completed data objective is a canonical monthly-return history for all four assets from
1395/01 through 1405/05. The portfolio objective, risk measure, constraints, and estimation
design will be specified before any new weights are calculated. Treat 1405/01–1405/05 as YTD.

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
- `src/asset_allocation/` and `tests/`: reserved for implementation and verification.
- `data/raw/`: project-owned canonical histories and immutable snapshots.
- `data/interim/` and `data/processed/analysis/`: derived inputs and approved analytical tables.
- `notebooks/`, `logs/`, `outputs/`, `reports/`: exploration, logs, and presentation.

See [workflow](docs/WORKFLOW.md), [data contract](docs/DATA_CONTRACT.md), and
[source register](docs/SOURCES.md), and [independence audit](docs/INDEPENDENCE.md).


## Canonical monthly asset panel

After collecting the authoritative daily sources, build Solar Hijri month-end levels and returns:

```powershell
$env:PYTHONPATH = 'src'
python -m asset_allocation.build_monthly_return_panel
```

The builder writes `data/processed/analysis/monthly_asset_levels.csv` and
`data/processed/analysis/monthly_asset_returns.csv`. Daily assets use the last valid observation
within each Jalali month; اعتماد additionally requires `has_trade=true`. Returns are calculated
from adjacent month-end levels and missing values remain blank with an explicit reason.

No portfolio-result dataset is currently authoritative. The previous annual allocation engine,
its generated results, and its diagnostics were retired pending a revised risk-adjusted design.

## TGJU 18-karat gold collector

Collect the daily price series with:

```powershell
$env:PYTHONPATH = 'src'
python -m asset_allocation.collectors.tgju_gold_18k
```
Housing uses official CBI monthly values through 1403/05 and an explicitly flagged, chain-linked
Kilid extension afterward. The common-period audit found weak agreement, so the extension is a
secondary proxy rather than an equivalent continuation; see [housing](docs/HOUSING.md).
