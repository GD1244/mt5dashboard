import { type ClassValue, clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function formatCurrency(amount: number): string {
  const absAmount = Math.abs(amount);
  
  if (absAmount >= 1000000) {
    return `$${(amount / 1000000).toFixed(2)}M`;
  }
  if (absAmount >= 1000) {
    return `$${(amount / 1000).toFixed(1)}K`;
  }
  
  return `$${amount.toFixed(2)}`;
}

export function formatNumber(num: number, decimals: number = 2): string {
  return num.toLocaleString('en-US', {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  });
}

export function formatPercentage(value: number): string {
  const sign = value >= 0 ? '+' : '';
  return `${sign}${value.toFixed(2)}%`;
}

export function getProfitColor(profit: number): string {
  if (profit > 1000) return 'text-emerald-400';
  if (profit > 500) return 'text-emerald-300';
  if (profit > 100) return 'text-emerald-200';
  if (profit > 0) return 'text-emerald-100';
  if (profit === 0) return 'text-zinc-400';
  if (profit > -100) return 'text-orange-300';
  if (profit > -500) return 'text-orange-400';
  return 'text-red-400';
}

export function getHeatmapClass(heatScore: number): string {
  if (heatScore > 0.8) return 'bg-emerald-900/80 border-emerald-700';
  if (heatScore > 0.4) return 'bg-emerald-800/80 border-emerald-600';
  if (heatScore > 0.1) return 'bg-emerald-700/80 border-emerald-500';
  if (heatScore > -0.1) return 'bg-zinc-800/80 border-zinc-600';
  if (heatScore > -0.4) return 'bg-orange-900/80 border-orange-700';
  if (heatScore > -0.8) return 'bg-red-900/80 border-red-700';
  return 'bg-red-950/80 border-red-800';
}

export function getRankIcon(rank: number): string {
  if (rank === 1) return '🥇';
  if (rank === 2) return '🥈';
  if (rank === 3) return '🥉';
  return '';
}

export function getRankClass(rank: number): string {
  if (rank === 1) return 'rank-gold';
  if (rank === 2) return 'rank-silver';
  if (rank === 3) return 'rank-bronze';
  return 'text-zinc-400';
}

export function formatTimeAgo(timestamp: string): string {
  const date = new Date(timestamp);
  const now = new Date();
  const diff = now.getTime() - date.getTime();
  
  const seconds = Math.floor(diff / 1000);
  const minutes = Math.floor(seconds / 60);
  const hours = Math.floor(minutes / 60);
  
  if (seconds < 60) return `${seconds}s ago`;
  if (minutes < 60) return `${minutes}m ago`;
  if (hours < 24) return `${hours}h ago`;
  return date.toLocaleDateString();
}