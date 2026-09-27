# Gold / Ayar status — 2026-09-27

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
