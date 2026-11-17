# ZYROX AI — Google OAuth 2.0 Setup Guide

This guide provides step-by-step instructions to configure **Google Sign-In** for ZYROX AI using OAuth 2.0 with PKCE (Proof Key for Code Exchange).

---

## 1. Google Cloud Console Setup

### Step 1: Create or Select a Google Cloud Project
1. Navigate to the [Google Cloud Console](https://console.cloud.google.com/).
2. In the top navigation bar, select your existing project or click **New Project** (e.g. `ZYROX AI`).

### Step 2: Configure the OAuth Consent Screen
1. In the left navigation menu, go to **APIs & Services** > **OAuth consent screen**.
2. Select **External** user type and click **Create**.
3. Fill in the App Information:
   * **App name:** `ZYROX AI`
   * **User support email:** Your email address (e.g. `taikry@zyrox.ai`)
   * **Developer contact email:** Your email address
4. Click **Save and Continue**.
5. Under **Scopes**, click **Add or Remove Scopes** and select:
   * `openid`
   * `.../auth/userinfo.email`
   * `.../auth/userinfo.profile`
6. Click **Save and Continue**.
7. If your app is in "Testing" mode, add your test Google accounts under **Test users**.

---

## 2. Create OAuth 2.0 Client Credentials

1. Go to **APIs & Services** > **Credentials**.
2. Click **+ Create Credentials** at the top and select **OAuth client ID**.
3. Set **Application type** to **Web application**.
4. Set **Name** to `ZYROX AI Web Client`.
5. Under **Authorized JavaScript origins**, add:
   * `http://localhost:8000`
   * `http://127.0.0.1:8000`
   * `http://localhost:3000`
   * `https://taikry-ai-trading.onrender.com`
6. Under **Authorized redirect URIs**, add:
   * `http://localhost:8000/api/v1/auth/google/callback`
   * `http://127.0.0.1:8000/api/v1/auth/google/callback`
   * `https://taikry-ai-trading.onrender.com/api/v1/auth/google/callback`
7. Click **Create**.
8. A modal will appear displaying your **Client ID** and **Client Secret**. Copy both values.

---

## 3. Configure Environment Variables

### Local Development (`.env`)
Add the following to your root `.env` file:

```env
GOOGLE_CLIENT_ID=your_client_id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=GOCSPX-your_client_secret_here
GOOGLE_REDIRECT_URI=http://localhost:8000/api/v1/auth/google/callback
```

### Production (Render Dashboard)
1. Open the [Render Dashboard](https://dashboard.render.com/).
2. Select your `zyroxai` web service.
3. Go to **Environment** tab.
4. Add the following environment variables:
   * `GOOGLE_CLIENT_ID`: `your_client_id.apps.googleusercontent.com`
   * `GOOGLE_CLIENT_SECRET`: `GOCSPX-your_client_secret_here`
   * `GOOGLE_REDIRECT_URI`: `https://taikry-ai-trading.onrender.com/api/v1/auth/google/callback`
5. Click **Save Changes** (Render will redeploy with the new credentials).

---

## 4. Verification & Testing

### Check Configuration Status via API
You can verify that the server recognizes your Google OAuth configuration:

```bash
curl -s http://localhost:8000/api/v1/auth/google/status
```

**Expected JSON Response:**
```json
{
  "configured": true,
  "status": "READY",
  "redirect_uri": "http://localhost:8000/api/v1/auth/google/callback",
  "required_env_vars": [],
  "note": "Google OAuth is ready for production activation upon providing Google Cloud Console credentials."
}
```

### Test User Journey
1. Open the website at `http://localhost:8000` (or `https://taikry-ai-trading.onrender.com`).
2. Click **Sign In** or **Get Started**.
3. In the authentication modal, click **Continue with Google** / **បន្តជាមួយ Google**.
4. You will be redirected to Google's consent screen.
5. Select your Google account and authorize the application.
6. Google redirects back to `/api/v1/auth/google/callback`:
   * Server validates PKCE S256 code challenge and anti-forgery state.
   * Server cryptographically verifies the Google ID token against Google's public JWKS.
   * New users are automatically provisioned with a **14-day Pro Trial**.
   * A 30-day `zyrox_session` cookie is issued.
   * You are redirected directly into `/dashboard/` with a success toast notification!
