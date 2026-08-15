# Zinc-Ingot Warehouse-Receipt Certificate: Research Workflow
## Update checkpoint — 2026-08-15
All four collectors were implemented incrementally. The certificate is now 256 calendar rows and
184 days of positive trading until 2026-08-13, LME equal to 4,709 rows until 2026-08-14 and currency
It has 13,067 rows until 05/20/1405. refresh physical market 338 rows of open months
re-read and extended canonical still remained 6,235 rows after merge;
The official benchmark also has 554 days and 41 real anchors unchanged. Direct certificate output
increased to 184 days at the intrinsic price; The main bubble remains because of the prohibition of extrapolation
It has 178 days until the last anchor on 2026-08-09. Both main notebooks run again
Fresh charts were saved in them.
- Source: Official CDC API of Iran Commodity Exchange, Bazar 22.
- Series start: 07/28/1404 equals 10-20-2025.
- old code: `CD1ZNI0001`; New code: `ZincIngot`; `CommodityID=30`.
- collector: `src/zinc/collectors/certificate.py`.
- shared logic: `../../shared/ime_data/certificate_collector.py` relative to the workspace root; It is also required when transferring the `shared/ime_data` folder.
- CSV: `data/raw/certificate/zinc_certificate_raw.csv`.
- Rules: keeping zero day, complete snapshot, merge on date, fourteen days refresh, atomic writing.
- validation: complete schema, unique date, fixed code/id/description, non-negative values and matching
  `TradesValue / TradesVolume` with `TodaySettlementPrice` on trading days.
- The price criterion in future analyzes is `TodaySettlementPrice` and the ratio of value to volume will only be validation.
- Status 2026-08-10: 252 rows until 2026-08-09; 182 days of positive transactions.
Normal execution from within `commodity/zinc`:
```powershell
python .\src\zinc\collectors\certificate.py
```

Full implementation only for reconstruction or audit:
```powershell
python .\src\zinc\collectors\certificate.py --full-refresh
```

The second incremental execution without increasing the number of rows and all schema controls, date,
OHLC, codes, CommodityID and price settlement has been successful.
Raw physical market data is now collected and validated; ultimate underlying,
The benchmark has been processed and the bubble has not yet been selected or generated.
## Preliminary review of the physical market — 2026-08-03
Review of full snapshots of the official commodity exchange API, between 07/28/1404 and 05/07/1405
And it was done only for transactions with `Quantity > 0` and `Price > 0`. No data files
New production and no final filter was approved.
A general search for the word "on" returns 498 rows and 502,787 tons, but 92.80% of this volume
Zinc dust is not comparable with the zinc-ingot certificate and must remain outside the underlying basket. After restricting the scope to
"Zinc ingot":
- 415 rows, 54 trading days and 36,187 tons;
- 8 titles from 99.92 to 99.99, 24 producers and 57 symbols;
- Grade shares: 99.96 accounts for 44.87%, 99.97 for 23.45%, and 99.98 for
  17.64% and 99.95 equal to 11.22%;
- Main producers: Calcimine 29.64%, zinc smelting 18.86%, mineral processing
  Iran 9.88%, development of zinc industries in the Middle East 8.69% and Zanjan compounders 7.67%;
- Contracts: cash 87.12% and matching cash 12.88%; All rows of ingots have settlement
  Cash and 99.05% of the volume are in the industrial hall.
Conclusion: "Soil" should definitely be removed, but the choice of grade and producer is still not final.
First, the minimum purity, delivery standard and acceptable warehouses must be extracted; then
A defensible basket of eligible ingot grades can be constructed using a daily volume-weighted price. Selecting a single
The manufacturer alone is not recommended without a certificate of equivalence.
The main recommended resource for the future collector is the official public API of the stock exchange. BrsApi only
For discovery, fallback is kept and no keys are stored in the project.
## Current stage: raw collector of the physical market
`src/zinc/collectors/physical.py` with common logic
`shared/ime_data/ime_physical_collector.py` was created. Filter raw any product name
Normalized contains zinc; Therefore, zinc soil is also deliberately used until the stage of analysis
It remains raw. Limitation on denomination, manufacturer, symbol, contract, settlement or volume of transactions
can't The full monthly response is created atomically before the archive and CSV filter.
Outputs:
```text
data/raw/physical/zinc_physical_raw.csv
data/raw/physical/api_snapshots/*.json.gz
```

### The result of complete collection and validation — 2026-08-03
To avoid repeated downloads, the most recent complete snapshot of each of the 233 months from the archive
The same official endpoint of the commodity exchange was copied to the independent Zinc folder in the copper project. Snapshots
Bazarand's total response and CSV were reconstructed from them with their own independent filter.
- 6,178 raw rows and 36 columns from 07/28/1387 to 07/05/1405 on 999 dates;
- After normalization, all 12 product titles include "Zinc";
- In raw: 47 producer titles, 168 symbols and 5 types of contracts;
- 3,428 rows of positive transactions on 756 dates;
- In positive transactions: 12 product titles, 40 producers, 127 symbols and 4 types of contracts;
- 2,750 supply of zero amount; No negative price/value, missing identity, completely duplicate row or
  duplicate business key;
- Every 233 monthly snapshots are unique, healthy and parsable.
The volume composition of the positive trades of the entire "Zn" group is misleading: Zn soil is 94.15% of the volume
forms, while the underlying asset is a zinc-ingot certificate. The principal ingot grades are:
from 99.96 with 85,266 tons, 99.98 with 83,405 tons, 99.97 with 71,242 tons and 99.95 with
23,020 tonnes; grades 99.90 through 99.99 are also available in smaller quantities. This statistic
It is descriptive and no rows have been removed from raw yet.
This review supports the final underlying decision: a volume-weighted basket of grades
99.97 and 99.98 in cash and cash matching contracts. Zinc and other grades only in
Wide raws are preserved and not included in the official benchmark.
### refresh, fix snapshot and test contracts — 2026-08-10
- The certificate was refreshed incrementally until 2026-08-09: 252 rows and 182 days
  Positive transaction.
- The physical market was refreshed until 05/18/1405: 6,235 rows, 3,462 positive transactions and
  1,003 dates.
- The old snapshot `physical_1403-11_20260801T114224Z.json.gz` is broken and according to
  The immutable policy was not deleted or overwritten. The official answer of the same month in the new snapshot
  `physical_1403-11_20260810T073129Z.json.gz` saved.
- The most recent snapshot of each of the 233 months is healthy and can be parsed; Complete and atomic reconstruction
  CSV produced exactly 6,235 rows of them.
- network-free tests in `tests/test_zinc_contracts.py`, schema and certificate identity,
  Extended filter on, non-negative values, exact duplicate, business key, health latest
  They control the snapshot every month and the selection of a new snapshot during rebuild. companion
  Pipeline tests are a total of fourteen tests in the Zinc test set.
- No underlying analysis, benchmark, processed file or bubble was created at this stage.
### Manual validation design for grades 99.97 and 99.98 — 2026-08-10
- The physical scope of only contracts `نقدی` and `نقدی (مچینگ)` with `Quantity > 0` and
  It is `Price > 0`.
- Daily prices for each grade and for the combined 99.97/99.98 basket are weighted by `Quantity`.
- notebook number of days added by entering 99.98 to 99.97 series and the number of days
  Added to the overlap with the certificate calculates separately.
- The certificate price criterion is `TodaySettlementPrice`; `TradesValue / TradesVolume` only
  validation is this column.
- Coverage, cross-grade price differences, and volume shares are reported with price, spread,
  The active days schematic volume and matrix have been prepared, but not yet implemented and interpreted.
## Current stop status
raw is complete and zinc soil should not be removed from it. hand notebook
`notebooks/zinc_analysis.ipynb` is retained for manual data richness analysis. underlying
The official pipeline uses the 99.97/99.98 grade basket in `نقدی` contracts and
It is `نقدی (مچینگ)`. Benchmark, three bubble definitions and regression test are made and
`notebooks/02_bubble_analysis.ipynb` provides a schematic representation of them at runtime.
## World price on LME — Westmetall — 2026-08-10
Official source used:```text
https://www.westmetall.com/en/markdaten.php?action=table&field=LME_Zn_cash
```

Independent collector `src/zinc/collectors/lme.py` collected the data year by year from 2008
does The first run of all years and the next run of only the year of the most recent observation until the current year
It refreshes. The HTML of each request is unchanged
`data/raw/lme/html_snapshots/zinc_<year>_<timestamp>.html` preserve and CSV canonical
`data/raw/lme/zinc_lme_raw.csv` is written atomically.
raw schema:
- `date`;
- `cash_settlement`, cash price in dollars per ton;
- `three_month`, quarterly price;
- `stock`, source reported inventory;
- `source_year`, `fetched_at_utc` and `source_url`.
The result of complete collection and second incremental execution:
- 4,704 unique and regular dates from 2008-01-02 to 2026-08-07;
- 19 years of source and 20 snapshots are available; Additional snapshot related to the second implementation audit
  The year is 2026;
- The second run only refreshed the year 2026 and had zero new or modified dates;
- 2 amounts of cash, 82 amounts of quarterly and 1 amount of stock in source `-` are either empty and without
  The conversions are preserved in raw; Other values ​​of all three columns have valid numeric format.
Intrinsic price formula, according to the copper method:
```text
LME_Zinc_USD_per_kg = LME_Zinc_cash_USD_per_ton / 1000
intrinsic_zinc_price_IRR_per_kg = LME_Zinc_USD_per_kg × free_market_USD_IRR
```

Free canonical dollar inside Zinc with workspace seed history and with collector TGJU to
It was refreshed on 05/17/1405. The file has 13,064 dates: 34 TGJU closing prices and 13,030
Historical value `legacy_high_low_midpoint`.
## Physical benchmark 99.97 and 99.98
`src/zinc/processing/build_physical_benchmark.py` retains only the two target grades and eligible contracts
Cash/cash matching and select rows `Quantity > 0` and `Price > 0` from wide raw
does The daily price is the benchmark with the weight of the trading volume:
```text
physical_weighted_price = Σ(Price_i × Quantity_i) / Σ Quantity_i
```

`zinc_9798_cash_daily.csv` contains 554 days from 2009-08-16 to 2026-08-09: 239
There are 239 two-grade days, 158 days with only 99.97, and 157 days with only 99.98. Total volume is 155,602 tonnes:
71,852 tons 99.97 and 83,750 tons 99.98.
## LME and dollar alignment
Last observation of LME cash and free dollar on the same day or before the target date with the as-of method
connects The source date and data age are preserved in the output. The maximum current LME age is 4 days.
The maximum age of the dollar is 10 days in the whole benchmark and 1 day in the certificate period.
## Three definitions of bubble
### 1. Physical market compared to intrinsic price
```text
physical_vs_intrinsic_bubble_pct =
    (physical_price / intrinsic_price - 1) × 100
```

`physical_vs_intrinsic_bubble.csv`: 554 views; Average -13.14%, median
-15.87%, minimum -36.02% and maximum 22.28%; 75 positive and 479 negative.
### 2. A certificate of intrinsic value
The price of the certificate is only `TodaySettlementPrice`; `TradesValue / TradesVolume` only
Validation is equal to it.
```text
certificate_vs_intrinsic_bubble_pct =
    (certificate_price / intrinsic_price - 1) × 100
```

`certificate_vs_intrinsic_bubble.csv`: 182 views; Average -20.13%, median
-18.58%, minimum -33.91% and maximum -10.54%; All 182 observations are negative.
### 3. The original bubble of the certificate relative to the estimated physical price
In 41 days, the actual ratio of `physical_price / intrinsic_price` is calculated and between
Consecutive anchors are interpolated linearly based on the calendar day. Before the first and after
The last anchor extrapolation is not performed.
```text
estimated_physical_price_t = interpolated_physical_ratio_t × intrinsic_price_t
certificate_bubble_pct =
    (certificate_price / estimated_physical_price - 1) × 100
```

`zinc_certificate_bubble.csv`: 178 days from 2025-10-26 to 2026-08-09, including 41
real anchor and 137 days of interpolation; Average 0.34%, median 1.02%, minimum -19.58% and
Maximum 16.97%; 102 positive and 76 negative.
## Experimental regression
Three proportional models without width from the origin, linear with width from the origin and polynomial of the second degree
Ridge are compared to `TimeSeriesSplit(5)`. feature only intrinsic price and target price
The benchmark is physical. Current selected model `proportional_no_intercept` with RMSE
It is 256,696.52 rials per kilogram. The main method is still ratio interpolation.
## Display outputs and notebook
| File | row | Application |
|---|---:|---|
| `zinc_9798_cash_daily.csv` | 554-day volume-weighted two-grade benchmark
| `physical_vs_intrinsic_bubble.csv` | 554 Direct physical-intrinsic bubble
| `certificate_vs_intrinsic_bubble.csv` | 184 Direct certificate-intrinsic bubble
| `zinc_certificate_bubble.csv` | 178 The main bubble of interpolation
| `intrinsic_regression.csv` | 184 The output of the experimental method
| `intrinsic_regression_metrics.csv` | 3 | Comparison of RMSE models
`notebooks/02_bubble_analysis.ipynb` makes all outputs read-only and
Tables, three bubble charts, price components, anchors, interpolation, regression and data age
displays notebook at checkpoint 2026-08-15 execution and the output of the charts is saved in the file itself.
## Architectural migration — 2026-08-03
`Cert` layer removed. Data in `data/`, collectors in `src/zinc/collectors/`
And the documentation is at `docs/`. CSVs and raw snapshots were transferred unchanged.
