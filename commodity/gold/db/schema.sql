-- Gold ETF research schema, version 1. Apply with psql -v ON_ERROR_STOP=1 -f schema.sql.
CREATE SCHEMA IF NOT EXISTS research;

CREATE TABLE IF NOT EXISTS research.instruments (
    instrument_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    asset_class text NOT NULL,
    instrument_key text NOT NULL UNIQUE,
    display_name text NOT NULL,
    exchange_code text UNIQUE,
    currency_code char(3) NOT NULL,
    unit_label text NOT NULL,
    created_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS research.daily_prices (
    instrument_id bigint NOT NULL REFERENCES research.instruments(instrument_id),
    observation_date date NOT NULL,
    close_irr numeric(24, 6) NOT NULL CHECK (close_irr >= 0),
    last_irr numeric(24, 6) NOT NULL CHECK (last_irr >= 0),
    trade_volume numeric(24, 6) NOT NULL CHECK (trade_volume >= 0),
    trade_count integer NOT NULL CHECK (trade_count >= 0),
    source_name text NOT NULL,
    source_snapshot_sha256 char(64) NOT NULL,
    loaded_at timestamptz NOT NULL DEFAULT now(),
    PRIMARY KEY (instrument_id, observation_date)
);

CREATE TABLE IF NOT EXISTS research.daily_nav (
    instrument_id bigint NOT NULL REFERENCES research.instruments(instrument_id),
    observation_date date NOT NULL,
    provider_key text NOT NULL,
    redemption_irr numeric(24, 6) NOT NULL CHECK (redemption_irr > 0),
    issuance_irr numeric(24, 6),
    statistical_irr numeric(24, 6),
    source_snapshot_sha256 char(64) NOT NULL,
    loaded_at timestamptz NOT NULL DEFAULT now(),
    PRIMARY KEY (instrument_id, observation_date, provider_key)
);

-- A method key lets later valuation rules coexist with this exact-date method.
CREATE TABLE IF NOT EXISTS research.bubble_observations (
    instrument_id bigint NOT NULL REFERENCES research.instruments(instrument_id),
    observation_date date NOT NULL,
    method_key text NOT NULL,
    nav_provider_key text NOT NULL,
    bubble_pct numeric(18, 10) NOT NULL,
    spread_irr numeric(24, 6) NOT NULL,
    expanding_percentile numeric(12, 8) NOT NULL
        CHECK (expanding_percentile >= 0 AND expanding_percentile <= 100),
    expanding_decile smallint NOT NULL CHECK (expanding_decile BETWEEN 1 AND 10),
    recent_weighted_percentile numeric(12, 8) NOT NULL
        CHECK (recent_weighted_percentile >= 0 AND recent_weighted_percentile <= 100),
    history_count integer NOT NULL CHECK (history_count > 0),
    half_life_days numeric(10, 2) NOT NULL CHECK (half_life_days > 0),
    calculated_at timestamptz NOT NULL DEFAULT now(),
    PRIMARY KEY (instrument_id, observation_date, method_key),
    FOREIGN KEY (instrument_id, observation_date)
        REFERENCES research.daily_prices(instrument_id, observation_date),
    FOREIGN KEY (instrument_id, observation_date, nav_provider_key)
        REFERENCES research.daily_nav(instrument_id, observation_date, provider_key)
);

CREATE INDEX IF NOT EXISTS bubble_method_date_idx
    ON research.bubble_observations(method_key, observation_date DESC);

CREATE OR REPLACE VIEW research.latest_gold_bubbles AS
SELECT DISTINCT ON (i.instrument_key, b.method_key)
    i.instrument_key, i.display_name, b.observation_date, b.method_key,
    p.close_irr, n.redemption_irr, b.bubble_pct, b.expanding_percentile,
    b.expanding_decile, b.recent_weighted_percentile, b.history_count,
    b.nav_provider_key
FROM research.bubble_observations b
JOIN research.instruments i USING (instrument_id)
JOIN research.daily_prices p USING (instrument_id, observation_date)
JOIN research.daily_nav n ON n.instrument_id = b.instrument_id
    AND n.observation_date = b.observation_date
    AND n.provider_key = b.nav_provider_key
WHERE i.asset_class = 'gold_etf'
ORDER BY i.instrument_key, b.method_key, b.observation_date DESC;
