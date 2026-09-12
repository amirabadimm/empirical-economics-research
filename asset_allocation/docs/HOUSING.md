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
