# Empirical Economics Research

[![CI](https://github.com/amirabadimm/empirical-economics-research/actions/workflows/ci.yml/badge.svg)](https://github.com/amirabadimm/empirical-economics-research/actions/workflows/ci.yml)

This repository is a portfolio of reproducible empirical economics research on price
formation, market integration, exchange-rate transmission, and applied market analysis.
The current projects study Iranian commodity certificate markets by combining domestic
physical-market transactions, international benchmark prices, and the free-market exchange
rate. Planned extensions include housing markets, the Iran Energy Exchange, and broader
applied microeconomic and macro-financial questions.

The repository is designed as a living research environment. It separates source-data
collection from analytical processing, preserves source provenance, records methodological
decisions, and tests the main economic transformations without committing credentials or
restricted raw market data.

## Research themes

- Price discovery and basis formation across related markets
- International-to-domestic price transmission
- Exchange-rate pass-through
- Commodity and energy market microstructure
- Housing prices and regional market dynamics
- Reproducible empirical methods for markets with sparse or irregular data

## Current projects

| Project | Economic question | Main method | Status |
|---|---|---|---|
| [Copper](commodity/copper/README.md) | How does the copper warehouse receipt trade relative to comparable domestic cathode and an LME–FX benchmark? | Volume-weighted physical benchmark; as-of alignment; interpolation of the physical/intrinsic ratio | Complete pipeline; analytical QA continues |
| [Zinc](commodity/zinc/README.md) | How does the zinc-ingot certificate compare with an eligible 99.97/99.98 domestic basket? | Grade-filtered volume weighting; three bubble definitions; time-series regression sensitivity | Complete benchmark and valuation pipeline |
| [Iron-ore pellet](commodity/pellet/README.md) | Which physical-market basket is economically comparable with the pellet certificate? | Producer/contract exploration before benchmark approval | Exploratory stage |
| [Bitumen](commodity/bitumen/README.md) | Which grade, market, and delivery terms match the bitumen certificate? | Broad raw collection followed by eligibility research | Data collection complete; underlying unresolved |
| [Warehouse fees](commodity/warehouse_fees/README.md) | How have daily storage fees for all documented commodity certificates changed? | Official notices plus archived official tables | 43 exact-date intervals and 30 observations back to 2016 |

Current data coverage and next actions are summarized in [docs/STATUS.md](docs/STATUS.md).

## Economic methodology

The completed Copper and Zinc studies distinguish three related but economically different
measures:

1. domestic physical price relative to an international LME–FX intrinsic proxy;
2. certificate price relative to the same intrinsic proxy;
3. certificate price relative to an estimated comparable domestic physical price.

For target date \(t\), the transparent international factor is

```text
intrinsic_price_t = (LME_cash_USD_per_ton_t / 1000) × USD_IRR_t
```

LME and FX observations are joined as-of using the latest value on or before the target date,
with source dates and ages retained. Because domestic physical trading is sparse, the primary
certificate estimator interpolates the observed ratio of domestic physical price to intrinsic
price between exact certificate/physical anchors. It does not extrapolate outside the observed
anchor range. Regression is retained as a sensitivity analysis rather than the official method.

## Reproducibility and data governance

- Complete source responses are archived locally as immutable snapshots.
- Canonical raw CSVs are refreshed only by documented incremental, idempotent, and atomic collectors.
- Zero-trade source observations remain in raw data but do not enter traded-price benchmarks.
- Derived datasets are produced by versioned scripts under `src/<project>/processing`.
- Notebooks are analytical and presentation layers; they do not modify canonical raw data.
- Source dates, units, calendar conversions, and data ages are validated explicitly.
- Credentials are read only from environment variables and are never committed.

Raw market data, source snapshots, local environments, and bulk generated datasets are excluded
from Git. See [DATA_AVAILABILITY.md](DATA_AVAILABILITY.md) and
[docs/DATA_POLICY.md](docs/DATA_POLICY.md) for the rationale and reconstruction process.

## Repository structure

```text
commodity/                 Commodity-specific empirical projects
  copper/
  zinc/
  pellet/
  bitumen/
shared/ime_data/           Reusable Iran Mercantile Exchange collection logic
reports/                   Research reports, source documents, and reproducible figures
docs/                      Workspace architecture, status, and data policy
```

Future research domains can be added beside `commodity/` rather than forced into the commodity
schema—for example, `housing/` or `energy/`.

## Environment

Python 3.11 or newer is required. From the repository root:

```bash
python -m venv .venv
source .venv/bin/activate        # Windows Git Bash
python -m pip install -e ".[dev,notebooks]"
```

On Windows PowerShell, activate with `.\.venv\Scripts\Activate.ps1`.

Run the network-free tests:

```bash
python -m pytest -q
```

Tests that validate local canonical datasets skip automatically when those unversioned datasets
are unavailable. Parser, scope, calendar, atomic-write, and synthetic reconstruction tests remain
fully executable in a clean clone.

## Reports

- [Copper research report](reports/copper/research/copper_research_report.tex)
- [Zinc research report](reports/zinc/research/zinc_research_report.tex)

Each report documents data sources, benchmark construction, all three bubble definitions,
validation, results, limitations, and data-driven figures.

## Limitations

The international intrinsic series is a transparent benchmark, not a full import-parity price.
Taxes, transport, storage, financing, quality, delivery conditions, liquidity, and institutional
constraints may explain part of the domestic basis. Sparse physical-market anchors also limit
statistical precision. Results are research outputs and are not investment advice.

## Citation and reuse

Citation metadata is provided in [CITATION.cff](CITATION.cff). Source code is released under
the [MIT License](LICENSE); that license does **not** grant redistribution rights for third-party
market data. Contributions should follow [CONTRIBUTING.md](CONTRIBUTING.md).
