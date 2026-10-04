# Gold ETF NAV reliability audit — 2026-09-29

Audit/retrieval date: 2026-09-29. Comparison window: 2024-09-28 through
2026-09-28 inclusive. This audit checks reported redemption NAV, source identity,
provenance, date coverage, and agreement with current official manager records.
It does not independently value the underlying portfolios or recover historical
publication/revision vintages.

## Ayar Fipiran collection and rebuild - 2026-09-29

Selected source: Fipiran, registration 11586 / group 0, `cancelNav` in IRR.
Fresh collection: 2,997 unique NAV dates, 2018-06-20 through 2026-09-26.
Two-year window ending 2026-09-28: 448/465 traded dates covered, 17 missing.
Full-history bubble: 1,928 exact-date observations through 2026-09-26.
Archived-source audits were replayed after the rebuild: all 337 two-year traded
dates shared with saved TSETMC NAV agree exactly. The 111 additional covered
trading dates are not all independently corroborated. Mofid was not queried.
Previous TSETMC and Mofid files remain separate evidence. Other fund canonical
sources and shared code were not changed; the gold notebook was not executed.
This supersedes the earlier Ayar TSETMC selection and its 337/465, 1,536-row build.

## Current conclusion

| Fund | Selected source | Saved traded dates with NAV | Manager corroboration / reliability finding |
|---|---|---:|---|
| Ayar | Fipiran | 448/465 | All 337 dates shared with saved TSETMC agree. 17 missing dates; additional coverage is not independently manager-validated. No new Mofid data requested. |
| Tala | Fipiran | 465/465 | All 465 traded observations match the official manager; all 730 shared calendar dates match. |
| Kahroba | Fipiran | 464/465 | All 464 available traded observations match the official manager; all 729 shared calendar dates match. One missing NAV date. |
| Ganj | Fipiran | 462/465 | All 462 available traded observations match the official manager; all 724 shared calendar dates match. Three missing NAV dates. |
| Gohar | Fipiran | 464/464 | 462 traded observations match the manager; two differ, including a material conflict on 2026-09-09. Three calendar dates differ out of 730 shared dates. |

Denominators are the saved positive-volume, positive-trade-count price panel.
All five price files received a bounded September 29 refresh; the active two-year
panels include September 28 where traded. These counts describe saved positive
volume/trade-count rows and do not establish availability of later sessions.

Manager agreement corroborates what the fund currently publishes. Fipiran and
TSETMC may obtain data from the same upstream reporting chain, so their agreement
alone is weaker than verification against another publisher and is not proof of
independent valuation accuracy. Source-specific missingness remains explicit.

## Identity and provenance (original checkpoint counts; before Ayar Fipiran publication)

All five passed live Fipiran registration/group/name/InsCode checks, independent
TSETMC instrument-symbol checks, and TSETMC fund-detail name/registration checks.
Every inspected saved price and NAV observation was traced to its own archived
response bytes, with SHA256 checked before parsing. The audit covers 8,517 saved
price rows and 28,606 saved NAV rows across selected and comparison sources;
17,315 NAV rows belong to the selected source files. It found no duplicate
canonical dates, invalid positive-price/NAV values, missing source hashes, or
untraceable values. These full-source row counts are distinct from two-year
analysis coverage.

Source snapshots and canonical CSVs were not corrected to force agreement.
Manager histories are independent audit evidence in snapshots and derived audit
tables, not replacements for canonical Fipiran histories.

## Official manager checks

The manager domains came from the verified Fipiran directory. API routes and NAV
field meanings were inspected in each manager's public frontend.

| Fund | Manager request | Redemption NAV mapping and identity |
|---|---|---|
| Tala | `https://lotusgoldfund.capital/api/v1/public/nav/1` | `sellNAVPerShare`; `/api/v1/public/fundItems` maps fund 1 to طلا and InsCode 46700660505281786. |
| Kahroba | `https://kahroba.charismafunds.ir/api/v1/public/nav/1` | `sellNAVPerShare`; fund 1 links to InsCode 25559236668122210. Its other fund is not selected. |
| Gohar | `https://kianfunds3.ir/api/v2/public/reports/navps` | `redemption_price`; `portfolio_id=1`, verified gold portfolio; homepage identifies registration 11556. |
| Ganj | `https://iran-kfunds5.ir/Reports/FundNAVList` | HTML column `قیمت ابطال`; every row's fund group must equal `صندوق سرمایه گذاری سیمای کاردان`. All 37 pages of the bounded two-year report were read. |

Tala and Kahroba dates are converted from the source `jalaliDate` using
`jdatetime`, not by guessing offsets. Their frontend labels `sellNAVPerShare`
as `قیمت ابطال`. Gohar's `date_time` contains a local timezone; its date portion
is retained as the valuation date rather than shifted to another date in UTC.
Ganj's displayed Jalali dates are converted similarly. All four manager sources
supplied 731 distinct dates in the inclusive two-year calendar window. Tala's
full response had one exact duplicate; no conflicting manager duplicates were
found.

For Gohar the exact query is `portfolio_id=1`,
`start_date=2024-09-28T00:00:00.000Z`,
`end_date=2026-09-28T23:59:59.999Z`, `page=1`, `size=1000`.
Its 731 returned rows equal `total_count`, so no unseen pages remain.
Ganj's date filter is `FromDate=1403/07/07`, `ToDate=1405/07/06`.
Its first request uses `BasketId=1`; the server's own pagination links return
`BasketId=0`. The parser accepts only the verified sole group name on every row.
Pages 1–37 yielded exactly 731 daily rows.

## Gohar: three conflicts and a unit change

| Valuation date | Saved Fipiran NAV (IRR) | Current manager NAV (IRR) | In saved traded panel? |
|---|---:|---:|---|
| 2026-07-01 | 814,143 | 814,145 | Yes; a 2 IRR difference |
| 2026-09-09 | 1,189,025 | 1,135,616 | Yes; material |
| 2026-09-10 | 1,189,015 | 1,135,606 | No |

On September 9 the saved closing price is 1,144,639 IRR. The Fipiran-based
premium is **−3.732974%**, while using the current manager NAV gives
**+0.794547%**: a **4.527521 percentage-point** difference, including a sign change.
This date must remain flagged pending source reconciliation; do not present its
premium as fully validated. The July 1 discrepancy changes the premium by only
0.000245 percentage points. No arbitrary tolerance silently hides either conflict.

The earlier reported **4.49% TSETMC/Fipiran discrepancy on September 11** was a
different observation, outside the saved traded sample. The current manager
reports 1,135,597 IRR, exactly matching Fipiran, versus the saved TSETMC value of
1,189,005. That date is absent from the fresh TSETMC response, which is not
evidence that TSETMC corrected it.

The manager also reports:

| Date | NAV (IRR) | Total units |
|---|---:|---:|
| 2026-09-26 | 1,136,728 | 272,757,872 |
| 2026-09-27 | 14,339 | 21,820,629,760 |
| 2026-09-28 | 14,800 | 21,865,629,760 |

The September 27 unit count is exactly **80 times** September 26's count. This
supports an 80-for-1 unit split interpretation of the abrupt NAV scale change;
a formal corporate-action notice was not independently found in the manager's
retrieved news listing. The fresh TSETMC traded close moves from 1,140,903 IRR on
September 26 to 14,713 IRR on September 28. The same-date post-change NAV is
14,800 IRR. Never interpret the unadjusted NAV level drop as a 98.74% investment
loss or combine a pre-change price with a post-change NAV.

## Tala, Kahroba, and Ganj

Their selected Fipiran values are corroborated by the current manager histories
on every shared date in the audit window. This resolves the earlier provider
disagreements in favor of consistency with the manager's currently published
records, without proving why TSETMC differs or whether later revisions occurred.

Tala's saved TSETMC history differs from the manager on 18 of 520 shared calendar
dates, including 16 traded dates. The largest impact is 1.447187 percentage points
on the premium. Kahroba's five TSETMC differences include only three traded dates;
their maximum premium impact is 0.008548 percentage points. Its larger 0.44% NAV
difference was on a nontrading date. Ganj's 463 TSETMC overlaps also match.

Missing Fipiran trading dates remain blank in selected outputs, although the
official manager has values for them:

| Fund | Missing selected date | Manager NAV, audit evidence only (IRR) |
|---|---|---:|
| Kahroba | 2026-07-01 | 164,441 |
| Ganj | 2025-03-18 | 66,459 |
| Ganj | 2026-08-11 | 162,773 |
| Ganj | 2026-08-19 | 170,795 |

Ganj's full source history begins before its gold strategy. The validation above
applies to the explicit two-year gold period; it does not approve its older
fixed-income/legacy observations for gold research.

## Superseded Ayar TSETMC selection and response stability

At the earlier September 29 checkpoint, the validated collector
wrote 2,284 TSETMC historical NAV dates (2018-06-20–2026-09-08) into
`data/raw/funds/ayar/nav_tsetmc.csv`. Mofid's old `nav.csv` remains frozen evidence.
The two-year build has 337 NAV matches out of 465 traded dates, with 128 explicit
missing values. The rebuilt full-history bubble has 1,536 matched observations
from 2018-07-22 through 2026-09-08. Its incomplete and lagged coverage limits
comparability with the former 1,949-observation Mofid-based result.

A separately archived live Fipiran Ayar history contains 2,997 dates through
2026-09-26 and covers 448/465 saved trading dates in the two-year window. All 456
shared calendar dates with the new canonical TSETMC file, including all 337
selected traded dates, agree exactly. Fipiran was used for comparison only;
the selected Ayar source remains TSETMC. No Mofid collection was performed.

TSETMC responses are not stable complete histories. During this audit an Ayar
request returned 2,067 unique dates through September 5, while the subsequent
collector request returned 2,284 dates through September 8. In the same two-year
window they overlap on only 449 dates. Tala's fresh TSETMC response omitted 324
full-history dates present in its saved canonical file, and Gohar's omitted 330.
One Tala value changed on a shared date. Fipiran's four saved histories had no
value changes on overlapping dates in the audit window.

This is why source responses are archived independently, canonical collection
merges incrementally, and absence from one response is not treated as a deletion
or a corrected NAV. Agreement statistics must always state their intersection.

## Reproduction and outputs

```powershell
# Fetch fresh evidence; raw canonical NAV/price CSVs are not updated by these audits.
python -B commodity/gold/audit_nav_reliability.py --live
python -B commodity/gold/audit_manager_nav.py --live

# Omit --live to replay the most recent archived audit requests.
python -B commodity/gold/audit_nav_reliability.py
python -B commodity/gold/audit_manager_nav.py
```

Responses and per-request metadata are preserved in
`data/raw/funds/<fund>/snapshots/reliability`. Manager endpoints were discovered
from separately archived homepages and frontend bundles. Each archived response
has a SHA256 name and metadata with URL/parameters/retrieval time. Request hashes
and paths are also in the audit JSON reports.

Derived deliverables under `data/processed/analysis/nav_reliability/`:

- `audit.json`: fund identities, saved-row provenance, live source coverage and comparisons.
- `coverage.csv`: exact-date coverage and missing dates for each provider snapshot.
- `provider_disagreements.csv`: provider/retrieval differences and traded-date impact.
- `large_nav_changes.csv`: explicit 30% absolute consecutive-NAV-change screening.
- `manager_audit.json`: manager identities, requests, comparison counts and Gohar unit data.
- `manager_nav_validation.csv`: normalized manager observations as audit evidence only.
- `manager_disagreements.csv`: manager-versus-provider differences.
- `trading_date_validation.csv`: selected NAV, comparison NAVs, price, source hashes,
  premium sensitivity, and `validation_status` for every saved trading date.

Validation status distinguishes `manager_agrees`, `manager_conflict`,
`provider_agreement_only`, and `missing_selected_nav`; it is not a guarantee of
asset valuation accuracy. No missing NAV was filled or cross-provider history
silently combined. The four Fipiran raw CSVs remain unchanged by this audit.

Shared market-analysis code and other commodity datasets were not modified.
The gold notebook consumes the rebuilt Ayar bubble, but was not executed during
this audit. Its presentation was not reviewed. All three existing bubble tests
passed. Targeted invalid-date/value, conflicting-duplicate, exact-duplicate and
Jalali-conversion checks passed. All 85 archived audit request hashes were
verified; all 2,320 date annotations match the rebuilt selected NAV tables.
Whole-workspace refresh or validation is not claimed.
