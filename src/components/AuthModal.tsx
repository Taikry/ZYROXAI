import React, { useState } from 'react';
import { useLanguage } from '../hooks/useLanguage';
import { X, Lock, Mail, User as UserIcon, Send, AlertCircle, CheckCircle2, Loader2, ArrowRight } from 'lucide-react';

interface AuthModalProps {
  isOpen: boolean;
  onClose: () => void;
  initialMode?: 'signin' | 'signup';
}

export const AuthModal: React.FC<AuthModalProps> = ({
  isOpen,
  onClose,
  initialMode = 'signin'
}) => {
  const { isKhmer } = useLanguage();
  const [mode, setMode] = useState<'signin' | 'signup'>(initialMode);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [fullName, setFullName] = useState('');
  const [termsAccepted, setTermsAccepted] = useState(true);
  const [loading, setLoading] = useState(false);
  const [telegramLoading, setTelegramLoading] = useState(false);
  const [googleLoading, setGoogleLoading] = useState(false);
  const [showPhoneOtp, setShowPhoneOtp] = useState(false);
  const [phoneNumber, setPhoneNumber] = useState('');
  const [otpCode, setOtpCode] = useState('');
  const [otpSent, setOtpSent] = useState(false);
  const [phoneLoading, setPhoneLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [successMsg, setSuccessMsg] = useState<string | null>(null);

  if (!isOpen) return null;

  const handleGoogleLogin = async () => {
    setGoogleLoading(true);
    setErrorMsg(null);
    try {
      const res = await fetch('/api/v1/auth/google/status');
      const data = await res.json();
      if (data.status === 'NEEDS_CONFIGURATION') {
        setErrorMsg(
          isKhmer
            ? 'Google OAuth ត្រូវការការកំណត់ GOOGLE_CLIENT_ID នៅក្នុង .env (NEEDS_CONFIGURATION)។'
            : 'Google OAuth is awaiting credentials in .env (GOOGLE_CLIENT_ID / GOOGLE_CLIENT_SECRET).'
        );
        setGoogleLoading(false);
        return;
      }
      window.location.href = '/api/v1/auth/google/login';
    } catch (err: any) {
      setErrorMsg(err.message || 'Failed to connect to Google OAuth service');
      setGoogleLoading(false);
    }
  };

  const handleRequestPhoneOtp = async () => {
    setPhoneLoading(true);
    setErrorMsg(null);
    try {
      const res = await fetch('/api/v1/auth/phone/request-otp', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ phone_number: phoneNumber })
      });
      const data = await res.json();
      if (data.status === 'NEEDS_CONFIGURATION') {
        setErrorMsg(
          isKhmer
            ? 'សេវា Phone SMS OTP ត្រូវការ Twilio credentials នៅក្នុង .env (NEEDS_CONFIGURATION)។'
            : 'Phone SMS OTP service is awaiting Twilio credentials in .env (TWILIO_ACCOUNT_SID).'
        );
        setPhoneLoading(false);
        return;
      }
      if (!data.success) {
        setErrorMsg(data.message || 'Failed to send verification SMS');
        setPhoneLoading(false);
        return;
      }
      setOtpSent(true);
      setSuccessMsg(isKhmer ? 'កូដផ្ទៀងផ្ទាត់ត្រូវបានផ្ញើតាម SMS។' : 'Verification code sent via SMS.');
      setPhoneLoading(false);
    } catch (err: any) {
      setErrorMsg(err.message || 'Failed to send OTP');
      setPhoneLoading(false);
    }
  };

  const handleVerifyPhoneOtp = async () => {
    setPhoneLoading(true);
    setErrorMsg(null);
    try {
      const res = await fetch('/api/v1/auth/phone/verify-otp', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ phone_number: phoneNumber, code: otpCode })
      });
      const data = await res.json();
      if (!data.success) {
        setErrorMsg(data.message || 'Invalid or expired OTP');
        setPhoneLoading(false);
        return;
      }
      setSuccessMsg(isKhmer ? 'បានផ្ទៀងផ្ទាត់ជោគជ័យ! កំពុងបើកផ្ទាំងបញ្ជា...' : 'Phone verified! Redirecting to Dashboard...');
      setTimeout(() => {
        window.location.href = '/dashboard/?auth_success=phone';
      }, 800);
    } catch (err: any) {
      setErrorMsg(err.message || 'Verification failed');
      setPhoneLoading(false);
    }
  };

  const handleTelegramLogin = async () => {
    setTelegramLoading(true);
    setErrorMsg(null);
    try {
      const res = await fetch('/api/v1/auth/telegram/login?format=json');
      const data = await res.json();
      if (data.status === 'NEEDS_CONFIGURATION') {
        const bot = data.details?.bot_username || 'zyroxloginbot';
        setErrorMsg(
          isKhmer
            ? `Telegram Login ត្រូវការ Client ID ពី Bot @${bot} នៅក្នុង .env (TELEGRAM_LOGIN_CLIENT_ID)។`
            : `Telegram Login Bot @${bot} is awaiting configuration in .env (TELEGRAM_LOGIN_CLIENT_ID).`
        );
        setTelegramLoading(false);
        return;
      }
      if (data.auth_url) {
        window.location.href = data.auth_url;
      } else {
        window.location.href = '/api/v1/auth/telegram/login';
      }
    } catch (err: any) {
      setErrorMsg(err.message || 'Failed to connect to Telegram login service');
      setTelegramLoading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setErrorMsg(null);
    setSuccessMsg(null);

    try {
      if (mode === 'signup') {
        const res = await fetch('/api/v1/auth/signup', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            full_name: fullName,
            email,
            password,
            terms_accepted: termsAccepted,
            language: isKhmer ? 'kh' : 'en'
          })
        });
        const data = await res.json();
        if (!res.ok) throw new Error(data.detail || 'Sign up failed');
        setSuccessMsg(
          isKhmer
            ? 'គណនីបានបង្កើតជោគជ័យ! ការសាកល្បង ១៤ ថ្ងៃត្រូវបានធ្វើឱ្យសកម្ម។'
            : 'Account created successfully! 14-day institutional trial activated.'
        );
        setTimeout(() => {
          window.location.href = '/dashboard/';
        }, 1200);
      } else {
        const res = await fetch('/api/v1/auth/login', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ email, password })
        });
        const data = await res.json();
        if (!res.ok) throw new Error(data.detail || 'Sign in failed');
        setSuccessMsg(
          isKhmer ? 'បានផ្ទៀងផ្ទាត់ជោគជ័យ! កំពុងបើកផ្ទាំងបញ្ជា...' : 'Authenticated! Redirecting to Terminal Dashboard...'
        );
        setTimeout(() => {
          window.location.href = '/dashboard/';
        }, 800);
      }
    } catch (err: any) {
      setErrorMsg(err.message || 'Authentication error');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-3 sm:p-4 bg-black/85 backdrop-blur-md animate-fade-in overflow-y-auto">
      <div className="relative w-full max-w-md max-h-[92vh] overflow-y-auto bg-[#090F0C] border border-[#00E59B]/30 rounded-2xl p-5 sm:p-8 shadow-[0_0_50px_rgba(0,229,155,0.15)] my-auto">
        {/* Glow accent */}
        <div className="absolute -top-24 -right-24 w-48 h-48 bg-[#00E59B]/10 rounded-full blur-3xl pointer-events-none" />

        {/* Close Button */}
        <button
          onClick={onClose}
          className="absolute top-5 right-5 p-1.5 rounded-lg text-[#87938D] hover:text-[#F5F8F6] hover:bg-white/5 transition-colors cursor-pointer"
        >
          <X className="w-5 h-5" />
        </button>

        {/* Header */}
        <div className="mb-6">
          <div className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md bg-[#00E59B]/10 border border-[#00E59B]/20 text-[10px] font-mono text-[#00E59B] uppercase font-bold tracking-wider mb-2">
            ZYROX AI AUTHENTICATION
          </div>
          <h2 className="text-xl sm:text-2xl font-bold text-[#F5F8F6]">
            {mode === 'signup'
              ? (isKhmer ? 'ចាប់ផ្តើមសាកល្បង ១៤ ថ្ងៃឥតគិតថ្លៃ' : 'Start 14-Day Free Trial')
              : (isKhmer ? 'ចូលប្រើប្រាស់ ZYROX AI' : 'Sign In to ZYROX AI')}
          </h2>
          <p className="text-xs text-[#87938D] mt-1">
            {mode === 'signup'
              ? (isKhmer ? 'មិនត្រូវការកាតធនាគារឡើយ។ ចូលប្រើប្រាស់ប្រព័ន្ធ AI ពេញលេញ។' : 'No credit card required. Full institutional terminal access.')
              : (isKhmer ? 'ចូលទៅកាន់ផ្ទាំងបញ្ជាវិភាគទីផ្សារ និងទិន្នន័យផ្សាយផ្ទាល់។' : 'Access your trading intelligence terminal and live quotas.')}
          </p>
        </div>

        {/* Error / Success Alerts */}
        {errorMsg && (
          <div className="mb-4 p-3 rounded-xl bg-red-500/10 border border-red-500/30 text-red-400 text-xs flex items-start gap-2">
            <AlertCircle className="w-4 h-4 shrink-0 mt-0.5" />
            <span>{errorMsg}</span>
          </div>
        )}

        {successMsg && (
          <div className="mb-4 p-3 rounded-xl bg-[#00E59B]/10 border border-[#00E59B]/30 text-[#00E59B] text-xs flex items-start gap-2">
            <CheckCircle2 className="w-4 h-4 shrink-0 mt-0.5" />
            <span>{successMsg}</span>
          </div>
        )}

        {/* Social Authentication Row */}
        <div className="space-y-2.5 mb-4">
          {/* Telegram Login Button */}
          <button
            type="button"
            onClick={handleTelegramLogin}
            disabled={telegramLoading || googleLoading || phoneLoading || loading}
            className="w-full py-2.5 px-4 rounded-xl bg-gradient-to-r from-[#229ED9] to-[#1e87bb] hover:from-[#28a8e6] hover:to-[#229ED9] text-white font-bold text-xs sm:text-sm flex items-center justify-center gap-2.5 shadow-[0_4px_16px_rgba(34,158,217,0.3)] transition-all cursor-pointer disabled:opacity-60 disabled:cursor-not-allowed group"
          >
            {telegramLoading ? (
              <Loader2 className="w-4 h-4 animate-spin" />
            ) : (
              <Send className="w-4 h-4 group-hover:translate-x-0.5 transition-transform" />
            )}
            <span>
              {isKhmer
                ? (telegramLoading ? 'កំពុងភ្ជាប់ Telegram...' : 'បន្តជាមួយ Telegram')
                : (telegramLoading ? 'Connecting Telegram...' : 'Continue with Telegram')}
            </span>
          </button>

          {/* Google OAuth Button */}
          <button
            type="button"
            onClick={handleGoogleLogin}
            disabled={telegramLoading || googleLoading || phoneLoading || loading}
            className="w-full py-2.5 px-4 rounded-xl bg-[#1A1F26] hover:bg-[#252C36] border border-white/10 hover:border-white/20 text-[#F5F8F6] font-semibold text-xs sm:text-sm flex items-center justify-center gap-2.5 transition-all cursor-pointer disabled:opacity-60 disabled:cursor-not-allowed group"
          >
            {googleLoading ? (
              <Loader2 className="w-4 h-4 animate-spin text-red-400" />
            ) : (
              <svg className="w-4 h-4" viewBox="0 0 24 24">
                <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
                <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
                <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.06H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.94l2.85-2.22.81-.63z"/>
                <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.06l3.66 2.84c.87-2.6 3.3-4.52 6.16-4.52z"/>
              </svg>
            )}
            <span>
              {isKhmer
                ? (googleLoading ? 'កំពុងភ្ជាប់ Google...' : 'បន្តជាមួយ Google (OAuth 2.0)')
                : (googleLoading ? 'Connecting Google...' : 'Continue with Google')}
            </span>
          </button>

          {/* Phone SMS OTP Toggle Button */}
          <button
            type="button"
            onClick={() => setShowPhoneOtp(!showPhoneOtp)}
            className="w-full py-2 px-4 rounded-xl bg-transparent hover:bg-white/5 border border-white/10 text-[#87938D] hover:text-[#F5F8F6] text-xs font-mono flex items-center justify-center gap-2 transition-all cursor-pointer"
          >
            <span>📱 {showPhoneOtp ? (isKhmer ? 'លាក់ការផ្ទៀងផ្ទាត់លេខទូរស័ព្ទ' : 'Hide Phone Verification') : (isKhmer ? 'ចូលប្រើជាមួយលេខទូរស័ព្ទ (Phone SMS)' : 'Continue with Phone SMS OTP')}</span>
          </button>
        </div>

        {/* Collapsible Phone OTP Form */}
        {showPhoneOtp && (
          <div className="mb-4 p-3.5 rounded-xl bg-[#050807] border border-[#00E59B]/30 space-y-3 animate-fade-in">
            <span className="text-[11px] font-mono text-[#00E59B] font-bold block">
              📱 {isKhmer ? 'ផ្ទៀងផ្ទាត់លេខទូរស័ព្ទ (SMS OTP)' : 'Phone SMS OTP Verification'}
            </span>
            {!otpSent ? (
              <div className="flex gap-2">
                <input
                  type="tel"
                  placeholder="+85512345678"
                  value={phoneNumber}
                  onChange={(e) => setPhoneNumber(e.target.value)}
                  className="flex-1 px-3 py-2 bg-[#090F0C] border border-white/10 rounded-lg text-xs text-[#F5F8F6] font-mono focus:border-[#00E59B] outline-none"
                />
                <button
                  type="button"
                  onClick={handleRequestPhoneOtp}
                  disabled={phoneLoading || !phoneNumber}
                  className="px-3 py-2 bg-[#00E59B] hover:bg-[#39FFC0] text-[#050807] font-bold text-xs rounded-lg cursor-pointer disabled:opacity-50"
                >
                  {phoneLoading ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : (isKhmer ? 'ផ្ញើកូដ' : 'Send Code')}
                </button>
              </div>
            ) : (
              <div className="flex gap-2">
                <input
                  type="text"
                  placeholder="6-digit code"
                  maxLength={6}
                  value={otpCode}
                  onChange={(e) => setOtpCode(e.target.value)}
                  className="flex-1 px-3 py-2 bg-[#090F0C] border border-[#00E59B]/50 rounded-lg text-xs text-[#F5F8F6] font-mono text-center tracking-widest focus:border-[#00E59B] outline-none"
                />
                <button
                  type="button"
                  onClick={handleVerifyPhoneOtp}
                  disabled={phoneLoading || otpCode.length !== 6}
                  className="px-3 py-2 bg-[#00E59B] hover:bg-[#39FFC0] text-[#050807] font-bold text-xs rounded-lg cursor-pointer disabled:opacity-50"
                >
                  {phoneLoading ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : (isKhmer ? 'បញ្ជាក់' : 'Verify')}
                </button>
              </div>
            )}
          </div>
        )}

        {/* OR Divider */}
        <div className="relative flex items-center justify-center my-4">
          <div className="border-t border-white/10 w-full" />
          <span className="bg-[#090F0C] px-3 text-[10px] font-mono text-[#87938D] uppercase font-bold tracking-widest absolute">
            {isKhmer ? 'ឬជាមួយអ៊ីមែល' : 'OR WITH EMAIL'}
          </span>
        </div>

        {/* Email/Password Form */}
        <form onSubmit={handleSubmit} className="space-y-3.5">
          {mode === 'signup' && (
            <div>
              <label className="block text-xs font-medium text-[#87938D] mb-1">
                {isKhmer ? 'ឈ្មោះពេញ ឬឈ្មោះហៅក្រៅ' : 'Full Name or Trader Handle'}
              </label>
              <div className="relative">
                <UserIcon className="absolute left-3 top-3 w-4 h-4 text-[#87938D]" />
                <input
                  type="text"
                  value={fullName}
                  onChange={(e) => setFullName(e.target.value)}
                  placeholder="e.g. Alex Trader"
                  required={mode === 'signup'}
                  className="w-full pl-9 pr-3 py-2.5 rounded-xl bg-[#050807] border border-white/10 focus:border-[#00E59B] text-xs text-[#F5F8F6] placeholder-[#87938D]/50 outline-none transition-colors"
                />
              </div>
            </div>
          )}

          <div>
            <label className="block text-xs font-medium text-[#87938D] mb-1">
              {isKhmer ? 'អាសយដ្ឋានអ៊ីមែល' : 'Email Address'}
            </label>
            <div className="relative">
              <Mail className="absolute left-3 top-3 w-4 h-4 text-[#87938D]" />
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="alex@trader.com"
                required
                className="w-full pl-9 pr-3 py-2.5 rounded-xl bg-[#050807] border border-white/10 focus:border-[#00E59B] text-xs text-[#F5F8F6] placeholder-[#87938D]/50 outline-none transition-colors"
              />
            </div>
          </div>

          <div>
            <label className="block text-xs font-medium text-[#87938D] mb-1">
              {isKhmer ? 'ពាក្យសម្ងាត់ (យ៉ាងតិច ៨ តួអក្សរ)' : 'Password (min. 8 characters)'}
            </label>
            <div className="relative">
              <Lock className="absolute left-3 top-3 w-4 h-4 text-[#87938D]" />
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••••••"
                minLength={8}
                required
                className="w-full pl-9 pr-3 py-2.5 rounded-xl bg-[#050807] border border-white/10 focus:border-[#00E59B] text-xs text-[#F5F8F6] placeholder-[#87938D]/50 outline-none transition-colors"
              />
            </div>
          </div>

          {mode === 'signup' && (
            <div className="flex items-start gap-2 pt-1">
              <input
                type="checkbox"
                id="modal-terms"
                checked={termsAccepted}
                onChange={(e) => setTermsAccepted(e.target.checked)}
                required
                className="mt-0.5 rounded border-white/20 text-[#00E59B] focus:ring-0 bg-[#050807] cursor-pointer"
              />
              <label htmlFor="modal-terms" className="text-[11px] text-[#87938D] leading-tight">
                {isKhmer ? (
                  <>ខ្ញុំយល់ព្រមនឹង <span className="text-[#00E59B]">លក្ខខណ្ឌសេវាកម្ម</span> និង <span className="text-[#00E59B]">គោលការណ៍ភាពឯកជន</span></>
                ) : (
                  <>I agree to the <span className="text-[#00E59B]">Terms of Service</span> and <span className="text-[#00E59B]">Privacy Policy</span></>
                )}
              </label>
            </div>
          )}

          <button
            type="submit"
            disabled={loading || telegramLoading}
            className="w-full py-3 px-4 rounded-xl bg-gradient-to-r from-[#00E59B] to-[#39FFC0] hover:brightness-110 text-[#050807] font-bold text-xs flex items-center justify-center gap-2 shadow-[0_0_20px_rgba(0,229,155,0.3)] transition-all cursor-pointer disabled:opacity-60 disabled:cursor-not-allowed mt-2"
          >
            {loading ? (
              <Loader2 className="w-4 h-4 animate-spin" />
            ) : (
              <>
                <span>
                  {mode === 'signup'
                    ? (isKhmer ? 'ធ្វើឱ្យសកម្មការសាកល្បង ១៤ ថ្ងៃ' : 'Activate 14-Day Free Trial')
                    : (isKhmer ? 'ចូលប្រើប្រាស់ផ្ទាំងបញ្ជា' : 'Sign In to Dashboard')}
                </span>
                <ArrowRight className="w-3.5 h-3.5" />
              </>
            )}
          </button>
        </form>

        {/* Mode Switcher */}
        <div className="mt-5 text-center text-xs text-[#87938D]">
          {mode === 'signup' ? (
            <>
              {isKhmer ? 'មានគណនីរួចហើយ?' : 'Already have an account?'}{' '}
              <button
                type="button"
                onClick={() => { setMode('signin'); setErrorMsg(null); setSuccessMsg(null); }}
                className="text-[#00E59B] hover:underline font-semibold cursor-pointer ml-1"
              >
                {isKhmer ? 'ចូលប្រើប្រាស់' : 'Sign In'}
              </button>
            </>
          ) : (
            <>
              {isKhmer ? 'មិនទាន់មានគណនី?' : 'Need an account?'}{' '}
              <button
                type="button"
                onClick={() => { setMode('signup'); setErrorMsg(null); setSuccessMsg(null); }}
                className="text-[#00E59B] hover:underline font-semibold cursor-pointer ml-1"
              >
                {isKhmer ? 'សាកល្បងឥតគិតថ្លៃ ១៤ ថ្ងៃ' : 'Start 14-Day Free Trial'}
              </button>
            </>
          )}
        </div>
      </div>
    </div>
  );
};
