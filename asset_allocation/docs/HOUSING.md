# Tehran housing data

## Active sources

The primary housing source is the Central Bank of Iran publication
`گزارش تحولات بازار معاملات مسکن شهر تهران`:

https://www.cbi.ir/category/16994.aspx

The 87 official PDF reports are preserved byte-for-byte under
`data/raw/housing/cbi/reports/`. The ChatGPT-assisted extraction workbook is
`data/interim/cbi_tehran_housing_monthly_1395_1403M05.xlsx`.

## Coverage and variable

The workbook contains 101 Tehran-wide monthly observations:

- 1395/01–1402/12: complete monthly coverage.
- 1403/01–1403/05: complete within the available CBI report corpus.

## CBI extraction audit and adjudications

The extracted workbook is evidence, not a silently editable canonical series. Reproducible
source adjudications live in `config/housing_cbi_overrides.csv`; the panel builder checks the
recorded original value before applying each entry. Four values were corrected after visual
review of the official report tables:

| Month | Original extraction | Corrected level | Official evidence |
|---|---:|---:|---|
| 1396/12 | 48.987 | 57.591 | `96012.pdf`, Table 2 current month |
| 1397/01 | 55.220 | 55.280 | `97.1.pdf`, Table 2 current month; repeated in `9801.pdf` |
| 1397/04 | 91.728 | 69.728 | `9704.pdf`, Table 2 current month; repeated in `9705.pdf` |
| 1397/07 | 0.6811 | 86.109 | rendered `9707.pdf`, Table 2 current month; repeated in `9708.pdf` |

All levels are million IRR per square metre. In `9707.pdf`, the RTL PDF text layer converts the
visually rendered Table 2 values `80958` and `86109` thousand IRR/m² into text resembling
`6.156` and `681.1`. The earlier extraction trusted that damaged text layer and normalized the
latter to `0.6811`. This created artificial returns of approximately -99.16% and +13,377.32%.

Two official adjacent-report revision disagreements remain disclosed. For 1396/12, the current
report gives 57.591 while `97.1.pdf` later repeats a revised 56.386; the current-report value is
used under the established methodology. For 1398/08, the current report gives 126.832 while the
next report repeats 124.637; 126.832 is retained and flagged. Neither disagreement is hidden or
resolved by interpolation.

The generated `housing_data_quality_audit.csv` has one row per CBI month and diagnoses duplicate
keys, gaps, nonpositive values, order-of-magnitude changes, and absolute monthly returns above
25%. The threshold only triggers review; it does not replace values.

For 1397, the corrupted extraction produced monthly sample standard deviation 38.6235 and
annualized volatility 133.7956. Correcting only 1397/07 reduces these to 0.1331 and 0.4612;
therefore the Mehr error accounts for 99.66% of the former annualized-volatility magnitude.
After all verified corrections, monthly standard deviation is 0.0406, annualized volatility is
0.1408, and compounded housing appreciation is 0.9172.

The variable is the average transaction price per square metre of residential units
transacted in Tehran, measured in million IRR per square metre. It is a transaction-
composition-sensitive average rather than a constant-quality repeat-sales index.

## Provenance

An observation may come from its own current-month report, an exact previous-month
comparison printed in the following report, an exact same-month-prior-year comparison,
or an explicit current-report headline. These recovery methods use only exact CBI-
published values. No interpolation, extrapolation, smoothing, growth-rate inversion,
or secondary-source substitution is allowed within the CBI regime.

Every observation retains its source PDF, provenance method, extraction method and
available transaction count. The workbook also contains report-level audit and coverage
worksheets.

## Return construction

After independent validation, monthly capital appreciation is calculated from price
levels:

```text
monthly_return_t = price_t / price_(t-1) - 1
```

Returns must be recomputed programmatically. They exclude rent, maintenance, vacancy,
taxes, transaction costs and liquidity costs, so they must not be called total housing
returns.

## Validation required before processing

Validate chronological continuity, unique month keys, missing months, positive prices,
unit consistency, recomputed returns, source-PDF existence, and provenance. Flag values
recovered from adjacent reports. Never fill a missing month merely to run optimization.

Kilid is used as an explicitly flagged secondary extension after 1403/05. Its snapshot is under
`data/raw/housing/kilid/snapshots/`. The sources overlap for 12 months, 1402/06–1403/05. Kilid's
raw level differs from CBI by 10.97% on average and 19.61% at maximum; their overlapping monthly
return correlation is 0.288 and return MAE is 2.29 percentage points. They are therefore not
treated as equivalent measurements.

The extension is chain-linked at 1403/05. Kilid is converted from million toman/m² to million
IRR/m², then multiplied by `CBI_1403/05 / Kilid_1403/05 = 885 / 866 = 1.021939953811`.
CBI remains unchanged through 1403/05. From 1403/06 onward, linked levels preserve Kilid's own
month-to-month returns while avoiding an artificial level jump at the source boundary. Every
Kilid-derived row is flagged `secondary_proxy_low_overlap_similarity`.

Housing levels and returns are published as rows in `monthly_asset_levels.csv` and
`monthly_asset_returns.csv`. The panel uses CBI through 1403/05 and linked Kilid thereafter.
The 1395/01 return remains missing because 1394/12 is unavailable. Raw Kilid levels, link factors,
source regimes, and quality flags are retained in the level panel. Earlier SCI, D-learn,
Aloomelek, Esfand-only and other mixed-source outputs remain retired.
