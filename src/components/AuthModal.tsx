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
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [successMsg, setSuccessMsg] = useState<string | null>(null);

  if (!isOpen) return null;

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

        {/* 1-Click Telegram Login Button (OIDC) */}
        <button
          type="button"
          onClick={handleTelegramLogin}
          disabled={telegramLoading || loading}
          className="w-full py-3 px-4 rounded-xl bg-gradient-to-r from-[#229ED9] to-[#1e87bb] hover:from-[#28a8e6] hover:to-[#229ED9] text-white font-bold text-sm flex items-center justify-center gap-2.5 shadow-[0_4px_20px_rgba(34,158,217,0.35)] transition-all cursor-pointer disabled:opacity-60 disabled:cursor-not-allowed group mb-4"
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
