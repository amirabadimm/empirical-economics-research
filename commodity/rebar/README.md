# Steel Rebar Physical-Market Research

## Research objective

Build an auditable physical-market dataset for Iranian steel rebar from the official Iran Mercantile Exchange (IME). The initial project is intentionally an exploratory data pipeline: it preserves the full rebar-labelled source universe before any analytical comparison, price benchmark, or eligibility basket is approved.

## Current stage

Canonical physical and certificate records remain separate under `data/raw/{physical,certificate}`.
The optional A3 / 12 mm physical analysis lives under `data/processed/physical`; no rebar bubble
exists.

Physical collection refreshed on 2026-08-29: 31,641 rebar-labelled IME rows from 1387/06/03
through 1405/06/07. The active exploratory chart scope is plainly specified straight A3 / 12 mm
rebar under cash or cash-matching contracts. The broad raw scope remains immutable, and no
producer/delivery-validated comparable-product benchmark has been approved.

Continuous-certificate collection now covers 268 official daily records from 2025-10-20 through
2026-08-27, including 194 traded days. Certificate/physical comparison remains exploratory.

The raw scope includes every IME row whose normalized `GoodsName` identifies rebar, including all producers, standards, diameters, symbols, contract types, settlement terms, currencies, and zero-quantity offers. This is a source scope, not an assertion of economic comparability.

## Run the collector

From the repository root:

```powershell
python .\commodity\rebar\src\rebar\collectors\physical.py
python .\commodity\rebar\src\rebar\processing\build_a3_12_cash_daily.py
python .\commodity\rebar\src\rebar\collectors\certificate.py
```

The initial run queries all available IME months. Later runs refresh the current Jalali month and two preceding months. Complete responses are archived once in `shared/data/raw/ime/physical`; the historical Rebar-local archive is frozen but remains a valid rebuild input. Use `--start-month` and `--end-month` only for bounded recovery, and `--rebuild-from-snapshots` to reproduce the canonical CSV from shared plus legacy evidence.

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
the 30 most frequent labels while the returned table contains all labels. The bubble panel states
that no validated Rebar bubble exists; it does not infer one.

## Certificate data

The official continuous rebar certificate collector uses commodity ID `29`, legacy code
`CD1RBR0001`, and current code `SteelRebar`. The current canonical history has 268 records from
2025-10-20 through 2026-08-27, including 194 traded days.

No rebar bubble is computed at this stage. Historical launch notices identify the certificate
deliverable as A3 / 18 mm rebar, but the current continuous contract and warehouse specification
must be checked from official IME documentation before an analytical filter is approved. The
existing A3 / 12 mm series remains a separate physical-market exploration only.
