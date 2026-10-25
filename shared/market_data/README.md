# Shared Market Data

## Latest FX refresh — 2026-10-18

A repeat live check starting at 16:03 Asia/Tehran returned zero new dates and
zero revised closes; coverage and the row count below remain unchanged.

The copper maintenance run added three TGJU dates. The canonical USD/IRR CSV now
contains 13,121 rows through 1405/07/25 (2026-10-17); no visible existing close
was revised. This supersedes the earlier coverage checkpoints below. Copper's
dependent outputs were rebuilt; this does not establish freshness for other
consumers such as Zinc or Asset Allocation. FX and IME snapshot tests passed.

Cross-commodity external inputs have one workspace owner here. Commodity projects consume these
inputs directly and must not maintain local copies.

## USD/IRR contract

- Collector: `shared/market_data/fx.py`
- Canonical CSV: `shared/data/raw/fx/usd_to_rial.csv`
- Immutable pages: `shared/data/raw/fx/tgju_snapshots/`
- Grain and key: one observation per Persian calendar date (`date_pr`)
- Price unit: Iranian rial per US dollar
- Current source method: TGJU daily close
- Preserved historical method: `legacy_high_low_midpoint`

The collector validates the table shape, numeric values, Jalali/Gregorian equivalence, duplicate
dates, and conflicting records. It archives the downloaded page before atomically replacing the
canonical CSV. Copper and Zinc both read this exact file.

The 2026-10-10 collector refresh added four dates, bringing the canonical series to 13,114 dates through 1405/07/16 (2026-10-08). Asset Allocation reads this file directly for its derived weekly real estate fund versus USD/IRR comparison; its regression outputs remain under `asset_allocation/data/processed/analysis`. This supersedes the 2026-10-05 coverage checkpoint.

## LME contract

`shared/market_data/lme.py` owns Westmetall download, parsing, validation, immutable-page
archiving, and atomic refresh. Copper and Zinc keep explicit metal configurations and separate
canonical CSVs because Copper and Zinc are distinct source series.

Run from the workspace root:

```powershell
python .\shared\market_data\fx.py
```
