# Zinc Certificate Valuation

## Notebook distribution view (2026-10-13)

The final cells of `notebooks/01_zinc_analysis.ipynb` and `notebooks/02_bubble_analysis.ipynb` now use the current empirical-distribution CSV schema. They display signed histograms, empirical CDFs, absolute-exceedance charts, and recent observations for the three governed comparisons. Their earlier expanding-rank descriptions are superseded; sources and production formulas did not change.
## Live refresh checkpoint (2026-10-13)

Live collection and the shared production rebuild completed. Certificate raw: 307 rows through 2026-10-12 (228 traded); physical raw: 6,465 rows; eligible physical: 567 days through 1405/07/19. Primary comparison: 223 rows; physical/intrinsic: 567; certificate/intrinsic: 228; distribution: 1,018. Research-only studies were not part of the production pipeline. The research-only intrinsic regression was also rebuilt to 228 rows and 54 anchors after a stale 210-row table failed alignment verification. Zinc's full suite then passed 14 tests and 233 subtests.

## Research question

How does the Iranian zinc-ingot warehouse receipt trade relative to an eligible domestic physical basket and to an LME-FX intrinsic benchmark?

The project is designed to separate three economically different objects: the domestic physical market, the exchange-traded certificate, and an international intrinsic benchmark. The headline comparison is certificate versus estimated comparable domestic physical value, not certificate versus LME alone.

## Data

The production workflow combines:

- IME zinc certificate trades;
- broad IME physical zinc-market data;
- LME cash zinc;
- the shared free-market USD/IRR series.

The October 13 source checkpoint records 6,465 broad physical-market rows and 307 certificate rows, including 228 positive-trading dates through 2026-10-12. The approved physical benchmark contains 567 daily observations through 2026-10-11; the bounded primary comparison contains 223 certificate days through that physical anchor.

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

Verified against local output on 2026-10-17, the primary sample contains **223 modeled certificate days** from 2025-10-26 through 2026-10-11. Of these, **54** are observed physical anchors and **169** are bounded interpolations. This supersedes the 206-day September headline checkpoint.

The certificate premium to estimated domestic physical value averages **1.88%**, with a median of **2.73%**.

The direct certificate-to-LME-FX comparison shows an average **20.58% discount on those same 223 dates**. Its full 228-date sample averages a 20.43% discount; the paired comparison avoids mixing sample windows. These are unweighted daily descriptive statistics.

The difference is the central empirical finding of the project: the domestic physical-market basis is economically important, and using the international benchmark alone gives a very different view of relative valuation.

## Historical distributions

The current standardized distribution table keeps signed bubble values, full-sample empirical percentiles, and absolute-exceedance percentages. The notebooks show histograms, empirical CDFs, and absolute-exceedance panels. Earlier expanding and recency-weighted distribution descriptions are superseded for the current Zinc builder.

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
