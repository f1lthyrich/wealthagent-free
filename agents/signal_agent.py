import pandas as pd
import ta
from data.market_data import MarketData

class SignalAgent:
    def scan(self, crypto_data, stock_data):
        signals = []
        md = MarketData()
        
        for symbol in crypto_data.keys():
            data = md.get_historical_data(symbol, days=30)
            if data and len(data) > 20:
                signal = self._analyze(data, symbol, 'crypto')
                if signal:
                    signals.append(signal)
        
        for symbol in stock_data.keys():
            data = md.get_historical_data(symbol, days=30)
            if data and len(data) > 20:
                signal = self._analyze(data, symbol, 'stock')
                if signal:
                    signals.append(signal)
        
        return signals
    
    def _analyze(self, hist_data, symbol, asset_type):
        df = pd.DataFrame(hist_data)
        df['rsi'] = ta.momentum.RSIIndicator(df['close']).rsi()
        
        macd = ta.trend.MACD(df['close'])
        df['macd'] = macd.macd()
        df['macd_signal'] = macd.macd_signal()
        
        bb = ta.volatility.BollingerBands(df['close'])
        df['bb_low'] = bb.bollinger_lband()
        
        latest = df.iloc[-1]
        prev = df.iloc[-2]
        
        if pd.isna(latest['rsi']):
            return None
        
        score = 50
        
        if latest['rsi'] < 30:
            score += 15
        elif latest['rsi'] > 70:
            score -= 15
        
        if not pd.isna(latest['macd']) and not pd.isna(latest['macd_signal']):
            if latest['macd'] > latest['macd_signal'] and prev['macd'] <= prev['macd_signal']:
                score += 10
        
        if latest['close'] < latest['bb_low']:
            score += 10
        
        action = 'HOLD'
        if score >= 70:
            action = 'BUY'
        elif score <= 30:
            action = 'SELL'
        
        if abs(score - 50) >= 15:
            return {
                'asset': symbol.split('/')[0] if '/' in symbol else symbol,
                'asset_type': asset_type,
                'action': action,
                'confidence': min(abs(score - 50) * 1.5, 95),
                'expected_return': (score - 50) * 0.3
            }
        return None
