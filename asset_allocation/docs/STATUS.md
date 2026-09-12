# Status

Updated: 2026-09-12

## Confirmed scope

The CBI Tehran housing corpus has been corrected to the project lifecycle layout:
87 official PDFs are preserved under `data/raw/housing/cbi/reports/`, while the
101-row extracted monthly workbook remains in `data/interim`. All copied PDFs passed
SHA-256 equality checks. The same byte-identical corpus was copied to the Housing
repository raw layer and the extraction workbook to its staging layer.

The study covers Tehran housing sale price per square metre, TGJU 18-karat gold, fixed income,
and Tehran Stock Exchange equities from 1395/01 through 1405/05. Canonical monthly levels and
returns are retained. The notebook implements ex-post Stage I risky-sleeve optimization for the
years 1396-1404 and a five-month 1405 YTD period through Mordad. Results after 1403/05 use the
documented chain-linked Kilid housing proxy. Stage II is implemented as ex-post risk-aversion
sensitivity, not as an investor-specific allocation recommendation.

## Fixed income

اعتماد is the only selected fixed-income source. Bank-deposit and اخزا alternatives were
retired on 2026-09-09 after the window changed to 1395/01–1405/05. Their immutable raw
evidence remains frozen but inactive. The raw TSETMC history
covers 2015-03-14 through 2026-09-07 and every month of 1395 has traded observations.
Its total-return treatment,
distributions, and early non-trading rows still need an issuer and listing audit before returns
are calculated.

## TSE total index

The official TSETMC index API for instrument 32097828799138957 supplies daily observations from
2008-12-04 through 2026-09-07. The canonical panel contains all 125 return months from 1395/01
through 1405/05, based on the final valid TSETMC close in each Jalali month. The annual derivative,
historical collector, and TGJU collector were retired. Their raw files remain frozen inactive
under the immutable-source policy and are not merged with the official series.

## Local inventory

No ready-to-use histories for the four selected assets were found in readable E:/Work or E:/Housing
files. Housing has standardized liquidity, CPI, and construction-input series, not a Tehran
residential sale-price-per-square-metre series. This does not claim a search of every drive or
cloud.

## Stage

- Asset scope and target window: recorded.
- Fixed-income raw collection: started; selected proxy regime recorded.
- TEDPIX TSETMC raw collection: complete for the active window.
- Canonical level panel: complete, 126 months × four assets, including explicit missing levels.
- Canonical return panel: complete, 125 months × four assets, without filling missing returns.
- CBI housing extraction audit: complete; four source-verified corrections are applied through
  a checked override layer and a 101-row quality report is regenerated with the panels.
- Stage I benchmark-relative risky-sleeve analysis: implemented and numerically validated in the
  notebook for 1396-1404 and 1405/01-05 YTD, with explicit housing-source-regime disclosure.
- Stage II total-portfolio allocation: ex-post mean-variance sensitivity implemented for
  gamma values from 0 through 50 on the documented grid; an investor-specific policy remains
  unspecified.
- Alternative fixed-volatility analysis: implemented at the end of the notebook. One annualized
  covariance model estimated from all 113 aligned months in 1396–1405/05 is reused in every year
  for both Stage I tracking error and Stage II total-portfolio volatility.

## Gold collection

TGJU 18-karat gold daily data has been collected from 1392/04/31 through 1405/06/16 in IRR
per gram. The canonical panel selects the final valid observation in each Jalali month and
calculates adjacent month-end price appreciation. The required 1394/12 endpoint exists, giving
all 125 gold returns from 1395/01 through 1405/05.
Housing uses the official CBI monthly Tehran transaction-price corpus as its primary source.
The 101-row extraction covers 1395/01–1402/12 completely and 1403/01–1403/05 within scope.
Housing uses CBI through 1403/05 and a chain-linked Kilid proxy afterward. The 12-month overlap
does not show close equivalence: level MAPE is 10.97%, maximum absolute level gap is 19.61%,
monthly-return correlation is 0.288, and return MAE is 2.29 percentage points. Kilid is anchored
to CBI at 1403/05 with factor 1.021939953811 and every later row carries a low-similarity flag.
Housing now has 124 valid monthly returns; only 1395/01 remains missing for lack of 1394/12.
The corrected 1397 sequence removes the artificial -99%/+13,000% pair. Its housing returns now
have 4.06% monthly sample volatility and 14.08% annualized volatility. Official revision
disagreements for 1396/12 and 1398/08 remain explicitly flagged under the current-report rule.
