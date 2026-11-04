# ZYROX AI — Incident Response & Rollback Procedures

## 1. Quick Emergency Controls

### 1.1 Pause Telegram Signal Dispatching
To stop all automated Telegram messages immediately without taking the web app or APIs offline:
1. Open Render Dashboard -> `zyroxai` -> **Environment**.
2. Set `TELEGRAM_ENABLED=false`.
3. Save changes. Render triggers a rolling restart within seconds.
4. Signal analysis, web cockpits, and user queries remain fully operational.

### 1.2 Silence Lifecycle Event Messages
To allow daily trade setups to be sent while silencing TP/SL/BE notifications:
1. Verify `TELEGRAM_SEND_LIFECYCLE_EVENTS=false` in the Render environment.
2. Restart the service.

---

## 2. Render Code Rollback
If a newly deployed build exhibits production instability:
1. Navigate to the **Deploys** tab in the Render Dashboard.
2. Locate the previous stable deployment commit SHA.
3. Click the `...` menu and select **Rollback to this deploy**.
4. Render initiates an immediate rolling redeployment of the previous artifact.

---

## 3. Database Safety & Migration Rollbacks
All database migrations implemented in `taikry/database/versioned_migrations.py` are strictly non-destructive:
- Added columns (such as `take_profit_3` on `paper_trades`) are nullable with optional default values.
- Table additions (such as `aba_payway_transactions`, `vip_subscriptions`, `agent_learning_weights`) do not interfere with earlier application versions.
- **Do NOT drop tables or columns** during a rollback, as they may contain delivery logs or audit records created during operation.
- The tracking table `system_versioned_migrations` maintains state across restarts and will safely skip already-applied migrations upon redeployment.

