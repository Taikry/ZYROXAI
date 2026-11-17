"""
Migration 0014: Add google_user_id and phone_number columns to users table and create phone_otp_challenges.
Supports both SQLite and PostgreSQL idempotently.
"""
import logging
from sqlalchemy import text, inspect
from taikry.database.models import Base

logger = logging.getLogger("taikry.database.migrate_v61_auth")


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
        if "google_user_id" not in columns:
            if dialect == "sqlite":
                connection.execute(text("ALTER TABLE users ADD COLUMN google_user_id VARCHAR(64)"))
            else:
                connection.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS google_user_id VARCHAR(64)"))
            logger.info("Added google_user_id column to users table.")

        if "phone_number" not in columns:
            if dialect == "sqlite":
                connection.execute(text("ALTER TABLE users ADD COLUMN phone_number VARCHAR(32)"))
            else:
                connection.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS phone_number VARCHAR(32)"))
            logger.info("Added phone_number column to users table.")

        # Partial unique indexes for non-null values
        if dialect in ("sqlite", "postgresql"):
            try:
                connection.execute(text(
                    "CREATE UNIQUE INDEX IF NOT EXISTS ix_users_google_user_id ON users (google_user_id) WHERE google_user_id IS NOT NULL"
                ))
            except Exception as e:
                logger.debug("google_user_id index note: %s", e)

            try:
                connection.execute(text(
                    "CREATE UNIQUE INDEX IF NOT EXISTS ix_users_phone_number ON users (phone_number) WHERE phone_number IS NOT NULL"
                ))
            except Exception as e:
                logger.debug("phone_number index note: %s", e)

    logger.info("V6.1 Auth database migration completed successfully.")
