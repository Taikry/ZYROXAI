"""
Migration 0015: Add onboarding_completed, onboarding_step, onboarding_dismissed, and dashboard_preferences columns to users table.
Supports both SQLite and PostgreSQL idempotently.
"""
import logging
from sqlalchemy import text, inspect
from taikry.database.models import Base

logger = logging.getLogger("taikry.database.migrate_v62_onboarding")


def run_migration(engine=None) -> None:
    from taikry.database.session import engine as default_engine

    target_engine = engine or default_engine
    Base.metadata.create_all(bind=target_engine)
    inspector = inspect(target_engine)

    tables = inspector.get_table_names()
    if "users" not in tables:
        return

    columns = [col["name"] for col in inspector.get_columns("users")]
    dialect = target_engine.dialect.name

    with target_engine.begin() as connection:
        if "onboarding_completed" not in columns:
            if dialect == "sqlite":
                connection.execute(text("ALTER TABLE users ADD COLUMN onboarding_completed BOOLEAN NOT NULL DEFAULT 0"))
            else:
                connection.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS onboarding_completed BOOLEAN NOT NULL DEFAULT FALSE"))
            logger.info("Added onboarding_completed column to users table.")

        if "onboarding_step" not in columns:
            if dialect == "sqlite":
                connection.execute(text("ALTER TABLE users ADD COLUMN onboarding_step INTEGER NOT NULL DEFAULT 1"))
            else:
                connection.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS onboarding_step INTEGER NOT NULL DEFAULT 1"))
            logger.info("Added onboarding_step column to users table.")

        if "onboarding_dismissed" not in columns:
            if dialect == "sqlite":
                connection.execute(text("ALTER TABLE users ADD COLUMN onboarding_dismissed BOOLEAN NOT NULL DEFAULT 0"))
            else:
                connection.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS onboarding_dismissed BOOLEAN NOT NULL DEFAULT FALSE"))
            logger.info("Added onboarding_dismissed column to users table.")

        if "tutorial_version" not in columns:
            if dialect == "sqlite":
                connection.execute(text("ALTER TABLE users ADD COLUMN tutorial_version VARCHAR(20) DEFAULT 'v6.2.1'"))
            else:
                connection.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS tutorial_version VARCHAR(20) DEFAULT 'v6.2.1'"))
            logger.info("Added tutorial_version column to users table.")

        if "tutorial_last_seen_at" not in columns:
            if dialect == "sqlite":
                connection.execute(text("ALTER TABLE users ADD COLUMN tutorial_last_seen_at DATETIME"))
            else:
                connection.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS tutorial_last_seen_at TIMESTAMP WITH TIME ZONE"))
            logger.info("Added tutorial_last_seen_at column to users table.")

        if "dashboard_preferences" not in columns:
            if dialect == "sqlite":
                connection.execute(text("ALTER TABLE users ADD COLUMN dashboard_preferences TEXT DEFAULT '{}'"))
            else:
                connection.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS dashboard_preferences JSON DEFAULT '{}'"))
            logger.info("Added dashboard_preferences column to users table.")

    logger.info("V6.2 Onboarding database migration completed successfully.")
