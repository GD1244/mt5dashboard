'use client';

import { Account } from '@/store/dashboardStore';
import { 
  formatCurrency, 
  formatPercentage, 
  getProfitColor, 
  getHeatmapClass,
  getRankIcon,
  getRankClass,
  cn
} from '@/lib/utils';

interface AccountCardProps {
  account: Account;
  rank?: number;
  heatScore?: number;
  showRank?: boolean;
}

export function AccountCard({ account, rank, heatScore = 0, showRank = false }: AccountCardProps) {
  const profit24h = account.profit_24h;
  const hourlyRate = account.hourly_rate;
  const floatingPnl = account.floating_pnl;
  
  const isProfit = profit24h >= 0;
  const isHourlyProfit = hourlyRate >= 0;
  const isFloatingProfit = floatingPnl >= 0;
  
  return (
    <div className={cn(
      "relative rounded-xl border-2 p-4 transition-all duration-300",
      "hover:scale-[1.02] hover:shadow-xl",
      getHeatmapClass(heatScore)
    )}>
      {/* Rank Badge */}
      {showRank && rank && rank <= 3 && (
        <div className={cn(
          "absolute -top-3 -left-3 w-10 h-10 rounded-full flex items-center justify-center text-2xl",
          "bg-zinc-900 border-2 shadow-lg",
          rank === 1 ? "border-yellow-400" : 
          rank === 2 ? "border-gray-400" : "border-orange-600"
        )}>
          {getRankIcon(rank)}
        </div>
      )}
      
      {/* Rank Number (for non-top 3) */}
      {showRank && rank && rank > 3 && (
        <div className="absolute -top-2 -left-2 w-8 h-8 rounded-full bg-zinc-800 border border-zinc-600 flex items-center justify-center text-sm font-bold text-zinc-400">
          {rank}
        </div>
      )}
      
      {/* Account Header */}
      <div className="flex justify-between items-start mb-3">
        <div>
          <h3 className="font-mono text-lg font-bold text-zinc-100">
            #{account.login}
          </h3>
          <p className="text-xs text-zinc-400">Account ID</p>
        </div>
        
        {/* Floating PnL Badge */}
        <div className={cn(
          "px-2 py-1 rounded-md text-xs font-mono font-medium",
          isFloatingProfit ? "bg-emerald-500/20 text-emerald-300" : "bg-red-500/20 text-red-300"
        )}>
          {isFloatingProfit ? '+' : ''}{formatCurrency(floatingPnl)}
        </div>
      </div>
      
      {/* Main Metrics */}
      <div className="space-y-3">
        {/* Equity */}
        <div>
          <p className="text-xs text-zinc-400 mb-1">Equity</p>
          <p className="font-mono text-2xl font-bold text-zinc-100">
            {formatCurrency(account.equity)}
          </p>
        </div>
        
        {/* Balance */}
        <div className="flex justify-between items-center">
          <p className="text-xs text-zinc-400">Balance</p>
          <p className="font-mono text-sm text-zinc-300">
            {formatCurrency(account.balance)}
          </p>
        </div>
        
        {/* Divider */}
        <div className="border-t border-zinc-600/30 pt-3">
          <div className="grid grid-cols-2 gap-2">
            {/* 24h Profit Badge */}
            <div className={cn(
              "px-3 py-2 rounded-lg text-center",
              isProfit ? "bg-emerald-500/10" : "bg-red-500/10"
            )}>
              <p className="text-[10px] uppercase tracking-wider text-zinc-400 mb-1">24h</p>
              <p className={cn(
                "font-mono font-bold",
                getProfitColor(profit24h)
              )}>
                {isProfit ? '+' : ''}{formatCurrency(profit24h)}
              </p>
            </div>
            
            {/* Hourly Rate Badge */}
            <div className={cn(
              "px-3 py-2 rounded-lg text-center",
              isHourlyProfit ? "bg-blue-500/10" : "bg-orange-500/10"
            )}>
              <p className="text-[10px] uppercase tracking-wider text-zinc-400 mb-1">Hourly</p>
              <p className={cn(
                "font-mono font-bold",
                isHourlyProfit ? "text-emerald-300" : "text-orange-300"
              )}>
                {isHourlyProfit ? '+' : ''}{formatCurrency(hourlyRate)}/hr
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}