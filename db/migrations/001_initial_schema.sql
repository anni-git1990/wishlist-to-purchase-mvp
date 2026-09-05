-- ============================================================================
-- Myntra Wishlist Confidence Engine (WCE) - Database Migration Script
-- Version: 001_initial_schema.sql
-- Target Database: PostgreSQL 14+
-- Description: Core tables for wishlist items, user fit profiles, fit ML logs, and trigger audit
-- ============================================================================

BEGIN;

-- 1. Core Wishlist Items Table
CREATE TABLE IF NOT EXISTS wishlist_items (
    wishlist_item_id VARCHAR(64) PRIMARY KEY,
    user_id VARCHAR(64) NOT NULL,
    product_id VARCHAR(64) NOT NULL,
    sku_id VARCHAR(64) NOT NULL,
    added_timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    revisit_count INT DEFAULT 0,
    last_revisited_timestamp TIMESTAMP WITH TIME ZONE,
    status VARCHAR(32) DEFAULT 'ACTIVE' CHECK (status IN ('ACTIVE', 'MOVED_TO_BAG', 'REMOVED', 'PURCHASED', 'UNAVAILABLE')),
    experiment_group VARCHAR(64) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT idx_user_product UNIQUE (user_id, product_id)
);

CREATE INDEX IF NOT EXISTS idx_wishlist_user_status ON wishlist_items(user_id, status);
CREATE INDEX IF NOT EXISTS idx_wishlist_product_id ON wishlist_items(product_id);
CREATE INDEX IF NOT EXISTS idx_wishlist_added_ts ON wishlist_items(added_timestamp);

-- 2. User Fit Profiles Table (Encrypted / Anonymized Fit Preferences)
CREATE TABLE IF NOT EXISTS user_fit_profiles (
    user_id VARCHAR(64) PRIMARY KEY,
    height_cm NUMERIC(5,2) CHECK (height_cm BETWEEN 100 AND 250),
    weight_kg NUMERIC(5,2) CHECK (weight_kg BETWEEN 30 AND 250),
    preferred_fit_style VARCHAR(32) DEFAULT 'REGULAR' CHECK (preferred_fit_style IN ('SLIM', 'REGULAR', 'LOOSE', 'OVERSIZED')),
    consent_given BOOLEAN DEFAULT FALSE,
    consent_timestamp TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_fit_profiles_consent ON user_fit_profiles(user_id) WHERE consent_given = TRUE;

-- 3. Fit Recommendation Logs (ML Model Inferences & Audit Trail)
CREATE TABLE IF NOT EXISTS fit_recommendation_logs (
    recommendation_id VARCHAR(64) PRIMARY KEY,
    user_id VARCHAR(64) NOT NULL,
    product_id VARCHAR(64) NOT NULL,
    sku_id VARCHAR(64) NOT NULL,
    recommended_size VARCHAR(16) NOT NULL,
    confidence_level VARCHAR(32) NOT NULL CHECK (confidence_level IN ('HIGH', 'MEDIUM', 'LIMITED_EVIDENCE')),
    confidence_score NUMERIC(5,2) NOT NULL CHECK (confidence_score BETWEEN 0 AND 100),
    selected_size VARCHAR(16),
    recommendation_accepted BOOLEAN,
    evidence_breakdown JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_fit_logs_user_prod ON fit_recommendation_logs(user_id, product_id);
CREATE INDEX IF NOT EXISTS idx_fit_logs_confidence ON fit_recommendation_logs(confidence_level);

-- 4. Notification Trigger Logs (Decision Trigger Audit & Frequency Cap Ledger)
CREATE TABLE IF NOT EXISTS notification_trigger_logs (
    trigger_id VARCHAR(64) PRIMARY KEY,
    user_id VARCHAR(64) NOT NULL,
    product_id VARCHAR(64) NOT NULL,
    trigger_type VARCHAR(64) NOT NULL CHECK (trigger_type IN ('NEW_FIT_EVIDENCE', 'SIZE_BACK_IN_STOCK', 'LOW_INVENTORY_ALERT', 'OCCASION_REMINDER')),
    channel VARCHAR(32) NOT NULL CHECK (channel IN ('APNS', 'FCM', 'IN_APP')),
    sent_timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    opened_timestamp TIMESTAMP WITH TIME ZONE,
    converted_to_bag BOOLEAN DEFAULT FALSE,
    suppression_reason VARCHAR(64),
    payload_metadata JSONB DEFAULT '{}'::jsonb
);

CREATE INDEX IF NOT EXISTS idx_trigger_user_sent ON notification_trigger_logs(user_id, sent_timestamp);
CREATE INDEX IF NOT EXISTS idx_trigger_prod_sent ON notification_trigger_logs(product_id, sent_timestamp);

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
   NEW.updated_at = CURRENT_TIMESTAMP;
   RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_wishlist_items_updated_at BEFORE UPDATE ON wishlist_items FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_user_fit_profiles_updated_at BEFORE UPDATE ON user_fit_profiles FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

COMMIT;
