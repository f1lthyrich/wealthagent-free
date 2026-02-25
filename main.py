import time
import schedule
from datetime import datetime
from rich.console import Console
from rich.table import Table
from rich.live import Live
from rich.layout import Layout
from rich.panel import Panel
from rich.text import Text

from agents.arbitrage_agent import ArbitrageAgent
from agents.signal_agent import SignalAgent
from data.market_data import MarketData
from ui.notifications import Notifier

console = Console()

class WealthAgent:
    def __init__(self):
        self.market_data = MarketData()
        self.notifier = Notifier()
        self.arbitrage_agent = ArbitrageAgent()
        self.signal_agent = SignalAgent()
        self.opportunities = []
        self.last_update = None
        console.print("[bold green]🚀 WealthAgent Started[/bold green]")

    def scan(self):
        crypto = self.market_data.get_crypto_prices()
        stocks = self.market_data.get_stock_prices()
        
        opportunities = []
        
        # Arbitrage opportunities
        arb = self.arbitrage_agent.scan(crypto)
        for opp in arb:
            opportunities.append({
                'type': 'ARBITRAGE',
                'asset': opp['pair'],
                'action': f"{opp['buy_exchange']} → {opp['sell_exchange']}",
                'profit': opp['profit_pct'],
                'confidence': opp['confidence']
            })
        
        # Trading signals
        signals = self.signal_agent.scan(crypto, stocks)
        for sig in signals:
            if sig and sig.get('confidence', 0) > 60:
                opportunities.append({
                    'type': 'SIGNAL',
                    'asset': sig['asset'],
                    'action': sig['action'],
                    'profit': sig.get('expected_return', 0),
                    'confidence': sig['confidence']
                })
        
        opportunities.sort(key=lambda x: x['confidence'], reverse=True)
        self.opportunities = opportunities[:10]
        self.last_update = datetime.now()
        
        # Notify on good opportunities
        for opp in self.opportunities[:2]:
            if opp['confidence'] > 80:
                self.notifier.send_opportunity(opp)

    def dashboard(self):
        layout = Layout()
        layout.split_column(
            Layout(name="header", size=3),
            Layout(name="main"),
            Layout(name="footer", size=3)
        )
        
        header = Text(" WealthAgent-Free ", style="bold white on blue")
        layout["header"].update(Panel(header))
        
        table = Table(title="📊 Live Opportunities", header_style="bold cyan")
        table.add_column("Type", width=10)
        table.add_column("Asset", width=8)
        table.add_column("Action", width=25)
        table.add_column("Profit", width=8)
        table.add_column("Conf", width=6)
        
        for opp in self.opportunities:
            profit = f"{opp['profit']:.1f}%" if opp['profit'] else "-"
            table.add_row(
                opp['type'][:8],
                opp['asset'],
                opp['action'][:20],
                profit,
                f"{opp['confidence']:.0f}%"
            )
        
        layout["main"].update(Panel(table))
        
        crypto_count = len(self.market_data.crypto_prices)
        stock_count = len(self.market_data.stock_prices)
        update = self.last_update.strftime('%H:%M:%S') if self.last_update else 'Never'
        footer = Text(f" Crypto: {crypto_count} • Stocks: {stock_count} • Updated: {update} ")
        layout["footer"].update(Panel(footer, style="dim"))
        
        return layout

    def run(self):
        self.scan()
        schedule.every(5).minutes.do(self.scan)
        
        with Live(self.dashboard(), refresh_per_second=4, screen=True) as live:
            while True:
                try:
                    schedule.run_pending()
                    time.sleep(1)
                    live.update(self.dashboard())
                except KeyboardInterrupt:
                    console.print("\n[red]Shutting down...[/red]")
                    break

if __name__ == "__main__":
    agent = WealthAgent()
    agent.run()
