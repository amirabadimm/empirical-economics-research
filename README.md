# Empirical Economics Research

Gold's five-fund NAV research phase was closed on 2026-10-03 at the September 29
data checkpoint. Small NAV gaps and disputed Gohar dates remain flagged in the
[reliability audit](commodity/gold/docs/NAV_RELIABILITY.md); maintenance refreshes
remain available. The closeout did not collect newer data.

Documentation reviewed: 2026-09-28; gold NAV reliability updated 2026-09-29.
Tala, Kahroba, and Ganj match their manager records on shared dates; Gohar has
disputed values and Ayar's selected Fipiran history has gaps. See the
[reliability audit](commodity/gold/docs/NAV_RELIABILITY.md).
Mesghal's live historical NAV recheck yielded no accepted series; see
[the validation report](commodity/gold/docs/MESGHAL_NAV_VALIDATION.md).
Data checkpoints are project-specific; see
[current research status](docs/STATUS.md) and [workspace workflow](docs/WORKFLOW.md).

The six certificate research products share an execution engine and explicit per-product
pipeline manifests. See [Certificate research engine](shared/certificate_pipeline/README.md)
for offline rebuilds, optional source refresh, and the distinction between delivered
software and product-specific economic assumptions.

[![CI](https://github.com/amirabadimm/empirical-economics-research/actions/workflows/ci.yml/badge.svg)](https://github.com/amirabadimm/empirical-economics-research/actions/workflows/ci.yml)

This repository is a portfolio of reproducible empirical economics research on price
formation, market integration, exchange-rate transmission, and applied market analysis.
Projects cover Iranian commodity certificates, gold-fund NAV premiums, cross-asset allocation,
macroeconomic USD/IRR inputs, issuer financial statements, and ETF options. Commodity studies
combine domestic physical trades, international benchmarks, and exchange rates. The Iran Energy
Exchange feasibility study is retained as a closed research project.

The repository is designed as a living research environment. It separates source-data
collection from analytical processing, preserves source provenance, records methodological
decisions, and tests the main economic transformations without committing credentials or
restricted raw market data.

## Research themes

- Price discovery and basis formation across related markets
- International-to-domestic price transmission
- Exchange-rate pass-through
- Commodity and energy market microstructure
- Reproducible empirical methods for markets with sparse or irregular data

## Current projects

| Project | Economic question | Main method | Status |
|---|---|---|---|
| [Copper](commodity/copper/README.md) | How does the copper warehouse receipt trade relative to comparable domestic cathode and an LME–FX benchmark? | Volume-weighted physical benchmark; bounded physical/intrinsic ratio interpolation | 206 primary comparisons through 2026-09-20; refreshed 2026-09-27 |
| [Zinc](commodity/zinc/README.md) | How does the zinc-ingot certificate compare with an eligible 99.97/99.98 domestic basket? | Grade-filtered volume weighting; three bubble definitions | 206 primary comparisons through 2026-09-20; refreshed 2026-09-26 |
| [Gold ETFs](commodity/gold/README.md) | How do five liquid gold ETFs trade relative to redemption NAV? | Bounded TSETMC prices; five Fipiran NAV histories, with manager corroboration | September 29 incremental refresh: Ayar 448/465, Tala 465/465, Kahroba 464/465, Ganj 462/465, Gohar 464/464 two-year matches; Gohar disputed dates flagged |
| [Silver](commodity/silver/README.md) | How does the silver-bar certificate compare with eligible 999.9 cash trades? | Exact-date diagnostic with gram-to-kilogram conversion | Architecture and tests implemented; no data collected or benchmark approved |
| [Iron-ore pellet](commodity/pellet/README.md) | Which physical-market basket is economically comparable with the pellet certificate? | Producer/contract exploration before benchmark approval | Exploratory stage |
| [Bitumen](commodity/bitumen/README.md) | Which grade, market, and delivery terms match the bitumen certificate? | Broad raw collection followed by eligibility research | Data collection complete; underlying unresolved |
| [Steel rebar](commodity/rebar/README.md) | How does the certificate compare with same-day A3/18 cash trades and an A3/12 sensitivity? | Strict exact-date bubbles with explicit cross-diameter labeling | 5 A3/18 matches and 49 A3/12 sensitivity dates; specification QA open |
| [Pista](goods/pista/README.md) | What is the trading history of the reopened continuous pistachio certificate? | Official IME collection, Abtahi weekly-price audit, and bounded proxy comparison | 16 indicative premium dates; price unit and product match unconfirmed |
| [Warehouse fees](commodity/warehouse_fees/README.md) | How have daily storage fees for all documented commodity certificates changed? | Official notices plus archived official tables | 43 exact-date intervals and 30 observations back to 2016 |
| [Iran Energy Exchange](energy_exchange/README.md) | Is the certificate market sufficiently active for a broader empirical project? | Public-source mapping plus complete 21-symbol certificate-history feasibility test | Closed: activity too sparse and concentrated for the intended project |
| [National Copper — Codal](codal/national_copper/README.md) | What can issuer disclosures reveal about National Iranian Copper Industries Company? | Cumulative-to-quarter conversion with explicit audit lineage | 75 valid quarters; 18 complete years |
| [Ahrom options](options/README.md) | What is the historical contract universe and available daily option history for the Ahrom ETF? | TSETMC instrument discovery with OptionBaaz daily response archive | 996 contracts; 8,903 rows since 2025-12-17; older OptionBaaz gap |

Current data coverage and next actions are summarized in [docs/STATUS.md](docs/STATUS.md).

Two independent projects extend the portfolio:

- [Cross-asset allocation](asset_allocation/README.md): housing, gold, equities, and Etemad
  fixed-income monthly panels; historical optimization and risk-aversion sensitivity are
  implemented. The expert survey and final forward-looking allocation remain pending.
- [Economic USD/IRR](economic_usd/README.md): USD, liquidity, Iranian CPI, and U.S. CPI
  preparation is implemented. Dollar-liquidity valuation and five-anchor PPP are planned
  but have not been calculated.

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

Copper, Zinc, and Gold report signed expanding percentile ranks with equal weights and
exponential recency weights (default half-life: 90 calendar days). These describe historical
samples. Interpolated Copper/Zinc values can use later anchors, so their percentile histories
are not vintage-safe backtests. Gold uses exact-date NAV without filling missing dates.

- Complete IME physical responses are archived once in a shared content-addressed store; historical
  project-local snapshots remain frozen immutable evidence.
- Canonical raw CSVs are refreshed only by documented incremental, idempotent, and atomic collectors.
- Zero-trade source observations remain in raw data but do not enter traded-price benchmarks.
- Derived datasets are produced by versioned scripts under `src/<project>/processing`.
- Notebooks are analytical and presentation layers; they do not modify canonical raw data.
- Source dates, units, calendar conversions, and data ages are validated explicitly.
- Credentials are read only from environment variables and are never committed.
- Cross-commodity inputs have one canonical owner; Copper and Zinc share the same USD/IRR series.

Raw market data, source snapshots, local environments, and bulk generated datasets are excluded
from Git. See [DATA_AVAILABILITY.md](DATA_AVAILABILITY.md) and
[docs/DATA_POLICY.md](docs/DATA_POLICY.md) for the rationale and reconstruction process.

## Repository structure

Commodity data follows [the shared data architecture](docs/DATA_ARCHITECTURE.md): canonical
physical and certificate records are stored independently under `data/raw`, while every bubble
or comparison table is derived under `data/processed/bubble`.

```text
commodity/                 Commodity-specific empirical projects
  copper/
  zinc/
  pellet/
  bitumen/
  rebar/
  gold/
  silver/
  warehouse_fees/
goods/pista/               Pistachio certificates and weekly-price audit
asset_allocation/          Independent four-asset panels and historical allocation pilot
economic_usd/              Independent macroeconomic inputs and valuation plan
options/                   Ahrom option discovery and available daily histories
shared/certificate_pipeline/ Six-product execution and Power BI delivery engine
shared/ime_data/           Reusable Iran Mercantile Exchange collection logic
shared/market_data/        Shared cross-commodity inputs such as canonical USD/IRR
shared/market_analysis/    Commodity-invariant analysis and model-selection mechanics
shared/notebook_tools/     Read-only standardized commodity notebook dashboards
energy_exchange/           Iran Energy Exchange documentation and research
codal/                     Issuer-level Codal disclosure research
reports/                   Research reports, source documents, and reproducible figures
docs/                      Workspace architecture, status, and data policy
```

Future research domains can be added beside `commodity/` rather than forced into the commodity
schema—for example, `energy_exchange/`.

`economic_usd/` is an independent, data-preparation-only project for future fundamental USD/IRR research. It owns copies of its Iranian liquidity, free-market USD, Iranian CPI, and U.S. CPI inputs and does not import sibling-project code.

## Environment

Python 3.11 or newer is required. The two repositories on this workstation share the sibling
environment `..\Finenv`. From the repository root in PowerShell:

```powershell
py -m venv ..\Finenv
..\Finenv\Scripts\Activate.ps1
python -m pip install -e ".[dev,notebooks]"
```

VS Code is configured to select this shared environment automatically. `pyproject.toml` is the
canonical dependency and CI configuration; the installation above includes development and
notebook tools. CI creates an isolated environment. Asset Allocation and Economic USD document
their own independent environment setup.

Run the network-free tests:

```bash
python -m pytest -q
```

Tests that validate local canonical datasets skip automatically when those unversioned datasets
are unavailable. Parser, scope, calendar, atomic-write, and synthetic reconstruction tests remain
fully executable in a clean clone.

Root pytest discovers `commodity`, `codal`, `energy_exchange`, `shared`, and `options`.
Run `python -m pytest -q goods/pista/tests` separately; Asset Allocation and Economic USD
document their own test commands. Root CI does not automatically run those three suites.

## Rebuild and refresh

From the repository root after environment setup:

```powershell
# Inspect all six certificate pipelines without collecting or writing data.
python -m shared.certificate_pipeline.refresh all --plan
# Rebuild from existing local inputs (raw data are not included in a clean clone).
python -m shared.certificate_pipeline.refresh all
# Explicit online source collection followed by a production rebuild.
python -m shared.certificate_pipeline.refresh copper --collect
# Five-fund daily gold histories (bounded prices and recent Fipiran NAV).
python commodity/gold/collect_daily.py
python commodity/gold/collect_fipiran_nav.py
python commodity/gold/build_two_years.py --as-of 2026-09-28
# Run collectors with --full periodically to capture older revisions.
# Independent Ayar bubble workflow; add --collect to fetch Fipiran historical NAV and TSETMC prices first.
python commodity/gold/refresh.py
```

The six-product engine covers Copper, Zinc, Pellet, Rebar, Bitumen, and Pista. Each retains
local `refresh_powerbi.py` and `.cmd` launchers. Pista requires a manually supplied Abtahi
workbook. Gold and Silver have separate entry points; Silver's offline rebuild requires inputs
that have not yet been collected. See [workspace workflow](docs/WORKFLOW.md).

## Reports

- [Copper research report](reports/copper/research/copper_research_report.tex)
- [Zinc research report](reports/zinc/research/zinc_research_report.tex)
- [Cross-asset allocation pilot](asset_allocation/reports/ASSET_ALLOCATION_ANALYSIS_REPORT.md)
- [Pellet exploratory report](commodity/pellet/reports/FINAL_REPORT.md)

Copper and Zinc reports document their three valuation comparisons and reproducible figures.
Project-local reports retain their own scope and data vintage; a documentation review does
not imply that every report or notebook has been re-executed.

## Limitations

The international intrinsic series is a transparent benchmark, not a full import-parity price.
Taxes, transport, storage, financing, quality, delivery conditions, liquidity, and institutional
constraints may explain part of the domestic basis. Sparse physical-market anchors also limit
statistical precision. Results are research outputs and are not investment advice.

## Citation and reuse

Citation metadata is provided in [CITATION.cff](CITATION.cff). Source code is released under
the [MIT License](LICENSE); that license does **not** grant redistribution rights for third-party
market data. Contributions should follow [CONTRIBUTING.md](CONTRIBUTING.md).
