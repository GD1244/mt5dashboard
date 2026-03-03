'use client';

import { useDashboardStore } from '@/store/dashboardStore';
import { useSocket } from '@/hooks/useSocket';
import { formatCurrency, formatNumber, formatTimeAgo, cn } from '../lib/utils';

// Simple icon components
const SignalIcon = ({ className }: { className?: string }) => (
  <svg className={className} fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
    <path strokeLinecap="round" strokeLinejoin="round" d="M9.348 14.652a3.75 3.75 0 010-5.304m5.304 0a3.75 3.75 0 010 5.304m-7.425 2.121a6.75 6.75 0 010-9.546m9.546 0a6.75 6.75 0 010 9.546M5.106 18.894c-3.808-3.807-3.808-9.98 0-13.788m13.788 0c3.808 3.807 3.808 9.98 0 13.788M12 12h.008v.008H12V12zm.375 0a.375.375 0 11-.75 0 .375.375 0 01.75 0z" />
  </svg>
);

const SignalSlashIcon = ({ className }: { className?: string }) => (
  <svg className={className} fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
    <path strokeLinecap="round" strokeLinejoin="round" d="M3 3l18 18M9.348 14.652a3.75 3.75 0 010-5.304m5.304 0a3.75 3.75 0 010 5.304m-7.425 2.121a6.75 6.75 0 010-9.546m9.546 0a6.75 6.75 0 010 9.546M5.106 18.894c-3.808-3.807-3.808-9.98 0-13.788m13.788 0c3.808 3.807 3.808 9.98 0 13.788" />
  </svg>
);

const UsersIcon = ({ className }: { className?: string }) => (
  <svg className={className} fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
    <path strokeLinecap="round" strokeLinejoin="round" d="M15 19.128a9.38 9.38 0 002.625.372 9.337 9.337 0 004.121-.952 4.125 4.125 0 00-7.533-2.493M15 19.128v-.003c0-1.113-.285-2.16-.786-3.07M15 19.128v.106A12.318 12.318 0 018.624 21c-2.331 0-4.512-.645-6.374-1.766l-.001-.109a6.375 6.375 0 0111.964-3.07M12 6.375a3.375 3.375 0 11-6.75 0 3.375 3.375 0 016.75 0zm8.25 2.25a2.625 2.625 0 11-5.25 0 2.625 2.625 0 015.25 0z" />
  </svg>
);

const WalletIcon = ({ className }: { className?: string }) => (
  <svg className={className} fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
    <path strokeLinecap="round" strokeLinejoin="round" d="M21 12a2.25 2.25 0 00-2.25-2.25H15a3 3 0 11-6 0H5.25A2.25 2.25 0 003 12m18 0v6a2.25 2.25 0 01-2.25 2.25H5.25A2.25 2.25 0 013 18v-6m18 0V9M3 12V9m18 0a2.25 2.25 0 00-2.25-2.25H5.25A2.25 2.25 0 003 9m18 0V6a2.25 2.25 0 00-2.25-2.25H5.25A2.25 2.25 0 003 6v3" />
  </svg>
);

const TrendingUpIcon = ({ className }: { className?: string }) => (
  <svg className={className} fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
    <path strokeLinecap="round" strokeLinejoin="round" d="M2.25 18L9 11.25l4.306 4.307a11.95 11.95 0 015.814-5.519l2.74-1.22m0 0l-5.94-2.28m5.94 2.28l-2.28 5.941" />
  </svg>
);

const ClockIcon = ({ className }: { className?: string }) => (
  <svg className={className} fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
    <path strokeLinecap="round" strokeLinejoin="round" d="M12 6v6h4.5m4.5 0a9 9 0 11-18 0 9 9 0 0118 0z" />
  </svg>
);

const Squares2X2Icon = ({ className }: { className?: string }) => (
  <svg className={className} fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
    <path strokeLinecap="round" strokeLinejoin="round" d="M3.75 6A2.25 2.25 0 016 3.75h2.25A2.25 2.25 0 0110.5 6v2.25a2.25 2.25 0 01-2.25 2.25H6a2.25 2.25 0 01-2.25-2.25V6zM3.75 15.75A2.25 2.25 0 016 13.5h2.25a2.25 2.25 0 012.25 2.25V18a2.25 2.25 0 01-2.25 2.25H6A2.25 2.25 0 013.75 18v-2.25zM13.5 6a2.25 2.25 0 012.25-2.25H18A2.25 2.25 0 0120.25 6v2.25A2.25 2.25 0 0118 10.5h-2.25a2.25 2.25 0 01-2.25-2.25V6zM13.5 15.75a2.25 2.25 0 012.25-2.25H18a2.25 2.25 0 012.25 2.25V18A2.25 2.25 0 0118 20.25h-2.25A2.25 2.25 0 0113.5 18v-2.25z" />
  </svg>
);

const TableCellsIcon = ({ className }: { className?: string }) => (
  <svg className={className} fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
    <path strokeLinecap="round" strokeLinejoin="round" d="M3.375 19.5h17.25m-17.25 0a1.125 1.125 0 01-1.125-1.125M3.375 19.5h7.5c.621 0 1.125-.504 1.125-1.125m-8.625 1.125V5.625m0 12.75v-1.5c0-.621.504-1.125 1.125-1.125m0 1.125h17.25m-17.25 0a1.125 1.125 0 01-1.125-1.125M20.625 19.5h-7.5c-.621 0-1.125-.504-1.125-1.125m8.625 1.125V5.625m0 12.75v-1.5c0-.621-.504-1.125-1.125-1.125m0 1.125h-17.25m17.25-12.75h-7.5c-.621 0-1.125.504-1.125 1.125m8.625-1.125v1.5c0 .621-.504 1.125-1.125 1.125M3.375 5.625h7.5c.621 0 1.125.504 1.125 1.125m-8.625-1.125v1.5c0 .621.504 1.125 1.125 1.125" />
  </svg>
);

const TrophyIcon = ({ className }: { className?: string }) => (
  <svg className={className} fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
    <path strokeLinecap="round" strokeLinejoin="round" d="M16.5 18.75h-9m9 0a3 3 0 013 3h-15a3 3 0 013-3m9 0v-3.375c0-.621-.503-1.125-1.125-1.125h-.871M7.5 18.75v-3.375c0-.621.504-1.125 1.125-1.125h.872m5.007 0H9.497m5.007 0c-1.116-.013-2.136-.376-3.005-1.012M9.497 14.25c-1.116.013-2.136.376-3.005 1.012m11.49 1.012c-1.116-.013-2.136-.376-3.005-1.012M6 14.25c-1.116.013-2.136.376-3.005 1.012m15.01 1.012c1.116-.013 2.136-.376 3.005-1.012M6 16.365l1.364.455m11.272-1.819l-1.364-.455M12 12.75V9m0 3.75v-3.375c0-.621.504-1.125 1.125-1.125h1.5c.621 0 1.125.504 1.125 1.125V12.75m-4.5 0v-3.375c0-.621-.504-1.125-1.125-1.125h-1.5c-.621 0-1.125.504-1.125 1.125V12.75" />
  </svg>
);

const ArrowPathIcon = ({ className }: { className?: string }) => (
  <svg className={className} fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
    <path strokeLinecap="round" strokeLinejoin="round" d="M16.023 9.348h4.992v-.001M2.985 19.644v-4.992m0 0h4.992m-4.993 0l3.181 3.183a8.25 8.25 0 0013.803-3.7M4.031 9.865a8.25 8.25 0 0113.803-3.7l3.181 3.182m0-4.991v4.99" />
  </svg>
);

export function DashboardHeader() {
  const { 
    summary, 
    isConnected, 
    lastUpdate, 
    viewMode, 
    leaderboardMode,
    setViewMode, 
    setLeaderboardMode 
  } = useDashboardStore();
  
  const { requestUpdate } = useSocket();

  return (
    <header className="sticky top-0 z-50 glass border-b border-zinc-800">
      <div className="max-w-[1920px] mx-auto px-4 sm:px-6 lg:px-8">
        {/* Top Row */}
        <div className="flex items-center justify-between h-16">
          {/* Logo & Title */}
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-emerald-500 to-yellow-500 flex items-center justify-center">
              <TrendingUpIcon className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="text-lg font-bold text-white">MT5 Dashboard</h1>
              <p className="text-xs text-zinc-400">Multi-Account Performance Analytics</p>
            </div>
          </div>

          {/* Connection Status */}
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2">
              {isConnected ? (
                <>
                  <SignalIcon className="w-5 h-5 text-emerald-400" />
                  <span className="text-sm text-emerald-400">Connected</span>
                </>
              ) : (
                <>
                  <SignalSlashIcon className="w-5 h-5 text-red-400" />
                  <span className="text-sm text-red-400">Disconnected</span>
                </>
              )}
            </div>
            
            {lastUpdate && (
              <div className="flex items-center gap-1 text-xs text-zinc-400">
                <ClockIcon className="w-4 h-4" />
                <span>Updated {formatTimeAgo(lastUpdate)}</span>
              </div>
            )}
            
            <button
              onClick={requestUpdate}
              className="p-2 rounded-lg bg-zinc-800 hover:bg-zinc-700 text-zinc-300 transition-colors"
              title="Refresh"
            >
              <ArrowPathIcon className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* Summary Stats */}
        {summary && (
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 py-4 border-t border-zinc-800">
            <div className="flex items-center gap-3">
              <div className="p-2 rounded-lg bg-blue-500/10">
                <UsersIcon className="w-5 h-5 text-blue-400" />
              </div>
              <div>
                <p className="text-xs text-zinc-400">Accounts</p>
                <p className="font-mono text-lg font-bold text-white">
                  {formatNumber(summary.total_accounts, 0)}
                </p>
              </div>
            </div>

            <div className="flex items-center gap-3">
              <div className="p-2 rounded-lg bg-purple-500/10">
                <WalletIcon className="w-5 h-5 text-purple-400" />
              </div>
              <div>
                <p className="text-xs text-zinc-400">Total Equity</p>
                <p className="font-mono text-lg font-bold text-white">
                  {formatCurrency(summary.total_equity)}
                </p>
              </div>
            </div>

            <div className="flex items-center gap-3">
              <div className="p-2 rounded-lg bg-emerald-500/10">
                <TrendingUpIcon className="w-5 h-5 text-emerald-400" />
              </div>
              <div>
                <p className="text-xs text-zinc-400">24h Profit</p>
                <p className={cn(
                  "font-mono text-lg font-bold",
                  summary.total_profit_24h >= 0 ? "text-emerald-400" : "text-red-400"
                )}>
                  {summary.total_profit_24h >= 0 ? '+' : ''}
                  {formatCurrency(summary.total_profit_24h)}
                </p>
              </div>
            </div>

            <div className="flex items-center gap-3">
              <div className="p-2 rounded-lg bg-yellow-500/10">
                <ClockIcon className="w-5 h-5 text-yellow-400" />
              </div>
              <div>
                <p className="text-xs text-zinc-400">Avg Hourly Rate</p>
                <p className={cn(
                  "font-mono text-lg font-bold",
                  summary.avg_hourly_rate >= 0 ? "text-emerald-400" : "text-red-400"
                )}>
                  {summary.avg_hourly_rate >= 0 ? '+' : ''}
                  {formatCurrency(summary.avg_hourly_rate)}/hr
                </p>
              </div>
            </div>
          </div>
        )}

        {/* Controls */}
        <div className="flex items-center justify-between py-3 border-t border-zinc-800">
          <div className="flex items-center gap-2">
            {/* View Mode Toggle */}
            <div className="flex items-center bg-zinc-800 rounded-lg p-1">
              <button
                onClick={() => setViewMode('grid')}
                className={cn(
                  "flex items-center gap-2 px-3 py-1.5 rounded-md text-sm font-medium transition-colors",
                  viewMode === 'grid' 
                    ? "bg-zinc-700 text-white" 
                    : "text-zinc-400 hover:text-white"
                )}
              >
                <Squares2X2Icon className="w-4 h-4" />
                Grid
              </button>
              <button
                onClick={() => setViewMode('table')}
                className={cn(
                  "flex items-center gap-2 px-3 py-1.5 rounded-md text-sm font-medium transition-colors",
                  viewMode === 'table' 
                    ? "bg-zinc-700 text-white" 
                    : "text-zinc-400 hover:text-white"
                )}
              >
                <TableCellsIcon className="w-4 h-4" />
                Table
              </button>
            </div>

            {/* Leaderboard Mode Toggle */}
            <button
              onClick={() => setLeaderboardMode(!leaderboardMode)}
              className={cn(
                "flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-colors",
                leaderboardMode 
                  ? "bg-yellow-500/20 text-yellow-400 border border-yellow-500/30" 
                  : "bg-zinc-800 text-zinc-400 hover:text-white"
              )}
            >
              <TrophyIcon className="w-4 h-4" />
              Leaderboard
            </button>
          </div>

          {/* Top Performer */}
          {summary?.top_performer && (
            <div className="flex items-center gap-2 text-sm">
              <span className="text-zinc-400">Top:</span>
              <span className="font-mono font-bold text-yellow-400">
                #{summary.top_performer.login}
              </span>
              <span className={cn(
                "font-mono",
                summary.top_performer.profit_24h >= 0 ? "text-emerald-400" : "text-red-400"
              )}>
                {summary.top_performer.profit_24h >= 0 ? '+' : ''}
                {formatCurrency(summary.top_performer.profit_24h)}
              </span>
            </div>
          )}
        </div>
      </div>
    </header>
  );
}