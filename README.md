# Empirical Economics Research

**Mohammad Mahdi Amirabadi**
Reproducible empirical research on financial, commodity, and macroeconomic markets, with a focus on Iran.

[![CI](https://github.com/amirabadimm/empirical-economics-research/actions/workflows/ci.yml/badge.svg)](https://github.com/amirabadimm/empirical-economics-research/actions/workflows/ci.yml)

This repository is a research portfolio built around a simple standard: an empirical result should be traceable to its source data, economically interpretable, reproducible from code, and explicit about measurement limits. The projects combine market data engineering with applied economic analysis in price formation, asset pricing, market integration, portfolio choice, and derivatives.

The repository is intentionally broader than a single paper. The strongest completed and near-completed projects are highlighted below; exploratory and infrastructure-heavy work is kept separate from headline research claims.

## Featured research

| Project | Research question | Data and method | Selected result / status |
|---|---|---|---|
| [Gold ETF NAV premiums](commodity/gold/README.md) | How do liquid Iranian gold ETFs trade relative to same-date redemption NAV, and how unusual is a given premium or discount relative to each fund's own history? | Five ETFs; TSETMC prices; Fipiran redemption NAV; exact-date matching; expanding and recency-weighted empirical distributions | 8,000+ matched daily bubble observations in PostgreSQL, with explicit NAV-source reliability checks and a separate disposable intraday monitor |
| [Copper certificate valuation](commodity/copper/README.md) | Does the copper warehouse receipt trade at a premium or discount to a comparable domestic physical-market value? | IME certificate and physical trades; LME cash copper; USD/IRR; bounded interpolation between observed physical anchors | 206 certificate-trading days; estimated certificate premium to domestic physical value averages **5.73%**, median **7.16%** |
| [Zinc certificate valuation](commodity/zinc/README.md) | How does the zinc-ingot certificate compare with an eligible domestic physical basket and an LME-FX benchmark? | Grade-filtered physical basket; certificate trades; LME zinc; USD/IRR; bounded interpolation | 206 modeled days; certificate premium to estimated domestic physical value averages **0.80%**, versus an average direct certificate/intrinsic discount of **20.54%** |
| [Iran cross-asset allocation](asset_allocation/README.md) | How unstable are hindsight-efficient allocations across gold, equities, Tehran housing, and fixed income? | Monthly asset panels; source-audited housing series; long-only portfolio optimization; explicit risk-aversion sensitivity | Historical optimum is strongly regime-dependent; five of ten Stage-I solutions are corner portfolios, so the exercise does not identify a stable all-weather allocation |

## Research profile

The portfolio emphasizes four recurring themes:

- **Price formation and market integration:** comparing exchange-traded claims with economically comparable physical-market values.
- **Asset pricing and relative value:** NAV premiums, discounts, empirical distributions, and benchmark construction.
- **Macroeconomic transmission:** USD/IRR, international commodity prices, domestic price levels, and planned PPP/liquidity valuation.
- **Reproducible market research:** source provenance, immutable evidence, explicit data contracts, tests, and versioned processing pipelines.

The work is descriptive and measurement-focused unless a project explicitly states otherwise. Interpolated values are never presented as observed transactions, and the repository distinguishes empirical evidence from assumptions used to construct economic comparables.

## Selected empirical findings

### Copper

The primary copper comparison contains 206 certificate-trading days from 2025-10-26 through 2026-09-20. Thirty-six days have observed comparable physical anchors and 170 are bounded interpolations between anchors. The estimated certificate premium to domestic physical value averages **5.73%** with a median of **7.16%**. Interpretation is limited by the small and uneven physical-anchor sample.

### Zinc

The primary zinc output contains 206 modeled certificate days, including 50 observed anchors and 156 bounded interpolations. The certificate premium to estimated domestic physical value averages **0.80%**, while the direct certificate-to-LME-FX comparison averages a **20.54% discount**. The difference illustrates the economic importance of the domestic physical-market basis.

### Cross-asset allocation

The historical pilot compares 18-karat gold, TEDPIX, Tehran residential housing, and the Etemad fixed-income ETF. The identity of the hindsight-efficient risky asset changes sharply across regimes: gold dominates five periods, housing four, and equity one. Five of ten Stage-I solutions place the entire risky sleeve in a single asset. The result is intentionally framed as an ex-post diagnostic, not a forecast or portfolio recommendation.

### Gold ETFs

The gold project separates source reliability, daily research history, and live monitoring. Daily bubbles use same-date unadjusted closing prices and redemption NAV without interpolation. Historical ranks are calculated from observed daily bubbles; live readings are compared with those distributions but are not appended to the historical sample. NAV-source disagreements and gaps are retained as explicit quality flags rather than silently repaired.

## Other projects

| Project | Scope | Status |
|---|---|---|
| [Ahrom options](options/README.md) | Contract discovery and historical daily option-data pipeline for the Ahrom ETF | Dataset/infrastructure project: 996 contracts and 8,903 historical rows in the initial build |
| [Economic USD/IRR](economic_usd/README.md) | Iranian liquidity, free-market USD, Iranian CPI, and U.S. CPI preparation for PPP and liquidity-based valuation | Work in progress; data preparation implemented, valuation intentionally not yet claimed |
| [National Copper â€” Codal](codal/national_copper/README.md) | Issuer financial-statement reconstruction from cumulative disclosures | 75 valid quarters and 18 complete years |
| [Pistachio certificates](goods/pista/README.md) | IME certificate history and weekly physical-price audit | Exploratory; proxy and unit matching remain limitations |
| [Iran Energy Exchange](energy_exchange/README.md) | Market and regulatory mapping plus certificate-market feasibility analysis | Closed research project; intended empirical design rejected because trading activity was too sparse and concentrated |
| [Other commodity studies](commodity/) | Rebar, pellet, bitumen, silver, warehouse fees | Mixed completed, exploratory, and architecture-stage work; each project states its own status |

Current coverage and project-stage details live in [docs/STATUS.md](docs/STATUS.md). Operational history is kept there rather than treated as a research result.

## Methodological principles

Across projects, the repository uses a common set of research rules:

1. **Source data remain distinct from derived analysis.** Canonical physical trades, certificate trades, NAV, FX, and international benchmarks are not overwritten by analytical outputs.
2. **Raw evidence is immutable.** Source responses are archived with retrieval metadata and, where appropriate, content hashes.
3. **Alignment rules are explicit.** Exact-date joins, as-of joins, bounded interpolation, units, calendar conversions, and source ages are documented in project workflows.
4. **Derived values identify their construction.** Observed anchors, interpolated values, provider choice, and method keys remain visible in outputs.
5. **Limitations are part of the result.** Sparse trading, source transitions, publication timing, non-comparable market microstructure, and data gaps are documented rather than hidden.
6. **Notebooks are analytical and presentation layers.** Canonical raw datasets are modified only by documented collectors and builders.

## Repository structure

```text
commodity/                 Commodity-specific empirical projects
  copper/                  Copper certificate and physical-market valuation
  zinc/                    Zinc certificate and physical-market valuation
  gold/                    Gold ETF NAV research and monitoring
  rebar/ pellet/ bitumen/  Additional certificate studies
  silver/ warehouse_fees/
goods/pista/               Pistachio certificate and physical-price audit
asset_allocation/          Cross-asset allocation research
economic_usd/              Macroeconomic USD/IRR data and valuation design
options/                   Ahrom option contract and history pipeline
codal/                     Issuer-level financial disclosure research
energy_exchange/           Energy-market documentation and feasibility research
shared/                    Reusable collection and analytical infrastructure
reports/                   Research reports and reproducible figures
docs/                      Workspace architecture, workflow, and status
```

Within empirical projects, the preferred layout is:

```text
data/raw/        canonical source records and immutable evidence
data/interim/    temporary reproducible stages
data/processed/  approved analytical tables
src/             collection and processing code
tests/           network-free validation where possible
notebooks/       analysis and presentation
docs/            methodology, workflow, and status
```

## Reproducibility

Python 3.11 or newer is required. The root `pyproject.toml` is the canonical dependency and CI configuration for the shared workspace.

```bash
python -m venv .venv
# activate the environment for your platform
python -m pip install -e ".[dev,notebooks]"
python -m ruff check .
python -m pytest -q
```

The root CI runs on GitHub Actions. Tests that require unversioned market data skip explicitly when those inputs are unavailable; parser, calendar, scope, atomic-write, and synthetic reconstruction tests remain runnable in a clean clone. Independent projects document any additional test commands in their own READMEs.

## Data availability and governance

This repository versions original research code, tests, methodological documentation, report sources, and selected reproducible figures. Complete third-party market datasets and source-response archives are not redistributed through Git. See [DATA_AVAILABILITY.md](DATA_AVAILABILITY.md) and [docs/DATA_POLICY.md](docs/DATA_POLICY.md) for source, licensing, and reconstruction policy.

Credentials are read from environment variables and are never committed. Public-source availability does not by itself imply permission to redistribute an entire historical dataset.

## Deployment and database work

The gold project also demonstrates a production-style analytical workflow using PostgreSQL 17, Docker, SQL views, and scheduled refresh jobs. Deployment details are documented separately from empirical results in [commodity/gold/db/README.md](commodity/gold/db/README.md). Runtime secrets, database volumes, logs, and collected raw evidence remain outside Git by design.

## Reports

- [Copper research report](reports/copper/research/REPORT.md)
- [Zinc research report](reports/zinc/research/REPORT.md)
- [Cross-asset allocation historical pilot](asset_allocation/reports/ASSET_ALLOCATION_ANALYSIS_REPORT.md)

## Limitations

The international intrinsic-price series used in commodity work is a transparent benchmark rather than a complete import-parity model. Taxes, transport, storage, financing, quality, delivery conditions, liquidity, capital controls, and institutional constraints may explain part of observed domestic bases. Sparse physical-market anchors can also limit precision. Interpolated series are not vintage-safe trading backtests when later anchors contribute to earlier fitted values.

Results in this repository are research outputs, not investment advice.

## Citation and reuse

Citation metadata is provided in [CITATION.cff](CITATION.cff). Original source code is released under the [MIT License](LICENSE). That license applies to original code and documentation only; it does not grant redistribution rights for third-party data or publications.

For project-specific definitions, sample construction, caveats, and reproduction commands, follow the linked project README and workflow documentation rather than relying on the root summary alone.

