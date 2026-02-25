from plyer import notification

class Notifier:
    def send(self, title, message):
        try:
            notification.notify(
                title=title[:50],
                message=message[:100],
                timeout=3
            )
            return True
        except:
            return False
    
    def send_opportunity(self, opp):
        emoji = '💰' if opp['type'] == 'ARBITRAGE' else '📊'
        title = f"{emoji} {opp['type']}"
        
        if opp['type'] == 'ARBITRAGE':
            msg = f"{opp['asset']}: {opp['profit']:.1f}% profit"
        else:
            msg = f"{opp['asset']}: {opp['action']} ({opp['confidence']:.0f}%)"
        
        self.send(title, msg)
