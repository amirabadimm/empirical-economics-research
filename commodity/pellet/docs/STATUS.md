# Iron-Ore Pellet Research Status

Last updated: 2026-09-19
Stage: exploratory exact-date certificate valuation

The 23-row comparison has a reproducible processed CSV at `data/processed/bubble/pellet_certificate_bubble.csv` and a project-local Power BI delivery CSV at `outputs/power_bi/pellet_certificate_physical_comparison.csv`. Producer-composition risk remains open.

## Objective

Estimate the warehouse-receipt premium or discount relative to comparable domestic physical pellet trades. Global prices, exchange rates, and external intrinsic-value models are outside the current scope.

## Data checkpoint

- Certificate: 286 calendar observations and 208 positive-trading days through 2026-09-17.
- Physical market: 3,588 rows and 1,706 positive trades through 1405/06/23.
- Raw files and immutable snapshots remain unchanged.
- The active notebook now includes the governed workspace dashboard for source coverage,
  physical/certificate activity, goods composition, prices, and validated bubble visualization.
- The exploratory bubble contains 23 exact-date observations through 1405/05/25; no standalone processed benchmark has yet been approved.

## Benchmark rule

The candidate producers are Gol Gohar (`GOLG-PELL-00`) and Gohar Zamin (`GHZ-PELL-00`). Eligible observations require a cash or cash-matching contract, an explicitly cash settlement, and positive price and quantity. Cash/credit trades are excluded.

A single-producer day uses that producer's observed price; a two-producer day uses the simple mean. Certificate comparisons are exact-date only and require positive volume and price. No interpolation or carry-forward is used. Coverage is 17 single-producer and six two-producer days.

## Selection rationale

Selection uses all positive physical trades since certificate inception. Gol Gohar represents 32.69% and Gohar Zamin 22.85%, for a combined 55.54%. Chadormalu represents 9.77% and Sangan Khorasan 6.21%; both are excluded. The decision affects analysis only and never alters raw data.

## Validation findings

Only 16 strict-cash common dates exist for the selected producers over the full history: nine before and seven after certificate inception. The mean symmetric difference declines from 1.53% to 0.88%; both medians are zero. Four of the seven later dates have identical prices, and the largest later difference is 3.32%. The evidence does not support increased producer dispersion after certificate inception.

The largest valid historical difference occurs on 1401/04/11. Base price, offer quantity, delivery, warehouse, and settlement align, but demand-to-supply is 1.3 for Gol Gohar and 3.0 for Gohar Zamin. Stronger competition raises Gohar Zamin 10.60% above base versus 2.43% for Gol Gohar, producing a 7.67% symmetric difference. Available data do not identify the cause of buyer preference.

## Positive-bubble case

On 1404/10/21 the benchmark is Gol Gohar's IRR 94,566/kg cash price. The certificate settles at IRR 104,998/kg, implying +11.03%. Gohar Zamin's IRR 111,229/kg trade is excluded because settlement is cash/credit. A sensitivity mean reduces the bubble to +2.04%, demonstrating material composition risk.

## Next step

Extend exact-date coverage, report single- and two-producer results separately, and promote the benchmark to a processed output only after final approval. Until then, the notebook series remains exploratory.

The active notebook now uses interactive Plotly charts and executed successfully against the
2026-09-19 checkpoint. Static reports retain their earlier data vintage.
# Bubble distribution status

As of 2026-09-21, the standardized certificate-versus-physical distribution contains 23
observations. The existing producer-composition comparability warning remains applicable.
