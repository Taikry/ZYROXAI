"""Ensure one saved risk profile per authenticated user."""

import logging
from sqlalchemy import text

logger = logging.getLogger("taikry.database.migrate_user_risk_settings_unique")


def run_migration(engine=None) -> None:
    from taikry.database.session import engine as default_engine

    target_engine = engine or default_engine
    with target_engine.begin() as connection:
        # Keep the most recently updated row if an earlier build created duplicates.
        connection.execute(text("""
            DELETE FROM user_risk_settings
            WHERE user_id IS NOT NULL
              AND id NOT IN (
                  SELECT id FROM (
                      SELECT id, ROW_NUMBER() OVER (
                          PARTITION BY user_id
                          ORDER BY updated_at DESC, id DESC
                      ) AS row_number
                      FROM user_risk_settings
                      WHERE user_id IS NOT NULL
                  ) ranked
                  WHERE row_number = 1
              )
        """))
        connection.execute(text(
            "CREATE UNIQUE INDEX IF NOT EXISTS uq_user_risk_settings_user_id "
            "ON user_risk_settings (user_id) WHERE user_id IS NOT NULL"
        ))
    logger.info("Per-user risk settings uniqueness migration applied.")
