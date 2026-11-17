import React from 'react';

interface AnimatedLogoProps {
  size?: 'sm' | 'md' | 'lg' | 'hero';
  showText?: boolean;
  className?: string;
}

export const AnimatedLogo: React.FC<AnimatedLogoProps> = ({
  size = 'md',
  showText = true,
  className = '',
}) => {
  const iconSizes = {
    sm: 'w-7 h-7',
    md: 'w-9 h-9',
    lg: 'w-14 h-14',
    hero: 'w-20 h-20 md:w-28 md:h-28',
  };

  const textSizes = {
    sm: 'text-base font-bold',
    md: 'text-xl font-extrabold',
    lg: 'text-2xl font-black tracking-wider',
    hero: 'text-3xl md:text-5xl font-black tracking-wider',
  };

  return (
    <div className={`inline-flex items-center gap-3 select-none group ${className}`}>
      {/* Animated Icon Badge */}
      <div className={`relative ${iconSizes[size]} flex items-center justify-center`}>
        {/* Ambient Glow */}
        <div className="absolute inset-0 rounded-2xl bg-gradient-to-tr from-[#00E59B]/30 via-[#39FFC0]/20 to-transparent blur-md group-hover:blur-lg transition-all duration-500 scale-110" />

        {/* Outer Orbit Ring (rotates slowly) */}
        <div className="absolute inset-[-4px] rounded-2xl border border-[#00E59B]/20 animate-radar-spin pointer-events-none" />

        {/* SVG Shield & Monogram */}
        <div className="relative w-full h-full rounded-xl overflow-hidden p-1 bg-[#090F0C] border border-[#00E59B]/30 shadow-[0_0_15px_rgba(0,229,155,0.2)] group-hover:border-[#00E59B]/60 transition-colors duration-300">
          <svg
            viewBox="0 0 512 512"
            fill="none"
            xmlns="http://www.w3.org/2000/svg"
            className="w-full h-full"
          >
            <defs>
              <linearGradient id="logoEmeraldGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stopColor="#39FFC0" />
                <stop offset="50%" stopColor="#00E59B" />
                <stop offset="100%" stopColor="#00B981" />
              </linearGradient>
            </defs>

            {/* Inner Shield */}
            <polygon
              points="256,64 424,144 424,368 256,448 88,368 88,144"
              fill="#060B09"
              stroke="#00E59B"
              strokeOpacity="0.3"
              strokeWidth="14"
            />

            {/* High Impact 'Z' Monogram */}
            <path
              d="M168 184 H344 L168 328 H344"
              fill="none"
              stroke="url(#logoEmeraldGrad)"
              strokeWidth="42"
              strokeLinecap="round"
              strokeLinejoin="round"
            />

            {/* Central Energy Spark */}
            <circle cx="256" cy="256" r="14" fill="#39FFC0" />
          </svg>
        </div>
      </div>

      {/* Brand Text */}
      {showText && (
        <div className="flex flex-col">
          <div className="flex items-center gap-1.5 leading-none">
            <span className={`text-[#F5F8F6] tracking-tight ${textSizes[size]}`}>
              ZYROX
            </span>
            <span className={`text-[#00E59B] ${textSizes[size]}`}>
              AI
            </span>
          </div>
          <span className="text-[10px] uppercase font-mono tracking-[0.2em] text-[#87938D] group-hover:text-[#39FFC0] transition-colors mt-0.5">
            Trading Intelligence
          </span>
        </div>
      )}
    </div>
  );
};

