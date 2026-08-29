# Shared Market Data

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

## LME contract

`shared/market_data/lme.py` owns Westmetall download, parsing, validation, immutable-page
archiving, and atomic refresh. Copper and Zinc keep explicit metal configurations and separate
canonical CSVs because Copper and Zinc are distinct source series.

Run from the workspace root:

```powershell
python .\shared\market_data\fx.py
```
