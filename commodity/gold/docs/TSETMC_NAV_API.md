# TSETMC NAV endpoint verification — 2026-09-27

## Scope and evidence

Read-only requests verified historical daily redemption NAV for Ayar and latest
reported redemption NAV for Ayar and Ahram directly through TSETMC. Requests
succeeded without API keys and with TLS verification. The investigation inspected
TSETMC's public frontend bundle, then tested the routes used by its fund pages:

- Website: https://www.tsetmc.com/
- Inspected bundle: https://www.tsetmc.com/main.f24603b0cc21e2598771.js

The frontend calls `Fund/GetFundInDetail/{regNo}`, reads `fund.stats`, and labels
`navRed` as redemption price (قیمت ابطال). Its instrument panel calls
`Fund/GetETFByInsCode/{InsCode}` and labels `pRedTran` as redemption NAV.

This document records results from the investigation's tool output. Full response
bytes were not archived to repository source snapshots. Examples below are selected
observed records, not an archived dataset or a guarantee of future API behavior.
No collector, scheduler, source configuration, or analytical formula was changed.

## Verified identifiers

| Fund | Trading InsCode | Fund registration number (regNo) | Verification |
|---|---|---|---|
| Ayar / عیار | 34144395039913458 | 11586 | Historical and latest NAV |
| Ahram / اهرم | 17914401175772326 | Not resolved | Latest NAV only |

These are separate identifier namespaces. Historical fund details require `regNo`;
the latest ETF endpoint requires `InsCode`. Ahram was an endpoint test instrument,
not an approved member of a precious-metal ETF universe.

## Historical daily NAV

Verified request:

```text
GET https://cdn.tsetmc.com/api/Fund/GetFundInDetail/11586
```

HTTP 200 returned `fund.mfName` = `عیار مفید`. The `fund.stats` array contained
1,934 rows with 1,934 unique `recordDate` values and positive `navRed` throughout.
Sorted coverage was 2018-06-20 through 2026-09-18. Continuous daily coverage was
not established.

| Field | Meaning shown by TSETMC |
|---|---|
| recordDate | Record date |
| navRed | Redemption NAV |
| navSub | Subscription NAV |
| navStat | Statistical NAV |
| netAsset | Total net assets |

Selected first record:

```json
{"recordDate":"2018-06-20T00:00:00","navSub":10021.0,"netAsset":604238493321.0,"navStat":10006.0,"navRed":10006.0}
```

Selected last record:

```json
{"recordDate":"2026-09-18T00:00:00","navSub":636692.0,"netAsset":3193409171760499.5,"navStat":633816.0,"navRed":633816.0}
```

Registration discovery used:

```text
GET https://cdn.tsetmc.com/api/Fund/GetFunds/5
```

Its `funds` array included `mfName = عیار مفید` and `regNo = 11586`.
Other fund categories are used by the website; category 5 is not a universal ETF
directory. Verify each fund's identity and share class independently.

The directory's Ayar summary had `recordDate = 2026-09-25` and `navRed = 649271`,
later than the historical array's last date. Do not silently insert summary or live
values into the historical series. The endpoint does not establish whether the
history is adjusted, revised, or equivalent to Mofid's `NavReportType=Raw` series.

## Latest intraday NAV

Verified requests:

```text
GET https://cdn.tsetmc.com/api/Fund/GetETFByInsCode/34144395039913458
GET https://cdn.tsetmc.com/api/Fund/GetETFByInsCode/17914401175772326
```

Both returned HTTP 200. At retrieval time `2026-09-27T09:15:13.997488+00:00`,
their `etf` objects were:

```json
{"insCode":"34144395039913458","deven":20260927,"hEven":124412,"pRedTran":653019.0,"pSubTran":655981.0,"iClose":0}
```

```json
{"insCode":"17914401175772326","deven":20260927,"hEven":124405,"pRedTran":84015.0,"pSubTran":85248.0,"iClose":0}
```

`pRedTran` is redemption NAV; `pSubTran` is subscription NAV. `deven` encodes
YYYYMMDD and `hEven` encodes HHMMSS (pad to six digits when parsing). Preserve
`iClose` as supplied; its semantics were not verified.

Ayar's earlier responses had `hEven = 121808`, `pRedTran = 652773`, and then
`hEven = 122809`, `pRedTran = 652283` on the same source date. Changed values and
timestamps confirm intraday updates. They do not establish an update guarantee.

## Negative checks

- Adding `?dEven=20250923` to Ayar's latest endpoint returned a current-dated NAV,
  not a historical observation.
- Appending `/20250923` to the latest endpoint returned HTTP 404.
- The tested daily-price and historical intraday-price responses did not contain
  redemption NAV. These results do not establish that every other route lacks it.

## Minimal reproduction (read-only)

```python
import requests

base = "https://cdn.tsetmc.com/api/Fund"

response = requests.get(f"{base}/GetFundInDetail/11586", timeout=30)
response.raise_for_status()
history = response.json()["fund"]["stats"]

response = requests.get(
    f"{base}/GetETFByInsCode/34144395039913458", timeout=30
)
response.raise_for_status()
latest = response.json()["etf"]

print("Historical rows:", len(history))
print("Latest observation:", latest)
```

## Implications for a future 30-minute collector

Polling the latest endpoint every configurable 30 minutes is technically feasible;
no recurring collector was started. Preserve response bytes, retrieval time in UTC,
source dates/times, instrument identity, request metadata, content hash, and request
or validation failures. Immutable payloads may be content-addressed, but each
retrieval must retain its own record even when the content is unchanged.

Distinguish a new retrieval, a new source timestamp, and a changed value. Repeated
polls of the same source observation must not silently become independent new
observations in a historical distribution. Sampling semantics require approval.

The tested source timestamps contain no timezone offset. The frontend describes
the live timestamp as announcement time. Verify and document timezone and valuation
time semantics; do not automatically treat the fields as UTC or treat historical
midnight values as publication times. Check NAV age and quote synchronization before
calculating a bubble. A fresh retrieval does not make stale NAV current.

Unverified: historical 30-minute NAV, Ahram historical NAV, publication/revision
vintages, guaranteed availability/update cadence/rate limits, and full comparability
with existing manager-sourced NAV. Daily history alone cannot reconstruct intraday
bubbles or establish a vintage-safe backtest.

## Relationship to the existing project

The implemented gold collector still obtains Ayar NAV history from Mofid and market
prices from TSETMC. Existing raw files and calculated results retain that provenance.
The finding here establishes an additional tested TSETMC source, not a migration.
Any future integration should first compare overlapping observations and resolve
date coverage, units, share basis, adjustment policy, and revision handling.
