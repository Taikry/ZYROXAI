"""
Migration script: 0012_v7_saas_multi_tenant_rbac
==================================================
Creates multi-tenant RBAC tables:
- roles: Distinct system and custom role definitions
- permissions: Granular operational authorization primitives
- user_roles: User-to-role assignments
- role_permissions: Role-to-permission grants
- system_settings: Super Admin runtime configuration store
- feature_flags: Progressive rollout and feature access gates

Supports both SQLite (local development) and PostgreSQL (production).
Safely backfills existing users without altering existing data or breaking sessions.
"""
import os
import json
import logging
from sqlalchemy import text

logger = logging.getLogger("taikry.database.migrate_v7_rbac")

DEFAULT_PERMISSIONS = [
    ("users.read", "users", "View user accounts, profiles, and basic statistics"),
    ("users.manage", "users", "Update user statuses, plan overrides, and account lifecycle"),
    ("subscriptions.read", "subscriptions", "Inspect user subscriptions, trial durations, and quotas"),
    ("subscriptions.manage", "subscriptions", "Modify subscription plans, grant extensions, and manage pricing"),
    ("payments.read", "payments", "View payment transactions, invoice history, and reconciliation logs"),
    ("payments.manage", "payments", "Process manual payment verifications and refunds"),
    ("signals.read", "signals", "Inspect dispatched and active trade signals"),
    ("signals.manage", "signals", "Manage signal limits, deduplication rules, and broadcast triggers"),
    ("analysis.use", "analysis", "Run standard technical analysis and basic concept detection"),
    ("analysis.deep_research", "analysis", "Run V6 Best Setup, multi-agent fleet reviews, and deep research"),
    ("telegram.manage", "telegram", "Configure Telegram bot linkage, broadcasts, and channel delivery"),
    ("ai.providers.manage", "ai", "Manage AI provider models, routing policies, and API keys"),
    ("system.settings.manage", "system", "Configure global platform settings, maintenance modes, and security policies"),
    ("admins.manage", "system", "Create, promote, demote, or suspend platform administrators"),
    ("audit_logs.read", "system", "Access full security audit trail and system operational logs"),
]

DEFAULT_ROLES = [
    ("super_admin", "Super Administrator", "Full unrestricted access to all platform systems, secret management, and administrative governance.", True),
    ("admin", "Platform Administrator", "Operational administration for user support, subscriptions, signals, and system observability.", True),
    ("premium_user", "Premium Subscriber", "Full access to advanced technical intelligence, Best Setup, multi-agent fleet reviews, and Telegram alerts.", True),
    ("user", "Standard Trader", "Standard access to basic analysis, paper trading, and 14-day free trial features.", True),
]

ROLE_PERMISSIONS_MAP = {
    "super_admin": [p[0] for p in DEFAULT_PERMISSIONS],
    "admin": [
        "users.read", "users.manage",
        "subscriptions.read", "subscriptions.manage",
        "payments.read",
        "signals.read", "signals.manage",
        "analysis.use", "analysis.deep_research",
        "telegram.manage",
        "audit_logs.read"
    ],
    "premium_user": [
        "analysis.use", "analysis.deep_research",
        "signals.read",
        "subscriptions.read"
    ],
    "user": [
        "analysis.use",
        "subscriptions.read"
    ]
}


def run_migration(engine=None) -> None:
    from taikry.database.session import engine as default_engine
    target_engine = engine or default_engine

    dialect = target_engine.dialect.name
    logger.info(f"Running V7 Multi-Tenant RBAC migration on dialect: {dialect}")

    with target_engine.begin() as conn:
        if dialect == "postgresql":
            # 1. roles
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS roles (
                    id VARCHAR(50) PRIMARY KEY,
                    name VARCHAR(100) NOT NULL,
                    description VARCHAR(255) NULL,
                    is_system_role BOOLEAN NOT NULL DEFAULT TRUE,
                    created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT NOW()
                )
            """))
            conn.execute(text("CREATE INDEX IF NOT EXISTS ix_roles_is_system ON roles (is_system_role)"))

            # 2. permissions
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS permissions (
                    id VARCHAR(100) PRIMARY KEY,
                    category VARCHAR(50) NOT NULL,
                    description VARCHAR(255) NULL,
                    created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT NOW()
                )
            """))
            conn.execute(text("CREATE INDEX IF NOT EXISTS ix_permissions_category ON permissions (category)"))

            # 3. user_roles
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS user_roles (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                    role_id VARCHAR(50) NOT NULL REFERENCES roles(id) ON DELETE CASCADE,
                    granted_by INTEGER NULL,
                    granted_at TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT NOW(),
                    CONSTRAINT uq_user_role UNIQUE (user_id, role_id)
                )
            """))
            conn.execute(text("CREATE INDEX IF NOT EXISTS ix_user_roles_user_id ON user_roles (user_id)"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS ix_user_roles_role_id ON user_roles (role_id)"))

            # 4. role_permissions
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS role_permissions (
                    id SERIAL PRIMARY KEY,
                    role_id VARCHAR(50) NOT NULL REFERENCES roles(id) ON DELETE CASCADE,
                    permission_id VARCHAR(100) NOT NULL REFERENCES permissions(id) ON DELETE CASCADE,
                    granted_at TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT NOW(),
                    CONSTRAINT uq_role_permission UNIQUE (role_id, permission_id)
                )
            """))
            conn.execute(text("CREATE INDEX IF NOT EXISTS ix_role_permissions_role ON role_permissions (role_id)"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS ix_role_permissions_perm ON role_permissions (permission_id)"))

            # 5. system_settings
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS system_settings (
                    key VARCHAR(100) PRIMARY KEY,
                    value TEXT NULL,
                    is_secret BOOLEAN NOT NULL DEFAULT FALSE,
                    description VARCHAR(255) NULL,
                    updated_by INTEGER NULL,
                    updated_at TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT NOW()
                )
            """))

            # 6. feature_flags
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS feature_flags (
                    key VARCHAR(100) PRIMARY KEY,
                    enabled BOOLEAN NOT NULL DEFAULT FALSE,
                    description VARCHAR(255) NULL,
                    allowed_roles JSONB NULL,
                    rollout_percentage INTEGER NOT NULL DEFAULT 100,
                    updated_by INTEGER NULL,
                    updated_at TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT NOW()
                )
            """))
        else:
            # SQLite fallback
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS roles (
                    id VARCHAR(50) PRIMARY KEY,
                    name VARCHAR(100) NOT NULL,
                    description VARCHAR(255) NULL,
                    is_system_role BOOLEAN NOT NULL DEFAULT 1,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """))
            conn.execute(text("CREATE INDEX IF NOT EXISTS ix_roles_is_system ON roles (is_system_role)"))

            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS permissions (
                    id VARCHAR(100) PRIMARY KEY,
                    category VARCHAR(50) NOT NULL,
                    description VARCHAR(255) NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """))
            conn.execute(text("CREATE INDEX IF NOT EXISTS ix_permissions_category ON permissions (category)"))

            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS user_roles (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                    role_id VARCHAR(50) NOT NULL REFERENCES roles(id) ON DELETE CASCADE,
                    granted_by INTEGER NULL,
                    granted_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(user_id, role_id)
                )
            """))
            conn.execute(text("CREATE INDEX IF NOT EXISTS ix_user_roles_user_id ON user_roles (user_id)"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS ix_user_roles_role_id ON user_roles (role_id)"))

            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS role_permissions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    role_id VARCHAR(50) NOT NULL REFERENCES roles(id) ON DELETE CASCADE,
                    permission_id VARCHAR(100) NOT NULL REFERENCES permissions(id) ON DELETE CASCADE,
                    granted_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(role_id, permission_id)
                )
            """))
            conn.execute(text("CREATE INDEX IF NOT EXISTS ix_role_permissions_role ON role_permissions (role_id)"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS ix_role_permissions_perm ON role_permissions (permission_id)"))

            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS system_settings (
                    key VARCHAR(100) PRIMARY KEY,
                    value TEXT NULL,
                    is_secret BOOLEAN NOT NULL DEFAULT 0,
                    description VARCHAR(255) NULL,
                    updated_by INTEGER NULL,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """))

            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS feature_flags (
                    key VARCHAR(100) PRIMARY KEY,
                    enabled BOOLEAN NOT NULL DEFAULT 0,
                    description VARCHAR(255) NULL,
                    allowed_roles TEXT NULL,
                    rollout_percentage INTEGER NOT NULL DEFAULT 100,
                    updated_by INTEGER NULL,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """))

        # Seed Default Roles
        for role_id, name, desc, is_sys in DEFAULT_ROLES:
            existing_role = conn.execute(text("SELECT id FROM roles WHERE id = :rid"), {"rid": role_id}).fetchone()
            if not existing_role:
                conn.execute(text("""
                    INSERT INTO roles (id, name, description, is_system_role, created_at)
                    VALUES (:id, :name, :desc, :is_sys, CURRENT_TIMESTAMP)
                """), {"id": role_id, "name": name, "desc": desc, "is_sys": is_sys})

        # Seed Default Permissions
        for perm_id, cat, desc in DEFAULT_PERMISSIONS:
            existing_p = conn.execute(text("SELECT id FROM permissions WHERE id = :pid"), {"pid": perm_id}).fetchone()
            if not existing_p:
                conn.execute(text("""
                    INSERT INTO permissions (id, category, description, created_at)
                    VALUES (:id, :cat, :desc, CURRENT_TIMESTAMP)
                """), {"id": perm_id, "cat": cat, "desc": desc})

        # Seed Role Permissions mappings
        for role_id, perm_list in ROLE_PERMISSIONS_MAP.items():
            for perm_id in perm_list:
                existing_rp = conn.execute(text("""
                    SELECT id FROM role_permissions WHERE role_id = :rid AND permission_id = :pid
                """), {"rid": role_id, "pid": perm_id}).fetchone()
                if not existing_rp:
                    conn.execute(text("""
                        INSERT INTO role_permissions (role_id, permission_id, granted_at)
                        VALUES (:rid, :pid, CURRENT_TIMESTAMP)
                    """), {"rid": role_id, "pid": perm_id})

        # Seed initial feature flags
        initial_flags = [
            ("v6_technical_intelligence", True, "Enable V6 deterministic concept and regime engine", ["super_admin", "admin", "premium_user", "user"]),
            ("deep_research_pre_news", True, "Enable 11-agent deep pre-news research", ["super_admin", "admin", "premium_user"]),
            ("telegram_signal_broadcast", True, "Enable automated real-time Telegram signal dispatching", ["super_admin", "admin", "premium_user"]),
            ("ai_research_chat", True, "Enable bilingual AI research chat assistant", ["super_admin", "admin", "premium_user", "user"])
        ]
        for f_key, f_enabled, f_desc, f_roles in initial_flags:
            existing_f = conn.execute(text("SELECT key FROM feature_flags WHERE key = :k"), {"k": f_key}).fetchone()
            if not existing_f:
                roles_val = json.dumps(f_roles) if dialect != "postgresql" else f_roles
                conn.execute(text("""
                    INSERT INTO feature_flags (key, enabled, description, allowed_roles, rollout_percentage, updated_at)
                    VALUES (:k, :en, :desc, :roles, 100, CURRENT_TIMESTAMP)
                """), {"k": f_key, "en": f_enabled, "desc": f_desc, "roles": roles_val if dialect == "postgresql" else json.dumps(f_roles)})

        # Backfill existing users into user_roles table based on User.role
        super_admin_email = os.getenv("SAAS_ADMIN_EMAIL", "").strip().lower()
        users_rows = conn.execute(text("SELECT id, email, role FROM users")).fetchall()

        for u_id, u_email, u_role in users_rows:
            target_role = "user"
            u_role_clean = str(u_role or "").strip().lower()

            if super_admin_email and str(u_email).strip().lower() == super_admin_email:
                target_role = "super_admin"
                conn.execute(text("UPDATE users SET role = 'super_admin' WHERE id = :uid"), {"uid": u_id})
            elif u_role_clean in ("admin", "super_admin"):
                target_role = "admin"
                conn.execute(text("UPDATE users SET role = 'admin' WHERE id = :uid"), {"uid": u_id})
            elif u_role_clean == "premium_user":
                target_role = "premium_user"
            else:
                target_role = "user"
                conn.execute(text("UPDATE users SET role = 'user' WHERE id = :uid"), {"uid": u_id})

            # Check user_roles mapping
            ur_exists = conn.execute(text("""
                SELECT id FROM user_roles WHERE user_id = :uid AND role_id = :rid
            """), {"uid": u_id, "rid": target_role}).fetchone()
            if not ur_exists:
                conn.execute(text("""
                    INSERT INTO user_roles (user_id, role_id, granted_at) VALUES (:uid, :rid, CURRENT_TIMESTAMP)
                """), {"uid": u_id, "rid": target_role})

    logger.info("V7 Multi-Tenant RBAC migration successfully completed.")


if __name__ == "__main__":
    run_migration()
