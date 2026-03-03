#!/usr/bin/env python3
"""
MT5 Account Data Collector
Simulates collecting data from 40+ MT5 accounts for testing.
In production, this would connect to actual MT5 terminals via MT5 API.
"""

import asyncio
import aiohttp
import json
import random
from datetime import datetime, timedelta
from typing import List, Dict, Any
import argparse


class MT5AccountSimulator:
    """Simulates 40+ MT5 accounts with varying performance."""
    
    def __init__(self, num_accounts: int = 40):
        self.num_accounts = num_accounts
        self.accounts: Dict[str, Dict[str, Any]] = {}
        self._initialize_accounts()
    
    def _initialize_accounts(self):
        """Initialize simulated accounts with varying strategies."""
        strategies = [
            ('aggressive', 1.5, 0.02),    # High growth, high volatility
            ('moderate', 0.8, 0.01),       # Medium growth, medium volatility
            ('conservative', 0.4, 0.005),  # Low growth, low volatility
            ('volatile', 0.5, 0.03),       # Unpredictable
            ('recovery', -0.2, 0.015),     # Coming back from drawdown
        ]
        
        for i in range(self.num_accounts):
            strategy = strategies[i % len(strategies)]
            account_id = f"{1000 + i}"
            
            self.accounts[account_id] = {
                'account_id': account_id,
                'login': account_id,
                'balance': 10000.0,
                'equity': 10000.0,
                'floating_pnl': 0.0,
                'strategy': strategy[0],
                'growth_rate': strategy[1],
                'volatility': strategy[2],
                'trades_open': random.randint(0, 5)
            }
    
    def update_accounts(self):
        """Update account values based on their strategies."""
        for account_id, account in self.accounts.items():
            # Calculate random price movement
            drift = account['growth_rate'] * 0.1  # Hourly drift
            volatility = account['volatility']
            
            # Random walk
            change_pct = random.gauss(drift, volatility)
            change_amount = account['equity'] * (change_pct / 100)
            
            # Update equity and floating PnL
            account['equity'] += change_amount
            account['floating_pnl'] += change_amount * 0.3  # 30% unrealized
            
            # Occasionally realize profit/loss
            if random.random() < 0.1:  # 10% chance per update
                realized = account['floating_pnl'] * 0.5
                account['balance'] += realized
                account['floating_pnl'] -= realized
            
            # Update trades
            if random.random() < 0.2:
                account['trades_open'] = max(0, min(10, 
                    account['trades_open'] + random.randint(-2, 2)))
            
            # Ensure minimum values
            account['equity'] = max(1000, account['equity'])
            account['balance'] = max(1000, account['balance'])
    
    def get_account_data(self) -> List[Dict[str, Any]]:
        """Get current account data as list."""
        return [
            {
                'account_id': acc['account_id'],
                'login': acc['login'],
                'balance': round(acc['balance'], 2),
                'equity': round(acc['equity'], 2),
                'floating_pnl': round(acc['floating_pnl'], 2)
            }
            for acc in self.accounts.values()
        ]


class VPSCollector:
    """Collector that runs on VPS and sends data to dashboard server."""
    
    def __init__(self, server_url: str = 'http://localhost:5000', 
                 num_accounts: int = 40,
                 update_interval: int = 60):
        self.server_url = server_url
        self.update_interval = update_interval
        self.simulator = MT5AccountSimulator(num_accounts)
        self.session: aiohttp.ClientSession = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def send_data(self) -> bool:
        """Send account data to the dashboard server."""
        try:
            data = {
                'timestamp': datetime.now().isoformat(),
                'accounts': self.simulator.get_account_data()
            }
            
            async with self.session.post(
                f'{self.server_url}/socket.io/',
                json=data
            ) as response:
                if response.status == 200:
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] Sent data for {len(data['accounts'])} accounts")
                    return True
                else:
                    print(f"[Warning] Server returned {response.status}")
                    return False
                    
        except Exception as e:
            print(f"[Error] Failed to send data: {e}")
            return False
    
    async def run(self):
        """Main collection loop."""
        print(f"Starting VPS Collector")
        print(f"Server URL: {self.server_url}")
        print(f"Accounts: {self.simulator.num_accounts}")
        print(f"Update interval: {self.update_interval}s\n")
        
        while True:
            # Update simulated account values
            self.simulator.update_accounts()
            
            # Send to server
            await self.send_data()
            
            # Wait for next update
            await asyncio.sleep(self.update_interval)


def generate_test_data():
    """Generate test data for immediate use."""
    simulator = MT5AccountSimulator(num_accounts=40)
    
    # Simulate 24 hours of data
    print("Generating 24 hours of test data...")
    
    snapshots = []
    for hour in range(24):
        simulator.update_accounts()
        
        for acc in simulator.accounts.values():
            snapshots.append({
                'account_id': acc['account_id'],
                'login': acc['login'],
                'balance': round(acc['balance'], 2),
                'equity': round(acc['equity'], 2),
                'floating_pnl': round(acc['floating_pnl'], 2),
                'hour': hour
            })
    
    # Save to JSON
    with open('test_data.json', 'w') as f:
        json.dump({
            'generated_at': datetime.now().isoformat(),
            'account_count': len(simulator.accounts),
            'hours_simulated': 24,
            'latest_snapshots': simulator.get_account_data()
        }, f, indent=2)
    
    print(f"Generated {len(snapshots)} snapshots for {len(simulator.accounts)} accounts")
    print("Test data saved to test_data.json")
    
    return simulator.get_account_data()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='MT5 Account Data Collector')
    parser.add_argument('--server', default='http://localhost:5000', 
                       help='Dashboard server URL')
    parser.add_argument('--accounts', type=int, default=40,
                       help='Number of accounts to simulate')
    parser.add_argument('--interval', type=int, default=60,
                       help='Update interval in seconds')
    parser.add_argument('--generate-only', action='store_true',
                       help='Generate test data and exit')
    
    args = parser.parse_args()
    
    if args.generate_only:
        generate_test_data()
    else:
        # Run the collector
        async def main():
            async with VPSCollector(args.server, args.accounts, args.interval) as collector:
                await collector.run()
        
        try:
            asyncio.run(main())
        except KeyboardInterrupt:
            print("\nCollector stopped by user")