# First-wave source assurance

Last checked: 2026-09-01

This note supersedes any earlier wording that treated LME data as a gap or said that the difficult first-wave families had no clean source. LME cash, three-month, and stock data are already present in this project and must be reused. The source-by-source contract is in `first_wave_source_dictionary.csv`.

## Result

Every first-wave family now has an identified collection path. The paths are deliberately separated into:

- **A — collect now:** official API, bulk file, structured table, or an already-owned project series.
- **B — collect with a controlled extractor:** official PDF/XLS/HTML archive or release-by-release history.
- **C — licensed exact benchmark:** the authoritative data exist through a documented subscription API/export. A public indicator may coexist, but it is not renamed as the licensed benchmark.
- **D — do not manufacture:** no measured series exists with the requested meaning. Use only the separately named physical indicator in the dictionary.

There is no first-wave family left as an unresearched ambiguity. Some exact commercial benchmarks remain category C because existence and accessibility are different questions.

## Corrections to the earlier audit

| Family | Assured source path | Decision |
|---|---|---|
| LME cash, 3M, spread, stocks | Existing Westmetall-backed project collector | Already collected; never reacquire or call missing |
| COMEX settlements, volume, OI | CME Daily Bulletin page 62; dated bulletin/DataMine files for backfill | Official current collection is free and parseable; preserve maturity-level data before building rolls |
| COMEX warehouse stocks | CME depository/delivery reports | Collect official reports and retain registered/eligible/total fields |
| CFTC positioning | CFTC Public Reporting Environment Socrata plus annual historical files | Free official weekly series |
| SHFE curve, volume, OI, warrants, inventory | SHFE Daily Express, Daily Warrant, Weekly Inventory, Monthly/Annual and Historical Data downloads | Free official exchange route |
| Global mine, smelter, refined production | BGS World Mineral Statistics OGC API/Excel; USGS workbooks for validation | Free annual country panel; BGS has explicit mine/smelter/refined subcommodities |
| Global monthly fundamentals | ICSG public rolling Table 1 and dated press releases | Free public production, usage, balance, stocks, mine capacity/utilization, and refinery capacity/utilization snapshots; archive vintages |
| Full country monthly fundamentals and semis | ICSG Online Statistical Database/Bulletin | Exact systematic history exists but is licensed |
| Facility capacity/status | ICSG public interactive map; licensed Directory for full history | Public current backbone; paid history and full fields |
| Global smelter utilization | ICSG smelter production plus capacity on the same licensed basis | Exact route exists; do not mix unrelated numerator and denominator sources |
| China concentrate/refined/scrap trade | UN Comtrade API plus China Customs monthly tables | Free official quantity/value history; retain HS revision and detailed subheadings |
| TC/RC spot history | SMM `cu_tc_rcs` OAuth API or Fastmarkets `MB-CU-0287` API | Exact clean benchmarks are licensed, not unavailable |
| TC/RC public history | SMM long-term/quarterly announcement index, company reports, and COCHILCO historical report | Valid sparse benchmark/event series; never fill unannounced quarters or reconstruct weekly spot values |
| Yangshan premium | SMM warrant and bill-of-lading OAuth APIs with published definitions | Exact series and endpoints found; licensed |
| Shanghai CIF Grade A premium | Fastmarkets `MB-CU-0403`; CME `CUP` final monthly settlements | Exact daily is licensed; public official CME monthly settlement is a legitimate benchmark-derived series, not Yangshan warrant premium |
| US cathode premium | Fastmarkets `MB-CU-0002`; public USGS producer-cathode minus COMEX table | Exact commercial and defensible public monthly paths both exist and remain separately named |
| European cathode premium | Fastmarkets `MB-CU-0369`; Aurubis announced annual premium | Exact spot licensed; free producer-contract indicator is annual and is not called spot |
| Scrap market | BLS/FRED No.1 and No.2 copper scrap PPIs; USGS scrap use/secondary refined output; Comtrade HS 7404 | Free long price indexes plus physical supply/trade series; no invented dollar discount |
| Semis | NBS China copper-products output, USGS monthly brass/wire-rod tables, Eurostat PRODCOM; ICSG for global full history | Strong free regional physical panel; exact global systematic panel is licensed |
| Mine disruptions | COCHILCO company-month production, Peru MINEM operator-month XLSX, and major-producer filings/guidance | Build an evidence ledger from observed output and primary disclosures; no opaque estimated lost-tonnage model |
| China grid demand | NEA monthly YTD power-grid investment releases | Free official; month flow may be differenced with a February/year-reset rule |
| China property/industrial demand | NBS EasyQuery and DBnomics NBS mirror with source codes | Free official-statistics route; retain current versus accumulated fields |
| Vehicles/EVs/renewables | OICA annual production, IEA Global EV Data Explorer, IRENASTAT PxWeb | Free structured/downloadable physical drivers |
| Data centres | US Census monthly private data-center construction backcast to 2014; BEA computer-equipment investment; IEA electricity estimates | Defensible historical indicators found; do not manufacture a global copper-tonnage series |
| Global cycle | Exact JPMorgan/S&P Global Manufacturing PMI via subscription or official press-release archive; OECD BCI via SDMX as a distinct free alternative | Exact PMI exists; press releases support controlled public extraction, while systematic download is licensed |
| Macro/FX/rates/China credit | FRED/ALFRED, PBOC releases, EIA/BEA as applicable | Public APIs/files; preserve vintages and known methodology breaks |

## Non-negotiable naming rules

1. A proxy or regional indicator is never stored under the name of a different exact benchmark.
2. Trade unit value is not TC/RC, cathode premium, or scrap spot price.
3. CME CUP is a Shanghai CIF premium monthly settlement; it is not the SMM Yangshan warrant series.
4. BLS scrap PPIs are indexes; subtracting them from LME dollars is dimensionally invalid.
5. Data-center construction and electricity are demand drivers; they are not measured copper demand.
6. A disruption observation needs an official production value, a primary event/guidance disclosure, or both. Missing production versus an analyst forecast is not automatically a disruption.
7. All rolling exchange series are derived only after immutable maturity-level observations have been stored.

## Collection order

1. Reuse the existing LME assets and add only derived spreads in processed data.
2. Start official incremental collectors for CME, CFTC, SHFE, UN Comtrade, BGS, FRED/ALFRED, NBS/DBnomics, NEA, IRENA, IEA, Census/BEA, COCHILCO, Peru MINEM, and USGS.
3. Archive every ICSG public Table 1 and press-release vintage; parse after raw persistence.
4. Build the primary-disclosure mine/guidance registry and event ledger.
5. Add licensed adapters only after credentials and redistribution terms are supplied for SMM, Fastmarkets, S&P Global PMI, or ICSG.
6. Validate every derived series against its numerator/denominator unit, calendar, geography, and methodology version.

## Source evidence

- CME Daily Bulletin and official access change: https://www.cmegroup.com/market-data/daily-bulletin.html and https://www.cmegroup.com/articles/faqs/access-to-cme-group-settlement-data-faq.html
- CFTC Commitments of Traders and API route: https://www.cftc.gov/MarketReports/CommitmentsofTraders/index.htm
- SHFE statistical-data catalogue: https://www.shfe.com.cn/eng/reports/index.html
- BGS World Mineral Statistics API: https://www.bgs.ac.uk/mineralsuk/statistics/world-mineral-statistics/world-mineral-statistics-data-download/
- ICSG public statistics, database, and facility map: https://icsg.org/selected-copper-statistics/ , https://icsg.org/whats-icsg-online-statistical-database/ , and https://icsg.org/map-mines-smelters-refineries/
- SMM Yangshan API and definitions: https://data.smm.cn/dataapi/%E9%93%9C/cu_yangshan_copper_premium_bill_of_lading and https://hq.smm.cn/explain/copper
- Fastmarkets benchmark specifications/API: https://help.fastmarkets.com/en_US/metals-price-list and https://help.fastmarkets.com/en_US/apis_sub/fastmarkets-market-data-api
- USGS copper monthly archive: https://www.usgs.gov/centers/national-minerals-information-center/copper-statistics-and-information
- UN Comtrade: https://comtradeplus.un.org/TradeFlow
- Eurostat API: https://ec.europa.eu/eurostat/web/user-guides/data-browser/api-data-access/api
- China NBS copper-products series mirror: https://db.nomics.world/NBS/M_A02091J
- China NEA power statistics: https://www.nea.gov.cn/
- IEA EV data: https://www.iea.org/data-and-statistics/data-tools/global-ev-data-explorer
- IRENASTAT: https://pxweb.irena.org/pxweb/en/IRENASTAT/
- US Census construction spending: https://www.census.gov/construction/c30/c30index.html
- OECD BCI SDMX route: https://www.oecd.org/en/data/indicators/business-confidence-index-bci.html

