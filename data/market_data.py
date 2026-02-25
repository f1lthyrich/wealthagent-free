import ccxt
import yfinance as yf
import json
import os
import time
from datetime import datetime

class MarketData:
    def __init__(self):
        self.crypto_prices = {}
        self.stock_prices = {}
        self.cache_dir = "data/cache"
        os.makedirs(self.cache_dir, exist_ok=True)
        
        self.exchanges = {}
        for exchange_id in ['binance', 'coinbase', 'kraken']:
            try:
                exchange_class = getattr(ccxt, exchange_id)
                self.exchanges[exchange_id] = exchange_class({'enableRateLimit': True})
            except:
                continue
        
        self.crypto_list = ['BTC/USDT', 'ETH/USDT', 'SOL/USDT']
        self.stock_list = ['NVDA', 'TSLA', 'AAPL', 'MSFT', 'GOOGL']
    
    def get_crypto_prices(self):
        prices = {}
        for symbol in self.crypto_list:
            exchange_prices = []
            for name, exchange in self.exchanges.items():
                try:
                    ticker = exchange.fetch_ticker(symbol)
                    exchange_prices.append({
                        'exchange': name,
                        'price': ticker['last'],
                        'bid': ticker['bid'] or ticker['last'],
                        'ask': ticker['ask'] or ticker['last']
                    })
                    time.sleep(0.1)
                except:
                    continue
            
            if exchange_prices:
                avg = sum(p['price'] for p in exchange_prices) / len(exchange_prices)
                prices[symbol] = {
                    'price': avg,
                    'exchanges': exchange_prices
                }
        
        self.crypto_prices = prices
        return prices
    
    def get_stock_prices(self):
        prices = {}
        for symbol in self.stock_list:
            try:
                ticker = yf.Ticker(symbol)
                hist = ticker.history(period="1d")
                if not hist.empty:
                    prices[symbol] = {
                        'price': float(hist['Close'].iloc[-1])
                    }
            except:
                continue
        
        self.stock_prices = prices
        return prices
    
    def get_historical_data(self, symbol, days=30):
        cache = f"{self.cache_dir}/{symbol.replace('/', '_')}_{days}.json"
        
        if os.path.exists(cache):
            if time.time() - os.path.getmtime(cache) < 3600:
                with open(cache) as f:
                    return json.load(f)
        
        try:
            if '/USDT' in symbol:
                exchange = ccxt.binance()
                ohlcv = exchange.fetch_ohlcv(symbol, '1d', limit=days)
                data = [{
                    'timestamp': c[0],
                    'open': float(c[1]),
                    'high': float(c[2]),
                    'low': float(c[3]),
                    'close': float(c[4]),
                    'volume': float(c[5])
                } for c in ohlcv]
            else:
                ticker = yf.Ticker(symbol)
                hist = ticker.history(period=f"{days}d")
                data = [{
                    'timestamp': int(date.timestamp()),
                    'open': float(row['Open']),
                    'high': float(row['High']),
                    'low': float(row['Low']),
                    'close': float(row['Close']),
                    'volume': float(row['Volume'])
                } for date, row in hist.iterrows()]
            
            with open(cache, 'w') as f:
                json.dump(data, f)
            return data
        except:
            return []
