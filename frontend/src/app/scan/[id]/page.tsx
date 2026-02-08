'use client';

import { useEffect, useState, useRef } from 'react';
import html2canvas from 'html2canvas';
import { useParams, useRouter } from 'next/navigation';
import dynamic from 'next/dynamic';
import Link from 'next/link';
import { ArrowLeft, Download, Share2, Calendar, MapPin, Search, Grid3X3, Check, Copy, Loader2 } from 'lucide-react';
import StatsCards from '@/components/StatsCards';
import RankHistoryChart from '@/components/RankHistoryChart';
import { getSearchHistory, SearchHistoryItem } from '@/components/SearchHistory';

// Dynamic import for Leaflet
const GeoGridMap = dynamic(() => import('@/components/GeoGridMap'), {
  ssr: false,
  loading: () => (
    <div className="w-full h-[500px] bg-[var(--surface)] rounded-xl flex items-center justify-center">
      <div className="text-[var(--text-muted)]">Carregando mapa...</div>
    </div>
  ),
});

// Generate demo grid data based on coordinates
function generateDemoGridData(lat: number, lng: number, gridSize: number) {
  const points = [];
  const step = 0.003; // ~300m per step
  const half = Math.floor(gridSize / 2);

  let id = 1;
  for (let row = -half; row <= half; row++) {
    for (let col = -half; col <= half; col++) {
      const pointLat = lat + (row * step);
      const pointLng = lng + (col * step);

      // Generate realistic-looking random rank
      const distanceFromCenter = Math.sqrt(row * row + col * col);
      const baseRank = Math.floor(distanceFromCenter * 2) + 1;
      const randomFactor = Math.floor(Math.random() * 4) - 2;
      const rank = Math.max(1, Math.min(20, baseRank + randomFactor));

      let color = '#ef4444'; // red (11+)
      let status: 'success' | 'warning' | 'danger' = 'danger';

      if (rank <= 3) {
        color = '#22c55e'; // green
        status = 'success';
      } else if (rank <= 10) {
        color = '#eab308'; // yellow
        status = 'warning';
      }

      points.push({
        id: id++,
        lat: pointLat,
        lng: pointLng,
        rank: rank > 20 ? null : rank,
        status,
        color,
      });
    }
  }

  return points;
}

// Calculate stats from grid data
function calculateStats(gridData: { rank: number | null }[]) {
  const validRanks = gridData.filter(p => p.rank !== null).map(p => p.rank as number);
  const totalPoints = gridData.length;

  const averageRank = validRanks.length > 0
    ? validRanks.reduce((a, b) => a + b, 0) / validRanks.length
    : 0;

  const top3Count = validRanks.filter(r => r <= 3).length;
  const top10Count = validRanks.filter(r => r <= 10).length;

  // Visibility score: percentage of points in top 10
  const visibilityScore = totalPoints > 0 ? (top10Count / totalPoints) * 100 : 0;

  return {
    averageRank: Math.round(averageRank * 10) / 10,
    visibilityScore: Math.round(visibilityScore),
    top3Count,
    top10Count,
    totalPoints,
  };
}

export default function ScanDetailPage() {
  const params = useParams();
  const router = useRouter();
  const scanId = params.id as string;

  const [searchItem, setSearchItem] = useState<SearchHistoryItem | null>(null);
  const [gridData, setGridData] = useState<ReturnType<typeof generateDemoGridData>>([]);
  const [stats, setStats] = useState<ReturnType<typeof calculateStats> | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [notification, setNotification] = useState<{ message: string; type: 'success' | 'error' } | null>(null);
  const [isExporting, setIsExporting] = useState(false);

  // Show notification
  const showNotification = (message: string, type: 'success' | 'error' = 'success') => {
    setNotification({ message, type });
    setTimeout(() => setNotification(null), 3000);
  };

  // Ref for map container to capture heatmap
  const mapContainerRef = useRef<HTMLDivElement>(null);

  // Export PDF handler
  const handleExportPdf = async () => {
    if (!searchItem || !stats) return;

    setIsExporting(true);
    try {
      // Capture heatmap as base64 image
      let heatmapBase64: string | undefined;
      if (mapContainerRef.current) {
        try {
          const canvas = await html2canvas(mapContainerRef.current, {
            useCORS: true,
            allowTaint: true,
            backgroundColor: '#1C1E21',
            scale: 2, // Higher quality
          });
          heatmapBase64 = canvas.toDataURL('image/png');
        } catch (captureError) {
          console.warn('Failed to capture heatmap:', captureError);
        }
      }

      // Build request payload for backend PDF generation
      const payload = {
        business_name: searchItem.businessName,
        keyword: searchItem.keyword,
        scan_date: searchItem.createdAt,
        grid_size: searchItem.gridSize,
        radius_km: searchItem.radiusKm,
        lat: searchItem.lat,
        lng: searchItem.lng,
        average_rank: stats.averageRank,
        visibility_score: stats.visibilityScore,
        top3_count: stats.top3Count,
        top10_count: stats.top10Count,
        total_points: stats.totalPoints,
        heatmap_base64: heatmapBase64,
      };

      // Call backend API
      const response = await fetch('http://localhost:8000/api/reports/pdf/generate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload),
      });

      if (!response.ok) {
        throw new Error('Failed to generate PDF');
      }

      // Download the PDF
      const blob = await response.blob();
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `relatorio-${searchItem.businessName.replace(/\s+/g, '-').toLowerCase()}-${new Date().toISOString().split('T')[0]}.pdf`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);

      showNotification('Relatório PDF exportado com sucesso!');
    } catch (error) {
      console.error('PDF export error:', error);
      showNotification('Erro ao exportar relatório PDF', 'error');
    } finally {
      setIsExporting(false);
    }
  };


  // Share handler
  const handleShare = async () => {
    if (!searchItem || !stats) return;

    const shareText = `📍 Análise GBP Audit Bot - ${searchItem.businessName}

🔍 Palavra-chave: "${searchItem.keyword}"
📊 Posição Média: ${stats.averageRank}
👁️ Visibilidade: ${stats.visibilityScore}%
✅ Top 3: ${stats.top3Count}/${stats.totalPoints} pontos

Analisado em ${new Date(searchItem.createdAt).toLocaleDateString('pt-BR')}
—
GBP Audit Bot by Juan ⚡`;

    // Try Web Share API first
    if (navigator.share) {
      try {
        await navigator.share({
          title: `GBP Audit Bot - ${searchItem.businessName}`,
          text: shareText,
        });
        showNotification('Compartilhado com sucesso!');
        return;
      } catch (err) {
        // User cancelled or share failed, fall back to clipboard
      }
    }

    // Fallback to clipboard
    try {
      await navigator.clipboard.writeText(shareText);
      showNotification('Copiado para a área de transferência!');
    } catch (err) {
      showNotification('Erro ao compartilhar', 'error');
    }
  };

  useEffect(() => {
    // Find the search in history
    const history = getSearchHistory();
    const item = history.find(h => h.id === scanId);

    if (!item) {
      // Item not found, redirect to search page
      router.push('/search');
      return;
    }

    setSearchItem(item);

    // Generate demo data
    const grid = generateDemoGridData(item.lat, item.lng, item.gridSize);
    setGridData(grid);
    setStats(calculateStats(grid));
    setIsLoading(false);
  }, [scanId, router]);

  if (isLoading || !searchItem || !stats) {
    return (
      <div className="min-h-screen p-6 lg:p-8">
        <div className="animate-pulse space-y-6">
          <div className="h-8 bg-[var(--surface)] rounded w-1/4"></div>
          <div className="h-64 bg-[var(--surface)] rounded"></div>
          <div className="grid grid-cols-4 gap-4">
            {[...Array(4)].map((_, i) => (
              <div key={i} className="h-24 bg-[var(--surface)] rounded"></div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  // History data with proper ISO date
  const historyData = [
    { date: searchItem.createdAt, avg_rank: stats.averageRank },
  ];

  return (
    <div className="min-h-screen p-6 lg:p-8">
      {/* Header */}
      <header className="mb-8">
        <Link
          href="/search"
          className="inline-flex items-center gap-2 text-[var(--text-muted)] hover:text-white transition-colors mb-4"
        >
          <ArrowLeft className="w-4 h-4" />
          Voltar às Buscas
        </Link>

        <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4">
          <div>
            <h1 className="text-2xl font-bold">{searchItem.businessName}</h1>
            <p className="text-[var(--text-muted)] flex items-center gap-2 mt-1">
              <Search className="w-4 h-4" />
              <span className="italic">&ldquo;{searchItem.keyword}&rdquo;</span>
            </p>
          </div>

          <div className="flex items-center gap-3">
            <button
              onClick={handleExportPdf}
              disabled={isExporting}
              className="card py-2 px-4 flex items-center gap-2 hover:bg-[var(--surface-hover)] transition-colors disabled:opacity-50"
            >
              {isExporting ? (
                <Loader2 className="w-4 h-4 animate-spin" />
              ) : (
                <Download className="w-4 h-4" />
              )}
              <span className="text-sm">Exportar Relatório</span>
            </button>
            <button
              onClick={handleShare}
              className="card py-2 px-4 flex items-center gap-2 hover:bg-[var(--surface-hover)] transition-colors"
            >
              <Share2 className="w-4 h-4" />
              <span className="text-sm">Compartilhar</span>
            </button>
          </div>
        </div>

        {/* Notification Toast */}
        {notification && (
          <div className={`fixed top-6 right-6 z-50 px-4 py-3 rounded-lg shadow-lg flex items-center gap-2 animate-fade-in ${notification.type === 'success'
            ? 'bg-[var(--rank-green)] text-white'
            : 'bg-[var(--rank-red)] text-white'
            }`}>
            {notification.type === 'success' ? <Check className="w-4 h-4" /> : null}
            <span className="text-sm font-medium">{notification.message}</span>
          </div>
        )}

        {/* Meta info */}
        <div className="flex flex-wrap items-center gap-4 mt-4 text-sm text-[var(--text-muted)]">
          <span className="flex items-center gap-1">
            <Calendar className="w-4 h-4" />
            {new Date(searchItem.createdAt).toLocaleDateString('pt-BR', {
              day: '2-digit',
              month: 'long',
              year: 'numeric',
              hour: '2-digit',
              minute: '2-digit',
            })}
          </span>
          <span className="flex items-center gap-1">
            <Grid3X3 className="w-4 h-4" />
            Grade {searchItem.gridSize}x{searchItem.gridSize}
          </span>
          <span className="flex items-center gap-1">
            <MapPin className="w-4 h-4" />
            Raio de {searchItem.radiusKm}km
          </span>
        </div>
      </header>

      {/* Stats Cards */}
      <div className="mb-6">
        <StatsCards
          averageRank={stats.averageRank}
          visibilityScore={stats.visibilityScore}
          top3Count={stats.top3Count}
          top10Count={stats.top10Count}
          totalPoints={stats.totalPoints}
          trend={0} // No trend for first scan
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
                Grade {searchItem.gridSize}x{searchItem.gridSize} • Raio de {searchItem.radiusKm}km
              </p>
            </div>
            <div className="h-[500px]" ref={mapContainerRef}>
              <GeoGridMap points={gridData} />
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

          {/* Coordinates Info */}
          <div className="card">
            <h3 className="font-semibold mb-3">📍 Coordenadas</h3>
            <div className="text-sm text-[var(--text-muted)] space-y-1">
              <p>Latitude: <span className="text-white font-mono">{searchItem.lat}</span></p>
              <p>Longitude: <span className="text-white font-mono">{searchItem.lng}</span></p>
            </div>
            <a
              href={`https://www.google.com/maps?q=${searchItem.lat},${searchItem.lng}`}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-block mt-3 text-sm text-[var(--accent)] hover:underline"
            >
              Ver no Google Maps →
            </a>
          </div>

          {/* History Chart */}
          <RankHistoryChart history={historyData} />
        </div>
      </div>

      {/* Footer */}
      <footer className="mt-12 text-center text-sm text-[var(--text-muted)]">
        <p>GBP Audit Bot by <span className="gradient-text font-semibold">Juan</span> ⚡</p>
      </footer>
    </div>
  );
}
