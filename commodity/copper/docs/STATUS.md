# Copper Project Status

Last updated: 2026-09-01

## Global copper-market collection checkpoint

The global-market subsystem has been added without modifying the existing LME raw history.
Completed public collections are: BGS world copper statistics (13,836 observations, 1970 onward
depending on table), CFTC main COMEX Grade #1 disaggregated futures-only positioning (869 weekly
observations from 2010), IRENA world generating capacity by technology/grid status (543
observations, 2000-2025), NBS China copper-products output via DBnomics (44 current-vintage
observations), and 206 official USGS monthly Copper Mineral Industry Survey workbooks spanning
2005-2025 with source gaps as published.

FRED is registered but its server repeatedly reset connections during this collection session;
no partial canonical FRED file was written. IEA Global EV Outlook 2026 is free but its XLSX
download currently requires an IEA account session. Licensed physical-premium and spot TC/RC
series remain explicit entitlement inputs, not reconstructed substitutes.

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
