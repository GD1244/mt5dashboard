#!/usr/bin/env python3
"""
VPS Collector Service - Runs continuously on VPS with MT5 instances.
Collects account data and sends to dashboard server.
"""

import asyncio
import aiohttp
import json
import logging
import argparse
import time
import sys
from datetime import datetime
from typing import List, Dict, Any

# Import the MT5 connector
try:
    from mt5_connector import collect_all_accounts, get_single_account_data, MT5_AVAILABLE
except ImportError:
    MT5_AVAILABLE = False
    print("Warning: MT5 connector not available")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('vps_collector.log')
    ]
)
logger = logging.getLogger(__name__)


class VPSCollectorService:
    """Service that runs on VPS and continuously collects MT5 data."""
    
    def __init__(self, server_url: str, update_interval: int = 60):
        self.server_url = server_url
        self.update_interval = update_interval
        self.session: aiohttp.ClientSession = None
        self.running = False
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    def collect_accounts_data(self) -> List[Dict[str, Any]]:
        """Collect data from all MT5 instances."""
        if MT5_AVAILABLE:
            try:
                from mt5_connector import collect_all_accounts
                accounts = collect_all_accounts()
                if accounts:
                    logger.info(f"Collected data from {len(accounts)} MT5 account(s)")
                    return accounts
            except Exception as e:
                logger.error(f"Error collecting from MT5: {e}")
        
        # Fallback to simulation if MT5 not available
        logger.warning("MT5 not available, using simulation mode")
        return self._get_simulated_data()
    
    def _get_simulated_data(self) -> List[Dict[str, Any]]:
        """Generate simulated data for testing."""
        import random
        
        accounts = []
        for i in range(5):  # Simulate 5 accounts
            base_equity = 10000 + (i * 500)
            change = random.uniform(-100, 200)
            
            accounts.append({
                'account_id': f'10{10+i}',
                'login': f'10{10+i}',
                'balance': base_equity,
                'equity': base_equity + change,
                'floating_pnl': change,
                'timestamp': datetime.now().isoformat(),
            })
        
        return accounts
    
    async def send_data(self, accounts_data: List[Dict[str, Any]]) -> bool:
        """Send account data to dashboard server."""
        if not accounts_data:
            logger.warning("No data to send")
            return False
        
        try:
            payload = {
                'timestamp': datetime.now().isoformat(),
                'accounts': accounts_data,
                'source': 'vps_collector',
                'mt5_available': MT5_AVAILABLE,
            }
            
            async with self.session.post(
                f'{self.server_url}/socket.io/',
                json=payload,
                timeout=aiohttp.ClientTimeout(total=10)
            ) as response:
                if response.status == 200:
                    logger.info(f"Sent {len(accounts_data)} accounts to server")
                    return True
                else:
                    logger.error(f"Server returned status {response.status}")
                    return False
                    
        except aiohttp.ClientError as e:
            logger.error(f"Connection error: {e}")
            return False
        except Exception as e:
            logger.error(f"Error sending data: {e}")
            return False
    
    async def run(self):
        """Main collection loop."""
        self.running = True
        
        logger.info("=" * 60)
        logger.info("VPS Collector Service Started")
        logger.info(f"Server URL: {self.server_url}")
        logger.info(f"Update Interval: {self.update_interval}s")
        logger.info(f"MT5 Available: {MT5_AVAILABLE}")
        logger.info("=" * 60)
        
        while self.running:
            try:
                # Collect data from MT5 instances
                accounts_data = self.collect_accounts_data()
                
                # Send to dashboard server
                if accounts_data:
                    await self.send_data(accounts_data)
                
                # Wait for next update
                await asyncio.sleep(self.update_interval)
                
            except asyncio.CancelledError:
                logger.info("Collector cancelled")
                break
            except Exception as e:
                logger.error(f"Error in collection loop: {e}")
                await asyncio.sleep(self.update_interval)
    
    def stop(self):
        """Stop the collector."""
        self.running = False
        logger.info("Collector stopping...")


async def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='VPS MT5 Collector Service')
    parser.add_argument('--server', default='http://localhost:5000',
                       help='Dashboard server URL')
    parser.add_argument('--interval', type=int, default=60,
                       help='Update interval in seconds')
    parser.add_argument('--daemon', action='store_true',
                       help='Run as daemon/service')
    
    args = parser.parse_args()
    
    collector = VPSCollectorService(args.server, args.interval)
    
    try:
        async with collector:
            await collector.run()
    except KeyboardInterrupt:
        logger.info("Shutdown requested")
        collector.stop()
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    # Run the collector
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nCollector stopped by user")