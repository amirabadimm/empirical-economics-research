# Workflow — Bitumen deposit certificate
- Source: Official CDC API of Iran Commodity Exchange, Bazar 22.
- Series start: 07/28/1404 equals 10-20-2025.
- old code: `CD1BIT0001`; New code: `Bitumen`; `CommodityID=26`.
- collector: `src/bitumen/collectors/certificate.py`.
- shared logic: `../../shared/ime_data/certificate_collector.py` relative to the workspace root; It is also required when transferring the `shared/ime_data` folder.
- CSV: `data/raw/certificate/bitumen_certificate_raw.csv`.
- Rules: keeping zero day, complete snapshot, merge on date, fourteen days refresh, atomic writing.
- validation: complete schema, unique date, fixed code/id/description, non-negative values and matching
  `TradesValue / TradesVolume` with `TodaySettlementPrice` on trading days.
- The price criterion in future analyzes is `TodaySettlementPrice` and the ratio of value to volume will only be validation.
- 2026-08-03 situation: 246 rows until 2026-08-02; 178 days of positive transaction.
Normal execution from within `commodity/bitumen`:
```powershell
python .\src\bitumen\collectors\certificate.py
```

Full implementation only for reconstruction or audit:
```powershell
python .\src\bitumen\collectors\certificate.py --full-refresh
```

The second incremental execution without increasing the number of rows and all schema controls, date,
OHLC, codes, CommodityID and price settlement has been successful.
Raw physical market data is now collected and validated; ultimate underlying,
The benchmark has been processed and the bubble has not yet been selected or generated.
## Preliminary review of the physical market — 2026-08-03
Review of full snapshots of the official commodity exchange API, between 07/28/1404 and 05/07/1405
And it was done only for transactions with `Quantity > 0` and `Price > 0`. No data files
New production and no final filter was approved.
- 347 rows in 128 days and a total of 246,878 tons;
- 12 product titles, 40 manufacturers and 70 symbols; All by ton and bulk;
- Share of grades: bitumen 60/70 equal to 59.65%, PG 64-22 equal to 26.21%, PG 70-16
  equal to 5.16% and PG 70-10 equal to 2.92%;
- Main producers: Tabriz oil refining 24.14%, Dezhpa oil and bitumen refining 17.14%,
  Tehran Pasargad Oil 11.14%, Mehran Hesar Refining 10.63% and Arak Pasargad Oil 9.40%;
- Contracts: credit 36.89%, cash 28.70%, advance 14.83%, advance matching 9.32%,
  cash matching 9.00% and credit matching 1.27%;
- 98.02% of the volume in the oil products hall of the commodity exchange.
Result: This market is highly heterogeneous and the combination of all grades and types of financing is one price
It does not make a valid reference. Before the benchmark, the grade, standard, warehouse/delivery place and so on
Acceptable manufacturers of certificates are specified. The primary option after verifying the specification is to restrict
It is matching to the corresponding grade and cash and cash transactions; Loans and loans should not be without financial adjustment
be collected in cash. This filter has not been approved yet.
The main recommended resource for the future collector is the official public API of the stock exchange. BrsApi only
For discovery, fallback is kept and no keys are stored in the project.
## Current stage: raw collector of the physical market
`src/bitumen/collectors/physical.py` file using common logic
`shared/ime_data/ime_physical_collector.py` was created. The raw filter is intentionally broad:
Any row whose normalized product name includes "bitumen", without limitation of grade, producer,
The symbol, contract type, settlement or volume is preserved. Full snapshot of the monthly response before the filter
It is also archived.
Outputs:
```text
data/raw/physical/bitumen_physical_raw.csv
data/raw/physical/api_snapshots/*.json.gz
```

collector is incremental and atomic; The first performance of all months from 01/1386 and the following normal performance
It refreshes the last two months. Comparable grade selection, removal of contracts and construction
Benchmark is not done at this stage.
At first full run, curl/Schannel was slow and unstable. 201 months to 1402/09 Salem
archived; Continue with `IME_HTTP_TRANSPORT=requests`. Option
`--rebuild-from-snapshots` to rebuild the CSV from the latest healthy snapshot every additional month
done so that the existing archive will not be downloaded again.
### The result of complete collection and validation — 2026-08-03
After proxy timeout on the network, missing months of full snapshots of the same endpoint
Officials that were previously archived in the copper project were completed. Those snapshots answer the entire market
are physical, not copper-filtered data, and the URL, payload, time received, and the full response of the source
they keep The tar CSV was then reconstructed from the most recent healthy snapshot of each of the 233 months.
- 47,035 raw rows and 36 columns;
- Covering bitumen rows from 06/02/1387 to 05/12/1405 on 3,736 dates;
- All normalized commodity names include "bitumen";
- 51 product titles, 167 producer titles, 527 symbols and 8 types of contracts in raw;
- 24,154 rows of positive transactions on 3,460 dates from 06/02/1387 to 05/07/1405;
- In positive transactions: 37 product titles, 128 producers and 336 symbols;
- 22,880 supply of zero amount; No price or negative value, missing identity field, row completely
  duplicate or duplicate business key;
- 233 unique months and all of them can be parsed; In the review of 2026-08-09, the number of 258 snapshot files
  There were (25 healthy replicates). Deliberately rebuild the newest snapshot every month
  chooses
The initial volume composition of positive transactions shows that bitumen 60/70 is about 63.36%, bitumen 85/100
About 11.47%, PG 64-22 about 9.78% and MC250 about 4.02% of the volume.
This statistic is only descriptive; Still no grade, manufacturer or contract removal and no benchmark
not made
## Current stop status
raw is complete and all grades, manufacturers, domestic/export markets and contracts must
Stay in it. The analysis step should first determine the exact grade of the certificate backing, then
Separate domestic and export and cash contracts, matching, advances and loans. Still the file
processed, physical analysis notebook, official weighted price or bitumen certification bubble is not made.
## Architectural migration — 2026-08-03
`Cert` layer removed. Data in `data/`, collectors in `src/bitumen/collectors/`
And the documentation is at `docs/`. CSVs and raw snapshots were transferred unchanged.