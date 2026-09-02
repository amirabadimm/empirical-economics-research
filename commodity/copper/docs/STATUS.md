# Copper Project Status

Last updated: 2026-09-02

## Global copper-market collection checkpoint

The global-market subsystem has been added without modifying the existing LME raw history.
Completed public collections are: BGS world copper statistics (13,836 observations, 1970 onward
depending on table), CFTC main COMEX Grade #1 disaggregated futures-only positioning (869 weekly
observations from 2010), IRENA world generating capacity by technology/grid status (543
observations, 2000-2025), NBS China copper-products output via DBnomics (44 current-vintage
observations), and 206 official USGS monthly Copper Mineral Industry Survey workbooks spanning
2005-2025 with source gaps as published.

The second collection pass added 5,852 COCHILCO company-level observations. Monthly Chilean
country totals are complete from 2006-01 through 2026-05 with 22 company/aggregate columns and
no duplicate keys. The public UN Comtrade preview was queried for every month from 2000-01
through 2026-08 for HS 2603, 7403, and 7404 imports and exports. It returned only 781 aggregate
rows across a non-continuous 2010-2024 sample, so this output is explicitly marked
`unauthenticated_preview_incomplete`; a free API subscription key is required before promotion
to a complete trade-history input.

The CME collection now bypasses the live-site WAF without substituting a third-party dataset:
the collectors use Internet Archive replay of official CME files and preserve every source file.
All 76 distinct Copper Stocks XLS workbooks parse to 2,065 canonical warehouse/status rows across
76 activity dates from 2012-05-09 through 2026-08-31. All 131 distinct metals-bulletin PDFs parse
to 124 unique HG futures trade dates from 2014-06-27 through 2026-08-28. The bulletin table retains
Globex, legacy open-outcry, and PNT/PIT volume separately, their summed futures volume, open
interest, and the published daily open-interest change. Contract-month settlement extraction is
not yet promoted because the PDF text geometry requires a separate validation pass.

The SHFE presentation-layer slider is also no longer a data block. Official dated Daily Express
JSON files produced 54,426 copper contract observations across 4,536 trading dates from
2008-01-02 through 2026-09-02, including OHLC, previous/current settlement, volume, open interest,
open-interest change, and turnover where published. Official Daily Warrant files produced three
tax-status totals for 2,798 dates from 2014-05-19 through 2025-11-17. Official Weekly Inventory
files produced the same three categories for 557 dates from 2014-05-23 through 2025-11-14,
retaining physical inventory, inventory change, warrants, warrant change, and warehouse capacity.
The known warrant and weekly-inventory endpoints cease publishing after November 2025; this is
recorded as an endpoint transition, not forward-filled.

FRED is registered but its server repeatedly reset connections during this collection session;
no partial canonical FRED file was written. IEA Global EV Outlook 2026 is free but its XLSX
download currently requires an IEA account session. Licensed physical-premium and spot TC/RC
series remain explicit entitlement inputs, not reconstructed substitutes.

The live CME host still returns an IP/WAF denial, but its stock and bulletin datasets are now
collected through preserved official files. SHFE's report pages still show an interactive slider,
but dated official JSON data files are directly collectible. BLS's public API and bulk host remain
blocked from the current network.

The Census private-construction workbooks and exact data-center definition are confirmed, with
the named monthly series beginning in 2014. Census blocks the workbook download from the current
network and now requires an API key for Economic Indicators queries, so no partial or third-party
substitute was accepted.

Both active notebooks now include the governed workspace dashboard for source coverage,
physical/certificate activity, goods composition, prices, and validated bubble visualization.

The market-input collectors and all dependent valuation outputs have been refreshed. Processed
physical outputs now live under `data/processed/physical`, bubble/model outputs under
`data/processed/bubble`, and presentation tables under `data/processed/analysis`. Current
coverage is LME through 2026-08-28, shared free-market USD/IRR through 1405/06/05, certificate data
through 2026-08-27, and the approved NCI cash benchmark through 2026-08-24.

The primary certificate bubble contains 188 observations from 2025-10-26 through 2026-08-24,
including 32 exact physical anchors and 156 interpolated dates. Its mean premium is 5.64% and
its median is 7.17%. Certificate transaction value is present as `certificate_trades_value_irr`;
physical transaction value is now present as `physical_trades_value_irr` in the daily benchmark
and physical-versus-intrinsic output.
