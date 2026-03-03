'use client';

import { Account, LeaderboardEntry } from '@/store/dashboardStore';
import { 
  formatCurrency, 
  formatPercentage, 
  getProfitColor,
  getRankIcon,
  cn
} from '../lib/utils';

interface AccountTableProps {
  accounts: Account[];
  leaderboard: LeaderboardEntry[];
  showRank?: boolean;
}

export function AccountTable({ accounts, leaderboard, showRank = false }: AccountTableProps) {
  // Create a map for quick rank lookup
  const rankMap = new Map(leaderboard.map(entry => [entry.login, entry.rank]));
  const heatScoreMap = new Map(leaderboard.map(entry => [entry.login, entry.heat_score]));
  
  return (
    <div className="overflow-x-auto rounded-xl border border-zinc-800">
      <table className="w-full text-left">
        <thead className="bg-zinc-900 sticky top-0">
          <tr className="border-b border-zinc-800">
            {showRank && (
              <th className="px-4 py-3 text-xs font-medium text-zinc-400 uppercase tracking-wider w-16">
                Rank
              </th>
            )}
            <th className="px-4 py-3 text-xs font-medium text-zinc-400 uppercase tracking-wider">
              Account
            </th>
            <th className="px-4 py-3 text-xs font-medium text-zinc-400 uppercase tracking-wider text-right">
              Balance
            </th>
            <th className="px-4 py-3 text-xs font-medium text-zinc-400 uppercase tracking-wider text-right">
              Equity
            </th>
            <th className="px-4 py-3 text-xs font-medium text-zinc-400 uppercase tracking-wider text-right">
              Floating PnL
            </th>
            <th className="px-4 py-3 text-xs font-medium text-zinc-400 uppercase tracking-wider text-right">
              24h Profit
            </th>
            <th className="px-4 py-3 text-xs font-medium text-zinc-400 uppercase tracking-wider text-right">
              Hourly Rate
            </th>
          </tr>
        </thead>
        <tbody className="divide-y divide-zinc-800">
          {accounts.map((account, index) => {
            const rank = rankMap.get(account.login);
            const heatScore = heatScoreMap.get(account.login) || 0;
            const profit24h = account.profit_24h;
            const hourlyRate = account.hourly_rate;
            const isProfit = profit24h >= 0;
            const isHourlyProfit = hourlyRate >= 0;
            
            // Row background based on heat score
            let rowBgClass = 'bg-zinc-900/50';
            if (heatScore > 0.5) rowBgClass = 'bg-emerald-900/20';
            else if (heatScore > 0.1) rowBgClass = 'bg-emerald-800/10';
            else if (heatScore < -0.5) rowBgClass = 'bg-red-900/20';
            else if (heatScore < -0.1) rowBgClass = 'bg-orange-900/10';
            
            return (
              <tr 
                key={account.login}
                className={cn(
                  "transition-colors hover:bg-zinc-800/50",
                  rowBgClass,
                  index < 3 && showRank && "bg-opacity-30"
                )}
              >
                {showRank && (
                  <td className="px-4 py-3">
                    {rank && rank <= 3 ? (
                      <span className={cn(
                        "text-2xl",
                        rank === 1 ? "rank-gold" : 
                        rank === 2 ? "rank-silver" : "rank-bronze"
                      )}>
                        {getRankIcon(rank)}
                      </span>
                    ) : (
                      <span className="text-zinc-500 font-mono">{rank || '-'}</span>
                    )}
                  </td>
                )}
                <td className="px-4 py-3">
                  <span className="font-mono font-bold text-zinc-100">
                    #{account.login}
                  </span>
                </td>
                <td className="px-4 py-3 text-right">
                  <span className="font-mono text-zinc-300">
                    {formatCurrency(account.balance)}
                  </span>
                </td>
                <td className="px-4 py-3 text-right">
                  <span className="font-mono font-medium text-zinc-200">
                    {formatCurrency(account.equity)}
                  </span>
                </td>
                <td className="px-4 py-3 text-right">
                  <span className={cn(
                    "font-mono",
                    account.floating_pnl >= 0 ? "text-emerald-400" : "text-red-400"
                  )}>
                    {account.floating_pnl >= 0 ? '+' : ''}
                    {formatCurrency(account.floating_pnl)}
                  </span>
                </td>
                <td className="px-4 py-3 text-right">
                  <span className={cn(
                    "font-mono font-bold",
                    getProfitColor(profit24h)
                  )}>
                    {isProfit ? '+' : ''}
                    {formatCurrency(profit24h)}
                  </span>
                </td>
                <td className="px-4 py-3 text-right">
                  <span className={cn(
                    "font-mono",
                    isHourlyProfit ? "text-emerald-400" : "text-orange-400"
                  )}>
                    {isHourlyProfit ? '+' : ''}
                    {formatCurrency(hourlyRate)}/hr
                  </span>
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}