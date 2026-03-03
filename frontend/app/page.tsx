'use client';

import { useDashboardStore } from '@/store/dashboardStore';
import { useSocket } from '@/hooks/useSocket';
import { DashboardHeader } from '@/components/DashboardHeader';
import { AccountCard } from '@/components/AccountCard';
import { AccountTable } from '@/components/AccountTable';

export default function Dashboard() {
  const { 
    accounts, 
    leaderboard, 
    viewMode, 
    leaderboardMode,
    getSortedAccounts 
  } = useDashboardStore();
  
  useSocket();

  const sortedAccounts = getSortedAccounts();
  
  // Create rank and heat score maps
  const rankMap = new Map(leaderboard.map(entry => [entry.login, entry.rank]));
  const heatScoreMap = new Map(leaderboard.map(entry => [entry.login, entry.heat_score]));

  return (
    <div className="min-h-screen bg-zinc-950">
      <DashboardHeader />
      
      <main className="max-w-[1920px] mx-auto px-4 sm:px-6 lg:px-8 py-6">
        {viewMode === 'grid' ? (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 2xl:grid-cols-5 gap-4">
            {sortedAccounts.map((account) => (
              <AccountCard
                key={account.login}
                account={account}
                rank={rankMap.get(account.login)}
                heatScore={heatScoreMap.get(account.login) || 0}
                showRank={leaderboardMode}
              />
            ))}
          </div>
        ) : (
          <AccountTable 
            accounts={sortedAccounts}
            leaderboard={leaderboard}
            showRank={leaderboardMode}
          />
        )}
      </main>
    </div>
  );
}