# Zinc Certificate Valuation

## Research question

How does the Iranian zinc-ingot warehouse receipt trade relative to an eligible domestic physical basket and to an LME-FX intrinsic benchmark?

The project is designed to separate three economically different objects: the domestic physical market, the exchange-traded certificate, and an international intrinsic benchmark. The headline comparison is certificate versus estimated comparable domestic physical value, not certificate versus LME alone.

## Data

The production workflow combines:

- IME zinc certificate trades;
- broad IME physical zinc-market data;
- LME cash zinc;
- the shared free-market USD/IRR series.

The documented checkpoint contains 6,398 broad physical-market rows, including 3,581 positive trades. The approved physical benchmark contains 563 daily observations. Certificate data contain more than 200 positive-trading observations in the active sample, while the primary modeled comparison contains 206 certificate days through 2026-09-20.

Raw physical data intentionally retain both zinc ingot and zinc soil for auditability. Product filtering occurs only in the reproducible benchmark builder.

## Comparable physical underlying

Zinc soil is economically distinct from zinc ingot and never enters the approved benchmark.

The benchmark is a volume-weighted daily basket of 99.97 and 99.98 zinc ingots traded through cash or cash-matching contracts with positive executed price and quantity. This scope is explicit so that a statistically convenient but economically different product cannot silently enter the valuation.

## Method

The transparent international benchmark is

```text
intrinsic_price = LME_cash_USD_per_kg × USD_IRR
```

The primary method estimates the domestic physical basis by interpolating the observed physical-to-intrinsic ratio between exact certificate/physical anchors. Interpolation is bounded by observed anchors; there is no extrapolation outside the supported range.

Three valuation measures remain separate throughout the project:

- domestic physical price versus LME-FX intrinsic value;
- certificate price versus LME-FX intrinsic value;
- certificate price versus estimated comparable domestic physical value.

This separation matters because a large direct certificate-to-LME discount can coexist with a much smaller certificate-to-domestic-physical premium once the domestic basis is modeled.

## Main result

The primary output contains **206 modeled certificate days** from 2025-10-26 through 2026-09-20. Of these, **50** are observed physical anchors and **156** are bounded interpolations.

The certificate premium to estimated domestic physical value averages **0.80%**.

By contrast, the direct certificate-to-LME-FX comparison shows an average **20.54% discount**.

The difference is the central empirical finding of the project: the domestic physical-market basis is economically important, and using the international benchmark alone gives a very different view of relative valuation.

## Historical distributions

The standardized distribution table keeps signed bubble values and chronological empirical ranks. It reports an expanding equal-weight percentile and a recent-weighted percentile with a configurable 90-calendar-day half-life.

Certificate-versus-physical rows preserve `point_method` and `is_interpolated`, so observed anchors and model-derived days remain identifiable. Because bounded interpolation can use later anchors, these historical ranks are descriptive and are not presented as vintage-safe trading backtests.

## Reproduction

From the repository root:

```bash
python commodity/zinc/src/zinc/collectors/certificate.py
python commodity/zinc/src/zinc/collectors/physical.py
python commodity/zinc/src/zinc/collectors/lme.py
python shared/market_data/fx.py
python commodity/zinc/src/zinc/processing/build_physical_benchmark.py
python commodity/zinc/src/zinc/processing/build_intrinsic_bubbles.py
python commodity/zinc/src/zinc/processing/build_certificate_bubble.py
python commodity/zinc/src/zinc/processing/build_intrinsic_regression.py
```

For the standard production workflow, `python commodity/zinc/refresh_powerbi.py --collect` refreshes documented sources and rebuilds approved outputs. The shared certificate engine can also inspect or rebuild the pipeline from its manifest.

## Outputs

- `data/processed/physical/` — approved physical benchmark;
- `data/processed/bubble/` — certificate and intrinsic comparison tables;
- `data/processed/analysis/` — distribution and presentation outputs;
- `notebooks/01_zinc_analysis.ipynb` — manual grade and scope analysis;
- `notebooks/02_bubble_analysis.ipynb` — presentation-oriented valuation analysis;
- [`reports/zinc/research`](../../reports/zinc/research/) — English research report and reproducible figures.

Canonical physical and certificate records remain separate under `data/raw/{physical,certificate}`. Notebooks are read-only with respect to those canonical sources.

## Reproducibility and validation

The project documents 14 network-free contract and pipeline tests at its research checkpoint. Detailed methodology, source contracts, and processing rules are maintained in [`docs/WORKFLOW.md`](docs/WORKFLOW.md), while current coverage and operational refresh history belong in [`docs/STATUS.md`](docs/STATUS.md).

## Limitations

The LME-FX series is not a complete import-parity model. Transport, financing, storage, grade, delivery terms, market segmentation, liquidity, capital controls, and institutional constraints can contribute to the domestic basis.

The primary model is also limited by the density and timing of physical anchors. Interpolated values are transparent model outputs, not observed transactions. Results are research outputs, not investment advice.
