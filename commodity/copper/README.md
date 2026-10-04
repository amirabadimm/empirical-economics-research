# Copper Certificate Valuation

## Research question

Does the Iranian copper-cathode warehouse receipt trade at a premium or discount to a comparable domestic physical-market value, after accounting for movements in LME cash copper and the free-market USD/IRR exchange rate?

The project treats the certificate, domestic physical market, and international benchmark as distinct objects. The main empirical question is not whether the certificate differs from LME, but whether it differs from an economically comparable domestic physical value after the domestic basis is modeled explicitly.

## Data

The active production pipeline combines:

- IME copper-cathode warehouse-receipt trades;
- IME domestic physical copper-cathode trades;
- LME cash copper prices;
- the shared free-market USD/IRR series.

The latest production refresh documented 293 certificate rows, including 214 positive-volume observations, and 1,175 physical-market rows. The eligible daily physical benchmark contains 799 observations through 2026-09-20. LME coverage extends through 2026-09-25 and the shared USD/IRR series through 2026-09-26.

Canonical source records remain separate under `data/raw`; processed benchmarks and valuation outputs are reproducible derivatives.

## Comparable physical underlying

The approved domestic benchmark includes only National Iranian Copper Industries Company cathode under the historical symbols `NCI-CCAA-00` and `NCI-OACCAA-00`, using cash and cash-matching contracts with positive executed price and quantity.

Forward and credit contracts, other producers, and “copper cathode 2” are excluded from the main comparable basket. The daily physical benchmark is volume weighted.

This scope decision is economic rather than purely statistical: the benchmark is designed to represent the closest observable domestic physical underlying to the certificate.

## Method

The transparent international benchmark is

```text
intrinsic_price = LME_cash_USD_per_kg × USD_IRR
```

The main certificate valuation proceeds in two stages:

1. construct the observed ratio of comparable domestic physical price to LME-FX intrinsic value on dates with physical-market evidence;
2. interpolate that ratio only between exact observed anchors, then apply it to the international benchmark to estimate a domestic physical value on certificate dates.

No extrapolation is allowed outside the observed anchor range.

Three comparisons are kept separate:

- domestic physical price versus LME-FX intrinsic value;
- certificate price versus LME-FX intrinsic value;
- certificate price versus estimated comparable domestic physical value.

A time-series regression using intrinsic value as its sole feature is retained only as a sensitivity analysis; it is not the headline valuation method.

## Main result

The primary output contains **206 certificate-trading days** from 2025-10-26 through 2026-09-20. Of these, **36** are observed physical anchors and **170** are bounded interpolations between anchors.

The estimated certificate premium to domestic physical value averages **5.73%**, with a median of **7.16%**.

The result should be interpreted with care because the physical-anchor sample is small and temporally uneven. The interpolation is intended to preserve the observed domestic basis between anchors, not to claim that an unobserved physical trade actually occurred on each modeled day.

## Historical distributions

The standardized distribution output keeps signed bubble values and chronological empirical ranks. For each date, the project reports an expanding equal-weight percentile and a recency-weighted percentile using a configurable 90-calendar-day half-life.

Observed and interpolated certificate-versus-physical values remain distinguishable through `point_method` and `is_interpolated`. Interpolated series may use later anchors, so these distributions are descriptive historical analyses rather than vintage-safe trading backtests.

## Forward-gap diagnostic

The separate `nci_copper_forward_gap.csv` diagnostic preserves the cash-only benchmark scope while examining activity inside a long cash-market gap. It covers 16 forward-trade dates and 26,420 tonnes within the documented 102-day gap, comparing forward weighted prices with both cash anchors and a linear bridge.

This diagnostic is not substituted into the headline physical benchmark.

## Reproduction

From the repository root:

```bash
python commodity/copper/src/copper/collectors/lme.py
python shared/market_data/fx.py
python commodity/copper/src/copper/collectors/certificate.py
python commodity/copper/src/copper/collectors/physical.py
python commodity/copper/src/copper/processing/build_physical_benchmark.py
python commodity/copper/src/copper/processing/build_intrinsic_bubbles.py
python commodity/copper/src/copper/processing/build_certificate_bubble.py
python commodity/copper/src/copper/processing/build_intrinsic_regression.py
python commodity/copper/src/copper/processing/build_presentation_timeline.py
python commodity/copper/src/copper/processing/build_forward_gap_analysis.py
```

For the standard production workflow, `python commodity/copper/refresh_powerbi.py --collect` refreshes documented sources and rebuilds approved outputs. The shared certificate engine can also inspect or rebuild the pipeline from its manifest.

## Outputs

- `data/processed/physical/` — approved domestic physical benchmark and diagnostics;
- `data/processed/bubble/` — certificate and intrinsic comparison tables;
- `data/processed/analysis/` — presentation timelines and distribution outputs;
- `notebooks/01_lme_analysis.ipynb` — exploratory LME analysis;
- `notebooks/02_certificate_analysis.ipynb` — presentation-oriented certificate valuation;
- [`reports/copper/research`](../../reports/copper/research/) — English research report and reproducible figures.

## Reproducibility and validation

The latest documented production refresh passed all 17 copper and shared certificate-pipeline tests. Notebook calculations do not modify canonical source files, and the Power BI delivery layer copies canonical bubble values rather than recalculating a separate headline percentage.

Detailed source contracts, processing rules, and validation logic are documented in [`docs/WORKFLOW.md`](docs/WORKFLOW.md), while current coverage and operational checkpoints belong in [`docs/STATUS.md`](docs/STATUS.md).

## Limitations

The LME-FX series is a transparent benchmark, not a complete import-parity price. Taxes, transport, financing, storage, delivery terms, capital controls, liquidity, and institutional constraints can all contribute to the domestic basis.

The principal statistical limitation is sparse physical-market anchoring. The interpolation is bounded and transparent, but it cannot replace actual physical transactions. Results are research outputs, not investment advice.
