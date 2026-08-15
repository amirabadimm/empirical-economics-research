# Copper Warehouse-Receipt Certificate: Complete Research Workflow
The last update of the document: 24 August 1405 / 2026-08-15
## Update checkpoint — 2026-08-15
LME, currency, certificate and physical market collectors are implemented incrementally and all outputs
processed and the original notebooks were rebuilt. Current status: LME equal to 4,709 rows
Until 08-14-2026, currency equal to 13,067 rows until 05/20/1405, certificate equal to 256 rows
calendar and 184 positive transaction days until 2026-08-13, and physical raw equal to 1,165 rows until
It is 05/18/1405. The physical benchmark has 791 days. The main bubble is 178 days from
2025-10-26 to 2026-08-09, includes 28 real anchors and 150 interpolated days;
Its mean is 5.53% and its median is 7.06%. Selected sensitivity model with current data
It is `polynomial_degree_2_ridge`. Original notebooks with project kernel run without errors
And the output of the charts were saved in the notebooks themselves.
This document is the main reference for transferring, rebuilding and continuing the project on another system. The aim of the project is to measure the distance between the price of the copper cathode deposit certificate and the corresponding price of copper in the physical market of the Iran Commodity Exchange. All important data decisions, sources, filters, formulas, outputs and constraints are recorded in this file.
## 1. The main question of the project
We want to know whether the copper deposit certificate is positive or negative compared to the cathode copper traded in the physical market of the Commodity Exchange. The main issue is that:
- the certificate is traded in a large number of days;
- The physical copper market is mostly weekly and sometimes irregular;
- In the current period of the certificate, we have 178 days of positive transaction of the certificate, but only 26 days of positive physical transaction at the same time;
- Therefore, the direct bubble of the certificate compared to the actual physical price can only be calculated on the 26th, and the physical price must be estimated for other days.
The main and approved method of the project is "linear interpolation of the ratio of physical price to intrinsic price". Regression on inherent price is also made as an alternative and experimental method.
> Architecture migration 2026-08-03: `Cert` layer removed; LME, FX, certificate and physical market
> They were placed under an integrated project. Notebooks and logs were removed from raw and logic
> Collectors subscriber was transferred to `shared/ime_data`. The raw content was not changed.
## 2. Folder structure
```text
shared/ime_data/                 # collectorهای مشترک بورس کالا
projects/{bitumen,pellet,zinc}/  # پروژه‌های کالایی هم‌ساختار
commodity/copper/
├── src/copper/
│   ├── collectors/              # LME، ارز، گواهی و بازار فیزیکی
│   ├── processing/              # benchmark، حباب و timeline
│   ├── analysis/
│   └── tools/
├── data/
│   ├── raw/{lme,fx,certificate,physical}/
│   ├── interim/
│   └── processed/
├── notebooks/
├── logs/
├── outputs/
└── docs/
```

The project rule is to keep the raw response of the resources in `raw` and any computational or reproducible files in `processed`. The `src` folder is the location of pipeline executable scripts; The notebook is a place for analysis, graphing and testing and is not considered the main source of data collection. The common logic of the four-certificate collector is in `shared/ime_data/certificate_collector.py`, and the file inside each project defines only the explicit settings of the same commodity.
## 3. Data sources and access decisions
### 3.1. LME global copper price
Source:
```text
https://www.westmetall.com/en/markdaten.php?action=table&field=LME_Cu_cash
```

The `commodity/copper/src/copper/collectors/lme.py` script retrieves the data year by year from 2008. In the first execution, the entire date and in the subsequent executions only the year of the most recent observation until the current year will be read. Existing dates are updated when the source is modified and new dates are added. The HTML of each request for reproduction is stored in `data/raw/lme/html_snapshots`.
Current file `commodity/copper/data/raw/lme/copper_lme_raw.csv`:
- 4,699 rows;
- the period from 2008-01-02 to 2026-07-31;
- The main column of this project is `cash_settlement` with the unit of dollars per ton;
- There are three historical values ​​`-` in the cash price, which are outside the certificate period and are excluded from the calculations.
### 3.2. Free dollar to rial
The file `commodity/copper/data/raw/fx/usd_to_rial.csv` was first provided manually and is supplemented with `commodity/copper/src/copper/collectors/fx.py` from the historical table `price_dollar_rl` of TGJU site.
- The current column `price_irr` specifies the dollar price used and the column `price_method` specifies its method;
- New data and TGJU recoverable OHLC dates are stored with closing price (`close`);
- The old rows that only the minimum and maximum averages are available in the old file are preserved and marked with `legacy_high_low_midpoint`;
- Its unit is Rial for every dollar;
- Jalali history is the main key to integration and maintenance;
- validates Jalali/Miladi conversion script;
- The source HTML is stored in `data/raw/fx/usd_snapshots`;
- In the initial cleaning on the 37th, a correction and a completely identical repetition was removed.
The current file has 13,060 unique dates and covers until 05/11/1405, equivalent to 08-02-2026. 30 recent dates have close restored and 13,030 old dates have legacy value preserved.
### 3.3. Copper deposit certificate
The main source is the official public API of Iran Commodity Exchange:
```text
https://dataapi.ime.co.ir/api/CDC/CDCTrades
```

Contract history codes used:
```text
CD1COP0001 (قدیمی) و CopperCthd (جدید)
```

The `collect_certificate.py` script receives daily responses incrementally, also reads the 14 days prior to the most recent local date to detect modifications, and keeps JSON snapshots.
Current raw file:
```text
data/raw/certificate/copper_certificate_raw.csv
```

- 246 calendar rows from 2025-10-20 to 2026-08-02;
- 178 days with `TradesVolume > 0`;
- The first 20 rows with `CD1COP0001` until 2025-11-11 and the continuation of the series with `CopperCthd` from 2025-11-12;
- Days without trading are also preserved with zero volume in raw;
- The official benchmark of the daily price of the certificate is `TodaySettlementPrice`; The ratio `TradesValue / TradesVolume` is used only as an independent control and the allowed difference due to rounding is at most half a rial.
### 3.4. Three additional certificates collected with the shared architecture
Three independent projects of the same level `Copper` have been created. Each project folders `src/<commodity>`,
`data/raw/certificate`, `data/processed` and README files, AGENTS and
It has independent WORKFLOW. All use the same common logic, but settings and CSV
Each item is separate:
| Project Old code New code CommodityID | Raw file
|---|---|---|---:|---|
| `Pellet` pellet `CD1IOP0001` | `IronOrePlt` | 28 `pellet_certificate_raw.csv` |
| Ingot on `Zinc` | `CD1ZNI0001` | `ZincIngot` | 30 | `zinc_certificate_raw.csv` |
| Bitumen `Bitumen` | `CD1BIT0001` | `Bitumen` | 26 `bitumen_certificate_raw.csv` |
In the state of 08-03-2026, all three files, like copper, have 246 calendar rows from 2025-10-20 to
2026-08-02 and they have 178 positive trading days. In all four series, the old code in 20 rows
2025-11-11 and the new code will be seen from 2025-11-12 onwards. Physical market, reference price
And the bubble of three new products have not yet been designed.
Independent validation of four CSVs PASSED the following:
- uniqueness and ascending order of history;
- matching Jalali and Gregorian dates;
- Stability of contract description, CommodityID and set of authorized codes;
- non-negativity of volume, value, prices and open position;
- placing the price of the first and last transaction in the minimum and maximum range;
- Difference less than 0.51 rials between `TradesValue / TradesVolume` and `TodaySettlementPrice`;
- The existence of a complete snapshot and the absence of an incomplete temporary file.
The second incremental execution of all four collectors kept the number of rows constant; Therefore
The idempotency of merge and the absence of duplicates were confirmed.
### 3.5. The physical market of the commodity exchange
Official source:
```text
https://www.ime.co.ir/subsystems/ime/services/home/imedata.asmx/GetAmareMoamelatList
```

The API response is in the envelope of the `d` field in the form of a JSON string and must be parsed again. `collect_physical.py` checks the data month by month from 1386/01 and refreshes the local two months before the most recent month in the next run. The complete snapshot of responses is saved as `json.gz`.
### 3.6. Decision about TSETMC and BrsApi
`api.tsetmc.com` official service and TSETMC official SOAP are subscription and paid and require organizational membership, username and contract. `cdn.tsetmc.com/api` public endpoints are stable without official contract and documentation. As a result, the final pipeline is not dependent on TSETMC and uses the official APIs of the commodity exchange. No API key is required to run the current pipeline.
User has full subscription `brsapi.ir`. endpoint of the physical market of this service on 2026-08-03
Tested with the recommended browser header and a one-day request HTTP 200 valid response with
Returns the appropriate schema for physical transactions. Trying to get too many days in cash
The sequence later stopped with an HTTP 402; So the output of that test run was incomplete and entered
No data set or calculated. This event can be caused by quota, rate limit or
Endpoint subscription setting does not mean no data.
Source decision up to this date:
1. The official public API of the commodity exchange remains the main source and production; because direct
   No API key, complete monthly history, archiveable and auditable.
2. BrsApi is a useful tool for quick discovery of schema, mutual control and fallback, but until
   When the quota, error behavior, historical coverage and its stability in full implementation are not confirmed,
   It does not replace the official source.
3. If the BrsApi enters the pipeline later, the raw response and its difference with the official source should be recorded
   and the collector should not overwrite the official healthy raw with the failure of the third source.
4. No API key or credentials stored in code, README, WORKFLOW, CSV, snapshot or log
   do not; The key should only be read from the environment variable and the key disclosed in the dialog should be replaced.
### 3.7. Preliminary examination of the physical market of three new certificates
Heterogeneity checking of full and intact snapshots to avoid more third-party API consumption
Commodity exchange official API done in `commodity/copper/data/raw/physical/api_snapshots`. this
Snapshots contain all physical market commodities before the copper filter. Scope of review
It was from 07/28/1404 to 05/07/1405 and only rows with `Quantity > 0` and `Price > 0`
They were counted in the traded statistics. The detailed result is recorded in the independent WORKFLOW of each item.
- Gundle: same product name, but 13 producers and a combination of cash, matching and advance; contrary to
  Copper does not have a single dominant producer.
- Zinc: zinc dust must be separated from zinc ingot; multiple ingot grades and 24
  is a producer.
- Bitumen: the most heterogeneous market, with 12 grades, 40 producers and cash, credit, advance contracts
  and types of matching.
At this stage, no final filter, benchmark or physical CSV has been created for these three products
is The necessary step before implementation is to match the technical specifications and delivery conditions of the certificate with the goods
Physical and then explicit verification of the basket is comparable.
## 4. Physical market refining decisions
In the initial review, multiple groups were seen including "Copper Cathode", "Copper Cathode 2", other manufacturers and cash, matching, self and loan contracts. After review, the final benchmark was intentionally limited to:
- Product: exactly "copper cathode";
- Manufacturer: Iran National Copper Industry Company;
- Two old and new symbol formats: `NCI-CCAA-00` and `NCI-OACCAA-00`;
- Only "cash" and "cash (matching)" contracts;
- Removal of Self, Self Matching, Nisseh, Copper Cathode 2 and all other manufacturers from CSV canonical;
- Keeping supplies with zero value in raw, but removing them from the traded price benchmark.
The current raw canonical file `copper_cathode_physical_raw.csv` has 1,163 rows and 36 columns, from 06/03/1387 to 05/04/1405.
### Definition of cash and cash matching
"Cash" is a transaction that is finalized in the main session of the offering and based on the competition/adjustment mechanism of the same offering. "Matching" is the additional step or mechanism of matching the orders with the confirmed terms and price of the supply. Both are cash; The difference is in the way the transaction is done, not necessarily in the nature of the settlement.
In our historical data:
- In 362 days, there were both types of positive transactions;
- In 361 days, there was exactly one cash row and one matching row;
- Only on 10/10/2013 there was one cash row and two matching rows;
- The registered cash price and all matching rows were equal on all common days;
- This does not mean making "separate balanced series over time"; The comparison was made at the level of each day and rows of the same day.
Despite the historical parity of prices, cash volume and separate matching are maintained in the control output. If in a future execution the price of the two methods diverges, `build_physical_benchmark.py` is intentionally stopped so that the single-price rule does not continue without checking.
## 5. Making a daily benchmark of the physical market
script:
```powershell
python .\src\copper\processing\build_physical_benchmark.py
```

Only rows with `Quantity > 0` and `Price > 0` are included in the calculation. Daily benchmark definition:
```text
physical_weighted_price = Σ(Price × Quantity) / Σ(Quantity)
```

Output:
```text
data/processed/nci_copper_cash_daily.csv
```

Current status:
- 789 positive transaction days;
- the period from 08-24-2008 to 07-26-2026, equivalent to 06/03/1387 to 05/04/1405;
- Only one final price column called `physical_weighted_price`;
- Cash volume, matching volume, matching share, number of rows, symbols and Jalali/Maladi date are maintained for control.
## 6. Data alignment
The LME and USD prices for each target date are linked by the as-of method to the last available observation on or before the same day. This is necessary for holidays and trading calendar differences. In the outputs, the source date and data age are preserved with the columns `lme_source_date`, `lme_age_days`, `usd_source_date` and `usd_age_days`.
Intrinsic price per kilogram of copper:
```text
LME_USD_per_kg = LME_cash_USD_per_ton / 1000
intrinsic_price_irr_per_kg = LME_USD_per_kg × free_market_USD_IRR
```

This inherent price does not directly consider internal costs, taxes, storage fees, shipping, quality, delivery restrictions and other frictions of the Iranian market; For this reason, the internal physical price is not necessarily equal to it.
## 7. Three different definitions of bubbles
These three charts should not be confused with each other.
### 7.1. Physical market bubble relative to intrinsic price
```text
physical_vs_intrinsic_bubble_pct =
    (physical_price / intrinsic_price - 1) × 100
```

The output `physical_vs_intrinsic_bubble.csv` contains all 789 physical market days. Current stats:
- Average: -8.42%;
- Median: -6.88%;
- Minimum: -57.52%;
- Maximum: 28.04%;
- 150 positive observations and 639 negative observations.
This indicator shows the distance of the physical domestic market from the LME-dollar.
### 7.2. The direct bubble of the certificate relative to the inherent price
```text
certificate_vs_intrinsic_bubble_pct =
    (certificate_price / intrinsic_price - 1) × 100
```

The output `certificate_vs_intrinsic_bubble.csv` contains 178 days of certificate transactions. Current stats:
- Average: -9.67%;
- Median: -9.53%;
- Minimum: -26.00%;
- Maximum: 3.76%;
- 13 positive observations and 165 negative observations.
This indicator shows the distance of the certificate from the LME-USD, not the bubble of the certificate relative to the domestic market.
### 7.3. The original bubble of the certificate relative to the estimated physical price
```text
certificate_bubble_pct =
    (certificate_price / estimated_physical_price - 1) × 100
```

This is the main criterion of the project, because its denominator is the corresponding price of the domestic market.
## 8. Main method: linear interpolation of ratio
On the 26th actual joint date, the following ratio is first calculated:
```text
physical_ratio = physical_price / intrinsic_price
```

Then this ratio itself is linearly interpolated between both real points based on the number of calendar days:
```text
interpolated_ratio_t = ratio_left + weight_t × (ratio_right - ratio_left)
estimated_physical_price_t = interpolated_ratio_t × intrinsic_price_t
```

Finally, the main bubble is calculated from the price of the certificate divided by the estimated physical price. No extrapolation is performed before the first or after the last actual point.
script:
```powershell
python .\src\copper\processing\build_certificate_bubble.py
```

Output `copper_certificate_bubble.csv`:
- 169 days from 2025-10-26 to 2026-07-26;
- 26 observed points;
- 143 interpolated days;
- average bubble: 5.17%;
- Median: 6.13%;
- Minimum: -14.52%;
- Maximum: 23.70%;
- 125 positive observations and 44 negative observations.
This result is the basis of the present summary of the presentation: the certificate has been a positive bubble relative to the corresponding physical price for a large part of the period and has limited appeal from a value investment perspective. This result is not a definitive buy or sell recommendation and is sensitive to sample limitations.
## 9. Alternative Test Method: Regression on LME × Dollar
Important modification: The regression should not be run as two separate and summable variables on LME and dollar. The unit explanatory variable is the intrinsic price:
```text
X = intrinsic_price = LME_USD_per_kg × USD_IRR
y = physical_price_irr_per_kg
```

The price of the certificate is not included in the regression fitting at all and is only used to calculate the bubble after the physical price is predicted.
The script `build_intrinsic_regression.py` compares three models with `TimeSeriesSplit(n_splits=5)`:
1. Proportional regression without width from the origin;
2. Linear regression with width from the origin;
3. Quadratic polynomial with RidgeCV.
The model with the lowest out-of-sample RMSE is selected and then fitted to all 26 points. In the current implementation, a linear model with a width from the origin is selected:
```text
estimated_physical_price = 1,929,020.20 + 0.75842654 × intrinsic_price
```

Unit output:
```text
data/processed/intrinsic_regression.csv
```

This file has 178 rows. The actual physical price column is filled only on 26 actual dates and remains empty on other dates. Current regression bubble statistics:
- Average: 4.67%;
- Median: 4.90%;
- Minimum: -13.55%;
- Maximum: 23.10%;
- 116 positive observations and 62 negative observations.
This method is complementary and experimental. The official main method of the project is still ratio interpolation, because we only have 26 points to estimate a statistical relationship and the possibility of instability of coefficients is high.
## 10. Time status of 26 physical transactions in the certification period
All 26 positive physical trades within the certificate window coincide exactly with one day of certificate trading. The first date is 08/04/1404 and the last date is 05/04/1405. The first date was restored only after connecting the old code of the certificate.
The pattern is unbalanced:
- Three initial observations on 08/04/1404, 09/02/1404 and 09/26/1404;
- then a break of 102 days until 01/09/1405;
- Since April 1405, transactions have become mostly weekly;
- There are 14 intervals of exactly 7 days, five intervals of one day and some intervals of 4 or 6 days.
Therefore, the binary chart whose horizontal axis is the row number of certificate days is not a "weekly distribution". For presentation, it is better to use the actual axis of Jalali history or to display the number of physical transactions by month.
## 11. Presentation files
Two timeline files are located in `processed` and with
`src/copper/processing/build_presentation_timeline.py` are reproduced:
- `presentation_timeline_daily.csv`: 287 calendar days, with glorious date, Excel serial and numerical flags;
- `presentation_timeline_events.csv`: 204 market events, suitable for scatter/timeline.
These files are made for drawing in Excel and PowerPoint. The display date is jalali and the value columns are stored as numbers.
## 12. Analysis notebook
File `analysis.ipynb` contains code and analytic output, a chart of three bubble definitions, physical market history, regression tests, and a modified regression on intrinsic price section.
Important points:
- Some old cells are experimental and may show separate bivariate regressions of LME and USD; That method has been abandoned;
- Modified section at the end of the notebook only uses `intrinsic_price`;
- data generation pipeline should be executed with `src` scripts, not relying on the order of execution of notebook cells;
- Kernel and relative paths should be checked before full implementation on the new system.
## 13. Complete implementation of the pipeline
From root `Copper`:
```powershell
python .\src/copper/collectors/lme.py
python .\src/copper/collectors/fx.py
```

Then:
```powershell
cd C:\Work\commodity\copper
python .\src\copper\collectors\certificate.py
python .\src\copper\collectors\physical.py
python .\src\copper\processing\build_physical_benchmark.py
python .\src\copper\processing\build_intrinsic_bubbles.py
python .\src\copper\processing\build_certificate_bubble.py
python .\src\copper\processing\build_intrinsic_regression.py
python .\src\copper\processing\build_presentation_timeline.py
```

Three new independent certificates are updated from the copper bubble pipeline and from the workspace root as follows:
```powershell
python .\commodity\pellet\src\pellet\collectors\certificate.py
python .\commodity\zinc\src\zinc\collectors\certificate.py
python .\commodity\bitumen\src\bitumen\collectors\certificate.py
```

The order of the builders is important: the physical benchmark must be built before the bubble files, and `build_intrinsic_bubbles.py` must be run before the regression, because the regression reads two intrinsic outputs.
Incremental behavior:
- LME: readout from the year of the most recent record;
- Dollar TGJU: add new date with close, overwrite visible OHLC dates with close and preserve legacy dates;
- Certificate: refresh default 14 days;
- physical: default refresh of two local months;
- Processed files: they are recreated from the current raw every time.
## 14. Software requirements
Python 3.9 or later is recommended. Main collectors mainly use the standard library and `curl`. For all analyzes and regressions:
```powershell
python -m pip install pandas numpy scikit-learn jdatetime matplotlib jupyter
```

New system tips:
- `curl` must be in PATH; In Windows 10/11 it usually already exists;
- Internet, TLS 1.2 and access to Westmetall, TGJU, `dataapi.ime.co.ir` and `www.ime.co.ir` domains are required;
- VPN may affect DNS, TLS or resource access, but pipeline does not have option to bypass VPN; Network configuration must be done at the system level;
- CSVs are written with `utf-8-sig` so official Persian source labels display correctly in Excel.
## 15. Transfer to another laptop checklist
1. Copy the entire `Copper` folder and the `shared/ime_data` peer folder, not just the notebook or `processed`. To transfer the set of four certificates, the folders `Pellet`, `Zinc` and `Bitumen` should also be transferred.
2. Be sure to transfer this irreplaceable data immediately:
- `commodity/copper/data/raw/lme/copper_lme_raw.csv`;
- `commodity/copper/data/raw/fx/usd_to_rial.csv`;
- total `commodity/copper/data/raw`;
- HTML/JSON/JSON.GZ snapshots for auditing;
- `presentation_timeline_*.csv` and their independent builder;
- Notebooks, READMEs, AGENTS and the same WORKFLOW.
3. The `__pycache__` folders are not necessary and can be omitted.
4. Install Python and dependencies.
5. First, just test reading the files:
```powershell
python -c "import pandas as pd; print(pd.read_csv(r'commodity/copper/data/raw/lme/copper_lme_raw.csv').shape)"
```

6. Then run processed constructors from `commodity/copper` and compare the number of rows with the next section.
7. Run internet collectors after making sure of the backup. Scripts write atomic, but raw and snapshots are the capital of project reproduction.
8. If the project is moved with Git, check that large data files or snapshots have not been deleted by `.gitignore`. Transfer is more secure with direct copy or full archive.
## 16. Check the accuracy after transfer
As of the date of this documentary, it is expected:
| File | Number of rows interval |
|---|---:|---|
| `copper_lme_raw.csv` | 4,709 | 2008-01-02 to 2026-08-14 |
| `usd_to_rial.csv` | 13,067 | Until 05/20/1405
| `copper_certificate_raw.csv` | 256 2025-10-20 to 2026-08-13 |
| `copper_cathode_physical_raw.csv` | 1,165 | 06/03/1387 to 05/18/1405 |
| `nci_copper_cash_daily.csv` | 791 2008-08-24 to 2026-08-09 |
| `physical_vs_intrinsic_bubble.csv` | 791 2008-08-24 to 2026-08-09 |
| `certificate_vs_intrinsic_bubble.csv` | 184 2025-10-20 to 2026-08-13 |
| `copper_certificate_bubble.csv` | 178 2025-10-26 to 2026-08-09 |
| `intrinsic_regression.csv` | 184 2025-10-20 to 2026-08-13 |
After updating resources, it is normal to increase the number of rows. More important conceptual controls are:
- The date must be unique and orderly;
- The number of anchors in the current period should be 26; This number should not be hard-coded in the code;
- Negative or zero price and volume should not enter the traded benchmark;
- The certificate is not in the feature regression model;
- the regression feature is the product of LME/kg and USD/IRR, not two separate variables;
- do not extrapolate outside of the two anchors, the beginning and the end, in the main method;
- The unit of all final prices is Rials per kilogram.
## 17. Investment restrictions and interpretation
- There are only 26 simultaneous physical views in the certificate window; This is the most important statistical limitation;
- The 102-day break and then the concentration of observations in the new months makes the sample unbalanced in terms of time;
- Interpolation assumes that the internal to intrinsic price ratio changes linearly between two supplies;
- Regression assumes that there is a relatively stable relationship between intrinsic price and internal price;
- as-of matching may use the last available LME or dollar on holidays; The age of the data in the output is preserved and must be controlled;
- Tax, storage cost, delivery cost, quality, transaction limit and liquidity can explain part of the price gap;
- A positive bubble alone does not mean a definite price drop, but it reduces the margin of confidence of the buyer;
- The yield of the certificate is a simultaneous function of global copper, the dollar, the state of the domestic market and the change of the bubble itself; Even as the LME and dollar grow, deflating the bubble can reduce returns.
Current Advisory Summary: In the current sample, the primary bubble of certification is mostly positive. Therefore, for value-based investing, the certificate has limited appeal in prices with positive bubbles, and it is better to observe the reduction of the bubble, the improvement of the trading depth and the increase of the sample length. This summary is analytical and does not constitute a personalized buy or sell recommendation.
## 18. Continuation plan
In future updates:
1. LME, dollar, certificate and physical market collectors are executed every week;
2. The processed ones are reconstructed in a specific order;
3. Report the number of anchors, time slots and LME/USD age;
4. Monitor the results of ratio interpolation and regression together;
5. As the sample gets bigger, stability tests of coefficients, rolling/expanding validation and simpler/stronger models should be investigated;
6. Maintenance fees, taxes and detailed specifications of certificate delivery should be added to the fair value model if available;
7. Presentation timeline after each refresh and the numbers of slides are controlled.
## Detection of forward transactions in the 102-day cash gap - 08-15-2026
`data/processed/nci_copper_forward_gap.csv` file with script
`src/copper/processing/build_forward_gap_analysis.py` of immutable snapshots of the physical market
The diagnostic scope is limited to exact symbol `NCI-OACCAA-00` and the exact copper-cathode product of National Iranian Copper Industries Company.
Iran, forward and forward matching contracts, and rows with positive price and volume.
This output includes 16 transaction dates and 26,420 tons in the open interval between two cash transactions on 09/26/1404 and
Covers 01/09/1405. For each day, the weighted price of the default with the previous spot price, the next spot price, and
A linear bridge is compared between two anchors. The range of difference with previous cash is 7.16% to 33.73% and with cash
Next is negative 14.05% to positive 7.26%. This data is diagnostic and injected into the main cash benchmark
No, because the maturity adjustment and financing cost have not been applied yet. The table and its diagram at the end
`notebooks/02_certificate_analysis.ipynb` is located.
## 19. checkpoint set of four certificates — 2026-08-03
After completing the copper pipeline, three independent projects `Pellet`, `Zinc` and `Bitumen` with the structure
They were built on the same level. Certificate data of all three projects with CDC common collector, old/new code
Connected, `TodaySettlementPrice` was collected as the same official price and validation.
As of this date, all three series of certificates have 246 calendar rows and 178 positive trading days.
For physical market, public file
`shared/ime_data/ime_physical_collector.py` was created. This logic:
- reads the official public API of the commodity exchange month by month;
- preserves the full response before the filter as `json.gz`;
- CSV writes a product atomically and incrementally;
- it is possible to fallback from curl/Schannel to `requests`;
- With `--rebuild-from-snapshots`, the latest healthy snapshot every month without re-downloading
  Converts to CSV canonical.
Physical market archives are the total market response, not the copper pre-filtered response. So for
Avoiding 233 duplicate downloads and VPN/TLS issues, full official snapshots available for
Building an independent archive on and completing the missing months of bitumen were used. provenance includes URL,
The payload, the time of receipt and the full text of the response are preserved in each snapshot.
| Project Raw Physical CSV | raw row | Positive transaction Real coverage
|---|---|---:|---:|---|
| pellet | `commodity/pellet/data/raw/physical/pellet_physical_raw.csv` | 3,446 | 1,592 | 13/04/1397 to 11/05/1405 |
| on | `commodity/zinc/data/raw/physical/zinc_physical_raw.csv` | 6,178 | 3,428 | 07/28/1387 to 05/07/1405 |
| Bitumen `commodity/bitumen/data/raw/physical/bitumen_physical_raw.csv` | 47,035 | 24,154 | 06/02/1387 to 05/12/1405 |
Validation of all three CSVs not completely duplicate row, negative price/value and missing identity
confirmed raw intentionally preserves zero value supplies and all contract types.
### Analytical status of the pellet
- Only one product name, ton unit, bulk, rial and factory warehouse;
- In positive transactions, 15 economic symbols were traded and several producer name changes;
- Six types of contracts; The current exploratory decision is to focus on cash and cash matching;
- `Price = TotalPrice / Quantity` relationship in 1,057 rows of this domain with the largest difference
  The rounding of 0.5 rials was confirmed;
- `01_physical_analysis.ipynb` with 18 valid cells and no saved output for daily comparison
  Companies, cash/matching and distance from the market were built;
- The underlying and the final benchmark have not been approved yet.
### Analytical status of zinc
- raw contains 12 titles and zinc soil has 94.15% of the total volume of the group;
- The soil on the base asset is not certified and will be separated from the ingot only during the analysis stage;
- Zinc ingots span grades 99.90 through 99.99 across multiple producers and symbols;
- No grade filter, company or contract and no final benchmark has been created yet.
### Analytical status of bitumen
- raw includes 51 titles, 167 producers, 527 symbols and 8 types of contracts;
- In positive transactions, bitumen 60/70 is about 63.36%, 85/100 is about 11.47%, PG 64-22
  About 9.78% and MC250 about 4.02% volume;
- Grade, domestic/export and cash/credit/advance conditions are not yet filtered;
- No final benchmark or bitumen bubble has been created.
The boundary of the next stage is clear: raw none of the three new goods are overwritten. First the specifications
The technical and delivery terms of the certificate are adapted to the physical market tiers; Then filter
Underlying is implemented with the user's approval in processed and then the weighted price and the bubble are made
will be
