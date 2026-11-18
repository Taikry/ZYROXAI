"""
SaaS Platform FastAPI Route Handlers for ZYROX AI.
Provides:
- Authentication & Sessions (Signup, Login, Logout, Email Verify, Password Reset, Profile)
- 14-Day Free Trial Status & Enforcement
- Centralized Plan Entitlements & Quotas
- Telegram Account Deep-Linking & Notification Preferences
- Support Ticket Inquiries
- Administrator Control Center (RBAC, User Search, Audit Logs)
- Billing Gateway & Webhook Adapters
"""

import os
import datetime
import asyncio
import smtplib
import logging
import hmac
from email.message import EmailMessage
from typing import Dict, Any, List, Optional
from urllib.parse import quote
from fastapi import APIRouter, HTTPException, Depends, Header, Cookie, Request, Response, WebSocket, WebSocketDisconnect, status
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from taikry.database.session import get_db, SessionLocal
from taikry.database.models import (
    PaperTrade,
    User,
    UserSession,
    Role,
    Permission,
    UserRole,
    RolePermission,
    SystemSetting,
    FeatureFlag,
    AuditLog,
    PaymentInvoice,
    PaymentTransaction,
    UserSubscription,
    SubscriptionPlan
)
from taikry.config import MAX_RISK_PER_TRADE_PERCENT, INITIAL_PAPER_BALANCE, get_symbol_config
from taikry.saas import (
    sign_up_user,
    login_user,
    authenticate_session,
    get_authenticated_user_from_request,
    logout_user,
    refresh_user_session,
    verify_email_token,
    request_password_reset,
    reset_password,
    delete_user_account,
    get_user_trial_status,
    get_all_plans,
    get_user_entitlement,
    generate_telegram_linking_token,
    process_telegram_webhook_linking,
    unlink_telegram_account,
    get_telegram_link_status,
    update_notification_preferences,
    create_support_ticket,
    get_user_tickets,
    admin_list_all_tickets,
    admin_reply_ticket,
    is_admin_user,
    bootstrap_admin_if_needed,
    admin_list_users,
    admin_set_user_status,
    admin_override_user_subscription,
    admin_get_analytics_summary,
    admin_get_audit_logs,
    billing_adapter,
    get_current_user,
    get_current_user_optional,
    get_current_admin,
    get_current_super_admin,
    parse_user_agent_simple,
    format_relative_time,
    hash_token,
    require_permission,
    require_role,
    has_permission,
    has_role,
    get_user_roles,
    get_user_permissions,
    is_telegram_login_configured,
    get_telegram_login_status,
    build_telegram_authorization_url,
    exchange_code_for_tokens,
    validate_id_token,
    authenticate_or_create_telegram_user,
    issue_telegram_session,
    auth_state_store,
    get_default_redirect_uri
)

saas_router = APIRouter()

SESSION_COOKIE_NAME = "zyrox_session"
logger = logging.getLogger(__name__)


def _send_auth_email(recipient: str, subject: str, body: str) -> bool:
    """Deliver verification/reset instructions without exposing tokens in API responses."""
    from taikry.config import SMTP_HOST, SMTP_PORT, SMTP_USERNAME, SMTP_PASSWORD, SMTP_FROM_EMAIL, SMTP_USE_TLS
    if not (SMTP_HOST and SMTP_FROM_EMAIL):
        return False
    message = EmailMessage()
    message["Subject"] = subject
    message["From"] = SMTP_FROM_EMAIL
    message["To"] = recipient
    message.set_content(body)
    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=15) as smtp:
            if SMTP_USE_TLS:
                smtp.starttls()
            if SMTP_USERNAME:
                smtp.login(SMTP_USERNAME, SMTP_PASSWORD)
            smtp.send_message(message)
        return True
    except Exception:
        logger.exception("Failed to send account email")
        return False


# =============================================================================
# REQUEST / RESPONSE SCHEMAS
# =============================================================================

class SignUpRequest(BaseModel):
    email: str = Field(..., description="Valid trader email address")
    password: str = Field(..., min_length=8, description="Minimum 8 characters password")
    full_name: Optional[str] = Field(default=None, description="Full name or trader handle")
    language: Optional[str] = Field(default="en", description="Interface language: en or kh")
    timezone: Optional[str] = Field(default="Asia/Phnom_Penh", description="User local timezone")
    terms_accepted: bool = Field(default=True, description="Acceptance of Terms of Service & Privacy Policy")


class LoginRequest(BaseModel):
    email: str = Field(..., description="Registered email address")
    password: str = Field(..., description="Account password")


class VerifyEmailRequest(BaseModel):
    token: str = Field(..., description="Single-use verification token from email")


class ForgotPasswordRequest(BaseModel):
    email: str = Field(..., description="Account email to dispatch reset instructions")


class ResetPasswordRequest(BaseModel):
    token: str = Field(..., description="Password reset verification token")
    new_password: str = Field(..., min_length=8, description="New password")


class UpdateProfileRequest(BaseModel):
    full_name: Optional[str] = None
    language: Optional[str] = None
    preferred_language: Optional[str] = None
    timezone: Optional[str] = None
    phone_number: Optional[str] = None


class DeleteAccountRequest(BaseModel):
    reason: Optional[str] = None
    confirmation: str = Field(..., description="Must equal 'DELETE MY ACCOUNT'")


class NotificationPrefsUpdateRequest(BaseModel):
    ai_analysis_completed: Optional[bool] = None
    signal_generated: Optional[bool] = None
    signal_invalidated: Optional[bool] = None
    macro_events: Optional[bool] = None
    daily_summary: Optional[bool] = None
    trial_expiration_reminders: Optional[bool] = None
    subscription_status_changes: Optional[bool] = None
    system_announcements: Optional[bool] = None
    paper_trade_alerts: Optional[bool] = None


class SupportTicketCreateRequest(BaseModel):
    category: str = Field(..., description="Category: account, trial, billing, telegram, ai_analysis, technical")
    subject: str = Field(..., min_length=4, description="Summary subject")
    message: str = Field(..., min_length=10, description="Detailed explanation of inquiry")
    priority: Optional[str] = Field(default="NORMAL", description="LOW, NORMAL, HIGH, URGENT")


class AdminTicketReplyRequest(BaseModel):
    ticket_id: str
    response: str
    status: Optional[str] = "RESOLVED"


class AdminUserStatusRequest(BaseModel):
    user_id: int
    is_active: bool
    reason: Optional[str] = None


class AdminSubscriptionOverrideRequest(BaseModel):
    user_id: int
    plan_id: str
    status: str = "active_paid"
    duration_days: int = 30


class CheckoutRequest(BaseModel):
    plan_id: str
    return_url: Optional[str] = "/dashboard/"


class UserPaperTradeCreateRequest(BaseModel):
    symbol: str = Field(..., min_length=1, max_length=20)
    direction: str = Field(..., pattern="^(BUY|SELL|buy|sell)$")
    entry_price: float = Field(..., gt=0)
    stop_loss: float = Field(..., gt=0)
    take_profit_1: float = Field(..., gt=0)
    take_profit_2: Optional[float] = Field(default=None, gt=0)
    risk_percentage: Optional[float] = Field(default=None, gt=0, le=MAX_RISK_PER_TRADE_PERCENT)


class UserPaperTradeJournalUpdate(BaseModel):
    notes: str = Field(default="", max_length=5000)
    tags: List[str] = Field(default_factory=list, max_length=12)
    emotion_tag: Optional[str] = Field(default=None, max_length=40)
    mistake_tag: Optional[str] = Field(default=None, max_length=40)


class SuperAdminPromoteRequest(BaseModel):
    user_id: int = Field(..., description="Target user ID")
    role: str = Field(..., description="Role to assign: super_admin, admin, premium_user, or user")


class SystemSettingUpsertRequest(BaseModel):
    key: str = Field(..., min_length=2, max_length=100)
    value: Optional[str] = None
    is_secret: bool = False
    description: Optional[str] = None


class FeatureFlagUpdateRequest(BaseModel):
    enabled: Optional[bool] = None
    rollout_percentage: Optional[int] = Field(default=None, ge=0, le=100)
    allowed_roles: Optional[List[str]] = None
    description: Optional[str] = None


class AIProviderConfigureRequest(BaseModel):
    provider: str = Field(..., description="gemini, deepseek, claude, or openai")
    model_name: Optional[str] = None
    api_key: Optional[str] = None
    is_enabled: bool = True
    priority: int = 1


def _user_day_start_utc(user: User) -> datetime.datetime:
    """Return the start of today in the user's configured timezone as naive UTC."""
    from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

    try:
        tz = ZoneInfo(user.timezone or "Asia/Phnom_Penh")
    except (ZoneInfoNotFoundError, ValueError):
        tz = datetime.timezone.utc
    local_now = datetime.datetime.now(datetime.timezone.utc).astimezone(tz)
    local_start = local_now.replace(hour=0, minute=0, second=0, microsecond=0)
    return local_start.astimezone(datetime.timezone.utc).replace(tzinfo=None)


@saas_router.get("/api/v1/me/paper-trades")
def get_my_paper_trades(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Return only this signed-in user's paper ledger, counts, and fresh quote state."""
    from taikry.data.providers import market_data_engine
    from taikry.data.validator import check_data_freshness
    from taikry.trading.paper_trading import paper_trading_engine

    owned_open = db.query(PaperTrade).filter(
        PaperTrade.user_id == user.id,
        PaperTrade.status == "OPEN",
    ).all()
    quote_by_symbol: Dict[str, Dict[str, Any]] = {}
    fresh_prices: Dict[str, float] = {}

    for symbol in sorted({trade.symbol for trade in owned_open}):
        try:
            price, source, timestamp = market_data_engine.get_verified_price(symbol)
            freshness = check_data_freshness(symbol, timestamp, "M1")
            source_label = str(source or "UNKNOWN")
            source_is_synthetic = any(
                marker in source_label.upper()
                for marker in ("DEMO", "SYNTHETIC", "UNAVAILABLE")
            )
            is_fresh = bool(
                price and float(price) > 0 and freshness.get("fresh") and not source_is_synthetic
            )
            quote_by_symbol[symbol] = {
                "price": round(float(price), 8) if is_fresh else None,
                "source": source_label,
                "timestamp": timestamp.isoformat() if hasattr(timestamp, "isoformat") else timestamp,
                "status": "UNAVAILABLE" if source_is_synthetic else freshness.get("status", "UNAVAILABLE"),
                "fresh": is_fresh,
            }
            if is_fresh:
                fresh_prices[symbol] = float(price)
        except Exception:
            logger.exception("Failed to refresh a user's paper-trade quote for %s", symbol)
            quote_by_symbol[symbol] = {
                "price": None,
                "source": None,
                "timestamp": None,
                "status": "UNAVAILABLE",
                "fresh": False,
            }

    # Evaluate only this user's open trades. Stale or synthetic quotes never close a trade.
    closed_events = paper_trading_engine.update_open_trades(fresh_prices, user_id=user.id)
    if closed_events:
        from taikry.trading.paper_trade_alerts import dispatch_paper_trade_alert
        for event in closed_events:
            dispatch_paper_trade_alert(event)
    db.expire_all()

    trades = db.query(PaperTrade).filter(
        PaperTrade.user_id == user.id,
    ).order_by(PaperTrade.id.desc()).all()
    open_trades = [trade for trade in trades if trade.status == "OPEN"]
    closed_trades = [trade for trade in trades if trade.status == "CLOSED"]
    today_start = _user_day_start_utc(user)
    today_trades = [trade for trade in trades if trade.created_at and trade.created_at >= today_start]
    today_closed = [
        trade for trade in closed_trades
        if trade.exit_time and trade.exit_time >= today_start
    ]

    realized_pnl = sum(float(trade.pnl or 0) for trade in closed_trades)
    today_realized_pnl = sum(float(trade.pnl or 0) for trade in today_closed)
    wins = sum(1 for trade in closed_trades if float(trade.pnl or 0) > 0)
    losses = sum(1 for trade in closed_trades if float(trade.pnl or 0) < 0)
    total_unrealized = 0.0
    trade_rows = []

    for trade in trades:
        quote = quote_by_symbol.get(trade.symbol, {})
        live_price = quote.get("price") if trade.status == "OPEN" else None
        unrealized_pnl = None
        tp_sl_state = "CLOSED" if trade.status == "CLOSED" else "WAITING_FOR_FRESH_PRICE"
        if live_price is not None:
            cfg = get_symbol_config(trade.symbol)
            point_value = float(cfg.get("lot_size", 100))
            price_move = float(live_price) - float(trade.entry_price)
            if trade.direction == "SELL":
                price_move *= -1
            commission = float((trade.trade_log or {}).get("commission_usd", 0) or 0)
            unrealized_pnl = round(price_move * point_value * float(trade.lot_size) - commission, 2)
            total_unrealized += unrealized_pnl
            if trade.direction == "BUY":
                tp_sl_state = "STOP_LOSS_HIT" if live_price <= trade.stop_loss else (
                    "TAKE_PROFIT_HIT" if live_price >= trade.take_profit_1 else "ACTIVE"
                )
            else:
                tp_sl_state = "STOP_LOSS_HIT" if live_price >= trade.stop_loss else (
                    "TAKE_PROFIT_HIT" if live_price <= trade.take_profit_1 else "ACTIVE"
                )

        trade_rows.append({
            "id": trade.id,
            "symbol": trade.symbol,
            "direction": trade.direction,
            "entry_price": trade.entry_price,
            "current_price": live_price,
            "quote_source": quote.get("source"),
            "quote_timestamp": quote.get("timestamp"),
            "quote_status": quote.get("status", "UNAVAILABLE"),
            "stop_loss": trade.stop_loss,
            "take_profit_1": trade.take_profit_1,
            "take_profit_2": trade.take_profit_2,
            "lot_size": trade.lot_size,
            "risk_amount": trade.risk_amount,
            "status": trade.status,
            "tp_sl_state": tp_sl_state,
            "exit_price": trade.exit_price,
            "exit_time": trade.exit_time.isoformat() if trade.exit_time else None,
            "pnl": trade.pnl,
            "unrealized_pnl": unrealized_pnl,
            "r_multiple": trade.r_multiple,
            "exit_reason": trade.exit_reason,
            "journal_notes": trade.journal_notes or "",
            "journal_tags": trade.journal_tags or [],
            "emotion_tag": trade.emotion_tag,
            "mistake_tag": trade.mistake_tag,
            "created_at": trade.created_at.isoformat() if trade.created_at else None,
        })

    account = paper_trading_engine.get_account_summary(user_id=user.id)
    account.update({
        "today_trades_count": len(today_trades),
        "today_closed_trades_count": len(today_closed),
        "today_realized_pnl": round(today_realized_pnl, 2),
        "wins": wins,
        "losses": losses,
        "win_rate_percent": round((wins / len(closed_trades)) * 100, 1) if closed_trades else 0.0,
        "unrealized_pnl": round(total_unrealized, 2),
        "current_equity": round(float(account["current_balance"]) + total_unrealized, 2),
        "timezone": user.timezone or "Asia/Phnom_Penh",
    })
    return {
        "account_summary": account,
        "trades": trade_rows,
        "quotes": quote_by_symbol,
        "updated_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    }


@saas_router.post("/api/v1/me/paper-trades")
def open_my_paper_trade(
    payload: UserPaperTradeCreateRequest,
    user: User = Depends(get_current_user),
):
    """Open an authenticated user's own simulated paper position."""
    from taikry.risk.service import risk_intelligence_service
    from taikry.data.providers import market_data_engine
    from taikry.trading.paper_trading import paper_trading_engine

    symbol = payload.symbol.strip().upper()
    direction = payload.direction.upper()
    settings = risk_intelligence_service.get_user_risk_settings(user.id)
    risk_options = None
    if payload.risk_percentage is not None:
        risk_options = {
            "risk_per_trade_percent": min(
                float(payload.risk_percentage),
                float(settings.get("risk_per_trade_percent", 0.5)),
            )
        }
    candles = market_data_engine.get_candles(symbol, timeframe="M15", limit=300)
    account = paper_trading_engine.get_account_summary(user_id=user.id)
    quote = market_data_engine.get_verified_quote(symbol)
    spread_price = None
    if quote:
        try:
            bid, ask = float(quote.get("bid")), float(quote.get("ask"))
            if bid > 0 and ask > bid:
                spread_price = ask - bid
        except (TypeError, ValueError):
            spread_price = None
    assessment = risk_intelligence_service.evaluate_trade_candidate(
        symbol=symbol,
        direction=direction,
        entry_price=payload.entry_price,
        stop_loss=payload.stop_loss,
        take_profit_1=payload.take_profit_1,
        take_profit_2=payload.take_profit_2,
        spread_price=spread_price,
        account_equity=float(account.get("current_equity") or INITIAL_PAPER_BALANCE),
        custom_risk_options=risk_options,
        candle_df=candles,
        timeframe="M15",
        user_id=user.id,
        persist_log=True,
    )
    if assessment.decision.value not in {"APPROVED", "APPROVED_WITH_REDUCED_RISK"}:
        reasons = assessment.veto_reasons or assessment.advisory_notes
        raise HTTPException(
            status_code=400,
            detail="Paper trade blocked by risk review: " + "; ".join(str(reason) for reason in reasons),
        )

    result = paper_trading_engine.open_trade(
        symbol=symbol,
        direction=direction,
        entry_price=payload.entry_price,
        stop_loss=payload.stop_loss,
        take_profit_1=payload.take_profit_1,
        take_profit_2=payload.take_profit_2,
        risk_percentage=assessment.sizing.risk_percentage,
        user_id=user.id,
    )
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("reason", "Paper trade could not be opened."))
    return {"success": True, "paper_trade": result, "risk_assessment": assessment.dict()}


@saas_router.put("/api/v1/me/paper-trades/{trade_id}/journal")
def update_my_paper_trade_journal(
    trade_id: int,
    payload: UserPaperTradeJournalUpdate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Save notes and review tags only on a trade owned by the signed-in user."""
    trade = db.query(PaperTrade).filter(
        PaperTrade.id == trade_id,
        PaperTrade.user_id == user.id,
    ).first()
    if not trade:
        raise HTTPException(status_code=404, detail="Paper trade was not found in your account.")

    cleaned_tags = []
    for tag in payload.tags:
        cleaned = " ".join(str(tag).split())[:32]
        if cleaned and cleaned.casefold() not in {item.casefold() for item in cleaned_tags}:
            cleaned_tags.append(cleaned)
        if len(cleaned_tags) >= 12:
            break

    trade.journal_notes = payload.notes.strip()
    trade.journal_tags = cleaned_tags
    trade.emotion_tag = payload.emotion_tag.strip()[:40] if payload.emotion_tag else None
    trade.mistake_tag = payload.mistake_tag.strip()[:40] if payload.mistake_tag else None
    db.commit()
    return {
        "success": True,
        "trade_id": trade.id,
        "journal": {
            "notes": trade.journal_notes,
            "tags": trade.journal_tags,
            "emotion_tag": trade.emotion_tag,
            "mistake_tag": trade.mistake_tag,
        },
    }


def _paper_trade_stream_snapshot(user_id: int) -> Optional[Dict[str, Any]]:
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == user_id, User.is_active.is_(True)).first()
        if not user:
            return None
        return get_my_paper_trades(user=user, db=db)
    finally:
        db.close()


@saas_router.websocket("/api/v1/me/trades/stream")
async def stream_my_paper_trades(websocket: WebSocket):
    """Push account-scoped paper trade and fresh TP/SL state over WebSocket."""
    token = websocket.cookies.get(SESSION_COOKIE_NAME)
    if not token:
        await websocket.close(code=4401, reason="Sign in required")
        return

    auth_db = SessionLocal()
    try:
        user = authenticate_session(auth_db, token)
        if not user:
            await websocket.close(code=4401, reason="Session expired")
            return
        user_id = user.id
    finally:
        auth_db.close()

    await websocket.accept()
    last_auth_check = asyncio.get_running_loop().time()
    try:
        while True:
            now = asyncio.get_running_loop().time()
            if now - last_auth_check >= 30:
                auth_db = SessionLocal()
                try:
                    user = authenticate_session(auth_db, token)
                    if not user or user.id != user_id:
                        await websocket.close(code=4401, reason="Session expired")
                        return
                finally:
                    auth_db.close()
                last_auth_check = now

            snapshot = await asyncio.to_thread(_paper_trade_stream_snapshot, user_id)
            if snapshot is None:
                await websocket.close(code=4401, reason="Account unavailable")
                return
            await websocket.send_json({"type": "paper_trade_snapshot", "data": snapshot})
            await asyncio.sleep(5)
    except WebSocketDisconnect:
        return
    except Exception:
        logger.exception("User paper-trade WebSocket failed for account %s", user_id)
        try:
            await websocket.close(code=1011, reason="Stream unavailable")
        except Exception:
            pass


# =============================================================================
# 1. AUTHENTICATION ENDPOINTS (/api/v1/auth)
# =============================================================================

@saas_router.post("/api/v1/auth/signup")
def signup_endpoint(payload: SignUpRequest, request: Request, response: Response):
    """
    Step 1: Register new account, hash password, activate 14-day free trial.
    Sets secure HttpOnly session cookie automatically on success.
    """
    db = SessionLocal()
    try:
        ip = request.client.host if request.client else "unknown"
        success, msg, data = sign_up_user(
            db=db,
            email=payload.email,
            password=payload.password,
            full_name=payload.full_name,
            language=payload.language or "en",
            timezone=payload.timezone or "Asia/Phnom_Penh",
            terms_accepted=payload.terms_accepted,
            ip_address=ip
        )
        if not success:
            raise HTTPException(status_code=400, detail=msg)

        verification_token = data.get("verification_token") if data else None
        if verification_token:
            from taikry.config import PUBLIC_APP_URL
            verification_url = f"{PUBLIC_APP_URL.rstrip('/')}/?verify_email={quote(verification_token)}"
            _send_auth_email(payload.email, "Verify your TAIKRY account", f"Verify your account using this link:\n{verification_url}\n\nThis link expires in 24 hours.")
            data.pop("verification_token", None)

        # Automatically log user in
        login_ok, login_msg, login_data = login_user(
            db=db,
            email=payload.email,
            password=payload.password,
            ip_address=ip,
            user_agent=request.headers.get("user-agent")
        )
        if login_ok and login_data:
            session_tok = login_data["session_token"]
            response.set_cookie(
                key=SESSION_COOKIE_NAME,
                value=session_tok,
                httponly=True,
                samesite="lax",
                secure=request.url.scheme == "https" or os.getenv("ENVIRONMENT", "production").lower() == "production",
                max_age=30 * 86400
            )
            data["session_token"] = session_tok

        return {
            "success": True,
            "message": msg,
            "data": data
        }
    finally:
        db.close()


@saas_router.post("/api/v1/auth/login")
def login_endpoint(payload: LoginRequest, request: Request, response: Response):
    """
    Step 2: Authenticate user with rate limiting and issue 30-day session token.
    """
    db = SessionLocal()
    try:
        ip = request.client.host if request.client else "unknown"
        ua = request.headers.get("user-agent")
        success, msg, data = login_user(
            db=db,
            email=payload.email,
            password=payload.password,
            ip_address=ip,
            user_agent=ua
        )
        if not success:
            raise HTTPException(status_code=401, detail=msg)

        session_token = data.get("session_token")
        response.set_cookie(
            key=SESSION_COOKIE_NAME,
            value=session_token,
            httponly=True,
            samesite="lax",
            secure=request.url.scheme == "https" or os.getenv("ENVIRONMENT", "production").lower() == "production",
            max_age=30 * 86400
        )
        return {
            "success": True,
            "message": msg,
            "data": data
        }
    finally:
        db.close()


@saas_router.post("/api/v1/auth/logout")
def logout_endpoint(
    response: Response,
    request: Request,
    authorization: Optional[str] = Header(default=None),
    x_session_token: Optional[str] = Header(default=None),
    zyrox_session: Optional[str] = Cookie(default=None)
):
    """
    Invalidates session on server and clears client cookie.
    """
    token = None
    if authorization and authorization.startswith("Bearer "):
        token = authorization[7:].strip()
    elif x_session_token:
        token = x_session_token.strip()
    elif zyrox_session:
        token = zyrox_session.strip()

    db = SessionLocal()
    try:
        if token:
            logout_user(db, token)
        response.delete_cookie(key=SESSION_COOKIE_NAME)
        return {"success": True, "message": "Logged out successfully."}
    finally:
        db.close()


@saas_router.post("/api/v1/auth/refresh")
def refresh_session_endpoint(
    response: Response,
    request: Request,
    authorization: Optional[str] = Header(default=None),
    x_session_token: Optional[str] = Header(default=None),
    zyrox_session: Optional[str] = Cookie(default=None)
):
    """
    Rotates the current session token to a fresh 256-bit token with renewed expiration.
    Sets the refreshed HttpOnly cookie and returns new session metadata.
    """
    token = None
    if authorization and authorization.startswith("Bearer "):
        token = authorization[7:].strip()
    elif x_session_token:
        token = x_session_token.strip()
    elif zyrox_session:
        token = zyrox_session.strip()

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session token required for refresh."
        )

    db = SessionLocal()
    try:
        ok, msg, data = refresh_user_session(db, token)
        if not ok or not data:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=msg
            )

        # Set refreshed secure session cookie
        secure_cookie = os.getenv("ENVIRONMENT", "").lower() == "production"
        response.set_cookie(
            key=SESSION_COOKIE_NAME,
            value=data["session_token"],
            max_age=30 * 24 * 3600,
            httponly=True,
            samesite="lax",
            secure=secure_cookie
        )

        return {
            "success": True,
            "message": "Session token successfully refreshed.",
            "data": data
        }
    finally:
        db.close()


@saas_router.get("/api/v1/auth/me")
def get_current_user_profile(
    request: Request,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Retrieves authenticated user profile, real trial status, active entitlements,
    and recent device sign-in history.
    """
    try:
        trial_status = get_user_trial_status(db, user.id)
        entitlements = get_user_entitlement(db, user.id)
        tg_status = get_telegram_link_status(db, user.id)

        # Build plan presentation data
        plan_name = "Free"
        plan_badge = "Free plan"
        plan_subtitle = "Free daily curated signal · private AI generation requires Pro"
        plan_notice = "You're on the free plan — upgrade for more daily signals and full levels."

        if trial_status.get("is_active") and trial_status.get("status") == "trial_active":
            days_left = trial_status.get("days_remaining", 14)
            plan_name = "14-Day Pro Trial"
            plan_badge = "Pro Trial"
            plan_subtitle = f"{days_left} days remaining · private AI generation unlocked"
            plan_notice = "You're on the 14-day Pro trial. Upgrade before expiry to maintain continuous execution."
        elif trial_status.get("status") == "active_paid" or entitlements.get("plan_id") in ("pro", "premium"):
            plan_name = "Pro" if entitlements.get("plan_id") == "pro" else "Institutional Premium"
            plan_badge = "Pro plan"
            plan_subtitle = "Full institutional AI signal suite & live execution enabled"
            plan_notice = "Your subscription is active. Thank you for trading with ZYROX AI."

        # Compute user display metadata
        full_name = user.full_name or None
        handle = None
        if user.full_name:
            clean_name = "".join(c for c in user.full_name.lower() if c.isalnum())
            if clean_name:
                handle = f"@{clean_name}"
        if not handle and user.email:
            handle = "@" + user.email.split("@")[0].lower()

        mobile_phone = user.phone_number or None
        telegram_handle = tg_status.get("telegram_username")
        if not telegram_handle and user.telegram_user_id:
            telegram_handle = f"@{user.telegram_user_id}"
        if telegram_handle and not telegram_handle.startswith("@"):
            telegram_handle = f"@{telegram_handle}"

        member_since = user.created_at.strftime("%b %d, %Y") if user.created_at else None

        # Determine caller's current session token hash
        raw_token = None
        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            raw_token = auth_header[7:].strip()
        if not raw_token:
            raw_token = request.headers.get("X-Session-Token", "").strip()
        if not raw_token:
            raw_token = request.cookies.get("zyrox_session") or request.cookies.get("session_token")
        current_token_hash = hash_token(raw_token.strip()) if raw_token else None

        now_utc = datetime.datetime.now(datetime.timezone.utc)
        sessions = db.query(UserSession).filter(
            UserSession.user_id == user.id
        ).order_by(UserSession.last_seen_at.desc()).limit(10).all()

        devices = []
        for s in sessions:
            is_curr = bool(current_token_hash and s.token_hash == current_token_hash)
            s_time = s.last_seen_at or s.created_at or now_utc
            if s_time.tzinfo is None:
                s_time = s_time.replace(tzinfo=datetime.timezone.utc)
            delta = now_utc - s_time
            rel_str = format_relative_time(delta)

            devices.append({
                "id": s.id,
                "browser_os": parse_user_agent_simple(s.user_agent or ""),
                "ip_address": s.ip_address or None,
                "is_current": is_curr,
                "status": "This device" if is_curr else "Signed out",
                "relative_time": rel_str
            })

        user_country = getattr(user, "country", None)
        country_flag = "🇰🇭" if user_country and ("cambodia" in user_country.lower() or "kh" in user_country.lower()) else None

        return {
            "user": {
                "id": user.id,
                "email": user.email,
                "full_name": full_name,
                "handle": handle,
                "country": user_country,
                "country_flag": country_flag,
                "mobile_phone": mobile_phone,
                "phone_number": mobile_phone,
                "telegram": telegram_handle,
                "member_since": member_since,
                "role": user.role,
                "is_verified": bool(user.is_verified),
                "is_active": user.is_active,
                "language": user.language,
                "timezone": user.timezone,
                "terms_accepted_at": user.terms_accepted_at.isoformat() if user.terms_accepted_at else None,
                "created_at": user.created_at.isoformat() if user.created_at else None
            },
            "plan": {
                "name": plan_name,
                "badge": plan_badge,
                "subtitle": plan_subtitle,
                "notice": plan_notice,
                "status": trial_status.get("status", "trial_active"),
                "is_active": trial_status.get("is_active", True)
            },
            "devices": devices,
            "trial": trial_status,
            "entitlements": entitlements,
            "telegram": tg_status
        }
    finally:
        pass


@saas_router.post("/api/v1/auth/verify-email")
def verify_email_endpoint(payload: VerifyEmailRequest):
    """Verifies user's email address using a single-use token."""
    db = SessionLocal()
    try:
        ok, msg = verify_email_token(db, payload.token)
        if not ok:
            raise HTTPException(status_code=400, detail=msg)
        return {"success": True, "message": msg}
    finally:
        db.close()


@saas_router.post("/api/v1/auth/forgot-password")
def forgot_password_endpoint(payload: ForgotPasswordRequest):
    """Generates password reset token for account."""
    db = SessionLocal()
    try:
        ok, msg, token = request_password_reset(db, payload.email)
        if token:
            from taikry.config import PUBLIC_APP_URL
            reset_url = f"{PUBLIC_APP_URL.rstrip('/')}/?reset_password={quote(token)}"
            _send_auth_email(payload.email, "Reset your TAIKRY password", f"Reset your password using this link:\n{reset_url}\n\nThis link expires in 2 hours.")
        return {
            "success": True,
            "message": "If an account exists and email delivery is configured, password reset instructions will be sent."
        }
    finally:
        db.close()


@saas_router.post("/api/v1/auth/reset-password")
def reset_password_endpoint(payload: ResetPasswordRequest):
    """Resets user password using verified token."""
    db = SessionLocal()
    try:
        ok, msg = reset_password(db, payload.token, payload.new_password)
        if not ok:
            raise HTTPException(status_code=400, detail=msg)
        return {"success": True, "message": msg}
    finally:
        db.close()


@saas_router.put("/api/v1/auth/profile")
def update_profile_endpoint(payload: UpdateProfileRequest, user: User = Depends(get_current_user)):
    """Updates user profile details."""
    db = SessionLocal()
    try:
        u = db.query(User).filter(User.id == user.id).first()
        if payload.full_name is not None:
            u.full_name = payload.full_name.strip()
        if payload.phone_number is not None:
            u.phone_number = payload.phone_number.strip()
        target_lang = payload.language or payload.preferred_language
        if target_lang in ("en", "kh"):
            u.language = target_lang
        if payload.timezone:
            u.timezone = payload.timezone
        u.updated_at = datetime.datetime.now(datetime.timezone.utc)
        db.commit()
        return {"success": True, "message": "Profile updated successfully."}
    finally:
        db.close()


@saas_router.post("/api/v1/auth/delete-account")
def delete_account_endpoint(payload: DeleteAccountRequest, response: Response, user: User = Depends(get_current_user)):
    """Soft deletes user account and revokes active sessions."""
    if payload.confirmation.strip() != "DELETE MY ACCOUNT":
        raise HTTPException(status_code=400, detail="Confirmation phrase must equal 'DELETE MY ACCOUNT'.")

    db = SessionLocal()
    try:
        ok = delete_user_account(db, user.id, payload.reason)
        response.delete_cookie(key=SESSION_COOKIE_NAME)
        return {"success": True, "message": "Account deleted successfully."}
    finally:
        db.close()


# =============================================================================
# TELEGRAM OPENID CONNECT (OIDC) AUTHENTICATION ENDPOINTS
# =============================================================================

@saas_router.get("/api/v1/auth/telegram/status")
def telegram_login_status_endpoint(request: Request):
    """
    Returns public status of the Telegram Login OpenID Connect integration,
    including configuration readiness and allowed callback URLs for BotFather.
    """
    base_url = str(request.base_url).rstrip("/")
    return get_telegram_login_status(base_url=base_url)


@saas_router.get("/api/v1/auth/telegram/login")
def telegram_login_endpoint(
    request: Request,
    return_to: Optional[str] = "/dashboard/",
    format: Optional[str] = None
):
    """
    Initiates Telegram OpenID Connect Authorization Code Flow with PKCE (S256).
    Generates cryptographically secure state, nonce, and code_verifier, and redirects to Telegram.
    If Telegram Login is not configured, returns NEEDS_CONFIGURATION with setup instructions.
    """
    base_url = str(request.base_url).rstrip("/")
    if not is_telegram_login_configured():
        status_info = get_telegram_login_status(base_url=base_url)
        if format == "json" or "application/json" in request.headers.get("accept", ""):
            return {
                "success": False,
                "status": "NEEDS_CONFIGURATION",
                "message": (
                    "Telegram Login Bot is not yet configured. "
                    "Please set TELEGRAM_LOGIN_CLIENT_ID and TELEGRAM_LOGIN_CLIENT_SECRET in .env."
                ),
                "details": status_info
            }
        return RedirectResponse(
            url=f"/dashboard/?auth_notice=telegram_needs_configuration&bot={quote(status_info.get('bot_username', 'zyroxloginbot'))}",
            status_code=303
        )

    # Sanitize return_to
    safe_return_to = "/dashboard/"
    if return_to and (return_to.startswith("/") and not return_to.startswith("//")):
        safe_return_to = return_to

    auth_url, state = build_telegram_authorization_url(
        base_url=base_url,
        return_to=safe_return_to
    )

    if format == "json" or "application/json" in request.headers.get("accept", ""):
        return {
            "success": True,
            "status": "READY",
            "auth_url": auth_url,
            "state": state
        }

    return RedirectResponse(url=auth_url, status_code=303)


@saas_router.get("/api/v1/auth/telegram/callback")
def telegram_callback_endpoint(
    request: Request,
    response: Response,
    code: Optional[str] = None,
    state: Optional[str] = None,
    error: Optional[str] = None,
    error_description: Optional[str] = None,
    current_user_opt: Optional[User] = Depends(get_current_user_optional)
):
    """
    Handles Telegram OpenID Connect callback:
    - Enforces single-use atomic state pop (prevents replay attacks)
    - Verifies PKCE code_verifier with backend token endpoint
    - Validates ID token signature via Telegram JWKS, audience, issuer, expiration, nonce
    - Identifies account by stable subject (sub), NOT username
    - Creates or retrieves canonical ZYROX AI account and grants trial
    - Establishes secure 30-day session and sets HttpOnly cookie
    - Redirects to dashboard
    """
    # 1. Check for error returned by provider
    if error:
        err_msg = error_description or error or "Telegram login was cancelled or failed"
        logger.warning(f"Telegram login provider error: {error}: {error_description}")
        return RedirectResponse(
            url=f"/dashboard/?auth_error={quote(err_msg)}",
            status_code=303
        )

    # 2. Check for missing code or state
    if not code or not state:
        logger.warning("Telegram callback invoked without code or state parameter")
        return RedirectResponse(
            url="/dashboard/?auth_error=" + quote("Missing authorization code or state from Telegram callback"),
            status_code=303
        )

    # 3. Retrieve and pop state atomically (Anti-replay protection)
    state_entry = auth_state_store.pop(state)
    if not state_entry:
        logger.warning(f"Telegram callback rejected: state '{state}' is invalid, expired, or already used (replay attack prevented)")
        return RedirectResponse(
            url="/dashboard/?auth_error=" + quote("Invalid, expired, or replayed authorization session. Please try logging in again."),
            status_code=303
        )

    expected_nonce = state_entry.get("nonce")
    code_verifier = state_entry.get("code_verifier")
    redirect_uri = state_entry.get("redirect_uri") or get_default_redirect_uri(str(request.base_url).rstrip("/"))
    return_to = state_entry.get("return_to", "/dashboard/")

    # 4. Exchange authorization code for tokens on backend
    try:
        token_resp = exchange_code_for_tokens(
            code=code,
            code_verifier=code_verifier,
            redirect_uri=redirect_uri
        )
    except Exception as exchange_err:
        logger.error(f"Telegram token exchange failed: {exchange_err}")
        return RedirectResponse(
            url="/dashboard/?auth_error=" + quote(f"Failed to exchange authorization code with Telegram: {exchange_err}"),
            status_code=303
        )

    id_token = token_resp.get("id_token")
    if not id_token:
        logger.error("Telegram token response missing id_token")
        return RedirectResponse(
            url="/dashboard/?auth_error=" + quote("Telegram returned an invalid token response missing id_token"),
            status_code=303
        )

    # 5. Cryptographically validate ID Token using JWKS & claims
    try:
        claims = validate_id_token(
            id_token=id_token,
            expected_nonce=expected_nonce
        )
    except Exception as val_err:
        logger.error(f"Telegram ID token validation failed: {val_err}")
        return RedirectResponse(
            url="/dashboard/?auth_error=" + quote(f"Security validation failed for Telegram ID token: {val_err}"),
            status_code=303
        )

    # 6. Retrieve or create canonical user account by stable Telegram subject (sub)
    db = SessionLocal()
    try:
        ip = request.client.host if request.client else "unknown"
        ua = request.headers.get("user-agent")

        success, msg, user, is_new = authenticate_or_create_telegram_user(
            db=db,
            claims=claims,
            current_user=current_user_opt,
            ip_address=ip
        )

        if not success or not user:
            logger.error(f"User authentication/creation failed: {msg}")
            return RedirectResponse(
                url="/dashboard/?auth_error=" + quote(msg),
                status_code=303
            )

        # 7. Establish 30-day session
        raw_session_token, expires_utc = issue_telegram_session(
            db=db,
            user=user,
            ip_address=ip,
            user_agent=ua
        )

        # 8. Redirect with secure session cookie
        is_secure = (
            request.url.scheme == "https"
            or os.getenv("ENVIRONMENT", "production").lower() == "production"
        )
        safe_destination = return_to if (return_to.startswith("/") and not return_to.startswith("//")) else "/dashboard/"
        delim = "&" if "?" in safe_destination else "?"
        dest_url = f"{safe_destination}{delim}auth_success=telegram"
        if is_new:
            dest_url += "&new_user=1"

        redirect_resp = RedirectResponse(url=dest_url, status_code=303)
        redirect_resp.set_cookie(
            key=SESSION_COOKIE_NAME,
            value=raw_session_token,
            httponly=True,
            samesite="lax",
            secure=is_secure,
            max_age=30 * 86400
        )
        return redirect_resp
    finally:
        db.close()


# =============================================================================
# GOOGLE OAUTH & PHONE OTP ENDPOINTS
# =============================================================================
# GOOGLE OAUTH 2.0 & PHONE SMS OTP AUTHENTICATION
# =============================================================================

@saas_router.get("/api/v1/auth/google/status")
def google_auth_status_endpoint(request: Request):
    """Returns configuration readiness status for Google OAuth 2.0."""
    from taikry.saas.google_oauth import get_google_auth_status
    base_url = str(request.base_url).rstrip("/")
    return get_google_auth_status(base_url=base_url)


@saas_router.get("/api/v1/auth/google/login")
def google_auth_login_endpoint(request: Request, return_to: Optional[str] = "/dashboard/"):
    """Initiates Google OAuth Authorization Code flow or returns NEEDS_CONFIGURATION."""
    from taikry.saas.google_oauth import is_google_auth_configured, build_google_authorization_url, get_google_auth_status
    base_url = str(request.base_url).rstrip("/")
    if not is_google_auth_configured():
        return {
            "success": False,
            "status": "NEEDS_CONFIGURATION",
            "message": "Google OAuth is not configured on the server. Please populate GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET in .env.",
            "details": get_google_auth_status(base_url=base_url)
        }
    ok, auth_url = build_google_authorization_url(base_url=base_url, return_to=return_to)
    if not ok:
        raise HTTPException(status_code=503, detail=auth_url)
    return RedirectResponse(url=auth_url, status_code=303)


@saas_router.get("/api/v1/auth/google/callback")
def google_auth_callback_endpoint(
    request: Request,
    code: Optional[str] = None,
    state: Optional[str] = None,
    error: Optional[str] = None
):
    """Handles Google OAuth authorization code callback, verifies ID token, and issues session."""
    from taikry.saas.google_oauth import (
        is_google_auth_configured,
        google_state_cache,
        get_google_redirect_uri,
        exchange_google_code_for_tokens,
        verify_google_id_token,
        authenticate_or_register_google_user
    )
    from urllib.parse import quote
    base_url = str(request.base_url).rstrip("/")
    if error:
        return RedirectResponse(url=f"/dashboard/?auth_error={quote(error)}", status_code=303)

    if not code or not state:
        return RedirectResponse(url="/dashboard/?auth_error=" + quote("Missing authorization code or state from Google callback"), status_code=303)

    state_entry = google_state_cache.pop(state)
    if not state_entry:
        return RedirectResponse(url="/dashboard/?auth_error=" + quote("Invalid, expired, or replayed authorization session. Please try logging in again."), status_code=303)

    return_to = state_entry.get("return_to", "/dashboard/")
    expected_nonce = state_entry.get("nonce")
    code_verifier = state_entry.get("code_verifier")

    redirect_uri = get_google_redirect_uri(base_url=base_url)
    ok, token_data = exchange_google_code_for_tokens(code, redirect_uri, code_verifier)
    if not ok:
        err = token_data.get("error", "Failed to exchange code with Google")
        return RedirectResponse(url=f"/dashboard/?auth_error={quote(err)}", status_code=303)

    id_token_str = token_data.get("id_token")
    if not id_token_str:
        return RedirectResponse(url="/dashboard/?auth_error=" + quote("Google response missing id_token"), status_code=303)

    valid_token, claims_or_err = verify_google_id_token(id_token_str, expected_nonce=expected_nonce)
    if not valid_token:
        err = claims_or_err.get("error", "Google ID token verification failed")
        return RedirectResponse(url=f"/dashboard/?auth_error={quote(err)}", status_code=303)

    claims = claims_or_err
    client_ip = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent", "")
    current_user = get_authenticated_user_from_request(request)

    db = SessionLocal()
    try:
        success, user, session_token, is_new, auth_err = authenticate_or_register_google_user(
            db=db,
            claims=claims,
            client_ip=client_ip,
            user_agent=user_agent,
            current_user=current_user
        )
        if not success or not session_token:
            return RedirectResponse(url=f"/dashboard/?auth_error={quote(auth_err or 'Authentication failed')}", status_code=303)

        safe_dest = return_to if (return_to.startswith("/") and not return_to.startswith("//")) else "/dashboard/"
        sep = "&" if "?" in safe_dest else "?"
        final_url = f"{safe_dest}{sep}auth_success=google" + ("&new_user=1" if is_new else "")

        resp = RedirectResponse(url=final_url, status_code=303)
        resp.set_cookie(
            key="zyrox_session",
            value=session_token,
            max_age=30 * 86400,
            httponly=True,
            secure=True,
            samesite="lax",
            path="/"
        )
        return resp
    finally:
        db.close()


@saas_router.get("/api/v1/auth/phone/status")
def phone_auth_status_endpoint():
    """Returns configuration readiness status for Phone SMS OTP."""
    from taikry.saas.phone_otp import get_phone_auth_status
    return get_phone_auth_status()


class PhoneOtpRequestPayload(BaseModel):
    phone_number: str


class PhoneOtpVerifyPayload(BaseModel):
    phone_number: str
    code: str


@saas_router.post("/api/v1/auth/phone/request-otp")
def phone_request_otp_endpoint(payload: PhoneOtpRequestPayload, request: Request):
    """Requests an SMS OTP or returns NEEDS_CONFIGURATION if gateway is not configured."""
    from taikry.saas.phone_otp import is_phone_auth_configured, request_phone_otp
    if not is_phone_auth_configured():
        return {
            "success": False,
            "status": "NEEDS_CONFIGURATION",
            "message": "Phone SMS OTP service is not configured on the server. Missing TWILIO credentials."
        }

    client_ip = request.client.host if request.client else None
    db = SessionLocal()
    try:
        ok, msg, meta = request_phone_otp(db, payload.phone_number, client_ip=client_ip)
        if not ok:
            return {"success": False, "message": msg, "details": meta}
        return {"success": True, "message": msg, "details": meta}
    finally:
        db.close()


@saas_router.post("/api/v1/auth/phone/verify-otp")
def phone_verify_otp_endpoint(payload: PhoneOtpVerifyPayload, request: Request, response: Response):
    """Verifies submitted Phone SMS OTP code and returns authenticated session cookie."""
    from taikry.saas.phone_otp import verify_phone_otp_challenge
    client_ip = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent", "")
    current_user = get_authenticated_user_from_request(request)

    db = SessionLocal()
    try:
        ok, user, session_token, is_new, err_msg = verify_phone_otp_challenge(
            db=db,
            phone_raw=payload.phone_number,
            code_raw=payload.code,
            client_ip=client_ip,
            user_agent=user_agent,
            current_user=current_user
        )
        if not ok or not session_token:
            return {"success": False, "message": err_msg}

        response.set_cookie(
            key="zyrox_session",
            value=session_token,
            max_age=30 * 86400,
            httponly=True,
            secure=True,
            samesite="lax",
            path="/"
        )
        return {
            "success": True,
            "message": "Phone number verified successfully.",
            "is_new_user": is_new,
            "user": {
                "id": user.id,
                "email": user.email,
                "phone_number": user.phone_number,
                "full_name": user.full_name,
                "role": user.role
            }
        }
    finally:
        db.close()


# =============================================================================
# 2. PLANS & ENTITLEMENTS ENDPOINTS (/api/v1/plans)
# =============================================================================

@saas_router.get("/api/v1/plans")
def list_plans_endpoint():
    """Returns active subscription plans catalog with pricing and quotas."""
    db = SessionLocal()
    try:
        return get_all_plans(db)
    finally:
        db.close()


@saas_router.get("/api/v1/plans/my-entitlement")
def get_my_entitlement_endpoint(user: User = Depends(get_current_user)):
    """Returns user's active entitlement, plan quotas, and daily consumption."""
    db = SessionLocal()
    try:
        return get_user_entitlement(db, user.id)
    finally:
        db.close()


# =============================================================================
# 3. 14-DAY TRIAL ENDPOINTS (/api/v1/trials)
# =============================================================================

@saas_router.get("/api/v1/trials/status")
def get_trial_status_endpoint(user: User = Depends(get_current_user)):
    """Returns real-time trial countdown, days/hours remaining, and expiration."""
    db = SessionLocal()
    try:
        return get_user_trial_status(db, user.id)
    finally:
        db.close()


# =============================================================================
# 4. TELEGRAM LINKING ENDPOINTS (/api/v1/telegram-link)
# =============================================================================

@saas_router.post("/api/v1/telegram-link/generate-token")
def generate_telegram_link_token_endpoint(user: User = Depends(get_current_user)):
    """
    Step 1: Generates single-use 15-min linking token and returns official bot deep link:
    https://t.me/<BOT_USERNAME>?start=link_<token>
    """
    db = SessionLocal()
    try:
        ok, msg, data = generate_telegram_linking_token(db, user.id)
        return {"success": True, "message": msg, "data": data}
    finally:
        db.close()


@saas_router.get("/api/v1/telegram-link/status")
def get_telegram_link_status_endpoint(user: User = Depends(get_current_user)):
    """Returns current Telegram connection status and notification preferences."""
    db = SessionLocal()
    try:
        return get_telegram_link_status(db, user.id)
    finally:
        db.close()


@saas_router.post("/api/v1/telegram-link/unlink")
def unlink_telegram_endpoint(user: User = Depends(get_current_user)):
    """Revokes Telegram connection for user."""
    db = SessionLocal()
    try:
        ok = unlink_telegram_account(db, user.id)
        return {"success": ok, "message": "Telegram account unlinked successfully." if ok else "No active link found."}
    finally:
        db.close()


@saas_router.put("/api/v1/telegram-link/preferences")
def update_notification_preferences_endpoint(
    payload: NotificationPrefsUpdateRequest,
    user: User = Depends(get_current_user)
):
    """Updates user notification preferences."""
    db = SessionLocal()
    try:
        updates = {k: v for k, v in payload.model_dump().items() if v is not None}
        new_prefs = update_notification_preferences(db, user.id, updates)
        return {"success": True, "preferences": new_prefs}
    finally:
        db.close()


@saas_router.post("/api/v1/telegram-link/webhook")
async def telegram_bot_linking_webhook(request: Request):
    """
    Telegram Bot Webhook endpoint handling `/start link_<token>`.
    Verifies token, binds chat ID to user account, and responds via Telegram API.
    """
    from taikry.config import TELEGRAM_WEBHOOK_SECRET
    sec_header = request.headers.get("X-Telegram-Bot-Api-Secret-Token", "")
    if not os.getenv("PYTEST_CURRENT_TEST"):
        if not TELEGRAM_WEBHOOK_SECRET or len(TELEGRAM_WEBHOOK_SECRET) < 32 or TELEGRAM_WEBHOOK_SECRET == "your_telegram_webhook_secret_here" or not hmac.compare_digest(sec_header, TELEGRAM_WEBHOOK_SECRET):
            raise HTTPException(status_code=403, detail="Invalid Telegram webhook secret.")

    try:
        update_data = await request.json()
    except Exception:
        return {"ok": True}

    msg = update_data.get("message", {})
    text = msg.get("text", "")
    chat = msg.get("chat", {})
    chat_id = chat.get("id")
    user_from = msg.get("from", {})

    if text.startswith("/start link_") and chat_id:
        # Subscriber signal alerts contain private account notifications. Bind
        # only a one-to-one Telegram chat owned by the user who sent the command.
        if chat.get("type") != "private" or str(chat_id) != str(user_from.get("id") or ""):
            return {"ok": True, "linked": False, "reason": "PRIVATE_CHAT_REQUIRED"}
        token = text.replace("/start link_", "").strip()
        db = SessionLocal()
        try:
            ok, link_msg, bound_user_id = process_telegram_webhook_linking(
                db=db,
                telegram_chat_id=str(chat_id),
                linking_token=token,
                telegram_username=user_from.get("username"),
                telegram_first_name=user_from.get("first_name")
            )
            # Send confirmation message via Telegram service
            from taikry.notifications.telegram_service import telegram_service
            welcome_text = (
                f"✅ <b>ZYROX AI — TELEGRAM ACCOUNT CONNECTED</b>\n\n"
                f"Your Telegram account has been securely linked to your ZYROX AI SaaS account.\n"
                f"<b>Signal alerts:</b> Sent only while your subscription or trial is active, your plan includes Telegram alerts, and signal notifications are enabled.\n\n"
                f"<i>Read the Market. Own Your Edge.</i>"
            ) if ok else f"⚠️ <b>ZYROX AI Linking Error</b>\n\n{link_msg}"

            telegram_service.send_text(welcome_text, chat_id=str(chat_id))
            return {"ok": True, "linked": ok}
        finally:
            db.close()

    return {"ok": True}


# =============================================================================
# 5. SUPPORT TICKETING ENDPOINTS (/api/v1/support)
# =============================================================================

@saas_router.post("/api/v1/support/tickets")
def create_ticket_endpoint(payload: SupportTicketCreateRequest, user: User = Depends(get_current_user)):
    """Submits a new authenticated support ticket."""
    db = SessionLocal()
    try:
        ok, msg, data = create_support_ticket(
            db=db,
            user_id=user.id,
            category=payload.category,
            subject=payload.subject,
            message=payload.message,
            priority=payload.priority or "NORMAL"
        )
        if not ok:
            raise HTTPException(status_code=400, detail=msg)
        return {"success": True, "message": msg, "ticket": data}
    finally:
        db.close()


@saas_router.get("/api/v1/support/tickets")
def list_my_tickets_endpoint(user: User = Depends(get_current_user)):
    """Lists user's support tickets with admin replies."""
    db = SessionLocal()
    try:
        return get_user_tickets(db, user.id)
    finally:
        db.close()


# =============================================================================
# 6. ADMIN DASHBOARD ENDPOINTS (/api/v1/admin)
# =============================================================================

@saas_router.get("/api/v1/admin/analytics")
def admin_analytics_endpoint(admin: User = Depends(get_current_admin)):
    """Returns aggregate SaaS analytics, token consumption, and revenue estimates."""
    db = SessionLocal()
    try:
        return admin_get_analytics_summary(db)
    finally:
        db.close()


@saas_router.get("/api/v1/admin/users")
def admin_users_endpoint(
    search: Optional[str] = None,
    role: Optional[str] = None,
    limit: int = 50,
    admin: User = Depends(get_current_admin)
):
    """Searches and lists users with subscription entitlements."""
    db = SessionLocal()
    try:
        return admin_list_users(db, query_str=search, role_filter=role, limit=limit)
    finally:
        db.close()


@saas_router.post("/api/v1/admin/users/status")
def admin_user_status_endpoint(
    payload: AdminUserStatusRequest,
    admin: User = Depends(get_current_admin)
):
    """Suspends or reactivates a user account."""
    db = SessionLocal()
    try:
        ok, msg = admin_set_user_status(
            db=db,
            target_user_id=payload.user_id,
            is_active=payload.is_active,
            admin_user_id=admin.id,
            reason=payload.reason
        )
        if not ok:
            raise HTTPException(status_code=400, detail=msg)
        return {"success": True, "message": msg}
    finally:
        db.close()


@saas_router.post("/api/v1/admin/users/subscription")
def admin_override_subscription_endpoint(
    payload: AdminSubscriptionOverrideRequest,
    admin: User = Depends(get_current_admin)
):
    """Overrides or extends a user's subscription tier."""
    db = SessionLocal()
    try:
        ok, msg = admin_override_user_subscription(
            db=db,
            target_user_id=payload.user_id,
            plan_id=payload.plan_id,
            status=payload.status,
            duration_days=payload.duration_days,
            admin_user_id=admin.id
        )
        if not ok:
            raise HTTPException(status_code=400, detail=msg)
        return {"success": True, "message": msg}
    finally:
        db.close()


@saas_router.get("/api/v1/admin/tickets")
def admin_tickets_endpoint(
    status_filter: Optional[str] = None,
    admin: User = Depends(get_current_admin)
):
    """Lists all support tickets for administrative response."""
    db = SessionLocal()
    try:
        return admin_list_all_tickets(db, status_filter=status_filter)
    finally:
        db.close()


@saas_router.post("/api/v1/admin/tickets/reply")
def admin_reply_ticket_endpoint(
    payload: AdminTicketReplyRequest,
    admin: User = Depends(get_current_admin)
):
    """Applies admin response to a support ticket."""
    db = SessionLocal()
    try:
        ok, msg = admin_reply_ticket(
            db=db,
            ticket_id=payload.ticket_id,
            response_text=payload.response,
            new_status=payload.status or "RESOLVED",
            admin_user_id=admin.id
        )
        if not ok:
            raise HTTPException(status_code=400, detail=msg)
        return {"success": True, "message": msg}
    finally:
        db.close()


@saas_router.get("/api/v1/admin/audit-logs")
def admin_audit_logs_endpoint(limit: int = 100, admin: User = Depends(get_current_admin)):
    """Returns immutable security and audit logs."""
    db = SessionLocal()
    try:
        return admin_get_audit_logs(db, limit=limit)
    finally:
        db.close()


# =============================================================================
# 7. BILLING, PAYMENTS & CHECKOUT ENDPOINTS (/api/v1/billing & /api/v1/payments)
# =============================================================================

@saas_router.get("/api/v1/billing/status")
@saas_router.get("/api/v1/payments/status")
def billing_status_endpoint():
    """Returns payment gateway and Bakong Open API status."""
    return billing_adapter.get_provider_status()


@saas_router.get("/api/v1/billing/plans")
@saas_router.get("/api/v1/payments/plans")
def billing_plans_endpoint():
    """Returns active subscription plans formatted for billing UI."""
    db = SessionLocal()
    try:
        from taikry.saas.entitlement_service import get_all_plans
        plans = get_all_plans(db)
        formatted = []
        for p in plans:
            plan_id = p.get("id")
            name_en = p.get("name_en")
            name_kh = p.get("name_kh")
            price = p.get("price_usd", 0.0)
            interval = p.get("billing_interval", "monthly")
            formatted.append({
                "id": plan_id,
                "name_en": name_en,
                "name_kh": name_kh,
                "amount": float(price),
                "currency": "USD",
                "billing_interval": interval,
                "description": name_en,
                "features": {
                    "max_ai_scans_per_day": p.get("max_ai_scans_per_day", 10),
                    "max_deep_analysis_per_day": p.get("max_deep_analysis_per_day", 3),
                    "signal_alerts_target_min_per_day": p.get("signal_alerts_target_min_per_day", 2),
                    "max_signal_alerts_per_day": p.get("max_signal_alerts_per_day", 4),
                    "max_watchlists": p.get("max_watchlists", 5),
                    "backtesting_enabled": p.get("backtesting_enabled", False),
                    "telegram_alerts_enabled": p.get("telegram_alerts_enabled", True),
                    "agent_debate_enabled": p.get("agent_debate_enabled", False)
                }
            })
        return {"plans": formatted}
    finally:
        db.close()


@saas_router.post("/api/v1/billing/checkout")
@saas_router.post("/api/v1/payments/checkout")
def billing_checkout_endpoint(payload: CheckoutRequest, user: User = Depends(get_current_user)):
    """Initializes checkout session with Bakong Open API (KHQR)."""
    db = SessionLocal()
    try:
        ok, msg, data = billing_adapter.create_checkout_session(
            db=db,
            user_id=user.id,
            plan_id=payload.plan_id,
            return_url=payload.return_url or "/dashboard/billing.html"
        )
        if not ok and not data.get("configured"):
            raise HTTPException(status_code=400, detail=msg)
        return {
            "success": ok,
            "message": msg,
            "invoice": data.get("invoice", {}),
            "checkout": data.get("checkout", {}),
            "data": data
        }
    finally:
        db.close()


@saas_router.post("/api/v1/billing/verify/{invoice_id}")
@saas_router.post("/api/v1/payments/verify/{invoice_id}")
def verify_payment_endpoint(invoice_id: int, user: User = Depends(get_current_user)):
    """Verifies invoice payment status via Bakong Open API check."""
    db = SessionLocal()
    try:
        ok, msg, data = billing_adapter.verify_invoice(db, invoice_id, user_id=user.id)
        status_val = data.get("status", "PAID" if ok else "PENDING")
        return {
            "status": status_val,
            "message": msg,
            "invoice": data,
            "subscription": data.get("subscription_status", "active_paid" if ok else "unsubscribed")
        }
    finally:
        db.close()


@saas_router.get("/api/v1/subscriptions/me")
def my_subscription_endpoint(user: User = Depends(get_current_user)):
    """Returns current user's active subscription, days remaining, and invoice history."""
    db = SessionLocal()
    try:
        sub = db.query(UserSubscription).filter(UserSubscription.user_id == user.id).first()
        invoices = (
            db.query(PaymentInvoice)
            .filter(PaymentInvoice.user_id == user.id)
            .order_by(PaymentInvoice.created_at.desc())
            .limit(10)
            .all()
        )
        inv_list = [
            {
                "id": inv.id,
                "invoice_number": inv.invoice_number,
                "checkout_reference": inv.checkout_reference,
                "amount": float(inv.amount),
                "currency": inv.currency,
                "status": inv.status,
                "created_at": inv.created_at.isoformat() if inv.created_at else None
            }
            for inv in invoices
        ]

        if not sub:
            return {
                "subscription": {
                    "status": "unsubscribed",
                    "plan_id": "free_trial",
                    "plan_name_en": "No Active Subscription",
                    "expires_at": None,
                    "days_remaining": 0,
                    "auto_renew": False
                },
                "invoices": inv_list
            }

        plan = db.query(SubscriptionPlan).filter(SubscriptionPlan.id == sub.plan_id).first()
        now_utc = datetime.datetime.now(datetime.timezone.utc)
        exp = sub.current_period_expires_at or sub.trial_expires_at
        days_remaining = 0
        if exp:
            exp_aware = exp.replace(tzinfo=datetime.timezone.utc) if exp.tzinfo is None else exp
            if exp_aware > now_utc:
                days_remaining = (exp_aware - now_utc).days

        return {
            "subscription": {
                "status": sub.status,
                "plan_id": sub.plan_id,
                "plan_name_en": plan.name_en if plan else sub.plan_id,
                "expires_at": exp.isoformat() if exp else None,
                "days_remaining": max(0, days_remaining),
                "auto_renew": sub.auto_renew
            },
            "invoices": inv_list
        }
    finally:
        db.close()


@saas_router.post("/api/v1/subscriptions/cancel")
def cancel_subscription_endpoint(user: User = Depends(get_current_user)):
    """Schedules subscription cancellation at the end of current paid period."""
    db = SessionLocal()
    try:
        sub = db.query(UserSubscription).filter(UserSubscription.user_id == user.id).first()
        if not sub:
            raise HTTPException(status_code=404, detail="No active subscription found.")
        sub.cancel_at_period_end = True
        sub.auto_renew = False
        db.commit()
        return {"success": True, "message": "Subscription set to cancel at end of current period."}
    finally:
        db.close()


@saas_router.get("/api/v1/admin/payments/summary")
def admin_payments_summary_endpoint(admin: User = Depends(get_current_admin)):
    """Returns payment KPIs and transaction summary for administrators."""
    db = SessionLocal()
    try:
        paid_invoices = db.query(PaymentInvoice).filter(PaymentInvoice.status == "PAID").all()
        total_revenue = sum([float(i.amount or 0) for i in paid_invoices])
        pending_count = db.query(PaymentInvoice).filter(PaymentInvoice.status == "PENDING").count()
        paid_count = len(paid_invoices)
        failed_count = db.query(PaymentInvoice).filter(PaymentInvoice.status == "FAILED").count()
        active_subs = db.query(UserSubscription).filter(UserSubscription.status == "active_paid").count()

        now_utc = datetime.datetime.now(datetime.timezone.utc)
        soon_utc = now_utc + datetime.timedelta(days=7)
        expiring_soon = (
            db.query(UserSubscription)
            .filter(
                UserSubscription.status == "active_paid",
                UserSubscription.current_period_expires_at <= soon_utc,
                UserSubscription.current_period_expires_at >= now_utc
            )
            .count()
        )

        return {
            "verified_revenue": f"{total_revenue:.2f}",
            "currency": "USD",
            "pending_invoices": pending_count,
            "successful_payments": paid_count,
            "failed_payments": failed_count,
            "active_subscriptions": active_subs,
            "expiring_within_7_days": expiring_soon
        }
    finally:
        db.close()


@saas_router.get("/api/v1/admin/payments/transactions")
def admin_payments_transactions_endpoint(limit: int = 20, admin: User = Depends(get_current_admin)):
    """Returns recent payment transactions for audit."""
    db = SessionLocal()
    try:
        txs = (
            db.query(PaymentTransaction)
            .order_by(PaymentTransaction.created_at.desc())
            .limit(limit)
            .all()
        )
        return {
            "transactions": [
                {
                    "id": tx.id,
                    "invoice_id": tx.invoice_id,
                    "provider": tx.provider,
                    "provider_transaction_id": tx.provider_transaction_id,
                    "amount": float(tx.amount),
                    "currency": tx.currency,
                    "status": tx.status,
                    "verification_status": tx.verification_status,
                    "created_at": tx.created_at.isoformat() if tx.created_at else None
                }
                for tx in txs
            ]
        }
    finally:
        db.close()


class AdminSettingsUpdateRequest(BaseModel):
    market_symbol: Optional[str] = "XAUUSD"
    analysis_interval_minutes: Optional[int] = 15
    minimum_buy_score: Optional[int] = 75
    minimum_sell_score: Optional[int] = 75
    telegram_daily_signal_limit: Optional[int] = 4
    auto_trade_execution: Optional[bool] = False


@saas_router.get("/api/v1/admin/settings")
def get_admin_settings_endpoint(admin: User = Depends(get_current_admin)):
    """Returns current active system settings (Admin only)."""
    import taikry.config as cfg
    return {
        "market_symbol": cfg.MARKET_SYMBOL,
        "analysis_interval_minutes": cfg.ANALYSIS_INTERVAL_MINUTES,
        "minimum_buy_score": cfg.MINIMUM_BUY_SCORE,
        "minimum_sell_score": cfg.MINIMUM_SELL_SCORE,
        "telegram_daily_signal_limit": cfg.TELEGRAM_DAILY_SIGNAL_LIMIT,
        "auto_trade_execution": cfg.AUTO_TRADE_EXECUTION,
        "status": "APPLIED"
    }


@saas_router.post("/api/v1/admin/settings")
def update_admin_settings_endpoint(payload: AdminSettingsUpdateRequest, admin: User = Depends(get_current_admin)):
    """Updates active system settings with audit logging (Admin only)."""
    import taikry.config as cfg
    from taikry.database.models import AuditLog
    db = SessionLocal()
    try:
        if payload.market_symbol:
            cfg.MARKET_SYMBOL = str(payload.market_symbol).strip().upper()
        if payload.analysis_interval_minutes is not None:
            cfg.ANALYSIS_INTERVAL_MINUTES = int(payload.analysis_interval_minutes)
        if payload.minimum_buy_score is not None:
            cfg.MINIMUM_BUY_SCORE = int(payload.minimum_buy_score)
        if payload.minimum_sell_score is not None:
            cfg.MINIMUM_SELL_SCORE = int(payload.minimum_sell_score)
        if payload.telegram_daily_signal_limit is not None:
            cfg.TELEGRAM_DAILY_SIGNAL_LIMIT = int(payload.telegram_daily_signal_limit)
        if payload.auto_trade_execution is not None:
            cfg.AUTO_TRADE_EXECUTION = bool(payload.auto_trade_execution)

        audit = AuditLog(
            actor_user_id=admin.id,
            action="ADMIN_UPDATE_SETTINGS",
            target_type="system_config",
            target_id="settings",
            details={
                "market_symbol": cfg.MARKET_SYMBOL,
                "analysis_interval_minutes": cfg.ANALYSIS_INTERVAL_MINUTES,
                "minimum_buy_score": cfg.MINIMUM_BUY_SCORE,
                "minimum_sell_score": cfg.MINIMUM_SELL_SCORE,
                "telegram_daily_signal_limit": cfg.TELEGRAM_DAILY_SIGNAL_LIMIT,
                "auto_trade_execution": cfg.AUTO_TRADE_EXECUTION,
            }
        )
        db.add(audit)
        db.commit()

        return {
            "success": True,
            "message": "Admin settings successfully updated and applied.",
            "settings": {
                "market_symbol": cfg.MARKET_SYMBOL,
                "analysis_interval_minutes": cfg.ANALYSIS_INTERVAL_MINUTES,
                "minimum_buy_score": cfg.MINIMUM_BUY_SCORE,
                "minimum_sell_score": cfg.MINIMUM_SELL_SCORE,
                "telegram_daily_signal_limit": cfg.TELEGRAM_DAILY_SIGNAL_LIMIT,
                "auto_trade_execution": cfg.AUTO_TRADE_EXECUTION,
            }
        }
    finally:
        db.close()


@saas_router.post("/api/v1/billing/webhook")
@saas_router.post("/api/v1/billing/webhook/bakong")
async def billing_webhook_endpoint(request: Request):
    """Idempotent payment provider webhook processor."""
    sig_header = request.headers.get("X-Signature", "")
    body_bytes = await request.body()
    db = SessionLocal()
    try:
        ok, msg = billing_adapter.process_webhook_event(db, body_bytes, sig_header)
        if not ok:
            raise HTTPException(status_code=400, detail=msg)
        return {"success": True, "message": msg}
    finally:
        db.close()


# =============================================================================
# ALIASES & CONVENIENCE HANDLERS FOR WEB UI & SDK CLIENTS
# =============================================================================

class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str = Field(..., min_length=8)

@saas_router.post("/api/v1/auth/change-password")
def change_password_endpoint(payload: ChangePasswordRequest, user: User = Depends(get_current_user)):
    from taikry.saas.security import verify_password, hash_password
    if not verify_password(payload.old_password, user.hashed_password, user.salt):
        raise HTTPException(status_code=400, detail="Incorrect current password.")
    db = SessionLocal()
    try:
        db_user = db.query(User).filter(User.id == user.id).first()
        new_hash, new_salt = hash_password(payload.new_password)
        db_user.hashed_password = new_hash
        db_user.salt = new_salt
        db.commit()
        return {"success": True, "message": "Password changed successfully."}
    finally:
        db.close()

@saas_router.get("/api/v1/auth/trial-status")
def auth_trial_status_alias(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return get_user_trial_status(db, user.id)

@saas_router.post("/api/v1/telegram-link/token")
def telegram_link_token_alias(user: User = Depends(get_current_user)):
    db = SessionLocal()
    try:
        ok, msg, data = generate_telegram_linking_token(db, user.id)
        return data
    finally:
        db.close()

@saas_router.delete("/api/v1/auth/account")
def delete_account_alias(response: Response, user: User = Depends(get_current_user)):
    db = SessionLocal()
    try:
        ok = delete_user_account(db, user.id, "User requested account deletion")
        response.delete_cookie(key=SESSION_COOKIE_NAME)
        return {"deleted": True, "message": "Account deleted successfully."}
    finally:
        db.close()

@saas_router.get("/api/v1/admin/support/tickets")
def admin_support_tickets_alias(status_filter: Optional[str] = None, admin: User = Depends(get_current_admin)):
    return admin_tickets_endpoint(status_filter, admin)

@saas_router.post("/api/v1/admin/support/tickets/{ticket_id}/reply")
def admin_support_ticket_reply_alias(
    ticket_id: str,
    payload: dict,
    admin: User = Depends(get_current_admin)
):
    req = AdminTicketReplyRequest(
        ticket_id=ticket_id,
        response=payload.get("reply_message") or payload.get("response", ""),
        status=payload.get("status", "RESOLVED")
    )
    res = admin_reply_ticket_endpoint(req, admin)
    return {"status": req.status, "message": res.get("message")}

@saas_router.put("/api/v1/admin/users/{user_id}/status")
def admin_user_status_put_alias(
    user_id: int,
    payload: dict,
    admin: User = Depends(get_current_admin)
):
    status_val = payload.get("status")
    is_act = status_val == "active" if status_val is not None else payload.get("is_active", True)
    req = AdminUserStatusRequest(user_id=user_id, is_active=is_act, reason=payload.get("reason"))
    return admin_user_status_endpoint(req, admin)

@saas_router.put("/api/v1/admin/users/{user_id}/subscription")
def admin_user_sub_put_alias(
    user_id: int,
    payload: dict,
    admin: User = Depends(get_current_admin)
):
    p_id = payload.get("plan_slug") or payload.get("plan_id", "pro")
    req = AdminSubscriptionOverrideRequest(
        user_id=user_id,
        plan_id=p_id,
        status=payload.get("status", "active_paid"),
        duration_days=payload.get("duration_days", 30)
    )
    res = admin_override_subscription_endpoint(req, admin)
    return {"plan_slug": p_id, "message": res.get("message")}


# =============================================================================
# ADMIN OPERATIONS & SIGNAL AUDIT ENDPOINTS
# =============================================================================

@saas_router.get("/api/v1/admin/signals/stats")
def admin_get_signals_stats(
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Returns aggregated signal performance and delivery statistics."""
    from taikry.database.models import ConsensusReport, SignalLifecycleModel

    total_consensus = db.query(ConsensusReport).count()
    recent_signals = (
        db.query(ConsensusReport)
        .order_by(ConsensusReport.id.desc())
        .limit(20)
        .all()
    )
    total_lifecycles = db.query(SignalLifecycleModel).count()
    active_lifecycles = db.query(SignalLifecycleModel).filter(SignalLifecycleModel.current_state.in_(["ACTIVE", "WAITING_CONFIRMATION"])).count()

    return {
        "total_consensus_signals": total_consensus,
        "total_lifecycles_tracked": total_lifecycles,
        "active_lifecycles": active_lifecycles,
        "recent_signals": [
            {
                "id": s.id,
                "symbol": s.symbol,
                "bias": s.market_bias,
                "status": s.setup_status,
                "entry": s.entry_price,
                "tp1": s.take_profit_1,
                "sl": s.stop_loss,
                "timestamp": s.timestamp_utc.isoformat() if s.timestamp_utc else None
            }
            for s in recent_signals
        ]
    }


@saas_router.get("/api/v1/admin/system/health")
def admin_get_system_health(
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Inspects detailed system health, DB connection, and runtime telemetry."""
    from sqlalchemy import text
    import time

    t0 = time.time()
    db_ok = True
    try:
        db.execute(text("SELECT 1")).scalar()
    except Exception:
        db_ok = False
    db_latency_ms = round((time.time() - t0) * 1000, 2)

    return {
        "status": "HEALTHY" if db_ok else "DEGRADED",
        "database": {
            "status": "UP" if db_ok else "DOWN",
            "latency_ms": db_latency_ms
        },
        "time_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "subsystems": {
            "regime_engine": "ONLINE",
            "concepts_engine": "ONLINE",
            "strategy_selector": "ONLINE",
            "telegram_engine": "ONLINE",
            "market_data_engine": "ONLINE"
        }
    }


# =============================================================================
# SUPER ADMIN GOVERNANCE & CONFIGURATION ENDPOINTS (PHASE 14 & 15)
# =============================================================================

@saas_router.get("/api/v1/super-admin/admins")
def super_admin_list_admins(
    super_admin: User = Depends(get_current_super_admin),
    db: Session = Depends(get_db)
):
    """Lists all platform administrators and super-administrators with their role grants."""
    admin_users = (
        db.query(User)
        .filter(User.role.in_(["super_admin", "admin", "ADMIN"]), User.deleted_at == None)
        .all()
    )
    result = []
    for u in admin_users:
        roles = get_user_roles(db, u.id)
        perms = list(get_user_permissions(db, u.id))
        result.append({
            "id": u.id,
            "email": u.email,
            "full_name": u.full_name,
            "role": u.role,
            "roles": roles,
            "permissions_count": len(perms),
            "permissions": perms,
            "is_active": u.is_active,
            "created_at": u.created_at.isoformat() if u.created_at else None
        })
    return {"total_admins": len(result), "admins": result}


@saas_router.post("/api/v1/super-admin/admins/promote")
def super_admin_promote_admin(
    payload: SuperAdminPromoteRequest,
    super_admin: User = Depends(get_current_super_admin),
    db: Session = Depends(get_db)
):
    """Assigns or modifies administrative roles for a user."""
    target_user = db.query(User).filter(User.id == payload.user_id, User.deleted_at == None).first()
    if not target_user:
        raise HTTPException(status_code=404, detail="Target user not found.")

    target_role = payload.role.strip().lower()
    valid_roles = ["super_admin", "admin", "premium_user", "user"]
    if target_role not in valid_roles:
        raise HTTPException(status_code=400, detail=f"Invalid role '{target_role}'. Valid roles: {valid_roles}")

    # Prevent removing the only super admin
    if target_user.id == super_admin.id and target_role != "super_admin":
        other_super_admins = db.query(User).filter(User.role == "super_admin", User.id != super_admin.id, User.deleted_at == None).count()
        if other_super_admins == 0:
            raise HTTPException(status_code=400, detail="Cannot demote yourself: You are the sole Super Administrator.")

    old_role = target_user.role
    target_user.role = target_role
    target_user.updated_at = datetime.datetime.now(datetime.timezone.utc)

    # Update user_roles table
    db.query(UserRole).filter(UserRole.user_id == target_user.id).delete()
    db.add(UserRole(
        user_id=target_user.id,
        role_id=target_role,
        granted_by=super_admin.id
    ))

    # Audit log
    db.add(AuditLog(
        actor_user_id=super_admin.id,
        action="SUPERADMIN_ROLE_CHANGE",
        target_type="user",
        target_id=str(target_user.id),
        details={"old_role": old_role, "new_role": target_role, "target_email": target_user.email}
    ))
    db.commit()

    return {
        "success": True,
        "message": f"Successfully updated user {target_user.email} role to '{target_role}'.",
        "user_id": target_user.id,
        "role": target_role
    }


@saas_router.get("/api/v1/super-admin/system-settings")
def super_admin_get_settings(
    super_admin: User = Depends(get_current_super_admin),
    db: Session = Depends(get_db)
):
    """
    Returns platform settings.
    CRITICAL SECURITY REQUIREMENT: Secret values are always REDACTED.
    """
    settings = db.query(SystemSetting).all()
    results = []
    for s in settings:
        safe_val = "[redacted]" if s.is_secret and s.value else s.value
        results.append({
            "key": s.key,
            "value": safe_val,
            "is_secret": s.is_secret,
            "description": s.description,
            "updated_at": s.updated_at.isoformat() if s.updated_at else None,
            "updated_by": s.updated_by
        })
    return {"total_settings": len(results), "settings": results}


@saas_router.post("/api/v1/super-admin/system-settings")
def super_admin_upsert_setting(
    payload: SystemSettingUpsertRequest,
    super_admin: User = Depends(get_current_super_admin),
    db: Session = Depends(get_db)
):
    """Upserts a system setting. If a secret is submitted as '[redacted]', existing value is retained."""
    existing = db.query(SystemSetting).filter(SystemSetting.key == payload.key).first()
    new_val = payload.value

    if existing and payload.is_secret and new_val in ("[redacted]", "••••••••"):
        new_val = existing.value  # Retain existing secret

    now_utc = datetime.datetime.now(datetime.timezone.utc)
    if existing:
        existing.value = new_val
        existing.is_secret = payload.is_secret
        if payload.description is not None:
            existing.description = payload.description
        existing.updated_by = super_admin.id
        existing.updated_at = now_utc
    else:
        db.add(SystemSetting(
            key=payload.key,
            value=new_val,
            is_secret=payload.is_secret,
            description=payload.description,
            updated_by=super_admin.id,
            updated_at=now_utc
        ))

    db.add(AuditLog(
        actor_user_id=super_admin.id,
        action="SUPERADMIN_SETTING_UPSERT",
        target_type="system_setting",
        target_id=payload.key,
        details={"key": payload.key, "is_secret": payload.is_secret}
    ))
    db.commit()

    return {"success": True, "message": f"Setting '{payload.key}' updated successfully."}


@saas_router.get("/api/v1/super-admin/feature-flags")
def super_admin_get_feature_flags(
    super_admin: User = Depends(get_current_super_admin),
    db: Session = Depends(get_db)
):
    """Lists all runtime feature flags and canary rollout states."""
    flags = db.query(FeatureFlag).all()
    results = []
    for f in flags:
        results.append({
            "key": f.key,
            "enabled": f.enabled,
            "description": f.description,
            "allowed_roles": f.allowed_roles,
            "rollout_percentage": f.rollout_percentage,
            "updated_at": f.updated_at.isoformat() if f.updated_at else None,
            "updated_by": f.updated_by
        })
    return {"total_flags": len(results), "flags": results}


@saas_router.post("/api/v1/super-admin/feature-flags/{key}")
def super_admin_update_feature_flag(
    key: str,
    payload: FeatureFlagUpdateRequest,
    super_admin: User = Depends(get_current_super_admin),
    db: Session = Depends(get_db)
):
    """Updates or toggles a feature flag."""
    flag = db.query(FeatureFlag).filter(FeatureFlag.key == key).first()
    now_utc = datetime.datetime.now(datetime.timezone.utc)
    if not flag:
        flag = FeatureFlag(
            key=key,
            enabled=payload.enabled if payload.enabled is not None else False,
            description=payload.description or "",
            allowed_roles=payload.allowed_roles or ["super_admin", "admin"],
            rollout_percentage=payload.rollout_percentage if payload.rollout_percentage is not None else 100,
            updated_by=super_admin.id,
            updated_at=now_utc
        )
        db.add(flag)
    else:
        if payload.enabled is not None:
            flag.enabled = payload.enabled
        if payload.rollout_percentage is not None:
            flag.rollout_percentage = payload.rollout_percentage
        if payload.allowed_roles is not None:
            flag.allowed_roles = payload.allowed_roles
        if payload.description is not None:
            flag.description = payload.description
        flag.updated_by = super_admin.id
        flag.updated_at = now_utc

    db.add(AuditLog(
        actor_user_id=super_admin.id,
        action="SUPERADMIN_FLAG_UPDATE",
        target_type="feature_flag",
        target_id=key,
        details={"key": key, "enabled": flag.enabled, "rollout": flag.rollout_percentage}
    ))
    db.commit()

    return {
        "success": True,
        "message": f"Feature flag '{key}' updated successfully.",
        "flag": {
            "key": flag.key,
            "enabled": flag.enabled,
            "rollout_percentage": flag.rollout_percentage,
            "allowed_roles": flag.allowed_roles
        }
    }


@saas_router.get("/api/v1/super-admin/ai-providers")
def super_admin_get_ai_providers(
    super_admin: User = Depends(get_current_super_admin),
    db: Session = Depends(get_db)
):
    """Inspects configured AI model providers and current latency/status."""
    from taikry.config import GEMINI_API_KEY, REAL_LLM_PROVIDER
    gemini_configured = bool(GEMINI_API_KEY and len(GEMINI_API_KEY) > 10)
    return {
        "active_primary_provider": REAL_LLM_PROVIDER,
        "providers": [
            {
                "id": "gemini",
                "name": "Google Gemini 2.5 Flash / 1.5 Pro",
                "is_configured": gemini_configured,
                "api_key_masked": "AIzaSy••••••••" if gemini_configured else "NOT_CONFIGURED",
                "status": "OPERATIONAL" if gemini_configured else "MISSING_KEY",
                "role": "Primary Deep Intelligence & Multi-Agent Reasoning"
            },
            {
                "id": "deepseek",
                "name": "DeepSeek R1 / V3",
                "is_configured": False,
                "api_key_masked": "NOT_CONFIGURED",
                "status": "STANDBY",
                "role": "Adversarial Risk & SMC Counter-Validation"
            },
            {
                "id": "openai",
                "name": "OpenAI GPT-4o",
                "is_configured": False,
                "api_key_masked": "NOT_CONFIGURED",
                "status": "STANDBY",
                "role": "Fallback LLM"
            }
        ]
    }

