# Copper Project Status

Last updated: 2026-08-29

The market-input collectors and all dependent valuation outputs have been refreshed. Processed
physical outputs now live under `data/processed/physical`, bubble/model outputs under
`data/processed/bubble`, and presentation tables under `data/processed/analysis`. Current
coverage is LME through 2026-08-25, shared free-market USD/IRR through 1405/05/31, certificate data
through 2026-08-25, and the approved NCI cash benchmark through 2026-08-24. The TGJU refresh
returned no usable response, so the shared FX checkpoint did not advance.

The primary certificate bubble contains 188 observations from 2025-10-26 through 2026-08-24,
including 32 exact physical anchors and 156 interpolated dates. Its mean premium is 5.64% and
its median is 7.17%. Certificate transaction value is present as `certificate_trades_value_irr`;
physical transaction value is now present as `physical_trades_value_irr` in the daily benchmark
and physical-versus-intrinsic output.
