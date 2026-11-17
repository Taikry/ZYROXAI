import { useState, useEffect, useCallback, useRef } from 'react';
import { MARKETS_DATA } from '../data/markets';
import { MarketAsset } from '../types';

export interface LivePriceDetails {
  symbol: string;
  price: number;
  bid: number;
  ask: number;
  spread: number;
  direction?: 'up' | 'down';
  provider: string;
  freshness: string;
  timestamp: string;
}

export interface UseRealtimeMarketsResult {
  markets: MarketAsset[];
  isLive: boolean;
  lastUpdated: Date | null;
  providerStatus: string;
  refresh: () => void;
  getAsset: (symbol: string) => MarketAsset | undefined;
}

export function useRealtimeMarkets(): UseRealtimeMarketsResult {
  const [markets, setMarkets] = useState<MarketAsset[]>(MARKETS_DATA);
  const [isLive, setIsLive] = useState<boolean>(false);
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null);
  const [providerStatus, setProviderStatus] = useState<string>('Connecting to Institutional Feed...');
  const priceHistoryRef = useRef<Record<string, number[]>>({});

  const fetchLivePrices = useCallback(async () => {
    try {
      const response = await fetch('/api/v1/realtime-prices');
      if (!response.ok) {
        throw new Error(`HTTP error ${response.status}`);
      }

      const data = await response.json();
      const rawPrices = data.prices as Record<string, any>;

      if (!rawPrices || typeof rawPrices !== 'object') {
        return;
      }

      setMarkets((prevMarkets) => {
        return prevMarkets.map((asset) => {
          const liveData = rawPrices[asset.symbol];
          if (!liveData || typeof liveData.price !== 'number' || liveData.price <= 0) {
            return asset;
          }

          const currentPrice = liveData.price;
          const prevPrice = asset.price;
          const direction = currentPrice >= prevPrice ? 'up' : 'down';

          // Update sparkline history
          if (!priceHistoryRef.current[asset.symbol]) {
            priceHistoryRef.current[asset.symbol] = [...asset.sparkline];
          }
          const history = priceHistoryRef.current[asset.symbol];
          history.push(currentPrice);
          if (history.length > 12) {
            history.shift();
          }

          // Calculate dynamic 24h change relative to first recorded candle/anchor
          const initial = history[0] || currentPrice;
          const calculatedChange = Number((((currentPrice - initial) / initial) * 100).toFixed(2));
          const change24h = asset.change24h !== undefined ? (liveData.change_24h ?? asset.change24h) : calculatedChange;

          return {
            ...asset,
            price: currentPrice,
            change24h: change24h,
            spread: liveData.spread ?? asset.spread,
            high24h: Math.max(asset.high24h, currentPrice),
            low24h: Math.min(asset.low24h, currentPrice),
            sparkline: [...history],
            bias: direction === 'up' ? 'BUY' : 'SELL',
          };
        });
      });

      setIsLive(true);
      setLastUpdated(new Date());
      setProviderStatus('Active Tickstream: OANDA v20 / Binance / Institutional Composite');
    } catch (err) {
      console.warn('Realtime price sync error (using local cache):', err);
      // Keep existing data, maintain operational state
    }
  }, []);

  useEffect(() => {
    fetchLivePrices();
    const interval = setInterval(fetchLivePrices, 4000);
    return () => clearInterval(interval);
  }, [fetchLivePrices]);

  const getAsset = useCallback(
    (symbol: string) => {
      return markets.find((m) => m.symbol.toUpperCase() === symbol.toUpperCase());
    },
    [markets]
  );

  return {
    markets,
    isLive,
    lastUpdated,
    providerStatus,
    refresh: fetchLivePrices,
    getAsset,
  };
}
