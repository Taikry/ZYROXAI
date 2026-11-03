"""Migration script: 0009_risk_intelligence_v3
Creates user_risk_settings and risk_assessment_logs tables for SQLite and PostgreSQL.
"""
import logging
from sqlalchemy import text

logger = logging.getLogger("taikry.database.migrate_risk_intelligence_v3")


def run_migration(engine=None) -> None:
    from taikry.database.session import engine as default_engine
    target_engine = engine or default_engine

    dialect = target_engine.dialect.name
    logger.info(f"Running Risk Intelligence V3 migration on dialect: {dialect}")

    with target_engine.begin() as conn:
        if dialect == "postgresql":
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS user_risk_settings (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER NULL,
                    risk_mode VARCHAR(32) NOT NULL DEFAULT 'BALANCED',
                    risk_per_trade_percent DOUBLE PRECISION NOT NULL DEFAULT 0.5,
                    min_risk_reward_ratio DOUBLE PRECISION NOT NULL DEFAULT 2.0,
                    max_daily_loss_percent DOUBLE PRECISION NOT NULL DEFAULT 2.5,
                    max_weekly_loss_percent DOUBLE PRECISION NOT NULL DEFAULT 5.0,
                    max_monthly_loss_percent DOUBLE PRECISION NOT NULL DEFAULT 10.0,
                    max_drawdown_percent DOUBLE PRECISION NOT NULL DEFAULT 8.0,
                    max_simultaneous_positions INTEGER NOT NULL DEFAULT 3,
                    max_portfolio_risk_percent DOUBLE PRECISION NOT NULL DEFAULT 5.0,
                    max_correlated_positions INTEGER NOT NULL DEFAULT 2,
                    news_filter_mode VARCHAR(32) NOT NULL DEFAULT 'STANDARD',
                    created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT NOW(),
                    updated_at TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT NOW()
                );
                CREATE INDEX IF NOT EXISTS ix_user_risk_settings_user_id ON user_risk_settings (user_id);

                CREATE TABLE IF NOT EXISTS risk_assessment_logs (
                    id SERIAL PRIMARY KEY,
                    assessment_id VARCHAR(64) UNIQUE NOT NULL,
                    user_id INTEGER NULL,
                    symbol VARCHAR(32) NOT NULL,
                    direction VARCHAR(16) NOT NULL,
                    entry_price DOUBLE PRECISION NULL,
                    stop_loss DOUBLE PRECISION NULL,
                    take_profit_1 DOUBLE PRECISION NULL,
                    take_profit_2 DOUBLE PRECISION NULL,
                    calculated_rr VARCHAR(16) NULL,
                    decision VARCHAR(32) NOT NULL,
                    risk_mode VARCHAR(32) NOT NULL DEFAULT 'BALANCED',
                    risk_percentage DOUBLE PRECISION NOT NULL,
                    account_equity DOUBLE PRECISION NOT NULL,
                    risk_amount_usd DOUBLE PRECISION NOT NULL,
                    recommended_lots DOUBLE PRECISION NOT NULL DEFAULT 0.01,
                    quality_score INTEGER NOT NULL DEFAULT 0,
                    market_regime VARCHAR(32) NOT NULL DEFAULT 'UNCERTAIN',
                    news_status VARCHAR(32) NOT NULL DEFAULT 'CLEAR',
                    portfolio_risk_pct DOUBLE PRECISION NOT NULL DEFAULT 0.0,
                    veto_reasons JSONB NOT NULL DEFAULT '[]'::jsonb,
                    advisory_notes JSONB NOT NULL DEFAULT '[]'::jsonb,
                    validation_details JSONB NOT NULL DEFAULT '{}'::jsonb,
                    created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT NOW()
                );
                CREATE INDEX IF NOT EXISTS ix_risk_assessment_logs_symbol ON risk_assessment_logs (symbol);
                CREATE INDEX IF NOT EXISTS ix_risk_assessment_logs_decision ON risk_assessment_logs (decision);
                CREATE INDEX IF NOT EXISTS ix_risk_assessment_logs_created_at ON risk_assessment_logs (created_at);
            """))
        else:
            # SQLite
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS user_risk_settings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NULL,
                    risk_mode VARCHAR(32) NOT NULL DEFAULT 'BALANCED',
                    risk_per_trade_percent REAL NOT NULL DEFAULT 0.5,
                    min_risk_reward_ratio REAL NOT NULL DEFAULT 2.0,
                    max_daily_loss_percent REAL NOT NULL DEFAULT 2.5,
                    max_weekly_loss_percent REAL NOT NULL DEFAULT 5.0,
                    max_monthly_loss_percent REAL NOT NULL DEFAULT 10.0,
                    max_drawdown_percent REAL NOT NULL DEFAULT 8.0,
                    max_simultaneous_positions INTEGER NOT NULL DEFAULT 3,
                    max_portfolio_risk_percent REAL NOT NULL DEFAULT 5.0,
                    max_correlated_positions INTEGER NOT NULL DEFAULT 2,
                    news_filter_mode VARCHAR(32) NOT NULL DEFAULT 'STANDARD',
                    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
                );
            """))
            conn.execute(text("CREATE INDEX IF NOT EXISTS ix_user_risk_settings_user_id ON user_risk_settings (user_id);"))

            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS risk_assessment_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    assessment_id VARCHAR(64) UNIQUE NOT NULL,
                    user_id INTEGER NULL,
                    symbol VARCHAR(32) NOT NULL,
                    direction VARCHAR(16) NOT NULL,
                    entry_price REAL NULL,
                    stop_loss REAL NULL,
                    take_profit_1 REAL NULL,
                    take_profit_2 REAL NULL,
                    calculated_rr VARCHAR(16) NULL,
                    decision VARCHAR(32) NOT NULL,
                    risk_mode VARCHAR(32) NOT NULL DEFAULT 'BALANCED',
                    risk_percentage REAL NOT NULL,
                    account_equity REAL NOT NULL,
                    risk_amount_usd REAL NOT NULL,
                    recommended_lots REAL NOT NULL DEFAULT 0.01,
                    quality_score INTEGER NOT NULL DEFAULT 0,
                    market_regime VARCHAR(32) NOT NULL DEFAULT 'UNCERTAIN',
                    news_status VARCHAR(32) NOT NULL DEFAULT 'CLEAR',
                    portfolio_risk_pct REAL NOT NULL DEFAULT 0.0,
                    veto_reasons TEXT NOT NULL DEFAULT '[]',
                    advisory_notes TEXT NOT NULL DEFAULT '[]',
                    validation_details TEXT NOT NULL DEFAULT '{}',
                    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
                );
            """))
            conn.execute(text("CREATE INDEX IF NOT EXISTS ix_risk_assessment_logs_symbol ON risk_assessment_logs (symbol);"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS ix_risk_assessment_logs_decision ON risk_assessment_logs (decision);"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS ix_risk_assessment_logs_created_at ON risk_assessment_logs (created_at);"))

    logger.info("Risk Intelligence V3 migration applied successfully.")
