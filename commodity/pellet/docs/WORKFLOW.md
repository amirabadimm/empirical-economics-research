# Workflow — Iron ore pellet deposit certificate
- Source: Official CDC API of Iran Commodity Exchange, Bazar 22.
- Series start: 07/28/1404 equals 10-20-2025.
- old code: `CD1IOP0001`; New code: `IronOrePlt`; `CommodityID=28`.
- collector: `src/pellet/collectors/certificate.py`.
- shared logic: `../../shared/ime_data/certificate_collector.py` relative to the workspace root; It is also required when transferring the `shared/ime_data` folder.
- CSV: `data/raw/certificate/pellet_certificate_raw.csv`.
- Rules: keeping zero day, complete snapshot, merge on date, fourteen days refresh, atomic writing.
- validation: complete schema, unique date, fixed code/id/description, non-negative values and matching
  `TradesValue / TradesVolume` with `TodaySettlementPrice` on trading days.
- The price criterion in future analyzes is `TodaySettlementPrice` and the ratio of value to volume will only be validation.
- Status 2026-08-10: 252 rows until 2026-08-09; 182 days of positive transactions.
Normal execution from within `commodity/pellet`:
```powershell
python .\src\pellet\collectors\certificate.py
```

Full implementation only for reconstruction or audit:
```powershell
python .\src\pellet\collectors\certificate.py --full-refresh
```

The second incremental execution without increasing the number of rows and all schema controls, date,
OHLC, codes, CommodityID and price settlement has been successful.
Raw physical market data is collected and validated, underlying the two companies selected and
The exploratory bubble is calculated in the notebook. Benchmark file processed independently yet
Not produced.
## Preliminary review of the physical market — 2026-08-03
Review of full snapshots of the official commodity exchange API, between 07/28/1404 and 05/07/1405
And it was done only for transactions with `Quantity > 0` and `Price > 0`. No data files
New production and no final filter was approved.
- 463 rows of transactions in 62 days and a total of 10,008,000 tons;
- Only one product name: "Iron ore bag"; ton unit and bulk packaging;
- 13 producers and 13 symbols;
- Volume shares were Gol Gohar 29.19%, Gohar Zamin 23.72%, Chadormalu 9.54%, and Opal Parsian
  Sangan 9.53% and Senabad Comprehensive Development 7.91%;
- Contracts: cash 48.26%, advance 39.44%, cash matching 7.60% and advance matching 4.70%;
- 97.55% of the volume in the industrial hall.
Result: The product name is consistent, but we don't have a single dominant producer like copper. before
Making a benchmark should be the quality specification of the certificate, grade and delivery terms with the manufacturers' supplies
to be adapted Primary option after homogeneity verification, the portfolio of qualified producers with price
It is the daily volume balance and cash separation from the predecessor; This option is not the final decision yet.
The main recommended resource for the future collector is the official public API of the stock exchange. BrsApi only
For discovery, fallback is kept and no keys are stored in the project.
## Current stage: raw collector of the physical market
File `src/pellet/collectors/physical.py` was created from common logic
Uses `shared/ime_data/ime_physical_collector.py`. Current domain intentionally
Broad: Exact match of the normalized name "iron ore ball", without manufacturer restrictions.
symbol, contract, settlement or volume. Zero value inputs are preserved in raw and full snapshot
It is also archived monthly before the filter.
Output after the first verified run:
```text
data/raw/physical/pellet_physical_raw.csv
data/raw/physical/api_snapshots/*.json.gz
```

The behavior of the collector is incremental and atomic: search for the first implementation from 01/2016 to this month.
and the next normal run will read and replace the last two months.
Execution note: in the first full execution, `curl` Windows after a number of requests with an error
Schannel encountered `SEC_E_NO_CREDENTIALS`, while the same warm-up and POST with HTTPS
Python answered 200 and the schema is complete. Common logic now only when curl fails
`requests` fallback; URL, payload, data source and archive rules have not changed.
### The result of complete execution and validation
Complete execution ended on 2026-08-03:
- 233 healthy and unique monthly snapshots from 01/1386 to 05/1405;
- All snapshots were parsed and there were no corrupted or incomplete responses;
- Raw CSV contains 3,446 rows and 36 columns;
- The actual coverage of the gundle rows from 04/13/1397 to 05/11/1405 and 426 dates are the same;
- All 3,446 rows after normalization are exactly "iron ore";
- 20 manufacturers, 17 symbols and 6 types of contracts are seen;
- 1,592 rows have a positive transaction price and amount and 1,854 supply rows have a zero value;
- There is no negative price or value, missing value in identity fields and absolutely duplicate rows.
Two rows on 09/11/1402 for symbol `GHZ-PELL-00` in summary key date/symbol/price/volume
are the same, but have different `arzehPk` and delivery dates; So two separate offers/transactions
and are properly preserved.
### Incremental refresh — 2026-08-10
- The certificate reached 252 rows by 2026-08-09; It has 182 days of positive transaction volume and no repeated dates.
- The physical market reached 3,467 rows by 05/18/1405; It has 1,606 positive transaction rows and 427 unique dates.
- Three new monthly snapshots were added for 1405/03 to 1405/05 and the number of physical snapshots reached 236.
- Both CSVs still retain the previous schema, non-negative values ​​and zero fully duplicated rows.
- This refresh did not change the raw domain and did not produce any benchmark or processed file.
The next step, without changing raw, was to profile 1,592 positive trades by manufacturer, symbol,
Contract type, settlement, delivery date and price dispersion. Underlying selection and construction
Benchmark is done only after viewing this report and user approval.
### Approved rule of benchmark and certification bubble — 2026-08-15
The benchmark date universe consists of strict-cash trading days for Gol Gohar and Gohar Zamin, not only
Their subscription. If only one of the two companies has traded in one day, the price of the same company
is the benchmark of the day; If both have traded, the simple average of the two prices is used.
Comparison with the certificate only on the exact date and only on the day with the trading volume and positive settlement price
Certification is done; carry-forward and interpolation are prohibited.
This rule was executed in the notebook on 22 common dates with positive certificate transactions: 16 dates
Single-company and 6 two-company dates. The output is currently exploratory and inside the notebook, and the file is processed
Not produced independently.
### Case study of the only positive bubble — 10/21/1404
On this benchmark date, the only qualifying strict-cash price is Gol Gohar at IRR 94,566/kg.
kg, and the settlement price of the certificate was set at 104,998 rials; The bubble increased by 11.03%.
Gohar Zamin's IRR 111,229/kg trade is outside scope because settlement is cash/credit.
Other excluded observations include Gol Gohar's IRR 107,332/kg forward cash/credit trade and
cash/credit were 111,229 rials; So cross-domain in-domain certification
The prices were the same day.
The clearing path of the certificate shows that the increase started before the comparison date: 81,844
Rials on December 10 and 103,483 Rials on December 17, equivalent to about 26.4% growth. On the 21st of the volume
208,726 units, trading range from 103,500 to 105,560 Rials and daily settlement growth of 6.99%
was So it's not a low-volume single trade. Sensitivity test with informal entry of price
The two-producer sensitivity mean is IRR 102,897.5/kg and implies a +2.04% bubble.
Recorded interpretation, price discovery time gap between continuous certificate market and physical cross-sectional supply
About 9 percent of the official bubble is sensitive to the single-company benchmark. No event
The specific contemporaneity was not found in the public news and the definitive root cause is not claimed. view
It is not removed and remains in the analysis with the label "single-firm/combination sensitive".
### LaTeX report output
The complete English report is in `reports/pellet_certificate_report.tex`. Four figures
Report with reports/build_report_figures.py directly from raw canonical CSVs and
Without changing them, they are created and saved in reports/figures. Execution control
The maker of the figures should have 22 bubble observations, 16 single days, 6 double days and exactly one
Confirm the positive bubble. XeLaTeX is not installed in the current environment and the PDF is not generated.
### Notebook of critical review of companies
`notebooks/01_physical_analysis.ipynb` supports transparent exploratory decision-making.
In the 2026-08-09 review of its reproducible outputs and execution counts for Git Pak
were Restarting the notebook is required to view the graphs. Its scope
Only "cash" and "cash (matching)" contracts have `Tasvieh == نقدی`,
`Price > 0` and `Quantity > 0`. Cash/Credit transactions even with Contract Type Cash
are deleted. `Price` remains the source price criterion and relation
`Price = TotalPrice / Quantity` is controlled with a rounding tolerance of 0.51 rials. in
269 rows of this domain, the biggest difference was 0.5 rials.
The notebook calculates the balanced price of each company/symbol on each day, first by contract and then by form
It makes a combination of cash + matching; Balancing is done only between rows of the same company and on the same day
It reports the principal producers, cash-versus-matching differences, and each producer's distance from the daily market-weighted price.
Same day cross-sectional comparison of a selected date and daily scatter chart for the underlying decision
It is located in it. No notebook output is saved in raw or raw CSV is overwritten.
## previous checkpoint of exploratory analysis
In the previous checkpoint, the space was limited to "cash" and "cash (matching)" contracts
The choice of companies was open. This step is now with the decision recorded in the checkpoint
2026-08-11 terminated. Contract restrictions and manufacturer selection only in analysis
are applied and do not modify the raw CSV. At the same checkpoint, the bubble is still calculated
had not been done; This situation has been replaced by the approved rule and heuristic calculation on 08-15-2026.
## Architectural migration — 2026-08-03
`Cert` layer removed. Data in `data/`, collectors in `src/pellet/collectors/`
And the documentation is at `docs/`. notebook was removed from raw and raw was transferred without changes.
## Modifying the scope of settlement and re-executing the analysis — 2026-08-15
The previous definition only handled `ContractType` and included rows with `Tasvieh =
نقدی/اعتباری`. At the user's decision, the scope was modified: the contract type should
Cash or cash matching and the type of settlement must be exactly cash. The entire notebook with this definition
It was implemented from the beginning. 269 ​​rows remained in 138 days and 13 symbols.
Since certificate inception, the strict-cash sample totals 1,430,000 tonnes. Gol Gohar accounts for 791,000 tonnes
(55.31%), Gohar Zamin 211,000 tonnes (14.76%), and Sangan Khorasan 85,000 tonnes (5.94%).
Chadormalu has no eligible strict-cash trades in this period. Gol Gohar and Gohar Zamin together
They made up 70.07% of the actual cash market.
Across the full history, Gol Gohar and Gohar Zamin share only 16 strict-cash dates: nine dates
before and 7 days after the start of the certificate. Symmetric difference
`100 × |P1-P2| / ((P1+P2)/2)` before certification average 1.53% and after
was 0.88%; The median of both periods is zero. After starting the certificate in 4 days out of 7 days of subscription
The prices were exactly equal and the largest symmetric difference was 3.32%. So increase
The dispute will not be confirmed after the certificate has started.
The apparent gaps on 1404/10/21 and 1404/11/12 are removed from common-date comparisons because Gohar Zamin only
There was a cash/credit settlement. On 12/03/1404, after removing the credit line, the cash price of each
Two companies are exactly 104,471 rials and the difference is zero. Result: Gaps of 17%, 23% and 7%
They were caused by the mixing of settlement methods, not the difference in the cash price of the two goods.
The benchmark scope is Gol Gohar and Gohar Zamin; raw files and snapshots remain unchanged. The rule
Joint and single company days are later approved and in the section "Approved Benchmark Rule and Certificate Bubble"
has been registered.
### Statistical basis for excluding Sangan Khorasan and Chadormalu
The basis for the selection of the manufacturer is the volume representation in the total positive transactions of the market since the beginning of the certificate.
and is not limited to the type of contract or settlement method. The total market volume is 10,751,000 tons:
Gol Gohar accounts for 3,306,000 tonnes (30.75%), Gohar Zamin 2,484,000 tonnes (23.10%), and Chadormalu
1,055,000 tons (9.81%) and Sangan Khorasan 608,000 tons (5.66%).
Gol Gohar and Gohar Zamin cover 53.86% of the total market; the combined share of Sangan Khorasan and Chadormalu
It is 15.47%. Each of the latter two companies is clearly smaller than the market leaders and the market
Ghalib is not at their disposal. The main reason for the removal is lower volume representation in all market conditions
Lack of common points and price difference are additional reasons. The data is both in raw and
exploratory analyzes are maintained. The cash settlement filter is applied only when making the benchmark price
It is possible, not when measuring the size and representation of the market.
### Case study 04/11/1401
The largest symmetric difference of real cash common points was checked on 04/11/1401. Base price
Both companies 28,298 rials, supply of both 50,000 tons, delivery date 04/14/1401, warehouse
Factory delivery and settlement terms were aligned and fully cash. Gol Gohar demand was 65 thousand tonnes (1.3 times supply).
Gohar Zamin demand was 150 thousand tonnes (3.0 times supply).
Gol Gohar trades at IRR 28,987/kg, 2.43% above base, while Gohar Zamin trades at IRR 31,299/kg,
Rial was 10.60% higher than the trading base. The difference in rials is 2,312 rials per kilogram.
The directional difference was 7.98% and the symmetric difference was 7.67%.
The immediate price mechanism is stronger competition for the Gohar Zamin offer. Available data
It does not prove buyer preference—quality, shipping, technical specifications, or business relationship. This date
It will not be removed and will be retained in the analysis as a true observation of market competition.
