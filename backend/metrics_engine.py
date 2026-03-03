#!/usr/bin/env python3
"""
Metrics Engine for MetaTrader 5 Dashboard.
Calculates 24h profit, hourly rate, and other performance metrics.
"""

from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from database import db, AccountSnapshot, AccountMetrics
import statistics


@dataclass
class LeaderboardEntry:
    """Leaderboard entry with ranking information."""
    rank: int
    account_id: str
    login: str
    balance: float
    equity: float
    floating_pnl: float
    profit_24h: float
    hourly_rate: float
    profit_24h_pct: float
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'rank': self.rank,
            'login': self.login,
            'balance': round(self.balance, 2),
            'equity': round(self.equity, 2),
            'floating_pnl': round(self.floating_pnl, 2),
            'profit_24h': round(self.profit_24h, 2),
            'hourly_rate': round(self.hourly_rate, 2),
            'profit_24h_pct': round(self.profit_24h_pct, 4),
            'heat_score': self._calculate_heat_score()
        }
    
    def _calculate_heat_score(self) -> float:
        """Calculate a heat score for color coding (-1 to 1)."""
        # Normalize profit_24h_pct to -1 to 1 range for heatmap
        # Assuming typical range of -5% to +5%
        raw_score = self.profit_24h_pct / 5.0
        return max(-1.0, min(1.0, raw_score))


class MetricsEngine:
    """Calculates performance metrics for MT5 accounts."""
    
    def __init__(self):
        self.db = db
    
    def calculate_account_metrics(self, account_id: str) -> Optional[AccountMetrics]:
        """
        Calculate current metrics for a single account.
        Compares current equity to 24h ago and 1h ago.
        """
        now = datetime.now()
        
        # Get current snapshot
        current = self.db.get_snapshot_at_time(account_id, now)
        if not current:
            return None
        
        # Get snapshot from 24 hours ago
        time_24h_ago = now - timedelta(hours=24)
        snapshot_24h = self.db.get_snapshot_at_time(account_id, time_24h_ago)
        
        # Get snapshot from 1 hour ago
        time_1h_ago = now - timedelta(hours=1)
        snapshot_1h = self.db.get_snapshot_at_time(account_id, time_1h_ago)
        
        # Calculate 24h profit
        if snapshot_24h:
            profit_24h = current.equity - snapshot_24h.equity
        else:
            # No 24h data available, use equity - 10000 (assuming starting balance)
            profit_24h = current.equity - 10000
        
        # Calculate hourly rate
        if snapshot_1h:
            hourly_rate = current.equity - snapshot_1h.equity
        else:
            # No 1h data, estimate from 24h profit if available
            if snapshot_24h:
                hours_diff = (current.timestamp - snapshot_24h.timestamp).total_seconds() / 3600
                hourly_rate = profit_24h / max(hours_diff, 1)
            else:
                hourly_rate = 0.0
        
        return AccountMetrics(
            account_id=current.account_id,
            login=current.login,
            balance=current.balance,
            equity=current.equity,
            floating_pnl=current.floating_pnl,
            profit_24h=profit_24h,
            hourly_rate=hourly_rate,
            timestamp=now
        )
    
    def calculate_all_metrics(self) -> List[AccountMetrics]:
        """Calculate metrics for all accounts."""
        accounts = self.db.get_all_accounts()
        metrics = []
        
        for account in accounts:
            metric = self.calculate_account_metrics(account['account_id'])
            if metric:
                metrics.append(metric)
        
        return metrics
    
    def generate_leaderboard(self, sort_by: str = 'profit_24h') -> List[LeaderboardEntry]:
        """
        Generate leaderboard sorted by specified metric.
        
        Args:
            sort_by: 'profit_24h', 'hourly_rate', 'equity', 'floating_pnl'
        """
        metrics = self.calculate_all_metrics()
        
        # Sort by specified metric (descending)
        reverse_sort = True
        if sort_by == 'profit_24h':
            metrics.sort(key=lambda m: m.profit_24h, reverse=True)
        elif sort_by == 'hourly_rate':
            metrics.sort(key=lambda m: m.hourly_rate, reverse=True)
        elif sort_by == 'equity':
            metrics.sort(key=lambda m: m.equity, reverse=True)
        elif sort_by == 'floating_pnl':
            metrics.sort(key=lambda m: m.floating_pnl, reverse=True)
        elif sort_by == 'balance':
            metrics.sort(key=lambda m: m.balance, reverse=True)
        else:
            metrics.sort(key=lambda m: m.profit_24h, reverse=True)
        
        # Create leaderboard entries with ranks
        entries = []
        for rank, metric in enumerate(metrics, start=1):
            # Calculate 24h profit percentage
            starting_equity = metric.equity - metric.profit_24h
            if starting_equity > 0:
                profit_24h_pct = (metric.profit_24h / starting_equity) * 100
            else:
                profit_24h_pct = 0.0
            
            entry = LeaderboardEntry(
                rank=rank,
                account_id=metric.account_id,
                login=metric.login,
                balance=metric.balance,
                equity=metric.equity,
                floating_pnl=metric.floating_pnl,
                profit_24h=metric.profit_24h,
                hourly_rate=metric.hourly_rate,
                profit_24h_pct=profit_24h_pct
            )
            entries.append(entry)
        
        return entries
    
    def get_dashboard_summary(self) -> Dict[str, Any]:
        """Get summary statistics for the dashboard."""
        metrics = self.calculate_all_metrics()
        
        if not metrics:
            return {
                'total_accounts': 0,
                'total_equity': 0,
                'total_balance': 0,
                'total_profit_24h': 0,
                'avg_hourly_rate': 0,
                'top_performer': None,
                'timestamp': datetime.now().isoformat()
            }
        
        total_equity = sum(m.equity for m in metrics)
        total_balance = sum(m.balance for m in metrics)
        total_profit_24h = sum(m.profit_24h for m in metrics)
        avg_hourly_rate = statistics.mean(m.hourly_rate for m in metrics)
        
        # Find top performer
        top = max(metrics, key=lambda m: m.profit_24h)
        
        return {
            'total_accounts': len(metrics),
            'total_equity': round(total_equity, 2),
            'total_balance': round(total_balance, 2),
            'total_profit_24h': round(total_profit_24h, 2),
            'avg_hourly_rate': round(avg_hourly_rate, 2),
            'top_performer': {
                'login': top.login,
                'profit_24h': round(top.profit_24h, 2)
            },
            'timestamp': datetime.now().isoformat()
        }
    
    def get_account_history(self, account_id: str, hours: int = 24) -> List[Dict[str, Any]]:
        """Get historical data for an account."""
        now = datetime.now()
        start_time = now - timedelta(hours=hours)
        
        snapshots = self.db.get_snapshots_for_period(account_id, start_time, now)
        
        return [{
            'timestamp': s.timestamp.isoformat(),
            'balance': s.balance,
            'equity': s.equity,
            'floating_pnl': s.floating_pnl
        } for s in snapshots]
    
    def calculate_heatmap_data(self) -> List[Dict[str, Any]]:
        """Calculate heatmap color data for all accounts."""
        leaderboard = self.generate_leaderboard('profit_24h')
        
        # Calculate min/max for normalization
        profits = [e.profit_24h for e in leaderboard]
        if not profits:
            return []
        
        max_profit = max(profits)
        min_profit = min(profits)
        profit_range = max_profit - min_profit if max_profit != min_profit else 1
        
        heatmap_data = []
        for entry in leaderboard:
            # Normalize to 0-1 range
            if profit_range > 0:
                normalized = (entry.profit_24h - min_profit) / profit_range
            else:
                normalized = 0.5
            
            heatmap_data.append({
                'login': entry.login,
                'profit_24h': entry.profit_24h,
                'heat_value': normalized,  # 0 = worst, 1 = best
                'heat_score': entry._calculate_heat_score()  # -1 to 1
            })
        
        return heatmap_data


# Singleton instance
metrics_engine = MetricsEngine()


if __name__ == '__main__':
    # Test the metrics engine
    print("Testing metrics engine...")
    
    # Add some historical test data
    from database import db
    
    now = datetime.now()
    
    # Create test data for the past 24 hours
    for i in range(25):
        timestamp = now - timedelta(hours=i)
        
        # Simulate varying performance
        base_equity_1 = 10500 + (i * 10)  # Growing
        base_equity_2 = 11200 + (i * 5)   # Slower growth
        base_equity_3 = 9800 - (i * 2)    # Declining
        
        db.save_snapshot('1001', '1001', base_equity_1, base_equity_1, 0)
        db.save_snapshot('1002', '1002', base_equity_2, base_equity_2, 0)
        db.save_snapshot('1003', '1003', base_equity_3, base_equity_3, 0)
    
    print("\nCalculating metrics for all accounts:")
    all_metrics = metrics_engine.calculate_all_metrics()
    for m in all_metrics:
        print(f"  {m.login}: 24h=${m.profit_24h:.2f}, hr=${m.hourly_rate:.2f}/hr")
    
    print("\nLeaderboard (by 24h profit):")
    leaderboard = metrics_engine.generate_leaderboard('profit_24h')
    for entry in leaderboard:
        medal = "🥇" if entry.rank == 1 else "🥈" if entry.rank == 2 else "🥉" if entry.rank == 3 else "  "
        print(f"  {medal} #{entry.rank} {entry.login}: +${entry.profit_24h:.2f} ({entry.profit_24h_pct:+.2f}%)")
    
    print("\nDashboard Summary:")
    summary = metrics_engine.get_dashboard_summary()
    print(f"  Total Accounts: {summary['total_accounts']}")
    print(f"  Total Equity: ${summary['total_equity']:.2f}")
    print(f"  24h Profit: ${summary['total_profit_24h']:.2f}")
    print(f"  Avg Hourly Rate: ${summary['avg_hourly_rate']:.2f}/hr")