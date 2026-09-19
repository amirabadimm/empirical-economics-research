# Pista data workflow

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
