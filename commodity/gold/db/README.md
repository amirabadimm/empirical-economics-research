# Gold ETF PostgreSQL store

## Five-minute disposable monitor

`live_schema.sql` adds one replaceable cache row per ETF, exposed by
`research.current_gold_bubbles`. `live_gold.py` uses TSETMC's latest traded
price (`pDrCotVal`) and current redemption NAV (`pRedTran`). It does not append
intraday observations to raw archives or daily history. The next poll replaces
the previous payload; after 24 hours without replacement it disappears from the
view and the next run purges the expired cache. Live value payloads are not logged.
These disposable responses are explicitly authorized transient inputs, distinct
from the immutable daily-source archives.

Four daily-only references are computed for each moment's bubble:

- Rolling preceding twelve calendar months: equal weights, `year_percentile`
  and `year_decile`.
- Rolling preceding six calendar months: equal weights, `six_month_percentile`
  and `six_month_decile`. The window advances by date; underlying daily records
  remain preserved.
- Full completed daily history with a 90-calendar-day half-life:
  `weighted_percentile` and `weighted_decile`.
- Rolling preceding two calendar years, never before 2024-01-01: equal weights,
  `two_year_percentile` and `two_year_decile`.

References exclude today's daily record and every intraday reading. The moment's
bubble is compared with daily bubbles using `<=` ties; it is not itself added to
the distribution. Decile 1 also includes a moment below the historical minimum.
Daily reference uses unadjusted closing price/Fipiran redemption NAV; live uses
last traded price/TSETMC current redemption NAV. The two measures can differ
because of timing and provider basis. `reference_last_date` and sample counts
show the actual history available, with missing daily NAV left unfilled.

Source times are interpreted in Asia/Tehran and retained separately. A current
bubble requires same-day price/NAV, neither older than 20 minutes, at most
15 minutes between them, and recorded trading activity. Otherwise the latest
source values are visible with `stale_or_unaligned` and null bubble/ranks.
Retrieval failures replace old readings with `fetch_error`; they never appear
as a successful new quote. Outside trading hours this status is expected.

The server adapter `run_server.py` uses its existing Docker environment settings
in memory. Versioned systemd units run the live job every five minutes from
12:00 through 18:00 Asia/Tehran (inclusive final 18:00 reading), the
canonical daily collectors and DB load at 23:30 Asia/Tehran, and a full-history
revision reconciliation on Sundays at 03:30 Asia/Tehran. Installation is:

```sh
docker exec -i investment_postgres sh -c 'psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -v ON_ERROR_STOP=1 -1' < commodity/gold/db/live_schema.sql
sudo install -m 644 commodity/gold/db/gold-*.service commodity/gold/db/gold-*.timer /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now gold-live.timer gold-daily.timer gold-full.timer
```

Inspect `systemctl list-timers 'gold-*'`, `journalctl -u gold-live.service`,
and query `SELECT * FROM research.current_gold_bubbles ORDER BY instrument_key`.
`research.gold_daily_reference` exposes the four reference distributions as dated
daily bubble samples with `observation_weight`; use it to plot or inspect the
histograms. The database has three views: latest daily bubbles, current disposable
bubbles, and daily reference distributions.
The view's `availability` marks closed market hours and missed-refresh staleness
dynamically; a prior reading is never labelled as a new quote. The live job also
checks the time, preventing off-hours requests after a persistent timer catch-up.
No weekday/holiday calendar is assumed; stale source dates suppress live bubbles
on non-trading days. Monitoring values are not logged as intraday history.
Daily jobs refresh server canonical CSVs and PostgreSQL. Existing local and
presentation CSVs are not implicitly rebuilt or transferred back to the workstation.
All three timers were enabled and the live and daily jobs verified on 2026-10-03.
The first daily refresh produced 8,531 prices, 18,051 NAV rows, and 8,213 bubbles.
Source price dates end September 30; selected NAV ends September 29 for Ayar and
October 2 for the other four. Exact-date bubbles end September 29 for Ayar and
September 30 for others. This server coverage supersedes the initial-load counts below.

This store publishes the five selected ETFs' daily TSETMC prices, Fipiran
redemption NAV, exact-date bubble observations, historical percentiles, and
deciles. The raw CSVs and immutable response snapshots remain canonical source
evidence outside Git. PostgreSQL is a queryable copy and derived analysis store.

`schema.sql` creates a reusable `research.instruments` registry with asset class,
currency and unit. Other projects can add source and analytical tables keyed by
`instrument_id`; gold prices, provider-specific NAV, and method-specific bubbles
remain separate. Source hashes accompany every price and NAV row. A future
calculation can use another `method_key` without replacing this series.

## Semantics

- Bubble percentage: `100 * (unadjusted close / same-date redemption NAV - 1)`.
  Only sessions with positive volume and trade count and an exact-date Fipiran
  NAV receive a bubble. Missing NAV remains absent from bubble observations.
- Each day's expanding percentile compares its signed bubble with all the
  fund's observed bubbles up to and including that date. Ties count as `<=`.
- Decile 1 means percentile `(0, 10]`; decile 10 means `(90, 100]`.
  The latest view shows the most recent matched observation, which can lag the
  latest price or NAV date. The 90-day recent-weighted percentile is stored
  separately and does not determine the decile.
- Historical distribution is the set of `bubble_observations` for a fund and
  method. Source revision and future methods can change ranks; this is an
  ex-post daily analysis, not an intraday trading signal.

## Server setup

The target server is `85.198.48.177`, Ubuntu 24.04. The repository is at
`/opt/empirical-economics-research` with a host `.venv`. The existing Docker
container `investment_postgres` runs PostgreSQL 17 with the `investment` database
and a persistent volume. The first five-fund load succeeded on 2026-10-03.
For a new deployment, clone or pull the repo and install Python 3.11+ and PostgreSQL.
Create a database and a least-privilege
application role using server-side administration. Keep the connection URL in the
server environment as `GOLD_DATABASE_URL`; never commit it or put it in command
arguments. Then, from the repository root:

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -e '.[database]'
psql "$GOLD_DATABASE_URL" -v ON_ERROR_STOP=1 -f commodity/gold/db/schema.sql
.venv/bin/python commodity/gold/db/load_gold.py
psql "$GOLD_DATABASE_URL" -c 'SELECT * FROM research.latest_gold_bubbles ORDER BY instrument_key'
```

The five local `commodity/gold/data/raw/funds/<fund>/{price,nav_fipiran}.csv`
files must be copied to the same paths on the server for initial load, together
with their immutable source snapshots when migrating the evidence archive.
Transfer these through an authenticated, encrypted channel such as `scp` or
`rsync`; Git carries only code, SQL migrations and documentation. Never overwrite
an existing server archive blindly: compare hashes and preserve differing
snapshots. Subsequent runs can use the documented collectors on the server and
then rerun the loader. The loader validates all five inputs before opening a
database transaction, takes an advisory lock, upserts source rows by fund/date,
and replaces only its own derived method series transactionally. Repeated loads
produce the same analytical values. `--fund <key>` restricts a run to one ETF.

For the historical distribution of Ayar:

```sql
SELECT b.observation_date, b.bubble_pct, b.expanding_percentile,
       b.expanding_decile, b.recent_weighted_percentile
FROM research.bubble_observations b
JOIN research.instruments i USING (instrument_id)
WHERE i.instrument_key = 'ayar'
  AND b.method_key = 'exact_date_close_fipiran_redemption_v1'
ORDER BY b.observation_date;
```

The latest daily query is `SELECT * FROM research.latest_gold_bubbles`. The initial
deployment contained 8,521 prices, 18,032 Fipiran NAV rows, and 8,202 matched bubble rows.
All 265 transferred source/evidence files matched the local SHA-256 manifest.
A repeat load reproduced the same analytical values. These are the saved
September 29 histories; deployment did not collect newer market data.
This initial deployment checkpoint is superseded by the scheduled monitoring
checkpoint in `docs/STATUS.md`. Server connection settings were
constructed in memory from its existing environment configuration; no credentials
were added to the repository.
