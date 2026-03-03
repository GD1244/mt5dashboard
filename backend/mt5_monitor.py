#!/usr/bin/env python3
"""
MT5 Process Monitor - Runs in background, detects MT5 processes,
connects to terminals via MT5 API, and pushes data to dashboard.
"""

import asyncio
import json
import logging
import time
import sys
import os
from datetime import datetime
from typing import List, Dict, Any, Optional
import subprocess
import signal
import threading

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('mt5_monitor.log')
    ]
)
logger = logging.getLogger(__name__)

# Global flag for graceful shutdown
running = True


class MT5ProcessMonitor:
    """Monitors system for MT5 processes and connects to them."""
    
    def __init__(self, dashboard_url: str = 'http://localhost:5000'):
        self.dashboard_url = dashboard_url
        self.connected_accounts: Dict[int, Dict] = {}  # pid -> account info
        self.mt5_pids: set = set()
        self.monitor_interval = 30  # Check for new MT5 processes every 30s
        self.data_interval = 60  # Collect data every 60s
        
        # Signal handlers for graceful shutdown
        signal.signal(signal.SIGTERM, self._signal_handler)
        signal.signal(signal.SIGINT, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals."""
        global running
        logger.info(f"Received signal {signum}, shutting down...")
        running = False
    
    def find_mt5_processes(self) -> List[int]:
        """Find all running MT5 process IDs."""
        pids = []
        try:
            # Windows
            if sys.platform == 'win32':
                result = subprocess.run(
                    ['tasklist', '/FI', 'IMAGENAME eq terminal64.exe', '/FO', 'CSV', '/NH'],
                    capture_output=True, text=True
                )
                for line in result.stdout.strip().split('\n'):
                    if line and 'terminal64' in line.lower():
                        parts = line.split('","')
                        if len(parts) > 1:
                            try:
                                pid = int(parts[1])
                                pids.append(pid)
                            except ValueError:
                                pass
            
            # Linux/Mac (using Wine or native)
            else:
                result = subprocess.run(
                    ['pgrep', '-f', 'terminal64.exe'],
                    capture_output=True, text=True
                )
                for line in result.stdout.strip().split('\n'):
                    if line:
                        try:
                            pids.append(int(line))
                        except ValueError:
                            pass
            
            # Also check for MetaTrader5 processes
            if sys.platform == 'win32':
                result = subprocess.run(
                    ['tasklist', '/FI', 'IMAGENAME eq MetaTrader5.exe', '/FO', 'CSV', '/NH'],
                    capture_output=True, text=True
                )
                for line in result.stdout.strip().split('\n'):
                    if line and 'metatrader' in line.lower():
                        parts = line.split('","')
                        if len(parts) > 1:
                            try:
                                pid = int(parts[1])
                                pids.append(pid)
                            except ValueError:
                                pass
        
        except Exception as e:
            logger.error(f"Error finding MT5 processes: {e}")
        
        return list(set(pids))
    
    def connect_to_mt5(self) -> bool:
        """Try to connect to MT5 via Python API."""
        try:
            import MetaTrader5 as mt5
            
            if not mt5.terminal_info():
                if not mt5.initialize():
                    logger.error(f"MT5 initialize failed: {mt5.last_error()}")
                    return False
            
            account_info = mt5.account_info()
            if account_info:
                logger.info(f"Connected to MT5 account: {account_info.login}")
                return True
            
            return False
            
        except ImportError:
            logger.error("MetaTrader5 module not installed")
            return False
        except Exception as e:
            logger.error(f"Error connecting to MT5: {e}")
            return False
    
    def collect_account_data(self) -> Optional[Dict[str, Any]]:
        """Collect data from connected MT5 terminal."""
        try:
            import MetaTrader5 as mt5
            
            if not mt5.terminal_info():
                return None
            
            account = mt5.account_info()
            if not account:
                return None
            
            # Get positions for floating PnL
            positions = mt5.positions_get()
            floating_pnl = sum(pos.profit for pos in positions) if positions else 0
            
            return {
                'account_id': str(account.login),
                'login': str(account.login),
                'balance': float(account.balance),
                'equity': float(account.equity),
                'floating_pnl': float(floating_pnl),
                'margin': float(account.margin),
                'margin_free': float(account.margin_free),
                'timestamp': datetime.now().isoformat(),
            }
            
        except Exception as e:
            logger.error(f"Error collecting data: {e}")
            return None
    
    async def send_to_dashboard(self, data: Dict[str, Any]) -> bool:
        """Send account data to dashboard server."""
        try:
            import aiohttp
            
            payload = {
                'timestamp': datetime.now().isoformat(),
                'accounts': [data],
                'source': 'mt5_monitor',
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f'{self.dashboard_url}/socket.io/',
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    if response.status == 200:
                        logger.info(f"Sent data for account {data['login']}")
                        return True
                    else:
                        logger.warning(f"Server returned {response.status}")
                        return False
                        
        except Exception as e:
            logger.error(f"Error sending data: {e}")
            return False
    
    async def monitor_loop(self):
        """Main monitoring loop."""
        global running
        
        logger.info("=" * 60)
        logger.info("MT5 Process Monitor Started")
        logger.info("=" * 60)
        logger.info(f"Dashboard URL: {self.dashboard_url}")
        logger.info(f"Monitor interval: {self.monitor_interval}s")
        logger.info(f"Data interval: {self.data_interval}s")
        logger.info("Press Ctrl+C to stop")
        logger.info("=" * 60)
        
        last_data_time = 0
        
        while running:
            try:
                # Find MT5 processes
                current_pids = self.find_mt5_processes()
                
                if current_pids:
                    logger.debug(f"Found {len(current_pids)} MT5 process(es): {current_pids}")
                    
                    # Try to connect if not already connected
                    if not self.connected_accounts:
                        if self.connect_to_mt5():
                            logger.info("Connected to MT5 terminal")
                
                else:
                    logger.debug("No MT5 processes found")
                    self.connected_accounts = {}
                
                # Collect and send data
                current_time = time.time()
                if current_time - last_data_time >= self.data_interval:
                    data = self.collect_account_data()
                    if data:
                        await self.send_to_dashboard(data)
                        self.connected_accounts[data['login']] = data
                    last_data_time = current_time
                
                # Wait before next check
                await asyncio.sleep(self.monitor_interval)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in monitor loop: {e}")
                await asyncio.sleep(self.monitor_interval)
        
        logger.info("Monitor loop stopped")
    
    def run(self):
        """Run the monitor."""
        try:
            asyncio.run(self.monitor_loop())
        except KeyboardInterrupt:
            logger.info("Stopped by user")
        finally:
            logger.info("MT5 Monitor shutdown complete")


def run_as_daemon():
    """Run the monitor as a background daemon."""
    import daemon
    import daemon.pidfile
    
    pidfile_path = '/tmp/mt5_monitor.pid'
    
    context = daemon.DaemonContext(
        pidfile=daemon.pidfile.PIDLockFile(pidfile_path),
        working_directory=os.getcwd(),
    )
    
    with context:
        monitor = MT5ProcessMonitor()
        monitor.run()


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='MT5 Process Monitor')
    parser.add_argument('--daemon', action='store_true', help='Run as daemon')
    parser.add_argument('--server', default='http://localhost:5000', help='Dashboard server URL')
    parser.add_argument('--interval', type=int, default=60, help='Data collection interval (seconds)')
    
    args = parser.parse_args()
    
    if args.daemon and sys.platform != 'win32':
        try:
            import daemon
            run_as_daemon()
        except ImportError:
            logger.error("python-daemon not installed. Run: pip install python-daemon")
            sys.exit(1)
    else:
        monitor = MT5ProcessMonitor(dashboard_url=args.server)
        monitor.data_interval = args.interval
        monitor.run()