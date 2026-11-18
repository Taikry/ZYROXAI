# ZYROX AI V6.1.1 — USER PROFILE & DEVICE HISTORY DATA INTEGRITY

**Product:** ZYROX AI — Intelligence Beyond The Market  
**Version:** V6.1.1 Production Hardening  
**Audited Endpoints:** `GET /api/v1/auth/me`, `POST /api/v1/auth/profile`  
**Web Module:** `taikry/web/app.js` (`loadAccountProfile()`)  
**Status:** IMPLEMENTED & VERIFIED  

---

## 1. Executive Summary

In version V6.1, UI mockups had populated the user profile endpoint with hardcoded personal details ("Heng Taikry", "0968288832", "@heng_taikry", "Jul 06, 2026", "Cambodia", and hardcoded Safari Mac device sessions from IP "175.100.52.54"). Any new user logging into the dashboard would see these placeholders instead of their actual account profile.

Under ZYROX AI V6.1.1:
1. **ZERO Hardcoded Placeholders:** All synthetic fallback constants have been eliminated from both the backend API and frontend JavaScript.
2. Unpopulated fields strictly return `None` (or empty strings in form inputs).
3. Session devices are read exclusively from real database records in the `user_sessions` table. If no sessions exist, an empty list (`[]`) is returned.
4. The `is_current` badge is granted **ONLY** when the session token hash in the database matches the caller's active session token hash.

---

## 2. Hardcoded Placeholders vs V6.1.1 Remediation

| Profile Field | Prior Value (Placeholder) | V6.1.1 Hardened Value |
| :--- | :--- | :--- |
| `user.full_name` | `"Heng Taikry"` | `user.full_name or None` |
| `user.mobile_phone` | `"0968288832"` | `user.phone_number or None` |
| `user.telegram` | `"@heng_taikry"` | `user.telegram_username or None` |
| `user.member_since` | `"Jul 06, 2026"` | `user.created_at.strftime(...) or None` |
| `user.country` | `"Cambodia"` | `user.country or None` |
| `user.is_verified` | `True` (Hardcoded) | `bool(user.is_verified)` |
| `devices` | Fabricated 2-device list (`175.100.52.54`) | Real rows from `user_sessions` table (or `[]`) |
| `is_current` | Forced `True` on device 0 | Exact match: `token_hash == hash_token(raw_token)` |

---

## 3. Database Schema Migration

To support persistent country assignment without schema collisions:
- Added `country = Column(String(64), nullable=True, default=None)` to the `User` model (`taikry/database/models.py`).
- Added idempotent SQLite/PostgreSQL column check to `taikry/database/migrate_v61_auth.py`.

---

## 4. Verification Suite

Tested and verified in:
1. `tests/test_v61_profile.py`:
   - `test_auth_me_unauthenticated`: Returns 401.
   - `test_auth_me_returns_profile_spec`: Authenticated profile matches user schema.
   - `test_update_profile_phone_and_language`: User can update their real mobile phone and language.
2. `tests/test_v611_profile_integrity.py`:
   - `test_profile_zero_hardcoded_placeholders_for_empty_user`: Confirms that an empty profile user returns `None` across all unset fields and `devices == []`.
   - `test_profile_current_device_exact_token_match`: Proves that among multiple session records, only the authentic active session token receives `is_current=True`.
