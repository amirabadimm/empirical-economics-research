# Mesghal historical redemption NAV validation

Collection and validation date: **2026-09-29**. Main requests were made at
08:56:27 UTC (12:26:27 Asia/Tehran); frontend and group-selection checks followed.
This is a new live investigation, with archived response evidence, superseding
the earlier unarchived Mesghal endpoint investigation for the checks below.

**NO — a verifiable historical redemption NAV series for Mesghal could not be obtained.**

This conclusion concerns the tested sources and requests. It is not proof that
no historical series exists elsewhere. No canonical Mesghal NAV CSV or new
price/NAV analysis was published. Existing price evidence and the five active
funds were not changed by this investigation.

## Verified identity

The live Fipiran directory was requested with:

```http
POST https://www.fipiran.com/services/fund/fundcompare/
Content-Type: application/json

{"regNos": [], "showMarketMakers": false}
```

It contained one row matching all of these fields:

| Field | Value |
|---|---|
| Exact Fipiran name | صندوق س.کالای آگاه (مثقال) |
| Symbol (`smallSymbolName`) | مثقال |
| Registration (`regNo`) | 11899 |
| Fipiran `groupId` | 2 |
| TSETMC `insCode` | 32469128621155736 |
| Manager | سبدگردان آگاه سهامی خاص |
| Listed website | zarinagahfund.com |

TSETMC `Instrument/GetInstrumentInfo/32469128621155736` independently returned
`lVal18AFC = مثقال`, `lVal18 = Mesghal`, and `instrumentID = IRTKZARA0001`.

Registration 11899 is not a unique group identifier in Fipiran. The directory
also contained group 1 (`مبتنی بر کالای آگاه`, parent fund without this trading
symbol/InsCode) and group 3 (`صندوق س.کالای آگاه (نقرات)`, a different symbol
and InsCode). Their NAV values must not be substituted for group 2.

## Historical Fipiran request and actual response

```http
GET https://www.fipiran.com/services/chart/getfundchart?regno=11899&groupId=2&showAll=true
```

Actual result: **HTTP 200**, `application/json; charset=utf-8`, **2 bytes**:

```json
[]
```

The exact bytes were archived before parsing. SHA256:

```text
4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945
```

| Historical-series check | Result |
|---|---|
| Historical rows / distinct NAV dates / valid daily observations | 0 / 0 / 0 |
| Earliest / latest historical NAV date | Unavailable / unavailable |
| `cancelNav` observed in a history row | No history row returned |
| Null, zero, negative, nonfinite NAV rows | 0 returned rows; this is not a validation pass |
| Duplicate rows / conflicting dates | 0 / 0 because the response is empty |
| Missing trading-date observations | All dates remain unmatched; no history is accepted |

The directory has a *current summary* for Mesghal: date `2026-09-28T00:00:00`,
`cancelNav = 198747.0`, `issueNav = 199671.0` (check archived directory for
other fields). A directory summary is not the requested historical chart series.

## TSETMC latest NAV cross-check

```http
GET https://cdn.tsetmc.com/api/Fund/GetETFByInsCode/32469128621155736
```

Actual HTTP 200 response:

```json
{"etf":{"insCode":"32469128621155736","deven":20260929,"hEven":122514,"pRedTran":200735.0,"pSubTran":201666.0,"iClose":0}}
```

The live TSETMC frontend labels `pRedTran` as `NAV ابطال` and the source date/time
as `زمان اعلام`. Thus this is its currently published redemption NAV snapshot.
Source time is 12:25:14 on 2026-09-29; the response itself supplies no timezone.
It is not a historical observation for 2026-09-28. No meaningful same-date
historical `cancelNav` comparison is possible because Fipiran returned no history.
The directory summary and this live observation have different dates and must
not be presented as a provider discrepancy.

## TSETMC historical identity failure

```http
GET https://cdn.tsetmc.com/api/Fund/GetFundInDetail/11899
GET https://cdn.tsetmc.com/api/Fund/GetFundInDetail/11899?groupId=2
```

Both returned HTTP 200 with byte-identical bodies, whose SHA256 is:

```text
d639c87e8726a52fdf05571b7e436e9bdaa4ccb12c8c5e6bf94db0a266f9a467
```

The returned `fund.mfName` is **صندوق س.کالای آگاه (نقرات)**. Its summary reports
`recordDate = 2026-09-20T00:00:00`, `navRed = 12528.0`. The `stats` array contains
1,014 rows on 1,008 distinct dates (2022-01-06 through 2026-09-20), with six
duplicate rows and no conflicting same-date `navRed` values. These structural
checks do **not** establish Mesghal identity. The entire response was rejected
as a Mesghal source. Its long history may mix legacy fund context; no subset
was relabelled or accepted as Mesghal.

The actual TSETMC frontend bundle linked by its homepage was downloaded and
inspected. Its `/Fund/:regNo` route passes the route's `regNo` to
`getFundInDetail`, and the fund directory navigates using each row's `regNo`.
That establishes the frontend's identifier semantics, but does not establish
unambiguous share/group selection for registration 11899. The tested `groupId=2`
query did not change the response. The inspected bundle exposes three Fund routes:
`GetFunds`, `GetFundInDetail`, and `GetETFByInsCode`.

The live `GetFunds/5` directory also labels registration 11899 as نقرات.
No independently verified Mesghal historical TSETMC series was obtained.

## Manager-site failure

The official website listed in the verified Fipiran row was requested:
`https://zarinagahfund.com`. It failed DNS resolution with
`NameResolutionError` / `[Errno 11002] getaddrinfo failed`. There was no HTTP
response body. The transport failure is recorded in request metadata. No
alternative manager domain or guessed NAV history was accepted.

## Evidence and reproduction

The reproducible read-only-source investigation is
[`investigate_mesghal_nav.py`](../investigate_mesghal_nav.py):

```powershell
python -B commodity/gold/investigate_mesghal_nav.py
```

It archives source bytes before parsing and emits a timestamped JSON report in
`data/processed/analysis/mesghal_nav_investigation_<UTC>.json`. It does not write
canonical NAV or trading-price CSVs. Canonical publication remains conditional
on valid history and verified identity through the normal collector workflow.

Additional public endpoints can be archived using `--probe-url <URL> --label <name>`.
The supplemental probes for this checkpoint were the TSETMC homepage, its linked
`main.f24603b0cc21e2598771.js`, `Fund/GetFunds/5`, and the `groupId=2` request above.

Evidence directory: `data/raw/funds/mesghal/snapshots/nav_investigation/`.
Bodies are named `<SHA256>.body`; per-request metadata preserves the full URL,
parameters, UTC retrieval time, HTTP status or transport error, content hash,
and the verified identity for the Fipiran history request. Identical response
bodies are not overwritten, and each request still gets separate metadata.

| Evidence | SHA256 |
|---|---|
| Fipiran identity directory | `872e08ec7b028cf3364a2e180448fe50d1846661b70d0d33fec156c4461bc52f` |
| Empty Fipiran chart | `4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945` |
| TSETMC instrument identity | `cadf30711aed9922f51cf5a46723f16fbf65207b9ca5cfe68d1775a73ac8c070` |
| TSETMC latest ETF NAV | `9e3f939b570ae5c076906730a88492aaf5911080a8dc06d64724ef6a0f65dd1f` |
| Rejected TSETMC historical response | `d639c87e8726a52fdf05571b7e436e9bdaa4ccb12c8c5e6bf94db0a266f9a467` |
| TSETMC fund directory | `eed30262d370bd361cb38aa47f72bb3418c60f1e2cd231cb945d79554c1cf139` |
| TSETMC frontend bundle | `3ba4d37ba96ac038995fdfd251b5bff6f68a50bb3f907647da6bf59f1e65d351` |

The initial machine-readable report is
`data/processed/analysis/mesghal_nav_investigation_20260929T085638517510Z.json`.
Supplemental requests are in their individually timestamped archive metadata.

No NAV was forward-filled, back-filled, interpolated, inferred from gold or market
prices, or copied across fund groups. No normalized historical NAV dataset was
created because none passed both the identity and history checks. Historical
publication times, revision vintages, and valuation-basis equivalence remain
unverified.
