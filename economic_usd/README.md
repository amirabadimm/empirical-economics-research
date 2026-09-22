# Economic USD/IRR Data Project

This independent project prepares the source data required to estimate the economic or fundamental value of the Iranian free-market USD/IRR exchange rate. The data-preparation stage is implemented; the remaining valuation stage will use two methods: a dollar-liquidity approach and purchasing power parity (PPP). The current pipeline deliberately performs no valuation or forecast until those methods are implemented explicitly.

## Agreed valuation direction

Two valuation tracks remain:

1. **Dollar liquidity:** estimate the exchange-rate value implied by Iranian liquidity expressed relative to the relevant dollar basis.
2. **Purchasing power parity:** compare Iranian and U.S. price levels while addressing the sensitivity of PPP estimates to the selected base period.

The main PPP design decision is to avoid relying on one arbitrary base year or a single observation date. The planned analysis will use **five anchors**. Each anchor will be calculated from the average of a representative **six-to-twelve-month period**, rather than from one day or one isolated monthly observation. The five resulting PPP paths will be reported separately and may also be summarized as a range or central estimate. The exact anchor periods and aggregation rule must be documented before implementation; no anchor dates are yet fixed by this README.

## Data

| Processed file | Definition | Source | Frequency and unit |
|---|---|---|---|
| `data/processed/iran_liquidity.csv` | Total liquidity (M2), equal to money plus quasi-money | Central Bank of Iran, Selected Economic Indicators | Monthly; thousand billion IRR |
| `data/processed/usd_free_market.csv` | Observed Iranian free-market US dollar price | TGJU current closes plus preserved legacy Bourseview history | Daily observed dates; IRR per USD |
| `data/processed/iran_urban_headline_cpi.csv` | All-items national CPI for Iranian urban households | Statistical Center of Iran | Monthly index; base Solar Hijri year 1400 |
| `data/processed/us_cpi_urban_all_items.csv` | CPI-U, All Items, U.S. city average, not seasonally adjusted | Federal Reserve Bank of St. Louis FRED, `CPIAUCNS` | Monthly index; 1982–84=100 |
| `data/processed/macro_monthly.csv` | Preliminary sparse join of the four inputs | Derived without interpolation | Solar Hijri monthly |
| `data/processed/data_quality_report.csv` | Coverage, duplicate, gap, and largest-change diagnostics | Derived validation output | One row per core series |

The copied CBI publication archive contains one source document per month from 1385-01 through 1404-12. The full SCI source workbook and full standardized CPI extraction are also retained. These copies make the project independent of the source repositories.

## Refresh

From `E:\Work\economic_usd` in PowerShell:

```powershell
$env:PYTHONPATH = 'src'
python -m economic_usd.update_usd
python -m economic_usd.run_pipeline
python -m unittest discover -s tests -v
```

Set `FRED_API_KEY` to use the official FRED JSON API. If it is absent, `fetch_us_cpi` uses FRED's official `fredgraph.csv` endpoint and records that method. Credentials are never stored.

## Definitions and limitations

- USD observations are trading-date observations, not daily calendar fills, monthly averages, or official/administered exchange rates. `macro_monthly.csv` selects the last observed USD record in each Jalali month.
- The historical USD seed contains a documented method transition from legacy daily high/low midpoint values to TGJU close values. The refresh uses TGJU closes and records `source` and `price_method` per row.
- Liquidity is published monthly. No interpolation or temporal disaggregation is performed.
- Iranian CPI selection is restricted to `metric=price_index`, `category_fa=شاخص کل`, `geography_fa=کل کشور - خانوارهای شهری`, and `frequency=monthly`. Inflation rates and subindices are excluded.
- The monthly master matches U.S. CPI to the Gregorian calendar month containing the Iranian month-end. This is only a deterministic calendar join, not a PPP assumption. PPP anchoring will be implemented separately using the agreed five period-average anchors.
- Raw source material is immutable evidence. Refresh scripts create new downloaded files or atomically replace collector-owned canonical outputs.

See `docs/WORKFLOW.md` and `docs/STATUS.md`.
