#!/usr/bin/env python3
"""
Betfair Paper Trading System

Simulates trading with virtual money using real market data.
Tests strategies without risking actual funds.

Usage:
    python paper_trading.py --balance 10 --strategy scalping
"""

import requests
import json
import time
from datetime import datetime
from pathlib import Path

# Credentials
USERNAME = "dnfarnot@gmail.com"
PASSWORD = "Tobiano01"
APP_KEY = "XmZEwtLsIRkf5lQ3"
CERT_FILE = r"C:\Users\aaron\Desktop\008\betfair_api_combined_20260225_152452.pem"

# Paper trading state
PAPER_STATE_FILE = Path("paper_trading_state.json")


class PaperTrader:
    """Paper trading simulator with real market data"""
    
    def __init__(self, starting_balance=10.00):
        self.starting_balance = starting_balance
        self.balance = starting_balance
        self.exposure = 0.0
        self.session_token = None
        self.trades = []
        self.open_positions = []
        
        # Load existing state
        self.load_state()
    
    def load_state(self):
        """Load paper trading state from file"""
        if PAPER_STATE_FILE.exists():
            with open(PAPER_STATE_FILE) as f:
                state = json.load(f)
                self.balance = state.get('balance', self.starting_balance)
                self.exposure = state.get('exposure', 0.0)
                self.trades = state.get('trades', [])
                self.open_positions = state.get('open_positions', [])
                print(f"Loaded state: ${self.balance:.2f} balance, {len(self.trades)} trades")
    
    def save_state(self):
        """Save paper trading state to file"""
        state = {
            'balance': self.balance,
            'exposure': self.exposure,
            'trades': self.trades,
            'open_positions': self.open_positions,
            'updated_at': datetime.now().isoformat()
        }
        with open(PAPER_STATE_FILE, 'w') as f:
            json.dump(state, f, indent=2)
    
    def login(self):
        """Login to Betfair API"""
        payload = f"username={USERNAME}&password={PASSWORD}"
        headers = {
            'X-Application': APP_KEY,
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        
        response = requests.post(
            'https://identitysso-cert.betfair.com/api/certlogin',
            data=payload,
            cert=CERT_FILE,
            headers=headers,
            timeout=15
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get('loginStatus') == 'SUCCESS':
                self.session_token = result.get('sessionToken')
                return True
        
        return False
    
    def get_markets(self, event_type_ids=['1', '2', '4', '7']):
        """Get available markets for scanning"""
        if not self.session_token:
            if not self.login():
                return []
        
        headers = {
            'X-Application': APP_KEY,
            'X-Authentication': self.session_token,
            'Content-Type': 'application/json'
        }
        
        # Get next horse races
        payload = {
            "jsonrpc": "2.0",
            "method": "SportsAPING/v1.0/listMarketCatalogue",
            "params": {
                "filter": {
                    "eventTypeIds": event_type_ids,
                    "marketTypeCodes": ["MATCH_ODDS", "WIN"],
                    "marketStartTime": {
                        "from": datetime.now().isoformat() + "Z"
                    }
                },
                "maxResults": 20,
                "marketProjection": ["EVENT", "RUNNER_DESCRIPTION"]
            },
            "id": 1
        }
        
        response = requests.post(
            'https://api.betfair.com/exchange/betting/json-rpc/v1',
            headers=headers,
            json=payload,
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json().get('result', [])
            return result
        
        return []
    
    def get_market_prices(self, market_id):
        """Get current prices for a market"""
        if not self.session_token:
            return None
        
        headers = {
            'X-Application': APP_KEY,
            'X-Authentication': self.session_token,
            'Content-Type': 'application/json'
        }
        
        payload = {
            "jsonrpc": "2.0",
            "method": "SportsAPING/v1.0/listMarketBook",
            "params": {
                "marketIds": [market_id],
                "priceProjection": {
                    "priceData": ["EX_ALL_OFFERS"]
                }
            },
            "id": 1
        }
        
        response = requests.post(
            'https://api.betfair.com/exchange/betting/json-rpc/v1',
            headers=headers,
            json=payload,
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json().get('result', [])
            if result:
                return result[0]
        
        return None
    
    def calculate_spread_ticks(self, back_price, lay_price):
        """Calculate spread in ticks"""
        if not back_price or not lay_price:
            return 999
        
        # Tick sizes vary by price
        if back_price < 2.0:
            tick = 0.01
        elif back_price < 3.0:
            tick = 0.02
        elif back_price < 4.0:
            tick = 0.05
        elif back_price < 6.0:
            tick = 0.1
        elif back_price < 10.0:
            tick = 0.2
        elif back_price < 20.0:
            tick = 0.5
        else:
            tick = 1.0
        
        return round((lay_price - back_price) / tick)
    
    def scan_opportunities(self):
        """Scan markets for trading opportunities"""
        print("\n" + "="*60)
        print("SCANNING MARKETS")
        print("="*60)
        
        markets = self.get_markets()
        
        if not markets:
            print("No markets found")
            return []
        
        opportunities = []
        
        for market in markets:
            market_id = market.get('marketId')
            market_name = market.get('marketName')
            event = market.get('event', {})
            event_name = event.get('eventName', 'Unknown')
            
            # Get prices
            book = self.get_market_prices(market_id)
            
            if not book:
                continue
            
            runners = book.get('runners', [])
            
            for runner in runners:
                runner_id = runner.get('selectionId')
                ex = runner.get('ex', {})
                available_to_back = ex.get('availableToBack', [])
                available_to_lay = ex.get('availableToLay', [])
                
                if not available_to_back or not available_to_lay:
                    continue
                
                back_price = available_to_back[0].get('price')
                lay_price = available_to_lay[0].get('price')
                back_size = available_to_back[0].get('size')
                lay_size = available_to_lay[0].get('size')
                
                spread_ticks = self.calculate_spread_ticks(back_price, lay_price)
                
                # Look for tight spreads (good for scalping)
                if spread_ticks <= 3 and back_size > 100 and lay_size > 100:
                    # Find runner name
                    runner_name = "Unknown"
                    for r in market.get('runners', []):
                        if r.get('selectionId') == runner_id:
                            runner_name = r.get('runnerName', 'Unknown')
                            break
                    
                    # Calculate guaranteed profit
                    stake = 1.0
                    if back_price and lay_price:
                        guaranteed_profit = stake * (lay_price - back_price) / back_price
                    else:
                        guaranteed_profit = 0
                    
                    opportunities.append({
                        'market_id': market_id,
                        'market_name': market_name,
                        'event_name': event_name,
                        'runner_id': runner_id,
                        'runner_name': runner_name,
                        'back_price': back_price,
                        'lay_price': lay_price,
                        'back_size': back_size,
                        'lay_size': lay_size,
                        'spread_ticks': spread_ticks,
                        'guaranteed_profit': guaranteed_profit,
                        'score': 100 - (spread_ticks * 10) + min(back_size + lay_size, 20)
                    })
        
        # Sort by score
        opportunities.sort(key=lambda x: x.get('score', 0), reverse=True)
        
        # Display top 5
        print(f"\nFound {len(opportunities)} opportunities:\n")
        
        for i, opp in enumerate(opportunities[:5], 1):
            print(f"{i}. {opp['event_name']} - {opp['runner_name']}")
            print(f"   Market: {opp['market_name']}")
            print(f"   BACK @ {opp['back_price']:.2f} (${opp['back_size']:.0f} avail)")
            print(f"   LAY  @ {opp['lay_price']:.2f} (${opp['lay_size']:.0f} avail)")
            print(f"   Spread: {opp['spread_ticks']} ticks")
            print(f"   Est. Profit: ${opp['guaranteed_profit']:.3f} per $1")
            print(f"   Score: {opp['score']}")
            print()
        
        return opportunities
    
    def place_paper_trade(self, opportunity, stake=1.0):
        """Simulate placing a trade (paper)"""
        back_price = opportunity['back_price']
        lay_price = opportunity['lay_price']
        
        # Simulate BACK bet
        back_stake = stake
        back_return = back_stake * back_price
        
        # Simulate LAY hedge
        lay_stake = stake
        lay_liability = lay_stake * (lay_price - 1)
        
        # Calculate P&L
        if back_price and lay_price:
            # If selection wins
            profit_if_win = (back_return - back_stake) - lay_liability
            
            # If selection loses
            profit_if_lose = lay_stake - back_stake
            
            # Guaranteed profit (should be positive for arbitrage)
            guaranteed = min(profit_if_win, profit_if_lose)
        else:
            guaranteed = 0
        
        trade = {
            'timestamp': datetime.now().isoformat(),
            'market_id': opportunity['market_id'],
            'runner_name': opportunity['runner_name'],
            'back_price': back_price,
            'lay_price': lay_price,
            'stake': stake,
            'guaranteed_profit': guaranteed,
            'type': 'SCALPING'
        }
        
        self.trades.append(trade)
        self.balance += guaranteed
        
        print(f"\n[TRADE EXECUTED]")
        print(f"  {opportunity['runner_name']}")
        print(f"  BACK ${stake:.2f} @ {back_price:.2f}")
        print(f"  LAY  ${stake:.2f} @ {lay_price:.2f}")
        print(f"  Profit: ${guaranteed:.3f}")
        print(f"  New Balance: ${self.balance:.2f}")
        
        self.save_state()
        
        return trade
    
    def run_scalping_session(self, num_trades=5, stake=1.0):
        """Run a paper trading scalping session"""
        print("\n" + "="*60)
        print("PAPER TRADING SESSION")
        print("="*60)
        print(f"Starting Balance: ${self.balance:.2f}")
        print(f"Target Trades: {num_trades}")
        print(f"Stake: ${stake:.2f}")
        
        starting_balance = self.balance
        
        for i in range(num_trades):
            print(f"\n--- Trade {i+1}/{num_trades} ---")
            
            opportunities = self.scan_opportunities()
            
            if opportunities:
                # Take best opportunity
                best = opportunities[0]
                
                if best['spread_ticks'] <= 3:
                    self.place_paper_trade(best, stake)
                else:
                    print("No good opportunities (spread too wide)")
            else:
                print("No opportunities found")
            
            if i < num_trades - 1:
                print("\nWaiting 10 seconds...")
                time.sleep(10)
        
        print("\n" + "="*60)
        print("SESSION COMPLETE")
        print("="*60)
        print(f"Starting Balance: ${starting_balance:.2f}")
        print(f"Final Balance: ${self.balance:.2f}")
        print(f"Profit/Loss: ${self.balance - starting_balance:.2f}")
        print(f"ROI: {((self.balance - starting_balance) / starting_balance * 100):.1f}%")
        print(f"Trades: {len(self.trades)}")
    
    def reset(self, balance=10.00):
        """Reset paper trading account"""
        self.balance = balance
        self.exposure = 0.0
        self.trades = []
        self.open_positions = []
        self.save_state()
        print(f"Reset to ${balance:.2f}")


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Betfair Paper Trading")
    parser.add_argument('--balance', type=float, default=10.00, help='Starting balance')
    parser.add_argument('--trades', type=int, default=5, help='Number of trades')
    parser.add_argument('--stake', type=float, default=1.0, help='Stake per trade')
    parser.add_argument('--scan', action='store_true', help='Just scan markets')
    parser.add_argument('--reset', action='store_true', help='Reset account')
    
    args = parser.parse_args()
    
    trader = PaperTrader(starting_balance=args.balance)
    
    if args.reset:
        trader.reset(args.balance)
        return
    
    if not trader.login():
        print("Failed to login")
        return
    
    if args.scan:
        trader.scan_opportunities()
    else:
        trader.run_scalping_session(num_trades=args.trades, stake=args.stake)


if __name__ == "__main__":
    main()
