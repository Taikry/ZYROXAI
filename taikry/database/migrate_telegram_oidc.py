"""
Migration 0013: Add telegram_user_id column to users table for Telegram Login OIDC.
Supports both SQLite and PostgreSQL idempotently.
"""

import logging
from sqlalchemy import text, inspect

logger = logging.getLogger("taikry.database.migrate_telegram_oidc")


def run_migration(engine=None) -> None:
    from taikry.database.session import engine as default_engine

    target_engine = engine or default_engine
    inspector = inspect(target_engine)
    
    # Check if 'users' table exists
    tables = inspector.get_table_names()
    if "users" not in tables:
        logger.info("Users table not yet created; skipping column addition.")
        return

    columns = [col["name"] for col in inspector.get_columns("users")]
    with target_engine.begin() as connection:
        if "telegram_user_id" not in columns:
            dialect = target_engine.dialect.name
            if dialect == "sqlite":
                connection.execute(text("ALTER TABLE users ADD COLUMN telegram_user_id VARCHAR(64)"))
            else:
                connection.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS telegram_user_id VARCHAR(64)"))
            logger.info("Added telegram_user_id column to users table.")

        # Create unique index if not existing
        dialect = target_engine.dialect.name
        if dialect == "sqlite":
            connection.execute(text(
                "CREATE UNIQUE INDEX IF NOT EXISTS ix_users_telegram_user_id ON users (telegram_user_id) WHERE telegram_user_id IS NOT NULL"
            ))
        else:
            connection.execute(text(
                "CREATE UNIQUE INDEX IF NOT EXISTS ix_users_telegram_user_id ON users (telegram_user_id) WHERE telegram_user_id IS NOT NULL"
            ))
    logger.info("Telegram Login OIDC database migration completed successfully.")
