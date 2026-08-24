# Steel Rebar Physical-Market Research

## Research objective

Build an auditable physical-market dataset for Iranian steel rebar from the official Iran Mercantile Exchange (IME). The initial project is intentionally an exploratory data pipeline: it preserves the full rebar-labelled source universe before any analytical comparison, price benchmark, or eligibility basket is approved.

## Current stage

Historical collection completed on 2026-08-24: 31,532 rebar-labelled IME rows from 1387/06/03
through 1405/06/01. The active exploratory chart scope is plainly specified straight A3 / 12 mm
rebar under cash or cash-matching contracts. The broad raw scope remains immutable, and no
producer/delivery-validated comparable-product benchmark has been approved.

The raw scope includes every IME row whose normalized `GoodsName` identifies rebar, including all producers, standards, diameters, symbols, contract types, settlement terms, currencies, and zero-quantity offers. This is a source scope, not an assertion of economic comparability.

## Run the collector

From the repository root:

```powershell
python .\commodity\rebar\src\rebar\collectors\physical.py
python .\commodity\rebar\src\rebar\processing\build_a3_12_cash_daily.py
```

The initial run queries all available IME months. Later runs refresh the current Jalali month and two preceding months. Use `--start-month` and `--end-month` only for a bounded recovery or source probe, and use `--rebuild-from-snapshots` only to reproduce the canonical CSV from the immutable local snapshots.

See [`docs/WORKFLOW.md`](docs/WORKFLOW.md) for the source contract, data governance, validation, and the decision gates required before building any derived benchmark.

## Exploratory price chart

[`notebooks/01_physical_price_analysis.ipynb`](notebooks/01_physical_price_analysis.ipynb) plots
the A3 / 12 mm daily output: volume-weighted cash trade price (`Price`) and offer-base price
(`ArzeBasePrice`) on Jalali dates, using a level chart and the daily percentage difference
`100 × (cash / offer base − 1)`. The builder first applies the documented strict A3 / 12 mm
product and cash-contract filter; it does not calculate a market-wide average across the broad
rebar-labelled raw universe.
