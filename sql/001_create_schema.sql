-- ============================================
-- Bangladesh Financial Platform - Phase 2 Schema
-- Star schema: dimension tables + fact tables
-- ============================================

CREATE TABLE IF NOT EXISTS dim_date (
    date_id         SERIAL PRIMARY KEY,
    full_date       DATE NOT NULL UNIQUE,
    calendar_year   INT NOT NULL,
    calendar_month  INT NOT NULL,
    calendar_day    INT NOT NULL,
    quarter         INT NOT NULL,
    fiscal_year     INT,            -- Bangladesh FY, stored as the ENDING year (e.g. 1974 for '1973-74')
    fiscal_year_label TEXT,         -- human-readable, e.g. '1973-74'
    is_fiscal_year_end BOOLEAN DEFAULT FALSE  -- TRUE for June 30 anchor rows
);

CREATE TABLE IF NOT EXISTS dim_currency (
    currency_id     SERIAL PRIMARY KEY,
    currency_code   TEXT NOT NULL UNIQUE,   -- e.g. 'USD', 'BDT', 'GBP'
    currency_name   TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS dim_source (
    source_id       SERIAL PRIMARY KEY,
    source_name     TEXT NOT NULL UNIQUE,   -- e.g. 'world_bank', 'bangladesh_bank', 'open_er_api'
    source_type     TEXT,                   -- 'api' or 'file'
    source_url      TEXT
);

CREATE TABLE IF NOT EXISTS fact_exchange_rate (
    fact_id         SERIAL PRIMARY KEY,
    date_id         INT NOT NULL REFERENCES dim_date(date_id),
    currency_id     INT NOT NULL REFERENCES dim_currency(currency_id),
    source_id       INT NOT NULL REFERENCES dim_source(source_id),
    rate_to_usd     NUMERIC(18, 6),
    rate_type       TEXT,           -- 'period_average', 'end_period', 'live'
    loaded_at       TIMESTAMPTZ DEFAULT now(),
    UNIQUE (date_id, currency_id, source_id, rate_type)
);

CREATE TABLE IF NOT EXISTS fact_inflation (
    fact_id         SERIAL PRIMARY KEY,
    date_id         INT NOT NULL REFERENCES dim_date(date_id),
    source_id       INT NOT NULL REFERENCES dim_source(source_id),
    inflation_rate  NUMERIC(10, 4),
    measure_type    TEXT,           -- e.g. 'CPI_point_to_point', 'CPI_annual'
    loaded_at       TIMESTAMPTZ DEFAULT now(),
    UNIQUE (date_id, source_id, measure_type)
);

CREATE TABLE IF NOT EXISTS fact_reserves (
    fact_id         SERIAL PRIMARY KEY,
    date_id         INT NOT NULL REFERENCES dim_date(date_id),
    source_id       INT NOT NULL REFERENCES dim_source(source_id),
    reserves_usd    NUMERIC(18, 2),
    loaded_at       TIMESTAMPTZ DEFAULT now(),
    UNIQUE (date_id, source_id)
);

CREATE TABLE IF NOT EXISTS fact_trade (
    fact_id         SERIAL PRIMARY KEY,
    date_id         INT NOT NULL REFERENCES dim_date(date_id),
    source_id       INT NOT NULL REFERENCES dim_source(source_id),
    exports_usd     NUMERIC(18, 2),
    imports_usd     NUMERIC(18, 2),
    trade_balance_usd NUMERIC(18, 2),
    loaded_at       TIMESTAMPTZ DEFAULT now(),
    UNIQUE (date_id, source_id)
);

CREATE TABLE IF NOT EXISTS fact_remittance (
    fact_id         SERIAL PRIMARY KEY,
    date_id         INT NOT NULL REFERENCES dim_date(date_id),
    source_id       INT NOT NULL REFERENCES dim_source(source_id),
    remittance_usd  NUMERIC(18, 2),
    loaded_at       TIMESTAMPTZ DEFAULT now(),
    UNIQUE (date_id, source_id)
);

CREATE INDEX IF NOT EXISTS idx_fact_exchange_rate_date ON fact_exchange_rate(date_id);
CREATE INDEX IF NOT EXISTS idx_fact_inflation_date ON fact_inflation(date_id);
CREATE INDEX IF NOT EXISTS idx_fact_reserves_date ON fact_reserves(date_id);
CREATE INDEX IF NOT EXISTS idx_fact_trade_date ON fact_trade(date_id);
CREATE INDEX IF NOT EXISTS idx_fact_remittance_date ON fact_remittance(date_id);
