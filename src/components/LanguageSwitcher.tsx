import React from 'react';
import { useLanguage } from '../hooks/useLanguage';
import { Globe } from 'lucide-react';

export const LanguageSwitcher: React.FC<{ compact?: boolean }> = ({ compact = false }) => {
  const { language, setLanguage } = useLanguage();

  return (
    <div className="inline-flex items-center p-1 rounded-xl bg-[#090F0C]/90 border border-[#00E59B]/20 backdrop-blur-md shadow-inner">
      {!compact && (
        <span className="pl-2 pr-1.5 text-[#87938D]">
          <Globe className="w-3.5 h-3.5 text-[#00E59B]" />
        </span>
      )}
      
      <button
        type="button"
        onClick={() => setLanguage('en')}
        className={`px-2.5 py-1 text-xs font-semibold rounded-lg transition-all duration-200 cursor-pointer ${
          language === 'en'
            ? 'bg-[#00E59B] text-[#050807] shadow-[0_0_12px_rgba(0,229,155,0.4)]'
            : 'text-[#87938D] hover:text-[#F5F8F6]'
        }`}
        aria-label="Switch to English"
      >
        EN
      </button>

      <button
        type="button"
        onClick={() => setLanguage('kh')}
        className={`px-2.5 py-1 text-xs font-semibold rounded-lg transition-all duration-200 cursor-pointer ${
          language === 'kh'
            ? 'bg-[#00E59B] text-[#050807] shadow-[0_0_12px_rgba(0,229,155,0.4)]'
            : 'text-[#87938D] hover:text-[#F5F8F6]'
        }`}
        aria-label="Switch to Khmer"
      >
        ខ្មែរ
      </button>
    </div>
  );
};

