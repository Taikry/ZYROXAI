"""
Migration script: 0010_v6_technical_intelligence
Creates v6_regime_results, v6_concept_detections, and v6_best_setups tables for SQLite and PostgreSQL.
"""
import logging
from sqlalchemy import text

logger = logging.getLogger("taikry.database.migrate_v6_models")


def run_migration(engine=None) -> None:
    from taikry.database.session import engine as default_engine
    target_engine = engine or default_engine

    dialect = target_engine.dialect.name
    logger.info(f"Running V6 Technical Intelligence migration on dialect: {dialect}")

    with target_engine.begin() as conn:
        if dialect == "postgresql":
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS v6_regime_results (
                    id SERIAL PRIMARY KEY,
                    symbol VARCHAR(32) NOT NULL,
                    timeframe VARCHAR(16) NOT NULL,
                    regime VARCHAR(40) NOT NULL,
                    strength INTEGER NOT NULL DEFAULT 50,
                    evidence JSONB NULL,
                    metrics JSONB NULL,
                    data_quality VARCHAR(32) DEFAULT 'SUFFICIENT',
                    created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT NOW()
                );
                CREATE INDEX IF NOT EXISTS ix_v6_regime_results_symbol ON v6_regime_results (symbol);
                CREATE INDEX IF NOT EXISTS ix_v6_regime_results_regime ON v6_regime_results (regime);
                CREATE INDEX IF NOT EXISTS ix_v6_regime_results_created_at ON v6_regime_results (created_at);

                CREATE TABLE IF NOT EXISTS v6_concept_detections (
                    id SERIAL PRIMARY KEY,
                    analysis_id VARCHAR(64) NOT NULL,
                    symbol VARCHAR(32) NOT NULL,
                    timeframe VARCHAR(16) NOT NULL,
                    category VARCHAR(40) NOT NULL,
                    concept_id VARCHAR(64) NOT NULL,
                    name VARCHAR(128) NOT NULL,
                    confidence INTEGER NOT NULL DEFAULT 50,
                    bias VARCHAR(20) NOT NULL DEFAULT 'NEUTRAL',
                    levels JSONB NULL,
                    evidence JSONB NULL,
                    chart_overlay JSONB NULL,
                    created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT NOW()
                );
                CREATE INDEX IF NOT EXISTS ix_v6_concept_detections_analysis_id ON v6_concept_detections (analysis_id);
                CREATE INDEX IF NOT EXISTS ix_v6_concept_detections_symbol ON v6_concept_detections (symbol);
                CREATE INDEX IF NOT EXISTS ix_v6_concept_detections_category ON v6_concept_detections (category);
                CREATE INDEX IF NOT EXISTS ix_v6_concept_detections_concept_id ON v6_concept_detections (concept_id);

                CREATE TABLE IF NOT EXISTS v6_best_setups (
                    id SERIAL PRIMARY KEY,
                    setup_id VARCHAR(64) UNIQUE NOT NULL,
                    user_id INTEGER NULL,
                    symbol VARCHAR(32) NOT NULL,
                    timeframe VARCHAR(16) NOT NULL,
                    direction VARCHAR(24) NOT NULL,
                    regime VARCHAR(40) NOT NULL,
                    strategy_id VARCHAR(64) NULL,
                    strategy_name VARCHAR(128) NULL,
                    quality_score INTEGER NOT NULL DEFAULT 50,
                    quality_classification VARCHAR(32) NOT NULL DEFAULT 'WATCHLIST',
                    entry_type VARCHAR(24) DEFAULT 'MARKET',
                    entry_price DOUBLE PRECISION NULL,
                    stop_loss DOUBLE PRECISION NULL,
                    stop_distance DOUBLE PRECISION NULL,
                    invalidation_reason TEXT NULL,
                    tp1 DOUBLE PRECISION NULL,
                    tp1_r DOUBLE PRECISION NULL,
                    tp2 DOUBLE PRECISION NULL,
                    tp2_r DOUBLE PRECISION NULL,
                    tp3 DOUBLE PRECISION NULL,
                    tp3_r DOUBLE PRECISION NULL,
                    risk_reward_ratio VARCHAR(20) NULL,
                    trade_plan_json JSONB NULL,
                    quality_score_json JSONB NULL,
                    mtf_status_json JSONB NULL,
                    ai_review_json JSONB NULL,
                    risk_manager_json JSONB NULL,
                    why_this_setup JSONB NULL,
                    created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT NOW()
                );
                CREATE INDEX IF NOT EXISTS ix_v6_best_setups_setup_id ON v6_best_setups (setup_id);
                CREATE INDEX IF NOT EXISTS ix_v6_best_setups_symbol ON v6_best_setups (symbol);
                CREATE INDEX IF NOT EXISTS ix_v6_best_setups_direction ON v6_best_setups (direction);
                CREATE INDEX IF NOT EXISTS ix_v6_best_setups_created_at ON v6_best_setups (created_at);
            """))
        else:
            # SQLite
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS v6_regime_results (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    symbol VARCHAR(32) NOT NULL,
                    timeframe VARCHAR(16) NOT NULL,
                    regime VARCHAR(40) NOT NULL,
                    strength INTEGER NOT NULL DEFAULT 50,
                    evidence TEXT NULL,
                    metrics TEXT NULL,
                    data_quality VARCHAR(32) DEFAULT 'SUFFICIENT',
                    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
                );
            """))
            conn.execute(text("CREATE INDEX IF NOT EXISTS ix_v6_regime_results_symbol ON v6_regime_results (symbol);"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS ix_v6_regime_results_regime ON v6_regime_results (regime);"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS ix_v6_regime_results_created_at ON v6_regime_results (created_at);"))

            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS v6_concept_detections (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    analysis_id VARCHAR(64) NOT NULL,
                    symbol VARCHAR(32) NOT NULL,
                    timeframe VARCHAR(16) NOT NULL,
                    category VARCHAR(40) NOT NULL,
                    concept_id VARCHAR(64) NOT NULL,
                    name VARCHAR(128) NOT NULL,
                    confidence INTEGER NOT NULL DEFAULT 50,
                    bias VARCHAR(20) NOT NULL DEFAULT 'NEUTRAL',
                    levels TEXT NULL,
                    evidence TEXT NULL,
                    chart_overlay TEXT NULL,
                    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
                );
            """))
            conn.execute(text("CREATE INDEX IF NOT EXISTS ix_v6_concept_detections_analysis_id ON v6_concept_detections (analysis_id);"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS ix_v6_concept_detections_symbol ON v6_concept_detections (symbol);"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS ix_v6_concept_detections_category ON v6_concept_detections (category);"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS ix_v6_concept_detections_concept_id ON v6_concept_detections (concept_id);"))

            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS v6_best_setups (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    setup_id VARCHAR(64) UNIQUE NOT NULL,
                    user_id INTEGER NULL,
                    symbol VARCHAR(32) NOT NULL,
                    timeframe VARCHAR(16) NOT NULL,
                    direction VARCHAR(24) NOT NULL,
                    regime VARCHAR(40) NOT NULL,
                    strategy_id VARCHAR(64) NULL,
                    strategy_name VARCHAR(128) NULL,
                    quality_score INTEGER NOT NULL DEFAULT 50,
                    quality_classification VARCHAR(32) NOT NULL DEFAULT 'WATCHLIST',
                    entry_type VARCHAR(24) DEFAULT 'MARKET',
                    entry_price REAL NULL,
                    stop_loss REAL NULL,
                    stop_distance REAL NULL,
                    invalidation_reason TEXT NULL,
                    tp1 REAL NULL,
                    tp1_r REAL NULL,
                    tp2 REAL NULL,
                    tp2_r REAL NULL,
                    tp3 REAL NULL,
                    tp3_r REAL NULL,
                    risk_reward_ratio VARCHAR(20) NULL,
                    trade_plan_json TEXT NULL,
                    quality_score_json TEXT NULL,
                    mtf_status_json TEXT NULL,
                    ai_review_json TEXT NULL,
                    risk_manager_json TEXT NULL,
                    why_this_setup TEXT NULL,
                    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
                );
            """))
            conn.execute(text("CREATE INDEX IF NOT EXISTS ix_v6_best_setups_setup_id ON v6_best_setups (setup_id);"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS ix_v6_best_setups_symbol ON v6_best_setups (symbol);"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS ix_v6_best_setups_direction ON v6_best_setups (direction);"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS ix_v6_best_setups_created_at ON v6_best_setups (created_at);"))

    logger.info("V6 Technical Intelligence migration applied successfully.")

