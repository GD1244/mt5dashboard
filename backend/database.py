#!/usr/bin/env python3
"""
SQLite Database Module for MetaTrader 5 Multi-Account Dashboard.
Handles account snapshots, metrics storage, and historical data.
"""

import sqlite3
import json
from datetime import datetime, timedelta
from dataclasses import dataclass
from typing import List, Optional, Dict, Any
from contextlib import contextmanager
import os

DATABASE_PATH = os.path.join(os.path.dirname(__file__), 'mt5_dashboard.db')


@dataclass
class AccountSnapshot:
    """Represents a single account snapshot at a point in time."""
    id: Optional[int]
    account_id: str
    login: str
    balance: float
    equity: float
    floating_pnl: float
    timestamp: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'account_id': self.account_id,
            'login': self.login,
            'balance': self.balance,
            'equity': self.equity,
            'floating_pnl': self.floating_pnl,
            'timestamp': self.timestamp.isoformat()
        }


@dataclass
class AccountMetrics:
    """Calculated metrics for an account."""
    account_id: str
    login: str
    balance: float
    equity: float
    floating_pnl: float
    profit_24h: float
    hourly_rate: float
    timestamp: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'login': self.login,
            'balance': round(self.balance, 2),
            'equity': round(self.equity, 2),
            'floating_pnl': round(self.floating_pnl, 2),
            'profit_24h': round(self.profit_24h, 2),
            'hourly_rate': round(self.hourly_rate, 2),
            'timestamp': self.timestamp.isoformat()
        }


class DatabaseManager:
    """Manages SQLite database operations for the MT5 Dashboard."""
    
    def __init__(self, db_path: str = DATABASE_PATH):
        self.db_path = db_path
        self._init_database()
    
    @contextmanager
    def _get_connection(self):
        """Context manager for database connections."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    def _init_database(self):
        """Initialize database tables."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Account snapshots table - stores hourly data
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS account_snapshots (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    account_id TEXT NOT NULL,
                    login TEXT NOT NULL,
                    balance REAL NOT NULL,
                    equity REAL NOT NULL,
                    floating_pnl REAL NOT NULL DEFAULT 0,
                    timestamp DATETIME NOT NULL
                )
            ''')
            
            # Create index for faster queries
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_snapshots_account_time 
                ON account_snapshots(account_id, timestamp)
            ''')
            
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_snapshots_timestamp 
                ON account_snapshots(timestamp)
            ''')
            
            # Accounts metadata table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS accounts (
                    account_id TEXT PRIMARY KEY,
                    login TEXT NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    last_seen DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Settings table for configuration
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS settings (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.commit()
            print(f"[Database] Initialized at {self.db_path}")
    
    def save_snapshot(self, account_id: str, login: str, balance: float, 
                      equity: float, floating_pnl: float = 0) -> AccountSnapshot:
        """Save a new account snapshot."""
        timestamp = datetime.now()
        
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Insert snapshot
            cursor.execute('''
                INSERT INTO account_snapshots (account_id, login, balance, equity, floating_pnl, timestamp)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (account_id, login, balance, equity, floating_pnl, timestamp))
            
            snapshot_id = cursor.lastrowid
            
            # Update accounts metadata
            cursor.execute('''
                INSERT INTO accounts (account_id, login, last_seen)
                VALUES (?, ?, ?)
                ON CONFLICT(account_id) DO UPDATE SET
                    login = excluded.login,
                    last_seen = excluded.last_seen
            ''', (account_id, login, timestamp))
            
            return AccountSnapshot(
                id=snapshot_id,
                account_id=account_id,
                login=login,
                balance=balance,
                equity=equity,
                floating_pnl=floating_pnl,
                timestamp=timestamp
            )
    
    def save_snapshots_batch(self, accounts_data: List[Dict[str, Any]]) -> List[AccountSnapshot]:
        """Save multiple account snapshots in a batch."""
        timestamp = datetime.now()
        snapshots = []
        
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            for data in accounts_data:
                cursor.execute('''
                    INSERT INTO account_snapshots (account_id, login, balance, equity, floating_pnl, timestamp)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    data['account_id'],
                    data['login'],
                    data['balance'],
                    data['equity'],
                    data.get('floating_pnl', 0),
                    timestamp
                ))
                
                snapshot_id = cursor.lastrowid
                snapshots.append(AccountSnapshot(
                    id=snapshot_id,
                    account_id=data['account_id'],
                    login=data['login'],
                    balance=data['balance'],
                    equity=data['equity'],
                    floating_pnl=data.get('floating_pnl', 0),
                    timestamp=timestamp
                ))
                
                # Update accounts metadata
                cursor.execute('''
                    INSERT INTO accounts (account_id, login, last_seen)
                    VALUES (?, ?, ?)
                    ON CONFLICT(account_id) DO UPDATE SET
                        login = excluded.login,
                        last_seen = excluded.last_seen
                ''', (data['account_id'], data['login'], timestamp))
            
            return snapshots
    
    def get_snapshot_at_time(self, account_id: str, target_time: datetime) -> Optional[AccountSnapshot]:
        """Get the closest snapshot to a specific time."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM account_snapshots
                WHERE account_id = ? AND timestamp <= ?
                ORDER BY timestamp DESC
                LIMIT 1
            ''', (account_id, target_time))
            
            row = cursor.fetchone()
            if row:
                return AccountSnapshot(
                    id=row['id'],
                    account_id=row['account_id'],
                    login=row['login'],
                    balance=row['balance'],
                    equity=row['equity'],
                    floating_pnl=row['floating_pnl'],
                    timestamp=datetime.fromisoformat(row['timestamp'])
                )
            return None
    
    def get_latest_snapshots(self) -> List[AccountSnapshot]:
        """Get the latest snapshot for each account."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT s.* FROM account_snapshots s
                INNER JOIN (
                    SELECT account_id, MAX(timestamp) as max_time
                    FROM account_snapshots
                    GROUP BY account_id
                ) latest ON s.account_id = latest.account_id AND s.timestamp = latest.max_time
            ''')
            
            snapshots = []
            for row in cursor.fetchall():
                snapshots.append(AccountSnapshot(
                    id=row['id'],
                    account_id=row['account_id'],
                    login=row['login'],
                    balance=row['balance'],
                    equity=row['equity'],
                    floating_pnl=row['floating_pnl'],
                    timestamp=datetime.fromisoformat(row['timestamp'])
                ))
            
            return snapshots
    
    def get_all_accounts(self) -> List[Dict[str, Any]]:
        """Get list of all tracked accounts."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT account_id, login, created_at, last_seen
                FROM accounts
                ORDER BY account_id
            ''')
            
            return [dict(row) for row in cursor.fetchall()]
    
    def get_snapshots_for_period(self, account_id: str, 
                                  start_time: datetime, 
                                  end_time: datetime) -> List[AccountSnapshot]:
        """Get all snapshots for an account within a time period."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM account_snapshots
                WHERE account_id = ? AND timestamp >= ? AND timestamp <= ?
                ORDER BY timestamp ASC
            ''', (account_id, start_time, end_time))
            
            snapshots = []
            for row in cursor.fetchall():
                snapshots.append(AccountSnapshot(
                    id=row['id'],
                    account_id=row['account_id'],
                    login=row['login'],
                    balance=row['balance'],
                    equity=row['equity'],
                    floating_pnl=row['floating_pnl'],
                    timestamp=datetime.fromisoformat(row['timestamp'])
                ))
            
            return snapshots
    
    def cleanup_old_data(self, days_to_keep: int = 30):
        """Remove snapshots older than specified days."""
        cutoff_date = datetime.now() - timedelta(days=days_to_keep)
        
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                DELETE FROM account_snapshots
                WHERE timestamp < ?
            ''', (cutoff_date,))
            
            deleted = cursor.rowcount
            print(f"[Database] Cleaned up {deleted} old snapshots")
            return deleted
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get database statistics."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Total accounts
            cursor.execute('SELECT COUNT(DISTINCT account_id) FROM accounts')
            total_accounts = cursor.fetchone()[0]
            
            # Total snapshots
            cursor.execute('SELECT COUNT(*) FROM account_snapshots')
            total_snapshots = cursor.fetchone()[0]
            
            # Date range
            cursor.execute('''
                SELECT MIN(timestamp), MAX(timestamp) 
                FROM account_snapshots
            ''')
            min_date, max_date = cursor.fetchone()
            
            return {
                'total_accounts': total_accounts,
                'total_snapshots': total_snapshots,
                'oldest_snapshot': min_date,
                'newest_snapshot': max_date
            }


# Singleton instance
db = DatabaseManager()


if __name__ == '__main__':
    # Test the database
    print("Testing database...")
    
    # Create test snapshots
    test_accounts = [
        {'account_id': '1001', 'login': '1001', 'balance': 10500.50, 'equity': 10480.30, 'floating_pnl': -20.20},
        {'account_id': '1002', 'login': '1002', 'balance': 11200.00, 'equity': 11350.00, 'floating_pnl': 150.00},
        {'account_id': '1003', 'login': '1003', 'balance': 9800.00, 'equity': 9750.00, 'floating_pnl': -50.00},
    ]
    
    snapshots = db.save_snapshots_batch(test_accounts)
    print(f"Saved {len(snapshots)} snapshots")
    
    # Get latest
    latest = db.get_latest_snapshots()
    print(f"Latest snapshots: {len(latest)}")
    
    # Get stats
    stats = db.get_statistics()
    print(f"Database stats: {stats}")