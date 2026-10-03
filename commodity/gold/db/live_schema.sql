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
