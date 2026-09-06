# Steel Rebar Physical-Market Research

## Research objective

Build an auditable physical-market dataset for Iranian steel rebar from the official Iran Mercantile Exchange (IME). The initial project is intentionally an exploratory data pipeline: it preserves the full rebar-labelled source universe before any analytical comparison, price benchmark, or eligibility basket is approved.

## Current stage

Canonical physical and certificate records remain separate under `data/raw/{physical,certificate}`.
The optional A3 / 12 mm physical analysis lives under `data/processed/physical`. A separate
exploratory exact-date A3 / 18 mm bubble lives under `data/processed/bubble`.

Physical collection refreshed on 2026-09-06: 31,752 rebar-labelled IME rows from 1387/06/03
through 1405/06/15. The active exploratory chart scope is plainly specified straight A3 / 12 mm
rebar under cash or cash-matching contracts. The broad raw selection remains unchanged, and no
producer/delivery-validated comparable-product benchmark has been approved.

Continuous-certificate collection now covers 275 official daily records from 2025-10-20 through
2026-09-05, including 199 traded days. Certificate/physical comparison remains exploratory.

The raw scope includes every IME row whose normalized `GoodsName` identifies rebar, including all producers, standards, diameters, symbols, contract types, settlement terms, currencies, and zero-quantity offers. This is a source scope, not an assertion of economic comparability.

## Run the collector

From the repository root:

```powershell
python .\commodity\rebar\src\rebar\collectors\physical.py
python .\commodity\rebar\src\rebar\processing\build_a3_12_cash_daily.py
python .\commodity\rebar\src\rebar\collectors\certificate.py
python .\commodity\rebar\src\rebar\processing\build_a3_18_exact_bubble.py
python .\commodity\rebar\src\rebar\processing\build_a3_12_exact_bubble.py
```

The initial run queries all available IME months. Later runs start two months before the latest stored Jalali month and continue through the current date. Complete responses are archived once in `shared/data/raw/ime/physical`; the historical Rebar-local archive is frozen but remains a valid rebuild input. Use `--start-month` and `--end-month` only for bounded recovery, and `--rebuild-from-snapshots` to reproduce the canonical CSV from shared plus legacy evidence.

See [`docs/WORKFLOW.md`](docs/WORKFLOW.md) for the source contract, data governance, validation, and the decision gates required before building any derived benchmark.

## Exploratory price chart

[`notebooks/01_physical_price_analysis.ipynb`](notebooks/01_physical_price_analysis.ipynb) plots
the A3 / 12 mm daily output: volume-weighted cash trade price (`Price`) and offer-base price
(`ArzeBasePrice`) on Jalali dates, using a level chart and the daily percentage difference
`100 × (cash / offer base − 1)`. The builder first applies the documented strict A3 / 12 mm
product and cash-contract filter; it does not calculate a market-wide average across the broad
rebar-labelled raw universe.

The notebook also follows the workspace dashboard contract with responsive, consistently themed
interactive Plotly figures:
source-coverage audit, separate physical and certificate volume charts, separate descriptive price panels, and a frequency table
computed from every raw physical record by the unmodified `GoodsName`. Its readable bar chart shows
the 30 most frequent labels while the returned table contains all labels. The bubble panel reads
only the processed exact-date CSV and never constructs a comparison inside the notebook.

## Certificate data

The official continuous rebar certificate collector uses commodity ID `29`, legacy code
`CD1RBR0001`, and current code `SteelRebar`. The current canonical history has 275 records from
2025-10-20 through 2026-09-05, including 199 traded days.

## Exploratory exact-date A3 / 18 mm bubble

`build_a3_18_exact_bubble.py` selects only plainly specified straight A3 / 18 mm physical rows,
cash or cash-matching contracts, rial quotes, tonne quantities, and positive executed quantity and
price. It volume-weights same-day physical rows and joins them only to positive-volume certificate
records on the exact Gregorian date. It does not interpolate, carry prices forward, mix forward
contracts, or adjust for storage, delivery, tax, or transaction costs.

The current output contains 5 exact-date observations from 2026-03-15 through 2026-05-26. Every
physical anchor is an Isfahan Steel (`ذوب آهن اصفهان`) cash trade. The percentage is
`100 × (certificate settlement / physical cash VWAP − 1)` and remains an exploratory gross quoted-
price diagnostic. Published launch descriptions identify A3 / 18 mm as the certificate product,
but the current official warehouse specification, lot conversion, producer eligibility, delivery
terms, and full fee/tax basis still require archival verification before this can be called an
approved economic benchmark. The A3 / 12 mm series remains a separate physical exploration.

## Intentional A3 / 12 mm cross-diameter diagnostic

At the researcher's request, `build_a3_12_exact_bubble.py` applies the same positive-trade,
cash/cash-matching, exact-date mechanics to plainly specified straight A3 / 12 mm physical trades.
It produces 48 observations from 2025-11-12 through 2026-09-02 using
`100 × (certificate settlement / A3/12 physical cash VWAP − 1)`. The CSV explicitly records
`intentional_cross_diameter_diagnostic_not_underlying_match`; it must not be interpreted as a
deliverable-underlying arbitrage series. It is useful as a nearby-diameter market diagnostic only.

## Refresh verification (2026-09-06)

The physical collector queried 1405/04 through 1405/06/15; the certificate collector queried
2026-08-13 through 2026-09-06. Latest observations are 1405/06/15 for physical and
2026-09-05 for certificates; a successful refresh does not imply a trade on every calendar day.
The rebuilt A3 / 12 mm physical table has 188 dates from 1387/07/14 through 1405/06/11.

Run the five commands above in order, stopping if any command fails, using a Python environment
with the repository dependencies installed. For the dashboard, install the `notebooks` extra;
for tests, install the `dev` extra. Validate with `python -m pytest commodity/rebar/tests -q`.
The notebook discovers the workspace from either the repository root or its own folder and
regenerates `outputs/figures/rebar_cash_vs_offer_base_price.html` when executed.
Refresh and validation evidence is local under `logs/*20260906.log`.

Saved notebook outputs are cleared to avoid retaining stale counts or bulk charts in Git;
execute the notebook for current inline views. The refreshed HTML chart remains local in `outputs/figures`.
