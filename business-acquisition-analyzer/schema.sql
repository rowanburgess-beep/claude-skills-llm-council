-- Optional Postgres schema for persisting scored listings.
-- Apply with: psql "$DATABASE_URL" -f schema.sql

CREATE TABLE IF NOT EXISTS businesses_for_sale (
    id                  SERIAL PRIMARY KEY,
    name                TEXT NOT NULL,
    source              TEXT,
    url                 TEXT,
    sector              TEXT,
    region              TEXT,
    raw_text            TEXT,
    notes               TEXT,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS listing_financials (
    id                  SERIAL PRIMARY KEY,
    business_id         INTEGER NOT NULL REFERENCES businesses_for_sale(id) ON DELETE CASCADE,
    asking_price        NUMERIC,
    revenue             NUMERIC,
    earnings_value      NUMERIC,
    earnings_basis      TEXT,
    passive_ebitda      NUMERIC,
    multiple            NUMERIC,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS owner_dependency (
    id                  SERIAL PRIMARY KEY,
    business_id         INTEGER NOT NULL REFERENCES businesses_for_sale(id) ON DELETE CASCADE,
    owner_involvement   TEXT,
    manager_in_place    BOOLEAN,
    staff_count         INTEGER,
    years_established   INTEGER
);

CREATE TABLE IF NOT EXISTS deal_signals (
    id                          SERIAL PRIMARY KEY,
    business_id                 INTEGER NOT NULL REFERENCES businesses_for_sale(id) ON DELETE CASCADE,
    reason_for_sale             TEXT,
    vendor_finance_offered      BOOLEAN,
    days_on_market              INTEGER,
    customer_concentration_pct  NUMERIC,
    recurring_revenue           BOOLEAN,
    contracts_in_place          BOOLEAN
);

CREATE TABLE IF NOT EXISTS opportunities_tracked (
    id                  SERIAL PRIMARY KEY,
    business_id         INTEGER NOT NULL REFERENCES businesses_for_sale(id) ON DELETE CASCADE,
    trigger_date        TIMESTAMPTZ NOT NULL DEFAULT now(),
    composite_score     NUMERIC NOT NULL,
    verdict             TEXT NOT NULL,
    pillar_scores       JSONB NOT NULL,
    red_flags           JSONB NOT NULL,
    status              TEXT NOT NULL DEFAULT 'new'
);
