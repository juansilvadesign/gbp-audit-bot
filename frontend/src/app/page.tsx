'use client';

import dynamic from 'next/dynamic';
import { useState } from 'react';
import Link from 'next/link';
import { MapPin, Search, Zap } from 'lucide-react';
import StatsCards from '@/components/StatsCards';
import RankHistoryChart from '@/components/RankHistoryChart';
import ProtectedRoute from '@/components/ProtectedRoute';
import UserMenu from '@/components/UserMenu';
import { useAuth } from '@/contexts/AuthContext';
const GeoGridMap = dynamic(() => import('@/components/GeoGridMap'), {
  ssr: false,
  loading: () => (
    <div className="w-full h-[500px] bg-[var(--surface)] rounded-xl flex items-center justify-center">
      <div className="text-[var(--text-muted)]">Carregando mapa...</div>
    </div>
  ),
});

// Demo data matching jsonfinal.md format
const demoScan = {
  project_id: 'locuz-001',
  business_name: 'Minha Empresa de TI',
  keyword: 'consultoria de tecnologia rio de janeiro',
  scan_date: '2026-01-31T12:00:00Z',
  summary: {
    average_rank: 4.2,
    visibility_score: 72,
    top3_count: 12,
    top10_count: 20,
    trend: 1.6, // Improvement from last week
  },
  grid_data: [
    // 5x5 grid demo data
    { id: 1, lat: -22.9650, lng: -43.1750, rank: 1, status: 'success' as const, color: '#22c55e' },
    { id: 2, lat: -22.9650, lng: -43.1787, rank: 2, status: 'success' as const, color: '#22c55e' },
    { id: 3, lat: -22.9650, lng: -43.1825, rank: 1, status: 'success' as const, color: '#22c55e' },
    { id: 4, lat: -22.9650, lng: -43.1862, rank: 3, status: 'success' as const, color: '#22c55e' },
    { id: 5, lat: -22.9650, lng: -43.1900, rank: 5, status: 'warning' as const, color: '#eab308' },

    { id: 6, lat: -22.9680, lng: -43.1750, rank: 2, status: 'success' as const, color: '#22c55e' },
    { id: 7, lat: -22.9680, lng: -43.1787, rank: 4, status: 'warning' as const, color: '#eab308' },
    { id: 8, lat: -22.9680, lng: -43.1825, rank: 1, status: 'success' as const, color: '#22c55e' },
    { id: 9, lat: -22.9680, lng: -43.1862, rank: 6, status: 'warning' as const, color: '#eab308' },
    { id: 10, lat: -22.9680, lng: -43.1900, rank: 8, status: 'warning' as const, color: '#eab308' },

    { id: 11, lat: -22.9711, lng: -43.1750, rank: 3, status: 'success' as const, color: '#22c55e' },
    { id: 12, lat: -22.9711, lng: -43.1787, rank: 2, status: 'success' as const, color: '#22c55e' },
    { id: 13, lat: -22.9711, lng: -43.1825, rank: 1, status: 'success' as const, color: '#22c55e' },
    { id: 14, lat: -22.9711, lng: -43.1862, rank: 3, status: 'success' as const, color: '#22c55e' },
    { id: 15, lat: -22.9711, lng: -43.1900, rank: 7, status: 'warning' as const, color: '#eab308' },

    { id: 16, lat: -22.9742, lng: -43.1750, rank: 5, status: 'warning' as const, color: '#eab308' },
    { id: 17, lat: -22.9742, lng: -43.1787, rank: 4, status: 'warning' as const, color: '#eab308' },
    { id: 18, lat: -22.9742, lng: -43.1825, rank: 2, status: 'success' as const, color: '#22c55e' },
    { id: 19, lat: -22.9742, lng: -43.1862, rank: 9, status: 'warning' as const, color: '#eab308' },
    { id: 20, lat: -22.9742, lng: -43.1900, rank: 12, status: 'danger' as const, color: '#ef4444' },

    { id: 21, lat: -22.9773, lng: -43.1750, rank: 8, status: 'warning' as const, color: '#eab308' },
    { id: 22, lat: -22.9773, lng: -43.1787, rank: 11, status: 'danger' as const, color: '#ef4444' },
    { id: 23, lat: -22.9773, lng: -43.1825, rank: 4, status: 'warning' as const, color: '#eab308' },
    { id: 24, lat: -22.9773, lng: -43.1862, rank: 15, status: 'danger' as const, color: '#ef4444' },
    { id: 25, lat: -22.9773, lng: -43.1900, rank: null, status: 'danger' as const, color: '#ef4444' },
  ],
  history: [
    { date: '2026-01-10', avg_rank: 12.5 },
    { date: '2026-01-17', avg_rank: 8.1 },
    { date: '2026-01-24', avg_rank: 5.8 },
    { date: '2026-01-31', avg_rank: 4.2 },
  ],
};

export default function DashboardPage() {
  const { user } = useAuth();
  const [gridSize, setGridSize] = useState(5);

  return (
    <ProtectedRoute>
      <div className="min-h-screen p-6 lg:p-8">
        {/* Header */}
        <header className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4 mb-8">
          <div>
            <div className="flex items-center gap-3 mb-2">
              <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-[var(--rank-green)] to-[var(--accent)] flex items-center justify-center">
                <MapPin className="w-5 h-5 text-white" />
              </div>
              <h1 className="text-2xl font-bold">GBP Audit Bot</h1>
            </div>
            <p className="text-[var(--text-muted)]">
              Monitoramento de rankings locais via Geogrid
            </p>
          </div>

          <div className="flex items-center gap-4">
            {/* Grid Size Selector */}
            <div className="card flex items-center gap-2 py-2">
              <span className="text-sm text-[var(--text-muted)]">Grade:</span>
              {[3, 5, 7].map((size) => (
                <button
                  key={size}
                  onClick={() => setGridSize(size)}
                  className={`px-3 py-1 rounded-lg text-sm font-medium transition-colors ${gridSize === size
                    ? 'bg-[var(--accent)] text-white'
                    : 'bg-[var(--surface-hover)] text-[var(--text-muted)] hover:text-white'
                    }`}
                >
                  {size}x{size}
                </button>
              ))}
            </div>

            {/* User Menu */}
            <UserMenu />
          </div>
        </header>

        {/* Project Info */}
        <div className="card mb-6">
          <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4">
            <div>
              <h2 className="text-xl font-semibold mb-1">{demoScan.business_name}</h2>
              <p className="text-[var(--text-muted)] flex items-center gap-2">
                <Search className="w-4 h-4" />
                <span className="italic">&ldquo;{demoScan.keyword}&rdquo;</span>
              </p>
            </div>
            <div className="flex items-center gap-3">
              <span className="text-sm text-[var(--text-muted)]">
                Última análise: {new Date(demoScan.scan_date).toLocaleDateString('pt-BR')}
              </span>
              <Link href="/search" className="bg-[var(--accent)] hover:bg-[var(--accent-hover)] text-white px-4 py-2 rounded-lg font-medium transition-colors flex items-center gap-2">
                <Search className="w-4 h-4" />
                Nova Busca
              </Link>
            </div>
          </div>
        </div>

        {/* Stats Cards */}
        <div className="mb-6">
          <StatsCards
            averageRank={demoScan.summary.average_rank}
            visibilityScore={demoScan.summary.visibility_score}
            top3Count={demoScan.summary.top3_count}
            top10Count={demoScan.summary.top10_count}
            totalPoints={demoScan.grid_data.length}
            trend={demoScan.summary.trend}
          />
        </div>

        {/* Main Content Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Map */}
          <div className="lg:col-span-2">
            <div className="card p-0 overflow-hidden">
              <div className="p-4 border-b border-[var(--surface-hover)]">
                <h3 className="font-semibold">🗺️ Mapa de Calor - Geogrid</h3>
                <p className="text-sm text-[var(--text-muted)]">
                  Grade {gridSize}x{gridSize} • Raio de 2km
                </p>
              </div>
              <div className="h-[500px]">
                <GeoGridMap points={demoScan.grid_data} />
              </div>
            </div>
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            {/* Legend */}
            <div className="card">
              <h3 className="font-semibold mb-4">📊 Legenda</h3>
              <div className="space-y-3">
                <div className="flex items-center gap-3">
                  <div className="w-6 h-6 rounded-full bg-[var(--rank-green)]" />
                  <div>
                    <span className="font-medium">Posição 1-3</span>
                    <p className="text-xs text-[var(--text-muted)]">Local Pack / Dominância</p>
                  </div>
                </div>
                <div className="flex items-center gap-3">
                  <div className="w-6 h-6 rounded-full bg-[var(--rank-yellow)]" />
                  <div>
                    <span className="font-medium">Posição 4-10</span>
                    <p className="text-xs text-[var(--text-muted)]">Visível, fora do Local Pack</p>
                  </div>
                </div>
                <div className="flex items-center gap-3">
                  <div className="w-6 h-6 rounded-full bg-[var(--rank-red)]" />
                  <div>
                    <span className="font-medium">Posição 11+</span>
                    <p className="text-xs text-[var(--text-muted)]">Invisível para usuários</p>
                  </div>
                </div>
              </div>
            </div>

            {/* History Chart */}
            <RankHistoryChart history={demoScan.history} />
          </div>
        </div>

        {/* Footer */}
        <footer className="mt-12 text-center text-sm text-[var(--text-muted)]">
          <p>GBP Audit Bot by <span className="gradient-text font-semibold">Juan</span> ⚡</p>
        </footer>
      </div>
    </ProtectedRoute>
  );
}
