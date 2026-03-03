import { create } from 'zustand';
import { devtools } from 'zustand/middleware';

export interface Account {
  login: string;
  balance: number;
  equity: number;
  floating_pnl: number;
  profit_24h: number;
  hourly_rate: number;
  timestamp: string;
}

export interface LeaderboardEntry {
  rank: number;
  login: string;
  balance: number;
  equity: number;
  floating_pnl: number;
  profit_24h: number;
  hourly_rate: number;
  profit_24h_pct: number;
  heat_score: number;
}

export interface DashboardSummary {
  total_accounts: number;
  total_equity: number;
  total_balance: number;
  total_profit_24h: number;
  avg_hourly_rate: number;
  top_performer: {
    login: string;
    profit_24h: number;
  } | null;
  timestamp: string;
}

export interface HeatmapData {
  login: string;
  profit_24h: number;
  heat_value: number;
  heat_score: number;
}

interface DashboardState {
  // Data
  accounts: Account[];
  leaderboard: LeaderboardEntry[];
  summary: DashboardSummary | null;
  heatmap: HeatmapData[];
  
  // UI State
  isConnected: boolean;
  lastUpdate: string | null;
  viewMode: 'grid' | 'table';
  leaderboardMode: boolean;
  sortBy: 'profit_24h' | 'hourly_rate' | 'equity' | 'floating_pnl';
  isLoading: boolean;
  error: string | null;
  
  // Actions
  setAccounts: (accounts: Account[]) => void;
  setLeaderboard: (leaderboard: LeaderboardEntry[]) => void;
  setSummary: (summary: DashboardSummary) => void;
  setHeatmap: (heatmap: HeatmapData[]) => void;
  setConnected: (connected: boolean) => void;
  setLastUpdate: (timestamp: string) => void;
  setViewMode: (mode: 'grid' | 'table') => void;
  setLeaderboardMode: (enabled: boolean) => void;
  setSortBy: (sort: 'profit_24h' | 'hourly_rate' | 'equity' | 'floating_pnl') => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
  
  // Computed
  getSortedAccounts: () => Account[];
  getTopPerformers: (count: number) => LeaderboardEntry[];
  getHeatmapColor: (login: string) => string;
}

export const useDashboardStore = create<DashboardState>()(
  devtools(
    (set, get) => ({
      // Initial state
      accounts: [],
      leaderboard: [],
      summary: null,
      heatmap: [],
      isConnected: false,
      lastUpdate: null,
      viewMode: 'grid',
      leaderboardMode: true,
      sortBy: 'profit_24h',
      isLoading: true,
      error: null,
      
      // Actions
      setAccounts: (accounts) => set({ accounts }),
      setLeaderboard: (leaderboard) => set({ leaderboard }),
      setSummary: (summary) => set({ summary }),
      setHeatmap: (heatmap) => set({ heatmap }),
      setConnected: (isConnected) => set({ isConnected }),
      setLastUpdate: (lastUpdate) => set({ lastUpdate }),
      setViewMode: (viewMode) => set({ viewMode }),
      setLeaderboardMode: (leaderboardMode) => set({ leaderboardMode }),
      setSortBy: (sortBy) => set({ sortBy }),
      setLoading: (isLoading) => set({ isLoading }),
      setError: (error) => set({ error }),
      
      // Computed
      getSortedAccounts: () => {
        const { accounts, sortBy, leaderboardMode } = get();
        let sorted = [...accounts];
        
        if (leaderboardMode) {
          sorted.sort((a, b) => b.profit_24h - a.profit_24h);
        } else {
          switch (sortBy) {
            case 'hourly_rate':
              sorted.sort((a, b) => b.hourly_rate - a.hourly_rate);
              break;
            case 'equity':
              sorted.sort((a, b) => b.equity - a.equity);
              break;
            case 'floating_pnl':
              sorted.sort((a, b) => b.floating_pnl - a.floating_pnl);
              break;
            default:
              sorted.sort((a, b) => b.profit_24h - a.profit_24h);
          }
        }
        
        return sorted;
      },
      
      getTopPerformers: (count) => {
        const { leaderboard } = get();
        return leaderboard.slice(0, count);
      },
      
      getHeatmapColor: (login) => {
        const { heatmap } = get();
        const entry = heatmap.find(h => h.login === login);
        
        if (!entry) return 'bg-zinc-800';
        
        const score = entry.heat_score;
        
        if (score > 0.8) return 'bg-emerald-900 border-emerald-700';
        if (score > 0.4) return 'bg-emerald-800 border-emerald-600';
        if (score > 0.1) return 'bg-emerald-700 border-emerald-500';
        if (score > -0.1) return 'bg-zinc-800 border-zinc-600';
        if (score > -0.4) return 'bg-orange-900 border-orange-700';
        if (score > -0.8) return 'bg-red-900 border-red-700';
        return 'bg-red-950 border-red-800';
      },
    }),
    { name: 'dashboard-store' }
  )
);