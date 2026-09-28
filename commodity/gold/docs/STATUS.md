# Gold status — 2026-09-28

## Active five-fund replacement checkpoint — 2026-09-28

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
