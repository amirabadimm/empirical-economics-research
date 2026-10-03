# Gold ETF PostgreSQL store

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

The target server is `85.198.48.177`. Its repository path and PostgreSQL state
still need inspection. After SSH access is available, clone or pull the repo and
install Python 3.11+ and PostgreSQL. Create a database and a least-privilege
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

The latest query is `SELECT * FROM research.latest_gold_bubbles`. The database
schema has not yet been applied to the server; the first live load and validation
remain deployment tasks.
