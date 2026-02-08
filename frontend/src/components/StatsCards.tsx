'use client';

import { TrendingUp, TrendingDown, Target, Eye, MapPin, Award } from 'lucide-react';

interface StatsCardsProps {
  averageRank: number | null;
  visibilityScore: number;
  top3Count: number;
  top10Count: number;
  totalPoints: number;
  trend?: number; // Positive = improvement, negative = decline
}

export default function StatsCards({
  averageRank,
  visibilityScore,
  top3Count,
  top10Count,
  totalPoints,
  trend,
}: StatsCardsProps) {
  return (
    <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
      {/* Average Rank (ARP) */}
      <div className="card">
        <div className="flex items-center justify-between mb-2">
          <span className="text-[var(--text-muted)] text-sm">Posição Média (ARP)</span>
          <Target className="w-5 h-5 text-[var(--accent)]" />
        </div>
        <div className="flex items-end gap-2">
          <span className="text-3xl font-bold">
            {averageRank !== null ? averageRank.toFixed(1) : '—'}
          </span>
          {trend !== undefined && (
            <span className={`flex items-center text-sm ${trend > 0 ? 'text-[var(--rank-green)]' : 'text-[var(--rank-red)]'}`}>
              {trend > 0 ? <TrendingUp className="w-4 h-4 mr-1" /> : <TrendingDown className="w-4 h-4 mr-1" />}
              {Math.abs(trend).toFixed(1)}
            </span>
          )}
        </div>
      </div>

      {/* Visibility Score */}
      <div className="card">
        <div className="flex items-center justify-between mb-2">
          <span className="text-[var(--text-muted)] text-sm">Visibilidade</span>
          <Eye className="w-5 h-5 text-[var(--rank-green)]" />
        </div>
        <div className="flex items-end gap-2">
          <span className="text-3xl font-bold">{visibilityScore.toFixed(0)}%</span>
        </div>
        <div className="mt-2 h-2 bg-[var(--surface-hover)] rounded-full overflow-hidden">
          <div
            className="h-full rounded-full transition-all duration-500"
            style={{
              width: `${visibilityScore}%`,
              background: `linear-gradient(90deg, var(--rank-green) 0%, var(--accent) 100%)`
            }}
          />
        </div>
      </div>

      {/* Top 3 Count */}
      <div className="card">
        <div className="flex items-center justify-between mb-2">
          <span className="text-[var(--text-muted)] text-sm">Top 3 (Local Pack)</span>
          <Award className="w-5 h-5 text-[var(--rank-green)]" />
        </div>
        <div className="flex items-baseline gap-1">
          <span className="text-3xl font-bold text-[var(--rank-green)]">{top3Count}</span>
          <span className="text-[var(--text-muted)]">/ {totalPoints}</span>
        </div>
        <div className="mt-1 text-xs text-[var(--text-muted)]">
          {((top3Count / totalPoints) * 100).toFixed(0)}% de dominância
        </div>
      </div>

      {/* Top 10 Count */}
      <div className="card">
        <div className="flex items-center justify-between mb-2">
          <span className="text-[var(--text-muted)] text-sm">Visível (Top 10)</span>
          <MapPin className="w-5 h-5 text-[var(--rank-yellow)]" />
        </div>
        <div className="flex items-baseline gap-1">
          <span className="text-3xl font-bold text-[var(--rank-yellow)]">{top10Count}</span>
          <span className="text-[var(--text-muted)]">/ {totalPoints}</span>
        </div>
        <div className="mt-1 text-xs text-[var(--text-muted)]">
          {((top10Count / totalPoints) * 100).toFixed(0)}% de cobertura
        </div>
      </div>
    </div>
  );
}
