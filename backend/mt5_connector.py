#!/usr/bin/env python3
"""
MetaTrader 5 Connector for VPS deployment.
Connects to local MT5 terminals and extracts account data.
"""

import json
import time
from datetime import datetime
from typing import List, Dict, Any, Optional
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Try to import MT5 - will be available on VPS with MT5 installed
try:
    import MetaTrader5 as mt5
    MT5_AVAILABLE = True
except ImportError:
    MT5_AVAILABLE = False
    logger.warning("MetaTrader5 module not available. Using simulation mode.")


class MT5Connector:
    """Connects to MetaTrader 5 and extracts account information."""
    
    def __init__(self):
        self.connected = False
        self.accounts_data: List[Dict[str, Any]] = []
        
    def initialize(self) -> bool:
        """Initialize connection to MetaTrader 5."""
        if not MT5_AVAILABLE:
            logger.error("MetaTrader5 module not available")
            return False
            
        # Initialize MT5
        if not mt5.initialize():
            logger.error(f"MT5 initialize failed, error code: {mt5.last_error()}")
            return False
            
        self.connected = True
        logger.info("MetaTrader 5 initialized successfully")
        return True
    
    def shutdown(self):
        """Shutdown MT5 connection."""
        if MT5_AVAILABLE and self.connected:
            mt5.shutdown()
            self.connected = False
            logger.info("MetaTrader 5 shutdown")
    
    def get_account_info(self) -> Optional[Dict[str, Any]]:
        """Get current account information."""
        if not MT5_AVAILABLE or not self.connected:
            return None
            
        account = mt5.account_info()
        if account is None:
            logger.error(f"Failed to get account info: {mt5.last_error()}")
            return None
            
        return {
            'login': str(account.login),
            'balance': float(account.balance),
            'equity': float(account.equity),
            'profit': float(account.profit),
            'margin': float(account.margin),
            'margin_free': float(account.margin_free),
            'margin_level': float(account.margin_level) if account.margin_level else 0,
        }
    
    def get_positions(self) -> List[Dict[str, Any]]:
        """Get current open positions."""
        if not MT5_AVAILABLE or not self.connected:
            return []
            
        positions = mt5.positions_get()
        if positions is None:
            return []
            
        return [{
            'ticket': pos.ticket,
            'symbol': pos.symbol,
            'volume': float(pos.volume),
            'profit': float(pos.profit),
            'price_open': float(pos.price_open),
            'price_current': float(pos.price_current),
        } for pos in positions]
    
    def calculate_floating_pnl(self) -> float:
        """Calculate total floating PnL from open positions."""
        positions = self.get_positions()
        return sum(pos['profit'] for pos in positions)
    
    def get_account_data(self) -> Optional[Dict[str, Any]]:
        """Get complete account data for dashboard."""
        account_info = self.get_account_info()
        if not account_info:
            return None
            
        floating_pnl = self.calculate_floating_pnl()
        positions = self.get_positions()
        
        return {
            'account_id': account_info['login'],
            'login': account_info['login'],
            'balance': account_info['balance'],
            'equity': account_info['equity'],
            'floating_pnl': floating_pnl,
            'positions_count': len(positions),
            'timestamp': datetime.now().isoformat(),
        }


class MultiAccountCollector:
    """Collector that handles multiple MT5 accounts/instances."""
    
    def __init__(self, server_url: str = 'http://localhost:5000'):
        self.server_url = server_url
        self.connectors: List[MT5Connector] = []
        self.account_paths: List[str] = []  # Paths to different MT5 installations
        
    def add_mt5_instance(self, path: Optional[str] = None):
        """Add an MT5 instance path to collect from."""
        self.account_paths.append(path or "default")
        
    def collect_from_all_accounts(self) -> List[Dict[str, Any]]:
        """Collect data from all configured MT5 instances."""
        accounts_data = []
        
        for i, path in enumerate(self.account_paths):
            try:
                connector = MT5Connector()
                
                # Try to initialize with specific path if provided
                if path != "default" and MT5_AVAILABLE:
                    # You can specify different MT5 data folders here
                    initialized = mt5.initialize(path=path)
                    connector.connected = initialized
                else:
                    initialized = connector.initialize()
                
                if initialized:
                    data = connector.get_account_data()
                    if data:
                        accounts_data.append(data)
                        logger.info(f"Collected data from account {data['login']}")
                    connector.shutdown()
                else:
                    logger.warning(f"Failed to initialize MT5 instance {i}")
                    
            except Exception as e:
                logger.error(f"Error collecting from MT5 instance {i}: {e}")
                
        return accounts_data
    
    def collect_single_account(self) -> Optional[Dict[str, Any]]:
        """Collect data from a single MT5 instance."""
        connector = MT5Connector()
        
        if not connector.initialize():
            return None
            
        try:
            data = connector.get_account_data()
            return data
        finally:
            connector.shutdown()


# Global collector instance
collector = MultiAccountCollector()


def collect_all_accounts() -> List[Dict[str, Any]]:
    """Convenience function to collect from all accounts."""
    return collector.collect_from_all_accounts()


def get_single_account_data() -> Optional[Dict[str, Any]]:
    """Get data from current MT5 instance."""
    return collector.collect_single_account()


if __name__ == '__main__':
    # Test the connector
    print("Testing MT5 Connector...")
    
    data = get_single_account_data()
    
    if data:
        print("\nAccount Data:")
        print(json.dumps(data, indent=2))
    else:
        print("\nNo MT5 connection available. Running in simulation mode.")
        
        # Demo mode
        demo_data = {
            'account_id': '1001',
            'login': '1001',
            'balance': 10500.50,
            'equity': 10480.30,
            'floating_pnl': -20.20,
            'timestamp': datetime.now().isoformat(),
        }
        print("\nDemo Data:")
        print(json.dumps(demo_data, indent=2))