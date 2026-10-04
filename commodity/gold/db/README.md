# Gold ETF PostgreSQL Store

This directory contains the versioned database schema, loader, live-monitor logic, and systemd units used by the gold ETF research project. Host-specific secrets and runtime state are intentionally kept outside Git.

## Database design

The PostgreSQL store separates permanent daily research history from disposable intraday state.

Core objects include:

- `research.instruments` — reusable instrument registry;
- `research.daily_prices` — daily market prices with source hashes;
- `research.daily_nav` — provider-specific daily NAV observations;
- `research.bubble_observations` — method-versioned daily premium/discount observations and historical ranks;
- `research.gold_live_state` — one replaceable current row per ETF;
- `research.latest_gold_bubbles` — latest matched daily observation per fund and method;
- `research.current_gold_bubbles` — current disposable live state;
- `research.gold_daily_reference` — daily samples used by the live historical-reference distributions.

PostgreSQL is a queryable analytical copy and derived store. Canonical raw CSVs and immutable source snapshots remain the source evidence outside Git.

## Daily research semantics

The daily bubble is

```text
100 * (unadjusted close / same-date redemption NAV - 1)
```

Only positive-volume, positive-trade-count sessions with an exact same-date Fipiran redemption NAV receive a daily bubble. Missing NAV remains missing.

Each stored daily observation includes chronological historical ranks. Expanding percentiles use all observed bubbles through the current date with ties counted using `<=`. A 90-calendar-day half-life recency-weighted percentile is stored separately.

Historical distributions are descriptive ex-post analyses, not intraday trading signals.

## Five-minute disposable monitor

`live_schema.sql` adds one replaceable cache row per ETF, exposed through `research.current_gold_bubbles`.

`live_gold.py` uses TSETMC's latest traded price (`pDrCotVal`) and current redemption NAV (`pRedTran`). Intraday responses are transient inputs: they do not enter raw archives or permanent daily history. Each successful poll replaces the prior state for that ETF, and expired rows disappear from the current view.

Four completed-daily-history reference distributions are calculated for a current live bubble:

- rolling preceding twelve calendar months, equal weighted;
- rolling preceding six calendar months, equal weighted;
- full completed daily history with a 90-calendar-day half-life;
- rolling preceding two calendar years, never beginning before 2024-01-01.

The live observation itself and today's daily record are excluded from those reference samples.

A current bubble requires same-day price and NAV, neither older than 20 minutes, no more than 15 minutes apart, and recorded trading activity. Otherwise the source values remain visible but bubble and rank fields are null with a non-fresh status.

Retrieval failures are represented explicitly and never masquerade as successful quotes.

## Scheduling

Versioned systemd units run three distinct jobs:

- `gold-live.timer` — every five minutes from 12:00 through 18:00 Asia/Tehran;
- `gold-daily.timer` — canonical daily source refresh and database load at 23:30 Asia/Tehran;
- `gold-full.timer` — weekly full-history revision reconciliation on Sunday at 03:30 Asia/Tehran.

Install the units from the repository root:

```bash
sudo install -m 644 commodity/gold/db/gold-*.service commodity/gold/db/gold-*.timer /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now gold-live.timer gold-daily.timer gold-full.timer
```

Inspect scheduling and service output with:

```bash
systemctl list-timers 'gold-*'
journalctl -u gold-live.service
journalctl -u gold-daily.service
```

The live view also labels closed-market and missed-refresh states dynamically, so an old reading is not presented as a new quote.

## Deployment

The reproducible Docker definition is versioned under [`../../../deployment/`](../../../deployment/). A production host should keep its real `.env`, database volume, logs, raw evidence, and SSH configuration outside Git.

A typical host checkout is:

```text
/opt/empirical-economics-research
```

Create a Python environment and install database dependencies:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -e '.[database]'
```

Keep the database connection URL in the host environment as `GOLD_DATABASE_URL`. Do not place credentials in command arguments, committed files, or documentation.

Initialize the schema and load canonical source data:

```bash
psql "$GOLD_DATABASE_URL" -v ON_ERROR_STOP=1 -f commodity/gold/db/schema.sql
psql "$GOLD_DATABASE_URL" -v ON_ERROR_STOP=1 -f commodity/gold/db/live_schema.sql
.venv/bin/python commodity/gold/db/load_gold.py
```

The loader validates all configured fund inputs before opening a database transaction, takes an advisory lock, upserts source rows by fund and date, and replaces only its own derived method series transactionally. Repeated loads are designed to reproduce the same analytical values for unchanged inputs.

Use `--fund <key>` to restrict a load to one ETF.

## Initial data migration

For an initial deployment, copy the canonical files

```text
commodity/gold/data/raw/funds/<fund>/price.csv
commodity/gold/data/raw/funds/<fund>/nav_fipiran.csv
```

and their immutable source evidence through an authenticated encrypted channel such as `scp` or `rsync`.

Git carries code, SQL migrations, configuration templates, and documentation. It does not carry the complete raw evidence archive.

Never overwrite an existing server archive blindly. Compare hashes and preserve differing snapshots.

## Example queries

Latest matched daily observations:

```sql
SELECT *
FROM research.latest_gold_bubbles
ORDER BY instrument_key;
```

Current disposable monitoring state:

```sql
SELECT *
FROM research.current_gold_bubbles
ORDER BY instrument_key;
```

Ayar's historical daily bubble series:

```sql
SELECT
    b.observation_date,
    b.bubble_pct,
    b.expanding_percentile,
    b.expanding_decile,
    b.recent_weighted_percentile
FROM research.bubble_observations b
JOIN research.instruments i USING (instrument_id)
WHERE i.instrument_key = 'ayar'
  AND b.method_key = 'exact_date_close_fipiran_redemption_v1'
ORDER BY b.observation_date;
```

The daily-reference view exposes the four live-comparison samples with an `observation_weight` column for plotting or verification.

## Verification checkpoint

The deployed workflow was verified on 2026-10-03 with all three timers enabled. The first scheduled daily refresh produced 8,531 price rows, 18,051 selected NAV rows, and 8,213 matched bubble observations. Those counts are an operational checkpoint, not a permanent research constant; current coverage belongs in [`../docs/STATUS.md`](../docs/STATUS.md).

No credentials are committed to the repository, and host identity is intentionally omitted from public documentation.
