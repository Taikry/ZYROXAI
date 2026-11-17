export type Language = 'en' | 'kh';

export interface MarketAsset {
  symbol: string;
  name: string;
  category: 'commodities' | 'crypto' | 'forex';
  price: number;
  change24h: number;
  high24h: number;
  low24h: number;
  bias: 'STRONG_BUY' | 'BUY' | 'WAIT' | 'SELL' | 'STRONG_SELL';
  sentiment: number; // 0 - 100
  volatility: 'LOW' | 'MEDIUM' | 'HIGH';
  timeframe: string;
  sparkline: number[];
  logo?: string;
  spread: number;
}

export interface AIAgent {
  id: string;
  nameEn: string;
  nameKh: string;
  roleEn: string;
  roleKh: string;
  descriptionEn: string;
  descriptionKh: string;
  status: 'ACTIVE' | 'PROCESSING' | 'CONSENSUS' | 'STANDBY';
  capabilitiesEn: string[];
  capabilitiesKh: string[];
  icon: string;
  latencyMs: number;
  confidence: number;
}

export interface PlatformFeature {
  id: string;
  titleEn: string;
  titleKh: string;
  descEn: string;
  descKh: string;
  icon: string;
  badgeEn?: string;
  badgeKh?: string;
  metrics?: string;
}

export interface TechnicalConcept {
  id: string;
  name: string;
  abbr: string;
  category: 'SMC' | 'ICT' | 'CLASSIC' | 'STRUCTURE';
  titleEn: string;
  titleKh: string;
  descEn: string;
  descKh: string;
  ruleEn: string;
  ruleKh: string;
  badge: string;
  action: 'ENTRY' | 'TARGET' | 'INVALIDATION' | 'FILTER';
}

export interface SignalPreview {
  symbol: string;
  marketName: string;
  direction: 'BUY' | 'SELL';
  entry: number;
  sl: number;
  tp1: number;
  tp2: number;
  tp3: number;
  riskReward: string;
  riskPercent: string;
  confidence: number;
  status: 'VERIFIED' | 'TARGET_HIT' | 'IN_PLAY';
  confluenceCount: number;
  reasonsEn: string[];
  reasonsKh: string[];
}

export interface ArchitectureNode {
  step: number;
  titleEn: string;
  titleKh: string;
  tech: string;
  roleEn: string;
  roleKh: string;
  detailEn: string;
  detailKh: string;
  icon: string;
}

