from datetime import datetime

class ArbitrageAgent:
    def __init__(self, min_profit=0.5):
        self.min_profit = min_profit
    
    def scan(self, market_data):
        opportunities = []
        if not market_data:
            return opportunities
        
        for symbol, data in market_data.items():
            if len(data.get('exchanges', [])) < 2:
                continue
            
            exchanges = data['exchanges']
            buy = min(exchanges, key=lambda x: x.get('ask', x.get('price', 0)))
            sell = max(exchanges, key=lambda x: x.get('bid', x.get('price', 0)))
            
            buy_price = buy.get('ask', buy.get('price', 0))
            sell_price = sell.get('bid', sell.get('price', 0))
            
            if buy_price == 0 or sell_price == 0:
                continue
            
            profit = ((sell_price - buy_price) / buy_price) * 100
            
            if profit >= self.min_profit:
                opportunities.append({
                    'pair': symbol,
                    'buy_exchange': buy.get('exchange', 'unknown'),
                    'sell_exchange': sell.get('exchange', 'unknown'),
                    'profit_pct': profit,
                    'confidence': min(profit * 2, 95),
                    'timestamp': datetime.now().isoformat()
                })
        
        return sorted(opportunities, key=lambda x: x['profit_pct'], reverse=True)
