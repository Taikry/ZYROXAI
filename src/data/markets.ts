import { MarketAsset } from '../types';

export const MARKETS_DATA: MarketAsset[] = [
  {
    symbol: "XAUUSD",
    name: "Gold / US Dollar",
    category: "commodities",
    price: 2738.45,
    change24h: 1.42,
    high24h: 2746.20,
    low24h: 2718.80,
    bias: "STRONG_BUY",
    sentiment: 82,
    volatility: "MEDIUM",
    timeframe: "15M",
    spread: 1.2,
    sparkline: [2718, 2722, 2720, 2727, 2724, 2731, 2729, 2735, 2732, 2738.45],
    logo: "/assets/logos/xau.svg"
  },
  {
    symbol: "BTCUSDT",
    name: "Bitcoin / Tether",
    category: "crypto",
    price: 91420.00,
    change24h: 3.85,
    high24h: 92100.00,
    low24h: 87800.00,
    bias: "BUY",
    sentiment: 88,
    volatility: "HIGH",
    timeframe: "1H",
    spread: 0.5,
    sparkline: [87800, 88400, 89100, 88900, 90200, 90700, 90100, 91100, 90900, 91420],
    logo: "/assets/logos/btc.png"
  },
  {
    symbol: "ETHUSDT",
    name: "Ethereum / Tether",
    category: "crypto",
    price: 3345.20,
    change24h: 2.15,
    high24h: 3390.00,
    low24h: 3260.00,
    bias: "BUY",
    sentiment: 76,
    volatility: "HIGH",
    timeframe: "1H",
    spread: 0.8,
    sparkline: [3260, 3285, 3270, 3310, 3295, 3330, 3315, 3350, 3335, 3345.2],
    logo: "/assets/logos/eth.png"
  },
  {
    symbol: "EURUSD",
    name: "Euro / US Dollar",
    category: "forex",
    price: 1.0842,
    change24h: -0.28,
    high24h: 1.0890,
    low24h: 1.0825,
    bias: "WAIT",
    sentiment: 48,
    volatility: "LOW",
    timeframe: "15M",
    spread: 0.6,
    sparkline: [1.088, 1.087, 1.0875, 1.086, 1.085, 1.0845, 1.0855, 1.084, 1.0848, 1.0842],
    logo: "/assets/logos/eu.png"
  },
  {
    symbol: "GBPUSD",
    name: "British Pound / US Dollar",
    category: "forex",
    price: 1.2985,
    change24h: 0.35,
    high24h: 1.3020,
    low24h: 1.2940,
    bias: "BUY",
    sentiment: 64,
    volatility: "MEDIUM",
    timeframe: "15M",
    spread: 0.9,
    sparkline: [1.294, 1.295, 1.2945, 1.2965, 1.296, 1.2975, 1.297, 1.298, 1.2978, 1.2985],
    logo: "/assets/logos/gb.png"
  },
  {
    symbol: "SOLUSDT",
    name: "Solana / Tether",
    category: "crypto",
    price: 218.40,
    change24h: 5.62,
    high24h: 224.50,
    low24h: 204.00,
    bias: "STRONG_BUY",
    sentiment: 91,
    volatility: "HIGH",
    timeframe: "15M",
    spread: 1.1,
    sparkline: [204, 208, 206, 212, 210, 215, 213, 217, 216, 218.4],
    logo: "/assets/logos/sol.png"
  }
];

export const TIMEFRAMES = ["1M", "5M", "15M", "1H", "4H", "1D"] as const;

