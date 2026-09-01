# Copper Data API and Clean-Source Audit

Last checked: 2026-09-01

This audit answers a narrow implementation question: which first-wave Copper datasets can be
collected through an official API, structured download, or other reproducible and legitimate
method? It does not treat a chart, search result, or proprietary benchmark as freely collectible.

Availability labels follow the research prompt:

- **A** — directly obtainable from a reliable source.
- **B** — obtainable but difficult, incomplete, paid, registration-gated, or manual.
- **C** — currently unavailable; a disclosed proxy would be required.
- **D** — definition or collection route still requires investigation.

## Strong API candidates

| Dataset | Access | Grade | Implementation note |
|---|---|---:|---|
| CFTC COMEX copper managed-money long, short, spreading, open interest | CFTC Public Reporting Environment Socrata API; Disaggregated Futures Only dataset `72hh-3qpy` | A | Weekly Tuesday positions, normally released Friday. Filter the exact COMEX copper contract and preserve report date, publication/retrieval date, futures-only scope, and CFTC contract identifiers. No token is currently required for moderate use. |
| Broad USD index | FRED API series `DTWEXBGS` | A | Daily, Index Jan 2006=100. FRED API requires a user API key; the FRED graph CSV route is a clean keyless download but has less metadata. Preserve source and licensing notes. |
| Effective federal funds rate | FRED API series `EFFR` | A | Daily percent. Preserve native missing days; do not manufacture weekend observations. |
| 10-year US real yield | FRED API series `DFII10` | A | Daily percent, inflation-indexed constant maturity. |
| Nominal Treasury yields | FRED API series such as `DGS10` | A | Daily percent. Use only if the research definition calls for nominal yields. |
| US and selected international macro vintages | FRED/ALFRED API | A | FRED exposes vintage dates and initial/revised observations. API key required. Respect third-party series restrictions in FRED notes. |
| Bilateral FX needed for normalization | FRED, Federal Reserve, or ECB official APIs | A | Choose one canonical owner in `shared/market_data`; preserve original quotation direction and calculate inverses only as derived fields. |
| Bilateral copper trade by HS code | UN Comtrade API | A/B | HS 2603 covers copper ores and concentrates; HS 7403 covers refined copper and copper alloys, unwrought. Free registration/API-key limits apply for larger pulls. Preserve HS revision, reporter, partner, flow, customs regime, quantity unit, net weight, and trade value. |
| General macro and development indicators | World Bank Indicators API | A | Keyless REST API for suitable annual/quarterly series. Use only after confirming the exact indicator definition; it is not a substitute for copper-specific statistics. |
| OECD short-term indicators | OECD SDMX API | A/B | Official SDMX REST service. Dataset structures and series keys must be discovered and pinned; availability varies by country and indicator. |

## Clean official downloads or structured pages

| Dataset | Access | Grade | Implementation note |
|---|---|---:|---|
| Existing LME cash, 3-month, and stock history | Westmetall HTML tables through the existing shared collector | A | Already active from 2008. Clean and reproducible, but Westmetall is a secondary source, not the authoritative LME history. Retain source identity and never relabel it as official LME data. |
| Official LME prices and detailed market data | LME licensed feeds / historical-data service | B | Official historical prices and many warehouse products are licensed. LME explicitly licenses official prices, warehouse reports, non-display use, distribution, and derived data. Do not build an undocumented scraper around access controls. |
| Chilean mine production by company | COCHILCO Monthly Electronic Bulletin HTML/XLS | A | Structured monthly tables include annual and monthly company production in kMt copper content. Pin table identity because table numbers displayed in URLs and page headings may differ over time. Preserve vintage because historical values can be revised. |
| COCHILCO metal prices, Chile production, exports, inventories, energy/water inputs | COCHILCO historical database and annual-statistics XLS files | A/B | Official Excel and HTML tables are cleaner than PDF transcription. Use XLS exports when stable; archive the original file and publication metadata. Coverage depends on table. |
| Global mine, smelter, refinery production and refined usage snapshot | ICSG Selected Copper Statistics | B | Latest snapshot is public, but full monthly historical series and country detail are part of the paid Copper Bulletin/database. Do not infer a free history from the latest public table. |
| Global mine, smelter, refinery, usage, balance history | ICSG Copper Bulletin / online database | B | Authoritative and structured but licensed: current listed subscription and database fees apply. Requires user-approved subscription access. |
| Facility capacities and status | ICSG interactive map / Directory | B | Free map lists facilities but restricts fields. Full Excel, capacities, forecasts, and historical capacity back to 1995 require a subscription. |
| COMEX copper warehouse stocks | CME Copper Stocks reports | A/B | Official warehouse/depository reports are publicly posted, including registered/eligible stocks and warehouse detail. Automate only against a stable downloadable file route and archive each report; the landing-page HTML alone is not a data API. |
| COMEX copper settlement price, volume, and open interest | CME product pages/DataMine/API | B | Delayed current settlements become viewable after midnight, while systematic history, continuous series, and APIs are licensed products. Do not assume free bulk historical access. CFTC open interest is not a replacement for contract-level CME volume/OI. |
| SHFE copper prices and warehouse inventory | SHFE official daily/weekly data downloads | A/B | Official pages publish market and inventory data, commonly as structured downloads, but endpoints and Chinese page structure require a tested collector. Preserve contract/month, warehouse/region, unit, tax basis, and publication date. |
| China copper concentrate imports | China Customs monthly HTML tables or UN Comtrade API | A/B | China Customs publishes monthly and year-to-date copper ore/concentrate quantity and value tables. UN Comtrade is easier to automate historically but can lag and may reflect later revisions. Preserve monthly flow versus YTD fields. |
| China refined copper imports and exports | UN Comtrade API / China Customs detailed trade data | A/B | HS 7403 is broader than a pure Grade A cathode benchmark. Investigate national tariff-line detail before calling it refined cathode. Gross imports and exports remain raw; net imports are derived. |
| China industrial production and product output | NBS China monthly releases/database | A/B | Official releases are structured HTML and include product output such as vehicles and NEVs, often with monthly and YTD values. The public interface is not a documented stable API. Detect cumulative versus monthly fields before differencing. |
| China official manufacturing PMI | NBS China / China Federation of Logistics and Purchasing release | A/B | Official monthly release is obtainable. Preserve official headline and subindices separately; do not substitute the proprietary S&P Global/Caixin PMI without a license. |
| China property and construction indicators | NBS China monthly releases/database | A/B | Official but definitions and YTD presentation require table-specific parsing and break documentation. |
| Global mine production by country | USGS Mineral Yearbook and Mineral Commodity Summaries | B | Official annual PDF/XLS-style publications are useful for long annual country history. Publication lag is long and estimates are revised. Prefer machine-readable companion files when supplied; otherwise store and validate table extraction. |
| Renewable capacity additions | IRENA official statistics downloads | A/B | Suitable for annual structural-demand context, not a direct copper-consumption measure. Confirm downloadable format and licensing before collection. |

## Mostly proprietary or not cleanly observable

| Dataset | Best legitimate source | Grade | Why it is not an immediate free collector |
|---|---|---:|---|
| Spot copper concentrate TC and RC | Fastmarkets, SMM, CRU, Wood Mackenzie, Argus or licensed terminals | B | Benchmark assessments and histories are generally proprietary. Public news snippets are not a reliable time series. |
| Annual benchmark TC/RC | Producer/smelter announcements, COCHILCO discussion, specialist agencies | B | Announcements can be collected as dated contract events, but a consistent historical benchmark series needs careful source reconciliation. |
| Concentrate market balance | ICSG/CRU/Wood Mackenzie and other industry datasets | B | Definitions depend on copper-in-concentrate supply and effective smelter feed requirement; full history is normally licensed. |
| Yangshan/China cathode premium | SMM, Fastmarkets, Refinitiv, Bloomberg or licensed data vendors | B | The recognized benchmarks are proprietary. Do not fabricate a free equivalent from isolated articles. |
| US cathode premium | Fastmarkets/other specialist assessments | B | Grade, delivery location, quotation basis, and history are proprietary. |
| European cathode premium | Fastmarkets/other specialist assessments | B | Same constraint; producer annual premiums may be stored as events but are not equivalent to a spot assessment. |
| Scrap discounts and availability | SMM/Fastmarkets/Argus/CRU or detailed transaction sources | B/C | Trade volume is observable, but physical discounts and immediately available scrap are assessment-based and heterogeneous. |
| Global smelter utilization | ICSG directory/database or specialist providers | B | Nameplate capacity, effective capacity, outages, and actual production must be reconciled; no single open high-frequency series is established. |
| Global copper semis production | ICSG Fabricators Directory and specialist providers | B | Broad international history is generally licensed; national official series can be collected piecemeal. |
| Global manufacturing PMI | S&P Global or licensed provider | B | The widely used global PMI is copyrighted/licensed. OECD industrial production is not the same concept. |
| Data-center copper demand | No single authoritative historical series | C/D | Data-center capacity/capex can be observed through several sources, but conversion to copper demand requires assumptions. Keep it out of the canonical first wave. |
| Mine disruption index | Company disclosures plus event normalization | D | Events are observable; comparable lost-tonnage estimates and expectation baselines require a separate methodology and must not be guessed. |

## Recommended implementation order in this repository

1. **Reuse existing data first:** build an LME cash/3M/stock derived table from the existing
   Westmetall-backed raw series. Do not recollect or duplicate it.
2. **Add a generic shared FRED collector:** store cross-commodity macro series under
   `shared/data/raw`, with series metadata and ALFRED vintage support where needed.
3. **Add a Copper CFTC wrapper:** query the CFTC Socrata dataset for the exact COMEX copper
   contract and keep weekly futures-only managed-money fields plus total open interest.
4. **Add COCHILCO structured-table inventory and collectors:** prefer XLS/HTML tables over PDFs;
   archive every source release and preserve vintages.
5. **Add trade via UN Comtrade:** begin with China HS 2603; investigate refined-copper tariff-line
   definitions before promoting HS 7403 aggregates.
6. **Add CME and SHFE inventories:** only after stable official download URLs and schemas have
   been tested with archived source files.
7. **Treat ICSG fundamentals as a licensing decision:** use public snapshots for validation and
   metadata, but do not pretend they provide the required historical monthly database.
8. **Leave TC/RC, physical premiums, scrap discounts, and global semis marked B/C** until access is
   legitimately obtained or a clearly labelled alternative is approved.

## Collector acceptance rule

A source is not promoted from this audit into an active collector until a test download has been
opened and inspected, its legal/access conditions recorded, its schema and units pinned, its
history checked, its revision behavior documented, and an idempotent raw archive path approved.
