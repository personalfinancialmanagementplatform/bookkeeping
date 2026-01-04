/**
 * 股票數據 Hook
 * 檔案位置: frontend/src/hooks/useStockData.js
 */

import { useState, useEffect, useCallback, useRef } from 'react';

const API_BASE = 'http://localhost:5005';

/**
 * 取得單一股票即時報價
 */
export const useStockQuote = (symbol, refreshInterval = 60000) => {
  const [quote, setQuote] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchQuote = useCallback(async () => {
    if (!symbol) return;
    
    setLoading(true);
    setError(null);
    
    try {
      const response = await fetch(`${API_BASE}/api/stocks/quote/${symbol}`);
      const data = await response.json();
      
      if (data.success) {
        setQuote(data);
      } else {
        setError(data.error || '無法取得報價');
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, [symbol]);

  useEffect(() => {
    fetchQuote();
    
    if (refreshInterval > 0) {
      const interval = setInterval(fetchQuote, refreshInterval);
      return () => clearInterval(interval);
    }
  }, [fetchQuote, refreshInterval]);

  return { quote, loading, error, refresh: fetchQuote };
};


/**
 * 批次取得多檔股票報價
 */
export const useBatchQuotes = (symbols, refreshInterval = 60000) => {
  const [quotes, setQuotes] = useState({});
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [lastUpdated, setLastUpdated] = useState(null);

  const fetchQuotes = useCallback(async () => {
    if (!symbols || symbols.length === 0) return;
    
    setLoading(true);
    setError(null);
    
    try {
      const response = await fetch(`${API_BASE}/api/stocks/quotes`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ symbols })
      });
      
      const data = await response.json();
      setQuotes(data);
      setLastUpdated(new Date());
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, [JSON.stringify(symbols)]);

  useEffect(() => {
    fetchQuotes();
    
    if (refreshInterval > 0) {
      const interval = setInterval(fetchQuotes, refreshInterval);
      return () => clearInterval(interval);
    }
  }, [fetchQuotes, refreshInterval]);

  return { quotes, loading, error, lastUpdated, refresh: fetchQuotes };
};


/**
 * 股票搜尋
 */
export const useStockSearch = () => {
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const debounceRef = useRef(null);

  const search = useCallback(async (query) => {
    if (!query || query.length < 1) {
      setResults([]);
      return;
    }

    if (debounceRef.current) {
      clearTimeout(debounceRef.current);
    }

    debounceRef.current = setTimeout(async () => {
      setLoading(true);
      
      try {
        const response = await fetch(
          `${API_BASE}/api/stocks/search?q=${encodeURIComponent(query)}`
        );
        const data = await response.json();
        setResults(data);
      } catch (err) {
        console.error('搜尋失敗:', err);
        setResults([]);
      } finally {
        setLoading(false);
      }
    }, 300);
  }, []);

  const clear = useCallback(() => {
    setResults([]);
  }, []);

  return { results, loading, search, clear };
};


/**
 * 持倉即時價格更新
 */
export const useHoldingsWithPrices = (holdings, refreshInterval = 60000) => {
  const [holdingsWithPrices, setHoldingsWithPrices] = useState([]);
  const [loading, setLoading] = useState(false);
  const [lastUpdated, setLastUpdated] = useState(null);

  const updatePrices = useCallback(async () => {
    if (!holdings || holdings.length === 0) {
      setHoldingsWithPrices([]);
      return;
    }

    setLoading(true);
    
    try {
      const symbols = holdings
        .filter(h => h.symbol && h.asset_type !== 'cash')
        .map(h => h.symbol);
      
      if (symbols.length === 0) {
        setHoldingsWithPrices(holdings);
        setLastUpdated(new Date());
        setLoading(false);
        return;
      }
      
      const response = await fetch(`${API_BASE}/api/holdings/refresh-prices`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ symbols })
      });
      
      const data = await response.json();
      
      const priceMap = {};
      data.updated.forEach(item => {
        priceMap[item.symbol] = item;
      });
      
      const updatedHoldings = holdings.map(holding => {
        const priceData = priceMap[holding.symbol];
        
        if (priceData) {
          const currentPrice = priceData.price;
          const quantity = holding.quantity || 0;
          const costPrice = holding.average_cost || holding.cost_price || 0;
          const marketValue = currentPrice * quantity;
          const costBasis = costPrice * quantity;
          const unrealizedPnL = marketValue - costBasis;
          const unrealizedPnLPercent = costBasis > 0 
            ? (unrealizedPnL / costBasis) * 100 
            : 0;
          
          return {
            ...holding,
            current_price: currentPrice,
            price_change: priceData.change,
            price_change_percent: priceData.change_percent,
            market_value: marketValue,
            unrealized_pnl: unrealizedPnL,
            unrealized_pnl_percent: unrealizedPnLPercent,
            price_updated: true
          };
        }
        
        const costPrice = holding.average_cost || holding.cost_price || 0;
        return {
          ...holding,
          current_price: costPrice,
          market_value: costPrice * (holding.quantity || 0),
          unrealized_pnl: 0,
          unrealized_pnl_percent: 0,
          price_updated: false
        };
      });
      
      setHoldingsWithPrices(updatedHoldings);
      setLastUpdated(new Date());
    } catch (err) {
      console.error('更新價格失敗:', err);
      setHoldingsWithPrices(holdings.map(h => ({
        ...h,
        current_price: h.average_cost || h.cost_price || 0,
        market_value: (h.average_cost || h.cost_price || 0) * (h.quantity || 0),
        price_updated: false
      })));
    } finally {
      setLoading(false);
    }
  }, [holdings]);

  useEffect(() => {
    updatePrices();
    
    if (refreshInterval > 0) {
      const interval = setInterval(updatePrices, refreshInterval);
      return () => clearInterval(interval);
    }
  }, [updatePrices, refreshInterval]);

  const summary = {
    totalMarketValue: holdingsWithPrices.reduce(
      (sum, h) => sum + (h.market_value || 0), 0
    ),
    totalCost: holdingsWithPrices.reduce(
      (sum, h) => sum + ((h.average_cost || h.cost_price || 0) * (h.quantity || 0)), 0
    ),
    totalUnrealizedPnL: holdingsWithPrices.reduce(
      (sum, h) => sum + (h.unrealized_pnl || 0), 0
    ),
    holdingsCount: holdingsWithPrices.length
  };
  
  summary.totalUnrealizedPnLPercent = summary.totalCost > 0 
    ? (summary.totalUnrealizedPnL / summary.totalCost) * 100 
    : 0;

  return { 
    holdings: holdingsWithPrices, 
    summary,
    loading, 
    lastUpdated, 
    refresh: updatePrices 
  };
};


/**
 * 風險問卷
 */
export const useRiskQuestionnaire = () => {
  const [questions, setQuestions] = useState([]);
  const [answers, setAnswers] = useState({});
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const loadQuestions = async () => {
      try {
        const response = await fetch(`${API_BASE}/api/risk-assessment/questions`);
        const data = await response.json();
        setQuestions(data.questions);
      } catch (err) {
        console.error('載入問卷失敗:', err);
      }
    };
    loadQuestions();
  }, []);

  const setAnswer = useCallback((questionId, value) => {
    setAnswers(prev => ({
      ...prev,
      [questionId]: value
    }));
  }, []);

  const calculateResult = useCallback(async () => {
    if (Object.keys(answers).length < 5) {
      return null;
    }

    setLoading(true);
    
    try {
      const response = await fetch(`${API_BASE}/api/risk-assessment/calculate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ answers })
      });
      
      const data = await response.json();
      setResult(data);
      return data;
    } catch (err) {
      console.error('計算失敗:', err);
      return null;
    } finally {
      setLoading(false);
    }
  }, [answers]);

  const reset = useCallback(() => {
    setAnswers({});
    setResult(null);
  }, []);

  const isComplete = Object.keys(answers).length >= 5;

  return {
    questions,
    answers,
    setAnswer,
    calculateResult,
    result,
    loading,
    isComplete,
    reset
  };
};


/**
 * 配置建議
 */
export const usePortfolioRecommendation = () => {
  const [recommendation, setRecommendation] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const getRecommendation = useCallback(async ({
    amount,
    risk_level = 'moderate',
    goal = 'wealth_growth',
    age,
    existing_holdings = []
  }) => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await fetch(`${API_BASE}/api/portfolio/recommend`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          amount,
          risk_level,
          goal,
          age,
          existing_holdings
        })
      });
      
      if (!response.ok) {
        const errData = await response.json();
        throw new Error(errData.error || '取得建議失敗');
      }
      
      const data = await response.json();
      setRecommendation(data);
      return data;
    } catch (err) {
      setError(err.message);
      return null;
    } finally {
      setLoading(false);
    }
  }, []);

  const getQuickRecommendation = useCallback(async (amount, profile = 'balanced') => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await fetch(
        `${API_BASE}/api/portfolio/quick-recommend?amount=${amount}&profile=${profile}`
      );
      const data = await response.json();
      setRecommendation(data);
      return data;
    } catch (err) {
      setError(err.message);
      return null;
    } finally {
      setLoading(false);
    }
  }, []);

  const clear = useCallback(() => {
    setRecommendation(null);
    setError(null);
  }, []);

  return {
    recommendation,
    loading,
    error,
    getRecommendation,
    getQuickRecommendation,
    clear
  };
};


export default {
  useStockQuote,
  useBatchQuotes,
  useStockSearch,
  useHoldingsWithPrices,
  useRiskQuestionnaire,
  usePortfolioRecommendation
};