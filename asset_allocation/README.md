# Iran Cross-Asset Allocation

Study historical allocation across Tehran residential housing prices per square metre,
TGJU 18-karat gold (750), an exchange-traded Iranian fixed-income fund, and the Tehran Stock
Exchange total index.

ETF, اخزا, and bank-deposit histories are collected separately before a fixed-income proxy is
chosen. The initial ETF candidate is اعتمادآفرین پارسیان (ticker: اعتماد), reported to have
begun in 1394. IRR and monthly analysis are proposed, pending source and housing-frequency
validation.

## Current stage

Four assets are registered. Local inventory completed with the access limitation recorded in
[status](docs/STATUS.md). Fixed-income source collection has started; return construction,
optimization, and backtesting are not implemented yet.

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

Find the best four-asset weight basket for each Solar Hijri year by maximizing
`(w.T @ expected_returns) / sqrt(w.T @ covariance @ w)`, subject to `sum(w) = 1`.
This uses portfolio covariance and does not subtract a risk-free rate. Short-selling rules
and weight caps remain unresolved. The working interpretation is a retrospective optimum
for each year, with incomplete 1405 labeled year-to-date.

Collect and validate one asset at a time:
1. Fixed-income candidates: اعتماد, bank deposits, and اخزا, each kept separate.
2. TGJU 18-karat gold.
3. Tehran apartment sale price per square metre.
4. Tehran Stock Exchange total index, starting with TSETMC.

Only after coverage and source validation, construct comparable periodic returns and implement
yearly optimization with an equal-weight baseline. Monthly frequency is proposed; housing
coverage determines feasibility. Fund distributions must be included, housing appreciation
excludes rent, and annual yields must not be used directly as monthly returns.

The fixed-income collector uses the public TSETMC closing-price API for `اعتماد`
(`66818022341772870`) and archives each raw JSON response before atomically refreshing the
canonical CSV. Run it from this project directory with:

```powershell
$env:PYTHONPATH = 'src'
python -m asset_allocation.collectors.tsetmc_fixed_income
```

The authoritative bank-deposit collector transcribes the one-year column from the CBI annual
table supplied for this study. It selects the maximum when CBI publishes an interval:

```powershell
$env:PYTHONPATH = 'src'
python -m asset_allocation.collectors.cbi_one_year_deposit_rate
```


## Layout

- `config/`: selected assets and research scope; paths are project-relative unless explicitly external.
- `src/asset_allocation/` and `tests/`: reserved for implementation and verification.
- `data/raw/`: project-owned canonical histories and immutable snapshots.
- `data/interim/` and `data/processed/analysis/`: derived inputs and numerical results.
- `notebooks/`, `logs/`, `outputs/`, `reports/`: exploration, logs, and presentation.

See [workflow](docs/WORKFLOW.md), [data contract](docs/DATA_CONTRACT.md), and
[source register](docs/SOURCES.md), and [independence audit](docs/INDEPENDENCE.md).

