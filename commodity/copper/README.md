# Copper Certificate Valuation

This commodity workspace now contains two governed research systems: the original Iranian
certificate-valuation study and a separate global copper-market data foundation. The latter
reuses the existing LME history and never reacquires it.

## Global copper-market data foundation

Public first-wave sources are organized under `data/raw/global_market/<source>` with immutable
source responses or files and atomic canonical manifests/tables. As of 2026-09-02 the collected
foundation contains BGS world copper statistics (13,836 rows), main-contract COMEX copper CFTC
positioning (869 weekly rows), IRENA world power capacity (543 rows), NBS China copper-products
output (44 rows), 206 USGS monthly copper survey workbooks, and COCHILCO company-level Chilean
mine production (5,852 rows; continuous country totals from 2006-01 through 2026-05). CME now
includes 76 preserved official Copper Stocks workbooks (2,065 warehouse/status rows covering 76
activity dates from 2012-05-09 through 2026-08-31) and 131 preserved official metals bulletins
(124 unique HG futures activity dates from 2014-06-27 through 2026-08-28, with Globex,
open-outcry, and PNT/PIT volume plus open interest and its daily change). The
SHFE foundation now contains 54,426 official copper contract-date observations across 4,536
trading dates from 2008-01-02 through 2026-09-02, plus daily copper warrants for 2,798 dates
from 2014-05-19 through 2025-11-17 and weekly inventory/capacity for 557 dates from 2014-05-23
through 2025-11-14. Warrants and weekly physical inventory remain separate measures. The
unauthenticated UN Comtrade preview returned 781 China copper-trade aggregates for a
non-continuous 2010-2024 sample; it is retained with an explicit incomplete-preview flag and is
not promoted as full history. Exact licensed PRA benchmarks
(Yangshan/US/Europe premiums and spot TC/RC) remain entitlement-gated and are not replaced with
fabricated free series.

The professional indicator/source registry is `docs/first_wave_source_dictionary.csv`; source
assurance and collection constraints are documented in `docs/FIRST_WAVE_SOURCE_ASSURANCE.md`.

## Research question

Does the Iranian copper-cathode warehouse receipt trade at a premium or discount to a
comparable domestic physical-market price, after accounting for movements in LME cash copper
and the free-market USD/IRR exchange rate?

## Current checkpoint

- Data checkpoint: 2026-08-26
- Certificate: 268 calendar observations, 194 positive-trading days, through 2026-08-27
- Canonical physical market: 1,171 rows through 1405/06/02
- LME cash copper: 4,719 observations through 2026-08-28
- Free-market USD/IRR: 13,079 observations through 1405/06/05
- Processed physical benchmark and forward-gap diagnostic: `data/processed/physical`
- Bubble and regression outputs: `data/processed/bubble`
- Presentation timelines: `data/processed/analysis`

## Comparable physical underlying

The approved domestic benchmark includes only National Iranian Copper Industries Company
cathode under the historical symbols `NCI-CCAA-00` and `NCI-OACCAA-00`, using cash and
cash-matching contracts with positive executed price and quantity. Forward, credit, other
producers, and “copper cathode 2” are excluded from the comparable scope.

The daily physical price is volume weighted. The primary certificate valuation interpolates
the ratio of domestic physical price to LME–FX intrinsic price between exact physical/certificate
anchors. No extrapolation is allowed outside the observed anchor range. A time-series regression
using intrinsic price as its sole feature is retained as an experimental sensitivity check.

The separate `nci_copper_forward_gap.csv` diagnostic preserves the cash-only benchmark scope.
It covers 16 forward-trade dates and 26,420 tonnes strictly inside the 102-day cash gap,
comparing each forward weighted price with both cash anchors and a linear bridge.

## Main current result

The primary output contains 188 certificate-trading days from 2025-10-26 to 2026-08-24:
32 exact physical anchors and 156 interpolated days. The estimated certificate premium to
domestic physical value averages 5.64%, with a median of 7.17%. Interpretation is limited by
the small and temporally uneven physical anchor sample.

## Reproduction from the repository root

```powershell
python .\commodity\copper\src\copper\collectors\lme.py
python .\shared\market_data\fx.py
python .\commodity\copper\src\copper\collectors\certificate.py
python .\commodity\copper\src\copper\collectors\physical.py
python .\commodity\copper\src\copper\collectors\global_market.py --sources nbs irena bgs cftc
python .\commodity\copper\src\copper\collectors\usgs_archive.py
python .\commodity\copper\src\copper\collectors\cochilco.py --report-year 2026 --report-month 6 --backfill
python .\commodity\copper\src\copper\collectors\comtrade.py
python .\commodity\copper\src\copper\collectors\cme.py
python .\commodity\copper\src\copper\collectors\cme_bulletins.py
python .\commodity\copper\src\copper\collectors\shfe.py
python .\commodity\copper\src\copper\collectors\shfe_inventory.py
python .\commodity\copper\src\copper\processing\build_physical_benchmark.py
python .\commodity\copper\src\copper\processing\build_intrinsic_bubbles.py
python .\commodity\copper\src\copper\processing\build_certificate_bubble.py
python .\commodity\copper\src\copper\processing\build_intrinsic_regression.py
python .\commodity\copper\src\copper\processing\build_presentation_timeline.py
python .\commodity\copper\src\copper\processing\build_forward_gap_analysis.py
```

The full methodology, source contracts, validations, and limitations are documented in
[`docs/WORKFLOW.md`](docs/WORKFLOW.md). The English research report is in
[`reports/copper/research`](../../reports/copper/research/).
