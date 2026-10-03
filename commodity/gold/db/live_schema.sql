-- Disposable latest readings, never used as historical distribution inputs.
CREATE TABLE IF NOT EXISTS research.gold_live_state (
    instrument_id bigint PRIMARY KEY REFERENCES research.instruments(instrument_id),
    retrieved_at timestamptz NOT NULL,
    expires_at timestamptz NOT NULL,
    price_source_at timestamptz,
    nav_source_at timestamptz,
    last_price_irr numeric(24,6),
    redemption_nav_irr numeric(24,6),
    bubble_pct numeric(18,10),
    year_percentile numeric(12,8),
    year_decile smallint CHECK (year_decile BETWEEN 1 AND 10),
    year_count integer NOT NULL,
    six_month_percentile numeric(12,8),
    six_month_decile smallint CHECK (six_month_decile BETWEEN 1 AND 10),
    six_month_count integer NOT NULL,
    weighted_percentile numeric(12,8),
    weighted_decile smallint CHECK (weighted_decile BETWEEN 1 AND 10),
    full_history_count integer NOT NULL,
    weighted_effective_count numeric(18,8),
    half_life_days integer NOT NULL DEFAULT 90,
    reference_last_date date,
    status text NOT NULL,
    detail text,
    price_payload jsonb,
    nav_payload jsonb,
    two_year_percentile numeric(12,8),
    two_year_decile smallint CHECK (two_year_decile BETWEEN 1 AND 10),
    two_year_count integer NOT NULL DEFAULT 0
);
ALTER TABLE research.gold_live_state ADD COLUMN IF NOT EXISTS two_year_percentile numeric(12,8);
ALTER TABLE research.gold_live_state ADD COLUMN IF NOT EXISTS two_year_decile smallint CHECK (two_year_decile BETWEEN 1 AND 10);
ALTER TABLE research.gold_live_state ADD COLUMN IF NOT EXISTS two_year_count integer NOT NULL DEFAULT 0;
CREATE OR REPLACE VIEW research.current_gold_bubbles AS
SELECT i.instrument_key, i.display_name, s.*,
    CASE WHEN (now() AT TIME ZONE 'Asia/Tehran')::time < time '12:00'
           OR (now() AT TIME ZONE 'Asia/Tehran')::time >= time '18:01'
         THEN 'market_closed'
         WHEN s.retrieved_at < now() - interval '10 minutes' THEN 'stale_reading'
         ELSE s.status END AS availability
FROM research.gold_live_state s
JOIN research.instruments i USING (instrument_id)
WHERE s.expires_at > now();

-- Query these daily-only weighted samples to plot any of the four distributions.
CREATE OR REPLACE VIEW research.gold_daily_reference AS
SELECT i.instrument_key, r.reference_method, b.observation_date, b.bubble_pct,
    CASE WHEN r.weighted THEN power(2::numeric,
         -((now() AT TIME ZONE 'Asia/Tehran')::date - b.observation_date) / 90.0)
         ELSE 1::numeric END AS observation_weight
FROM research.bubble_observations b
JOIN research.instruments i USING (instrument_id)
CROSS JOIN LATERAL (VALUES
    ('one_year', ((now() AT TIME ZONE 'Asia/Tehran')::date - interval '1 year')::date, false),
    ('six_month', ((now() AT TIME ZONE 'Asia/Tehran')::date - interval '6 months')::date, false),
    ('two_year', greatest(date '2024-01-01', ((now() AT TIME ZONE 'Asia/Tehran')::date - interval '2 years')::date), false),
    ('weighted_full', NULL::date, true)
) r(reference_method, start_date, weighted)
WHERE i.asset_class = 'gold_etf'
  AND b.method_key = 'exact_date_close_fipiran_redemption_v1'
  AND b.observation_date < (now() AT TIME ZONE 'Asia/Tehran')::date
  AND (r.start_date IS NULL OR b.observation_date >= r.start_date);
