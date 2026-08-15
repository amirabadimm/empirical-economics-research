# Iron-Ore Pellet Research Status

Last updated: 2026-08-15
Stage: exploratory exact-date certificate valuation

## Objective

Estimate the warehouse-receipt premium or discount relative to comparable domestic physical pellet trades. Global prices, exchange rates, and external intrinsic-value models are outside the current scope.

## Data checkpoint

- Certificate: 252 calendar observations and 182 positive-trading days through 2026-08-09.
- Physical market: 3,467 rows and 1,606 positive trades through 1405/05/18.
- Raw files and immutable snapshots remain unchanged.
- The exploratory bubble contains 22 exact-date observations; no standalone processed benchmark has yet been approved.

## Benchmark rule

The candidate producers are Gol Gohar (`GOLG-PELL-00`) and Gohar Zamin (`GHZ-PELL-00`). Eligible observations require a cash or cash-matching contract, an explicitly cash settlement, and positive price and quantity. Cash/credit trades are excluded.

A single-producer day uses that producer's observed price; a two-producer day uses the simple mean. Certificate comparisons are exact-date only and require positive volume and price. No interpolation or carry-forward is used. Coverage is 16 single-producer and six two-producer days.

## Selection rationale

Selection uses all positive physical trades since certificate inception. Gol Gohar represents 30.75% and Gohar Zamin 23.10%, for a combined 53.86%. Chadormalu represents 9.81% and Sangan Khorasan 5.66%; both are excluded. The decision affects analysis only and never alters raw data.

## Validation findings

Only 16 strict-cash common dates exist for the selected producers over the full history: nine before and seven after certificate inception. The mean symmetric difference declines from 1.53% to 0.88%; both medians are zero. Four of the seven later dates have identical prices, and the largest later difference is 3.32%. The evidence does not support increased producer dispersion after certificate inception.

The largest valid historical difference occurs on 1401/04/11. Base price, offer quantity, delivery, warehouse, and settlement align, but demand-to-supply is 1.3 for Gol Gohar and 3.0 for Gohar Zamin. Stronger competition raises Gohar Zamin 10.60% above base versus 2.43% for Gol Gohar, producing a 7.67% symmetric difference. Available data do not identify the cause of buyer preference.

## Positive-bubble case

On 1404/10/21 the benchmark is Gol Gohar's IRR 94,566/kg cash price. The certificate settles at IRR 104,998/kg, implying +11.03%. Gohar Zamin's IRR 111,229/kg trade is excluded because settlement is cash/credit. A sensitivity mean reduces the bubble to +2.04%, demonstrating material composition risk.

## Next step

Extend exact-date coverage, report single- and two-producer results separately, and promote the benchmark to a processed output only after final approval. Until then, the notebook series remains exploratory.
