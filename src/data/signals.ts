import { SignalPreview } from '../types';

export const DEMO_SIGNALS: { buy: SignalPreview; sell: SignalPreview } = {
  buy: {
    symbol: "XAUUSD",
    marketName: "Gold / US Dollar",
    direction: "BUY",
    entry: 2724.50,
    sl: 2717.00,
    tp1: 2739.50,
    tp2: 2750.75,
    tp3: 2762.00,
    riskReward: "1 : 3.5",
    riskPercent: "1.0%",
    confidence: 94.8,
    status: "VERIFIED",
    confluenceCount: 5,
    reasonsEn: [
      "Bullish Order Block mitigation at 15M discount zone ($2,723 - $2,725)",
      "Fair Value Gap (FVG) consequent encroachment tested with rejection wicks",
      "Sell-side liquidity sweep of Asian session lows prior to London open",
      "Break of Structure (BOS) confirmed on 1H timeframe with high volume",
      "Triple EMA alignment (EMA 20 > 50 > 200) signaling pro-trend bias"
    ],
    reasonsKh: [
      "តម្លៃប៉ះតំបន់ Order Block ទិញលើ 15M Discount Zone ($2,723 - $2,725)",
      "តម្លៃត្រឡប់មកបំពេញតុល្យភាព FVG រួចបង្កើតកន្ទុយច្រានឡើងលើ",
      "ការបោសសម្អាត Liquidity បាតផ្សារអាស៊ី មុនម៉ោង London Open",
      "ការបំបែករចនាសម្ព័ន្ធ BOS បញ្ជាក់លើ 1H ជាមួយបរិមាណធំ",
      "ខ្សែ EMA 20 > 50 > 200 បញ្ជាក់ពីកម្លាំងរុញច្រានបន្តឡើង"
    ]
  },
  sell: {
    symbol: "BTCUSDT",
    marketName: "Bitcoin / Tether",
    direction: "SELL",
    entry: 92450.00,
    sl: 93800.00,
    tp1: 89750.00,
    tp2: 87800.00,
    tp3: 85200.00,
    riskReward: "1 : 3.8",
    riskPercent: "1.0%",
    confidence: 92.4,
    status: "IN_PLAY",
    confluenceCount: 4,
    reasonsEn: [
      "Bearish Change of Character (CHoCH) detected on 1-Hour chart",
      "Buy-side liquidity swept above psychological level $93,000",
      "4-Hour Bearish Fair Value Gap (FVG) retested with heavy institutional selling",
      "RSI Bearish Divergence confirmed on both 1H and 4H timeframes"
    ],
    reasonsKh: [
      "ការផ្លាស់ប្តូរចរិតលក្ខណៈធ្លាក់ចុះ (Bearish CHoCH) លើតារាង 1 ម៉ោង",
      "ការបោសសម្អាត Buy-side Liquidity លើសកម្រិតចិត្តសាស្ត្រ $93,000",
      "តម្លៃឡើងប៉ះ Bearish FVG លើ 4H រួចមានសម្ពាធលក់យ៉ាងខ្លាំង",
      "សញ្ញា RSI Bearish Divergence បញ្ជាក់លើ 1H និង 4H ក្នុងពេលតែមួយ"
    ]
  }
};

