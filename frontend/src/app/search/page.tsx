'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { ArrowLeft } from 'lucide-react';
import Link from 'next/link';
import SearchForm, { SearchFormData } from '@/components/SearchForm';
import SearchHistory, { saveSearchToHistory } from '@/components/SearchHistory';
import ProtectedRoute from '@/components/ProtectedRoute';
import UserMenu from '@/components/UserMenu';
import { useAuth } from '@/contexts/AuthContext';

export default function NewSearchPage() {
  const router = useRouter();
  const { user, refreshUser } = useAuth();
  const [isLoading, setIsLoading] = useState(false);
  const [historyKey, setHistoryKey] = useState(0); // Force refresh

  const handleSearch = async (data: SearchFormData) => {
    setIsLoading(true);

    try {
      // Save to local history
      const savedItem = saveSearchToHistory({
        businessName: data.businessName,
        keyword: data.keyword,
        lat: data.lat,
        lng: data.lng,
        gridSize: data.gridSize,
        radiusKm: data.radiusKm,
        status: 'completed', // For demo, mark as completed
      });

      // In production, this would call the API:
      // const response = await createProject({
      //   business_name: data.businessName,
      //   target_keyword: data.keyword,
      //   central_lat: data.lat,
      //   central_lng: data.lng,
      //   default_radius_km: data.radiusKm,
      //   default_grid_size: data.gridSize,
      // });
      // await executeSearch(response.id, data.gridSize);

      // Simulate API delay
      await new Promise((resolve) => setTimeout(resolve, 1500));

      // Refresh user to update credits
      await refreshUser();

      // Redirect to the scan result page
      router.push(`/scan/${savedItem.id}`);

    } catch (error) {
      console.error('Search error:', error);
      setIsLoading(false);
    }
  };

  return (
    <ProtectedRoute>
      <div className="min-h-screen p-6 lg:p-8">
        {/* Header */}
        <header className="mb-8">
          <div className="flex items-center justify-between mb-4">
            <Link
              href="/"
              className="inline-flex items-center gap-2 text-[var(--text-muted)] hover:text-white transition-colors"
            >
              <ArrowLeft className="w-4 h-4" />
              Voltar ao Dashboard
            </Link>
            <UserMenu />
          </div>
          <h1 className="text-2xl font-bold">Nova Análise de Ranking</h1>
          <p className="text-[var(--text-muted)]">
            Configure os parâmetros para monitorar um novo negócio
          </p>
        </header>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Search Form */}
          <div className="lg:col-span-2">
            <SearchForm
              onSearch={handleSearch}
              isLoading={isLoading}
              creditsBalance={user?.credits_balance || 0}
            />

            {/* Help Section */}
            <div className="mt-6 card">
              <h3 className="font-semibold mb-3">💡 Dicas</h3>
              <ul className="text-sm text-[var(--text-muted)] space-y-2">
                <li>• Use o <strong>nome exato</strong> como aparece no Google Meu Negócio</li>
                <li>• Escolha palavras-chave que seus clientes usariam para encontrar você</li>
                <li>• Cole o link do Google Maps para extrair automaticamente as coordenadas</li>
                <li>• Grades maiores (7x7) dão mais precisão, mas consomem mais créditos</li>
              </ul>
            </div>
          </div>

          {/* Search History Sidebar */}
          <div>
            <SearchHistory key={historyKey} />
          </div>
        </div>
      </div>
    </ProtectedRoute>
  );
}
