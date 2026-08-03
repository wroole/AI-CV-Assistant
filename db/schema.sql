-- ============================================================================
-- AI CV Assistant - PostgreSQL schema
-- ============================================================================
-- Tables:
--   users                 - account + auth info (login, password hash, email)
--   subscription_plans    - catalog of plans (Free, Pro, Enterprise)
--   user_subscriptions     - which plan a user currently holds
-- ============================================================================
-- Run with:
--   psql "postgresql://user:password@localhost:5432/aicv" -f db/schema.sql
-- ============================================================================

-- Required for gen_random_uuid() in older Postgres versions.
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ----------------------------------------------------------------------------
-- Helper: automatic updated_at column
-- ----------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION set_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- ----------------------------------------------------------------------------
-- users
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS users (
    id                UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email             VARCHAR(255) NOT NULL UNIQUE,
    password_hash     VARCHAR(255) NOT NULL,
    full_name         VARCHAR(100),
    role              VARCHAR(20)  NOT NULL DEFAULT 'user'
                      CHECK (role IN ('user', 'admin')),
    is_active         BOOLEAN      NOT NULL DEFAULT TRUE,
    created_at        TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at        TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_users_email             ON users (email);

CREATE TRIGGER trg_users_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();

-- ----------------------------------------------------------------------------
-- subscription_plans - the catalog of available plans
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS subscription_plans (
    id                    UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name                  VARCHAR(50)  NOT NULL UNIQUE,            -- 'free', 'pro', 'enterprise'
    display_name          VARCHAR(100) NOT NULL,                    -- 'Pro Monthly'
    price_cents           INTEGER      NOT NULL DEFAULT 0,          -- price in cents (1599 = $15.99)
    currency              VARCHAR(3)   NOT NULL DEFAULT 'USD',
    interval              VARCHAR(10)  NOT NULL DEFAULT 'month'
                          CHECK (interval IN ('month', 'year')),
    max_analyses_per_month INTEGER      NOT NULL DEFAULT 0,         -- 0 = unlimited
    features              JSONB        NOT NULL DEFAULT '{}'::jsonb,
    is_active             BOOLEAN      NOT NULL DEFAULT TRUE,
    created_at            TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at            TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TRIGGER trg_subscription_plans_updated_at
    BEFORE UPDATE ON subscription_plans
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();

-- ----------------------------------------------------------------------------
-- user_subscriptions - one row per active/current subscription of a user
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS user_subscriptions (
    id                       UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id                  UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    plan_id                  UUID NOT NULL REFERENCES subscription_plans(id),
    status                   VARCHAR(20) NOT NULL DEFAULT 'active'
                             CHECK (status IN ('active', 'trialing', 'past_due', 'canceled', 'expired')),
    current_period_start     TIMESTAMP,
    current_period_end       TIMESTAMP,
    cancel_at_period_end     BOOLEAN    NOT NULL DEFAULT FALSE,
    created_at               TIMESTAMP  NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at               TIMESTAMP  NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_user_subscriptions_user_id  ON user_subscriptions (user_id);
CREATE INDEX IF NOT EXISTS idx_user_subscriptions_status    ON user_subscriptions (status);

CREATE TRIGGER trg_user_subscriptions_updated_at
    BEFORE UPDATE ON user_subscriptions
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();

-- ----------------------------------------------------------------------------
-- Seed default subscription plans
-- ----------------------------------------------------------------------------
INSERT INTO subscription_plans (name, display_name, price_cents, interval, max_analyses_per_month, features)
VALUES
    ('free',      'Free',      0,    'month', 3,
     '{"features": ["3 analyses / month", "Basic scoring", "Local LLM analysis"]}'),
    ('pro',       'Pro',       1599, 'month', 30,
     '{"features": ["30 analyses / month", "OpenAI API access", "HR mode", "PDF JD upload", "Priority processing"]}'),
    ('enterprise', 'Enterprise', 9999, 'year', 0,
     '{"features": ["Unlimited analyses", "OpenAI API access", "Team accounts", "API access", "Priority support"]}')
ON CONFLICT (name) DO NOTHING;
