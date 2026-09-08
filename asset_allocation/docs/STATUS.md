# Status

Updated: 2026-09-08

## Confirmed scope

Tehran housing sale price per square metre; TGJU 18-karat gold; an exchange-traded fixed-income fund;
and Tehran Stock Exchange total index. ETF, اخزا, and bank-deposit histories are collected as
separate fixed-income candidates before a proxy regime is selected. IRR and monthly frequency
are proposals.

## Local inventory

No ready-to-use histories for these four series were found in readable E:/Work or E:/Housing
files. Housing has standardized liquidity, CPI, and construction-input series, not a residential
sale-price-per-square-metre series. Its housing-market and capital-markets folders are topic
scaffolds. E:/Work contains USD/IRR, commodity, issuer, and option datasets instead.

Limitation: recursive listing of one options/data/raw/optionbaaz snapshot was access-denied.
Its contents were not audited. This finding does not claim a search of every drive or cloud.

TGJU gold and equity history pages were identified, but earliest dates, completeness, and
consistent definitions have not been verified:
- https://www.tgju.org/profile/geram18/history
- https://www.tgju.org/profile/bourse/history

## Stage

- Asset scope and target window: recorded.
- Independent local dependency manifest: created; environment installation not run.
- Local inventory: complete within the stated access limits.
- Historical collection: started for fixed-income sources; complete-window verification pending.
- Returns, optimizer, and evaluation: not implemented.
- Existing-project independence: dependencies audited at a high level; migration not performed.

## Updated optimization scope

Confirmed: four assets; one optimal basket per Solar Hijri year; maximize expected portfolio
return divided by portfolio volatility; weights sum to one. No risk-free-rate subtraction.
Volatility is sqrt(w.T @ Sigma @ w). Working design: retrospective within-year estimation.
Short-selling/weight bounds remain unresolved. Monthly input frequency and IRR are proposed.

Next: audit اعتماد's TSETMC price history, NAV, distributions, and actual first trade. Follow
with gold, housing, and total index in that order.
No new data was downloaded and no optimization was run in this workflow update. Existing-project
repository restructuring remains a separate pending task.

## Fixed-income decision — pending source verification

AFRA/افران is not the earliest candidate: its reported activity start is 1398/11/21. The
first candidate is صندوق سرمایه گذاری اعتمادآفرین پارسیان (ticker: اعتماد), reported by
the fund manager and market publications as the first exchange-traded fixed-income fund, with
an activity start of 1394/02/05. The project's fixed-income collection begins with this fund.
This date is a reported activity date, not yet a verified first TSETMC trading observation.
No final study start date has been set.

## Fixed-income collection — اعتماد

Collected 2026-09-08 from the public TSETMC closing-price API for instrument
`66818022341772870` (اعتمادآفرین پارسیان). The immutable 908,650-byte JSON response is stored
by SHA-256 under `data/raw/fixed_income/etf/tsetmc_snapshots/`; its canonical CSV has 2,761
unique Gregorian-date rows from 2015-03-14 through 2026-09-07. Of those rows, 2,706 have
positive trade count and volume. The first positive-trade row is 2015-03-15; this precedes the
fund's reported 1394 activity date and is followed by a 61-calendar-day gap ending 2015-05-17.
The finding needs a TSETMC listing-history/issuer audit before defining the usable fund-return
start. No returns, monthly aggregation, or proxy mixing has been produced.

## Bank-deposit collection — World Bank annual series

Collected 2026-09-08 from the public World Bank API, indicator `FR.INR.DPST` (deposit interest
rate, percent) for Iran. The immutable JSON response and canonical annual CSV are stored under
`data/raw/fixed_income/bank_deposits/`. It has 14 non-null annual observations from 2003 through
2016, so it covers Gregorian 2005–2016 (roughly Solar Hijri 1384–1395) but does not cover the
later study period. This is a partial bank-deposit proxy, not periodic returns or a mix with ETF/
اخزا data.

## Iranian-source cross-check — bank deposits

The World Bank series is not the official Iranian one-year term-deposit ceiling. Its metadata
identifies it as an annual IMF/IFS deposit-rate observation covering demand, time, or savings
deposits, with country-specific averaging and terms. Iranian announcements identify specific
contractual ceilings, which can differ materially. Examples: the CBI-backed bank agreement set
the one-year rate at 22% from 1393/02/09, while the World Bank 2014 observation is 16.9421%;
the Money and Credit Council set a maximum one-year rate of 20% from 1394/02/08, while the World
Bank 2015 observation is 16.3%. In 1399, the announced one-year ceiling was 16%.

Keep the World Bank series as an aggregate annual cross-check only. The planned investment proxy
is a separately sourced, effective-dated Iranian schedule for a named term (preferably one year);
it must not overwrite or be merged with the World Bank CSV.

## Iranian one-year policy schedule — initial collection

Collected 2026-09-08 from Iranian CBI-reported policy sources. The immutable source-page archive
and canonical schedule are under `data/raw/fixed_income/bank_deposits/`. Four verified effective
events are currently present: 20% on 1394/02/08, 18% on 1394/11/27, 16% on 1399/04/31, and 20.5%
on 1401/11/03. This confirms that the World Bank annual series and the announced one-year rate
are different constructs.

Coverage is intentionally incomplete: 1384–1393, 1395–1398, and 1400–1401 still require
retrievable primary or bank-issued evidence. Do not forward-fill this schedule or treat it as a
continuous return series.

## Fixed-income decision — CBI annual bank-deposit series

Superseded the World Bank and bank-specific exploratory series for the 1384–1396 bank-deposit
proxy. The canonical source is now the CBI annual table at cbi.ir/simplelist/1515.aspx, using its
one-year column. The CSV has 13 Jalali-year observations from 1384 through 1396. CBI intervals
are resolved to their maximum: 1385 and 1386 are 16%, and 1390–1392 are 20%. Existing World Bank
and exploratory Iranian files are retained as immutable evidence but are retired from analysis.

## Fixed-income regime selection

User-selected regime: use the CBI one-year deposit-rate series for 1384–1395 and the اعتماد ETF
from 1396 onward, targeting coverage through 1405. No splice return will be constructed at the
1396 boundary. The CBI bank-rate side is ready as annual nominal rate observations. اعتماد has
raw TSETMC history, but its total-return definition, distributions, and early listing/trading gap
must be audited before final fixed-income returns are calculated.
