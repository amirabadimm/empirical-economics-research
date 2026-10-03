# Gold status — 2026-09-29

## Five-minute monitor implementation — 2026-10-03

Disposable current-price/current-NAV cache and four daily-only reference ranks
are implemented, with five-minute polling only 12:00-18:00 Tehran, daily collection at 23:30 Tehran,
and weekly full-history reconciliation units. Latest cache replaces prior readings
and expires after 24 hours. Live deployment
and the first scheduled collector run are being verified; this section does not
claim newer daily data coverage.

## PostgreSQL integration deployed — 2026-10-03

Schema and five-fund loader are prepared locally for daily prices, Fipiran NAV,
exact-date bubble history, expanding percentile, and latest historical decile.
Deployment succeeded on Ubuntu 24.04 at `/opt/empirical-economics-research`, using
the existing PostgreSQL 17 Docker container and `investment` database. All 265
source/evidence files matched the local SHA-256 manifest. The database has 8,521
prices, 18,032 NAV rows, and 8,202 bubbles; repeat loading reproduced identical
analytical values. Latest-decile query returned five funds. No new market refresh
or scheduler was run. The September 29 source checkpoint remains unchanged.

## Research checkpoint closed — 2026-10-03

The five-fund daily price/NAV collection, two-year analysis, Ayar bubble rebuild,
and source-reliability audit are complete at the September 29 data checkpoint.
The small missing-NAV set and Gohar manager disagreements remain visible in the
per-date validation table; they do not block closing this phase. Interpret the
affected Gohar dates with that flag. Mesghal remains outside the active universe
because no verified historical NAV series was found. Routine incremental refresh
and periodic full-history revision checks are maintenance, not an unfinished
research deliverable. This is a documentation closeout, not a new data refresh.

## Incremental server collection — 2026-09-29

Routine five-fund refresh now requests Fipiran `showAll=false` (342 Ayar and
362–366 other recent NAV dates) and TSETMC `GetClosingPriceDailyList/{insCode}/30`
(30 recent price rows per fund). Both modes were verified live, followed by
the two-year build and archived reliability audits. Current build coverage is
Ayar 448/465, Tala 465/465, Kahroba 464/465, Ganj 462/465, and Gohar 464/464.
Initial loads and explicit `--full` request complete
histories. The canonical files merge by date and publish atomically; recent
responses must cover the last saved date. Full runs are needed periodically to find
revisions older than the recent response window. TSETMC comparison fund-detail
NAV remains a complete-history optional request via `--comparison-nav`.


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


## Earlier reliability checkpoint (Ayar selection superseded) — 2026-09-29

Live source identity/provenance checks passed for all five funds. Official
manager histories corroborate Tala (730 shared calendar dates), Kahroba (729),
and Ganj (724) with zero disagreements. Gohar disagrees with its manager on
three dates; September 9 is material (+4.527521 percentage points in premium
when using the manager value instead). Its September 27 unit count increases
80-fold. See [the reliability report](NAV_RELIABILITY.md) and the per-date audit
table; do not treat Gohar's complete coverage as fully validated NAV.

Ayar TSETMC collection now succeeded: 2,284 source NAV dates through September 8.
September 29 two-year build (as-of September 28): Ayar 337/465, Tala 464/464,
Kahroba 463/464, Ganj 461/464, Gohar 463/463. Ayar alone had its canonical prices
refreshed to September 28 during this audit. Its rebuilt full-history bubble has
1,536 observations, July 22, 2018 through September 8, 2026. Every selected Ayar
traded NAV agrees with the Fipiran audit history, but 128 two-year dates are missing.
TSETMC response coverage varies across requests; this is an incomplete sample.

The other four raw Fipiran histories were not changed. Their manager records are
independent validation evidence, including values for the four missing dates.
No source values were replaced, estimated, or filled. Mesghal remains unresolved.
Shared code and dependent commodity datasets were not changed; the gold notebook
was not executed. This checkpoint supersedes the earlier pending Ayar transition.

## Mesghal live source validation — 2026-09-29

Identity verified live: Fipiran `صندوق س.کالای آگاه (مثقال)`, registration 11899,
group 2, InsCode 32469128621155736. Historical Fipiran response: HTTP 200, `[]`,
zero observations. TSETMC's registration-based history was labelled نقرات and
rejected, including the byte-identical `groupId=2` response. The verified current
Mesghal ETF snapshot is not historical NAV. The listed manager site failed DNS.
No canonical NAV or new Mesghal analysis was published. Source bodies and request
metadata are archived; [full validation report](MESGHAL_NAV_VALIDATION.md).
This supersedes the earlier unarchived investigation for these checks, without
changing the active five-fund selection or the pending Ayar source transition.

## Superseded pending Ayar transition — earlier on 2026-09-29

Active Ayar code now selects TSETMC historical redemption NAV (registration 11586)
from a separate `nav_tsetmc.csv`. The old Mofid `nav.csv` and snapshots are retained.
Live TSETMC access failed here, so the new raw source has not been collected and
the Ayar analysis has not been rebuilt. The Ayar 464/464 and 1,949-row counts below
are superseded Mofid-based checkpoints, not verified TSETMC results.

## Historical five-fund replacement checkpoint — 2026-09-28

The Ayar bubble build no longer writes a separate
`data/processed/analysis/ayar_unmatched_prices.csv`. That file was header-only
at this checkpoint (zero unmatched traded dates) and was removed. Missing NAV
remains visible through `nav_available` in the two-year analysis tables.
The optional Ayar distribution image was removed locally and is no longer
listed as a deliverable; processed images are ignored by Git.

Mesghal is removed from the active two-year panel because no verified
historical redemption NAV was found. Its source and earlier derived files
remain preserved as exploratory evidence. The next high-turnover candidate,
Zarvan (TSETMC InsCode `28255729477187163`), starts on 2024-12-02 and lacks
the requested full two years. Gohar (InsCode `12390706505809150`) was selected
after verifying its trading history from 2017-12-05 and matching Fipiran
registration 11556, group 0, name `مبتنی بر کالای کیان` against both Fipiran's
fund directory and TSETMC's fund detail endpoint.

Gohar canonical source files contain 2,114 TSETMC price rows, 2,447 unique
TSETMC historical NAV dates, and 3,161 Fipiran historical NAV dates. The latter
spans 2018-02-01 through 2026-09-27. In the 2024-09-28 through 2026-09-28
processed window, Gohar has **463 traded dates and 463 exact-date Fipiran
redemption NAV matches**; latest traded date is 2026-09-26. The other active
funds remain Ayar 464/464, Tala 464/464, Kahroba 463/464, and Ganj 461/464.
These counts are derived-output coverage, distinct from the full source spans.
Fipiran and TSETMC historical NAV are independently archived. Their valuation
bases and historical publication times are not proven identical. On 497
overlapping NAV dates in the two-year window, their Gohar redemption values
disagree on 8 dates; the processed panel consistently uses Fipiran.

The preceding two-year checkpoint below is **superseded for active fund
selection**; its Mesghal row records the earlier investigation only. The
older five-fund source checkpoint likewise describes the prior selection.

## Superseded two-year price/NAV checkpoint — 2026-09-28

Window: 2024-09-28 through 2026-09-28 inclusive. The latest trading record
returned by TSETMC was 2026-09-27. Five processed tables under
`data/processed/analysis/<fund>_daily_price_nav_2y.csv` contain one row per
positive-volume, positive-trade-count session, the unadjusted closing price,
the exact-date redemption NAV where available, and source snapshots. Missing
NAV is null and `nav_available` is false; nothing is forward-filled.

| Fund | Traded price dates | Exact-date redemption NAV matches | Missing NAV dates | Selected two-year NAV source |
|---|---:|---:|---:|---|
| Ayar | 464 | 464 | 0 | Manager Mofid, raw |
| Tala | 464 | 464 | 0 | Fipiran historical |
| Kahroba | 464 | 463 | 1 (2026-07-01) | Fipiran historical |
| Mesghal | 464 | 0 | 464 | Unresolved |
| Ganj | 464 | 461 | 3 (2025-03-18, 2026-08-11, 2026-08-19) | Fipiran historical |

Ayar's documented collector was refreshed successfully: its raw manager NAV
now has 3,082 rows through 2026-09-27, and its existing derived bubble build
has 1,949 exact-date traded observations through 2026-09-27. Separately archived
Fipiran histories have 3,365 Tala, 1,889 Kahroba, and 6,616 Ganj NAV dates,
each through 2026-09-27. The older TSETMC NAV histories remain independent raw
evidence and are not overwritten. This checkpoint supersedes the counts below
for Ayar NAV, Tala/Kahroba/Ganj *selected analysis NAV*, and derived Ayar
coverage; it does not change their older source-coverage observations.

On overlapping dates within this window, Fipiran and TSETMC redemption NAV
disagree on 18 of 520 Tala dates (largest absolute relative difference 1.46%),
5 of 427 Kahroba dates (0.44%), and 0 of 463 Ganj dates. The selected two-year
tables use one consistent Fipiran series per fund; those provider differences
remain an unresolved source-comparability limit.

Fipiran lists Mesghal under registration 11899, group 2, with a current
redemption NAV, but `chart/getfundchart` returned an empty historical array for
that group. Its manager domain did not resolve. A complete five-fund NAV panel
is therefore not available from the verified sources tested here.
Direct TSETMC recheck on 2026-09-28 confirmed Mesghal's unique InsCode returns
only current ETF NAV; date query parameters were ignored. The historical
`GetFundInDetail/11899` response remained Naqrat even with tested group/type
query parameters. See [endpoint evidence](TSETMC_NAV_API.md). This was a
read-only verification, not a data refresh.

## Superseded five-fund collection checkpoint — 2026-09-28

Historical unadjusted daily trading rows were collected from TSETMC for all
five selected funds. Ayar's existing Mofid raw redemption NAV was retained;
historical TSETMC redemption NAV was collected for Tala, Kahroba, and Ganj.
Counts below are canonical CSV rows, not a continuous-session coverage claim.

| Fund | Price rows and source-date span | Redemption NAV rows and source-date span | Source |
|---|---|---|---|
| Ayar | 1,997; 2018-06-02–2026-09-27 | 3,080; 2018-04-21–2026-09-25 | Official Mofid raw NAV |
| Tala | 2,235; 2017-06-10–2026-09-27 | 2,865; 2017-06-10–2026-09-08 | TSETMC historical NAV |
| Kahroba | 1,248; 2021-07-06–2026-09-27 | 1,125; 2021-07-10–2026-09-04 | TSETMC historical NAV |
| Mesghal | 1,146; 2021-12-12–2026-09-27 | Unavailable | Identity/source unresolved |
| Ganj | 922; 2022-11-19–2026-09-27 | 4,854; 2010-01-14–2026-09-04 | TSETMC historical NAV |

The three TSETMC NAV histories stop earlier than the trading histories. Tala's
first source response contained 30 repeated dates with identical values, which
the collector validated and collapsed. A second response supplied a different
subset of Tala historical dates: the canonical atomic merge retained dates
from both valid responses and grew from 2,541 to 2,865 rows. The source's
response stability remains unverified. No derived five-fund bubble build was run.
The original Ayar production checkpoint below is superseded only for Ayar
*price source coverage*; its historical NAV provenance and prior derived-output
checkpoint remain distinct.

**Mesghal NAV blocker:** TSETMC instrument search resolves Mesghal to trading
InsCode `32469128621155736`, and the live ETF endpoint returns a current
redemption NAV. Public fund listings identify registration number 11899 for
Mesghal, but TSETMC's `GetFundInDetail/11899` currently returns the silver fund
Naqrat with NAV near 12,500 IRR. Fipiran's fund directory lists Mesghal under
group 2 but its tested historical chart endpoint returned an empty array for
that group. The manager's listed domain did not resolve in this environment.
Thus no historical Mesghal NAV has been saved. Current ETF NAV was not
substituted for daily history. This requires a validated historical provider.

## Endpoint research checkpoint — 2026-09-27

Verified directly through TSETMC: Ayar historical redemption NAV at
`Fund/GetFundInDetail/11586`, with 1,934 unique dates from 2018-06-20 through
2026-09-18 and positive `navRed` on every returned row. Latest NAV at
`Fund/GetETFByInsCode/{InsCode}` was verified for Ayar and Ahram; successive Ayar
responses changed intraday. Historical 30-minute NAV and Ahram historical NAV
remain unverified. See [the discovery record](TSETMC_NAV_API.md).

This was read-only discovery: no source snapshots or datasets were saved and no
collector, scheduler, or production source was changed. The documentation records
selected tool-observed results, not a complete archived API response.

## Existing production checkpoint — 2026-09-26

Implemented: official TSETMC price collection, official Mofid raw redemption-NAV
history, independent raw tables, exact-date premium, signed histogram, expanding
equal-weight and recent-weighted percentiles, and read-only interactive notebook.
Other funds are not yet configured.

Verification: 12 NAV-bubble/statistical tests passed; all notebook code cells
executed successfully; archived response SHA256 hashes matched filenames; a second
local rebuild reproduced both processed bubble CSVs byte-for-byte. Live incremental
collection beyond the initial download has not yet been exercised.

Initial build: 1,947 traded exact-date observations, 2018-06-09 through 2026-09-23;
zero traded dates missing NAV. The first date is the API's available traded record,
not an independently verified launch date. NAV history extends from 2018-04-21
through 2026-09-25. Latest matched premium: +0.953308%; expanding percentile
64.509502; recent-weighted percentile 31.141630 (90-calendar-day half-life).

Prices come from TSETMC; historical NAV comes from the official manager portal,
not a historical TSETMC NAV feed. The latest-only TSETMC ETF NAV is not used to
backfill history. Production collection uses TLS-verified direct APIs only.

Historical publication times and vintage NAV revisions are unavailable: this is
an ex-post daily close/NAV comparison, not a real-time arbitrage signal or
vintage-safe backtest. No forward fill, price adjustment or NAV interpolation.
