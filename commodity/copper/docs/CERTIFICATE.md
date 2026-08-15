# Copper Certificate and Physical-Market Data

Step-by-step description of the method, decisions, formulas, number of observations and path of files in
[`WORKFLOW.md`](WORKFLOW.md) is maintained and is the basis of project reporting and presentation.
This sub-project was created to collect and compare two datasets:
1. Copper cathode deposit certificate transactions with symbol `CopperCthd`;
2. Copper cathode transactions in the physical market of Iran Commodity Exchange.
The ultimate goal is to calculate the certificate bubble relative to the weighted price of physical market transactions.
## The implementation principle of the project
The work is done in stages and the start of each stage requires user approval.
The new certificate, the physical market and the bubble calculation method now have a verified collector and pipeline.
## Suggested steps
- [x] Step 1: Create structure, README and Agent instructions.
- [x] Step 2: Identification and validation of the official certificate source and possible endpoints.
- [x] Step 3: View the official certificate data sample and schema verification.
- [x] Step 4: Writing incremental certificate collector and collecting its complete history.
- [x] Step 5: Identification and sampling of copper cathode physical transactions.
- [x] Step 6: Write incremental physical market collector and collect history.
- [x] Step 7: Defining the matching rule of two markets and calculating the bubble in the processed data.
- [ ] Step 8: Quality control, scheduling documentation and weekly execution.
## Folder structure
```text
commodity/copper/
├── data/{raw,interim,processed}/
├── src/copper/{collectors,processing,analysis}/
├── notebooks/
├── logs/
├── outputs/
└── docs/
```

## Basic definition of bubble
After confirming the date matching method:
```text
bubble_irr_per_kg = certificate_close_irr_per_kg
                    - physical_weighted_irr_per_kg

bubble_pct = (certificate_close_irr_per_kg
              / physical_weighted_irr_per_kg - 1) × 100
```

The physical market does not trade every day. The approved method of step 7 is the ratio of physical price to intrinsic price
LME-calculates the currency at actual points and linearly interpolates the same ratio between points.
## Candidate resources
- Iran Commodity Exchange: reference source for final control of both markets;
- TSETMC APIs: certificate history candidate, subject to finding the actual symbol ID and coverage;
- Third-party sources: only for cross-checking, not automatic replacement of the official source.
No unknown identifier or endpoint should be fixed in the code without validation.
## Research report stage 2
The following candidates are from the source version of `0.4.0` open source library `fima` (published in
(Tir 1405) have been identified, but have not yet been confirmed by a live response in this project:
- Commodity exchange deposit certificate:
  `https://www.ime.co.ir/subsystems/ime/bazaremali/bazaremalidata.ashx`
- physical transactions of the commodity exchange:
  `https://www.ime.co.ir/subsystems/ime/services/home/imedata.asmx/GetAmareMoamelatList`
endpoint candidate certificate fields such as symbol, description, solar and Gregorian date, price
It reports the final and last, minimum and maximum, volume, value and number of transactions. endpoint
Physical also product, symbol, manufacturer, contract type, supply and transaction prices, quantity,
Returns the value, transaction and delivery date, warehouse, supplier, unit and hall.
Search TSETMC usually from route
`https://cdn.tsetmc.com/api/Instrument/GetInstrumentSearch/{query}` is done.
The reading tests of this step for TSETMC and IME timed out from the current environment; Therefore
`InsCode`, historical coverage, real live response schema and units not yet confirmed. this
timeout does not mean no symbol or data.
The readable diagnostic tool is located at `src/copper/tools/probe_sources.py`. This tool has no files
does not write and is executed with the following command:
```powershell
python .\src\probe_sources.py --timeout 30
```

In the test on August 10, 1405, all five requests were timed out in the TLS handshake phase:
Two commodity exchange endpoints and three TSETMC searches. No HTTP response like `401` or `403`
not received; As a result, there is no indication of the need for an API key and the current limitation
Network/IP is more likely.
After forcing the connection to IPv4 and TLS 1.2, the official exchange API responded. The ultimate source
The new certificate for this endpoint is:
```text
https://dataapi.ime.co.ir/api/CDC/CDCTrades
```

The real contract code in the answer is `CopperCthd` and its description "Copper Cathode Continuous Deposit Certificate"
is `CD1COP0001` did not work as a filter on the new endpoint. service
`api.tsetmc.com` is subscription and paid; public `cdn.tsetmc.com/api` endpoints but
They are without official contracts and documents and are not the main source in this project.
## Certificate collection
```powershell
python .\src\copper\collectors\certificate.py
```

Outputs:
- `data/raw/certificate/copper_certificate_raw.csv`
- `data/raw/certificate/api_snapshots/*.json`

The modified version connects both the old `CD1COP0001` and the new `CopperCthd`.
The current output has 246 unique rows from 2025-10-20 to 2026-08-02, which is 178 days.
It has a positive trading volume. Normal execution only 14 days ago, refresh the latest row
and found no new or modified rows. API for no deal days too
The record is kept at zero volume and settlement price; These rows are preserved in the raw data.
## The result of physical market sampling
Official physical market endpoint confirmed:
```text
https://www.ime.co.ir/subsystems/ime/services/home/imedata.asmx/GetAmareMoamelatList
```

The answer is in the envelope of the `d` field as a JSON string and must be parsed twice.
In the sample `1405/04/01` to `1405/05/10`, there are 6,935 total rows and 22 related rows.
Copper cathode was observed. Sample groups included the following:
- `NCI-OACCAA-00`, "Copper Cathode" product, produced by "National Copper Industries of Iran", contract
  cash and cash (matching);
- "Copper Cathode 2" products from Contact, Navid Alborz process and Horizon development and Middle East mines.
The main candidate for the benchmark certificate is `NCI-OACCAA-00`; Other manufacturers and products
"Copper Cathode 2" will not enter the benchmark until standard equivalence is proven. supplies
No transaction (`Quantity=0` or empty price) should be kept in raw, but from the balanced price of the transaction
be deleted
In the example, `Price` was about 19,477,000 Rials and compatible with the price scale of the certificate. with this
Now, the response reports `Unit=تن` and is `TotalPrice = Price × Quantity`; Therefore
`TotalPrice` unit and scale should not be guessed. The collector must leave the raw fields intact
Keep and build benchmark price directly from `Price` with official unit control.
## Physical market collection powershell
python .\src\copper\collectors\physical.py```

Outputs:
- `data/raw/physical/copper_cathode_physical_raw.csv`
- `data/raw/physical/api_snapshots/*.json.gz`

The first run of the API checks month by month from `1386/01` to the current day. The next implementation as
By default, it also refreshes the local month two months before the most recent one, and the updated months
completely replaces Therefore, both source modifications are recorded and duplicates are created
can't No API key or external Python dependency is required for normal execution and connection with
`curl`, IPv4 and TLS 1.2 are performed.
The collector keeps the entire market response as a compressed snapshot, but only in CSV
The rows of "Copper Cathode" belong to the old and new formats of the national symbol of Iran's copper industries, ie
Holds `NCI-CCAA-00` and `NCI-OACCAA-00`. Only "cash" contracts and
"Matchings" remain canonical in CSV; Salaf, Salaf (matching), loan and others
Producers are removed. Supplies with zero value are still retained.
The result of the full implementation on August 10, 1405:
- Initial execution before limiting the product group, 1,993 rows from `1387/06/03` to
  `1405/05/04` compiled;
- 15 producers and 26 symbols;
- the canonical table keeps only 1,733 rows of the "copper cathode" group after the stepwise decision;
- Cash, cash (matching), advance, advance (matching) and loan contracts.
In the next decision, the canonical table was divided into two old and new national symbols of Iran's copper industries and contracts
Cash was limited. The current situation is 1,163 rows: 791 cash rows and 372 cash rows (matching).
Self, self (matching), credit and other manufacturers are removed from CSV, but in snapshots
The full API is retrievable.
In the 362 days that both cash and cash (matching) methods have traded, the balanced price of the two methods in
All days have been exactly equal. For 9 days, they had only cash transaction (matching). Therefore
The main benchmark candidate is the volume weighted price of the combination of both methods; Transaction type and volume share
Matches should be maintained as control columns.
## Physical market daily benchmark
```powershell
python .\src\copper\processing\build_physical_benchmark.py
```

Script `src/copper/processing/build_physical_benchmark.py` Only rows traded with `Quantity > 0`
and enters `Price > 0` into the calculation and produces the following output atomically:
```text
data/processed/nci_copper_cash_daily.csv
```

Definition of the original price:
```text
physical_weighted_price = Σ(Price × Quantity) / Σ(Quantity)
```

This calculation is done on the combination of cash and cash (matching) every day. Because the price is two ways
All common days are equal, the output is only one price column named
It has `physical_weighted_price`. Volume of each method, matching volume share, current symbols and history
Solar/Maladi are still kept separately. If the cash price and matching are different in the future implementation
If so, the script will stop with a validation error so that the single price rule does not continue without checking.
The current output has 789 trading days from `1387/06/03` to `1405/05/04`.
This benchmark is an approved pipeline input, estimated physical price and certification bubble.
## Estimated physical price and certification bubble
```powershell
python .\src\copper\processing\build_certificate_bubble.py
```

The script first constructs the inherent price per kilo of copper:
```text
intrinsic_price = (LME cash USD/ton ÷ 1000) × free-market USD/IRR
```

On the current 26 actual common dates, the ratio `physical_price / intrinsic_price` is calculated.
This ratio between both real points in terms of calendar days is linearly interpolated and then in
The inherent price is multiplied every day. At the end:
```text
certificate_bubble_pct =
    (certificate_price / estimated_physical_price - 1) × 100
```

No extrapolation is done before the first or after the last anchor. Current output in
`data/processed/copper_certificate_bubble.csv` including 169 days from `2025-10-26` to
`2026-07-26` is: 26 actual points and 143 interpolated days. Source date and life of LME and
Dollars, two anchors of each ratio, ratio method and all intermediate prices are preserved in the output.
Two complementary direct measures are created with the following command:
```powershell
python .\src\copper\processing\build_intrinsic_bubbles.py
```

Outputs:
- `data/processed/physical_vs_intrinsic_bubble.csv`: All 789 actual physical price ratio
  at the inherent price of the LME-dollar;
- `data/processed/certificate_vs_intrinsic_bubble.csv`: All 178 days of certificate transaction
  compared to the intrinsic price of LME-dollar.
These two files do not do any physical price interpolation and with the original certificate bubble to
Estimated physical price is conceptually different.
Although the search was performed from `1386/01`, the first relevant row returned by the endpoint was for
It is `1387/06/03`. The second run only read the months `1405/03` to `1405/05` and
The final number before applying the group filter remained 1,993; As a result of incremental behavior and
idempotent verified. Full API snapshots are preserved and deprecated groups in
They can be recovered if needed.