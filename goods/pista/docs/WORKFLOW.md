# Pista data workflow

The refresh runs `analysis/build_bubble_distribution.py` after the bubble builder.
It atomically writes `data/processed/bubble/pistachio_bubble_distribution.csv` and saves its distribution,
empirical-CDF, and absolute-exceedance figure under `data/processed/analysis`. The 2026-09-21
checkpoint contains all 16 observed certificate-versus-physical comparisons.
The active notebook renders the distribution as a clean, interactive Plotly figure.

Power BI reads this project's `outputs/power_bi/pista_certificate_physical_comparison.csv`. Double-click `refresh_powerbi.cmd` to rebuild the observed weekly-price comparison and presentation CSV from existing raw inputs. The weekly-price units and product match remain unverified.

The command-line comparison builder is `analysis/build_certificate_bubble.py`; it reproduces the notebook's latest weekly Dahan-Bast quote within six days and writes the processed comparison atomically.

## IME certificate source

- Official IME endpoint: `https://dataapi.ime.co.ir/api/CDC/CDCTrades`.
- Market ID: `22`; contract code: `PistaCL`; commodity ID: `11`.
- Contract description: `گواهی سپرده پیوسته پسته`.
- Query begins 2026-08-25, the announced opening date of the continuous symbol.
- Earlier expiring pistachio certificate symbols are outside this dataset.
- First collection on 2026-09-19: 21 rows from 2026-08-25 through 2026-09-17;
  16 rows have positive trade volume.

## Collection

Run from the project root:

```powershell
python .\src\pista\collectors\certificate.py
```

The project collector pages the official response in date chunks, verifies contract
identity, schema, nonnegative values, and traded price/value consistency. It
retains complete response snapshots under `data/raw/certificate/api_snapshots`
and atomically writes the canonical CSV to
`data/raw/certificate/pista_certificate_raw.csv`. Normal runs refresh the last
14 days and merge by date; `--full-refresh` re-queries the full period.

## Abtahi weekly price source

The researcher obtained `data/raw/physical/Pistachio_Weekly_Prices.xlsx`
directly from [Abtahi Pistachio](https://www.abtahipistachio.com/) after contacting
several companies. It is a company-provided dataset, not an IME physical-market
transaction extract or a download from Abtahi's website. Preserve this workbook
unaltered as the received source file; the company website is an attribution link,
not the workbook's download URL.

The workbook has one sheet with 578 weekly dated rows from Jalali `1393/07/03`
through `1405/06/19`. Its columns are `Date (Jalali)` and minimum, maximum,
and average prices for each of `Khandan` and `Dahan-Bast`. Khandan has 572
populated weekly price rows; Dahan-Bast has 391. Empty cells are missing
observations, not zero prices. The workbook does not document the price unit,
specific grade/size, market location, or how the weekly figures were compiled.
These details require confirmation before economic comparisons or unit conversion.

This company price series remains independent of the IME `PistaCL` raw
certificate history. Do not describe it as executed exchange trades or use it as
an approved certificate underlying benchmark. A comparison requires confirmed
units and product specifications, Jalali-to-Gregorian date alignment, and an
explicit rule for matching weekly observations to certificate dates.

Raw files and API snapshots are not committed. Analyses must read these sources
without changing them and write derivatives only under `data/interim` or the
corresponding `data/processed/{physical,certificate,analysis}` directory.
Keep analysis code in `analysis/` and written findings in `report/`.

## Weekly price quality audit

Install the project dependencies and run from the project root:

```powershell
python -m pip install -e .
python .\analysis\audit_physical.py
python -m unittest discover -s tests -v
```

The audit reads the Abtahi workbook without changing it and writes separate
`data/interim/pistachio_physical_cleaned.csv` and
`data/interim/pistachio_physical_audit.csv` files. The CSVs are reproducible
local derivatives, not substitutes for the received workbook. The audit flags
duplicate or invalid Jalali dates, Min greater than Max, nonpositive prices,
Average arithmetic errors, ranges at least 25% of the midpoint, one-observation
changes of at least 25%, isolated deviations of at least 15% when neighbors
agree within 25%, unusual endpoint precision, and missing/date-gap boundaries.
It checks simple tenfold endpoint candidates but does not apply one without a
valid and uniquely supported replacement. Missing blocks are preserved.

Only deterministic Average arithmetic errors are corrected automatically;
the program recomputes Average from Min and Max. A price endpoint is not
changed merely because it is extreme. `manual_review` rows remain in the
cleaned CSV with their original prices and must be resolved or excluded under
an explicit analysis rule before returns, volatility, spreads, or models are
estimated. `keep` means a flag was documented without a supported correction.
The output includes row-level quality flags and a separate product-level audit
with neighboring observations and local deviation measures.

## Indicative certificate comparison

Run `analysis/pista_certificate_analysis.ipynb` from the project root or its
`analysis/` directory. The notebook reads the original Abtahi workbook and the
independent IME certificate CSV; it does not modify either or change the audit
flags. It recomputes Dahan-Bast midpoint as `(Min + Max) / 2` and keeps only
`PistaCL` dates with positive volume and settlement price. The latest weekly
price on or before each certificate date is eligible only through six calendar
days after the weekly observation. The exact same-date overlaps in this extract
have zero certificate volume, so they do not enter the traded-day comparison.

For the provisional unit assumption of toman per kilogram in the Abtahi file,
the aligned observed physical price in rial per kilogram is `10 x Dahan-Bast midpoint`. The
certificate represents one kilogram and its IME settlement price is treated as
rial per kilogram. The notebook calculates
`100 x (certificate settlement / converted physical midpoint - 1)` and writes
the date-level table to `data/processed/bubble/pista_certificate_bubble.csv`.
The current output contains 16 matched traded dates; the physical quote age is
two to six days and the indicative premium ranges from 6.13% to 30.96%.

The Abtahi price unit and precise grade/size remain unconfirmed. The certificate
is specified as Fandoqi Dahan-Bast, size 30-32, one kilogram per certificate
([IME announcement](https://tg.me/boursekalairan/18516)). The result is a
aligned weekly-price premium, not a validated arbitrage bubble. Do not
interpret it as exact-date physical trading or use it for econometric inference
without resolving unit, grade, transaction basis, and applicable costs.
