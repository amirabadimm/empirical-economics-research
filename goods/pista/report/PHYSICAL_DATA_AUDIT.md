# Weekly pistachio price audit

Source: `data/raw/physical/Pistachio_Weekly_Prices.xlsx`, provided directly by
Abtahi Pistachio. Source SHA-256:
`db61049d4bfa27d7ccad8984d4b6a58b0b2f32f2ece088e03fc90ba98ce31dfb`.
The workbook is preserved unchanged.

The reproducible audit in `analysis/audit_physical.py` processed 578 weekly rows.
It flagged 55 product observations: 38 retained unchanged and 17 requiring
manual review. No price or date was automatically corrected. The cleaned CSV
retains the same row count, date sequence, price values, and missing cells as
the source. The detailed evidence is in
`data/interim/pistachio_physical_audit.csv`; quality flags are also in
`data/interim/pistachio_physical_cleaned.csv`.

## Priority source checks

- `1396/12/24`, Khandan: Min 36,000 and Max 355,000. Dividing Max by ten
  would place it below Min; the intended Max is not established.
- `1398/03/02`, both products: Min 12,500/10,500 versus Max 120,000/100,000.
  Multiplying either Min by ten would exceed its Max.
- `1398/04/20`, Dahan-Bast: Min 90,000 and Max 850,000. Max divided by ten
  would be below Min.
- `1398/07/20`, Dahan-Bast: Min 7,500 and Max 70,000. A tenfold Min would
  exceed Max. Khandan Max is 90,002 on this date, following 90,001 on
  `1398/07/11`; both unusual values remain unchanged pending source review.
- `1399/11/19`, both products: midpoints fall about 73% below nearby weeks and
  reverse by the next observation. The likely entry or extraction error has no
  uniquely supported replacement.
- `1403/08/31`: invalid Jalali date. Its prices and original date are retained
  until the date can be checked against the source.
- Dahan-Bast has a 126-row missing opening block and a 54-row block from
  `1400/11/28` through `1402/02/07`. The first values after these gaps need
  context; no missing prices were filled.
- `1397/07/05` and `1404/01/21` show synchronized price increases across both
  products followed by declines. They may reflect real market movement and
  remain unchanged pending source confirmation.

The workbook does not identify price units, exact grades or sizes, location,
or compilation method. Resolve those specifications and the manual-review
cases before calculating returns, volatility, spreads, or econometric results.
