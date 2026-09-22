# Workflow

Run from the project root with `PYTHONPATH=src`.

1. `python -m economic_usd.run_pipeline` refreshes FRED CPIAUCNS and TGJU USD, validates and standardizes all four independent inputs, creates a sparse non-interpolated monthly join, and writes data-quality diagnostics.
2. Individual fetch, update, preparation, build, and validation modules can also run separately.
3. `python -m unittest discover -s tests -v` verifies core contracts.

No PPP, rebasing, anchor selection, regression, valuation, or forecasting currently occurs in this implemented workflow.

## Planned valuation stage

The next workflow stage will add two independent valuation outputs:

1. **Dollar-liquidity estimate:** define and calculate the exchange-rate value implied by the chosen liquidity-to-dollar relationship.
2. **PPP estimates:** create five independently documented PPP paths. Each path will use an anchor value calculated as the mean over a six-to-twelve-month window. A single-day anchor is not permitted because it would make the result excessively sensitive to temporary market conditions.

Before implementation, record the five anchor windows, the reason for selecting each window, the price-index treatment, the exchange-rate averaging rule, and the method used to compare or summarize the five paths. Preserve the separate results so the effect of anchor choice remains visible.
