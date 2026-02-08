'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { Clock, MapPin, Search, ChevronRight, Trash2 } from 'lucide-react';

export interface SearchHistoryItem {
  id: string;
  businessName: string;
  keyword: string;
  lat: number;
  lng: number;
  gridSize: number;
  radiusKm: number;
  createdAt: string;
  status: 'pending' | 'completed' | 'failed';
}

interface SearchHistoryProps {
  onSelectSearch?: (item: SearchHistoryItem) => void;
}

const STORAGE_KEY = 'gbp_check_search_history';

export function getSearchHistory(): SearchHistoryItem[] {
  if (typeof window === 'undefined') return [];
  try {
    const stored = localStorage.getItem(STORAGE_KEY);
    return stored ? JSON.parse(stored) : [];
  } catch {
    return [];
  }
}

export function saveSearchToHistory(item: Omit<SearchHistoryItem, 'id' | 'createdAt'>): SearchHistoryItem {
  const newItem: SearchHistoryItem = {
    ...item,
    id: crypto.randomUUID(),
    createdAt: new Date().toISOString(),
  };

  const history = getSearchHistory();
  history.unshift(newItem); // Add to beginning

  // Keep only last 20 items
  const trimmed = history.slice(0, 20);
  localStorage.setItem(STORAGE_KEY, JSON.stringify(trimmed));

  return newItem;
}

export function deleteSearchFromHistory(id: string): void {
  const history = getSearchHistory();
  const filtered = history.filter(item => item.id !== id);
  localStorage.setItem(STORAGE_KEY, JSON.stringify(filtered));
}

export function clearSearchHistory(): void {
  localStorage.removeItem(STORAGE_KEY);
}

export default function SearchHistory({ onSelectSearch }: SearchHistoryProps) {
  const [history, setHistory] = useState<SearchHistoryItem[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    setHistory(getSearchHistory());
    setIsLoading(false);
  }, []);

  const handleDelete = (id: string, e: React.MouseEvent) => {
    e.stopPropagation();
    deleteSearchFromHistory(id);
    setHistory(getSearchHistory());
  };

  const formatDate = (dateStr: string) => {
    const date = new Date(dateStr);
    return date.toLocaleDateString('pt-BR', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  if (isLoading) {
    return (
      <div className="card">
        <div className="animate-pulse space-y-3">
          <div className="h-4 bg-[var(--surface-hover)] rounded w-1/3"></div>
          <div className="h-12 bg-[var(--surface-hover)] rounded"></div>
          <div className="h-12 bg-[var(--surface-hover)] rounded"></div>
        </div>
      </div>
    );
  }

  if (history.length === 0) {
    return (
      <div className="card text-center py-8">
        <Clock className="w-10 h-10 mx-auto mb-3 text-[var(--text-muted)] opacity-50" />
        <p className="text-[var(--text-muted)]">Nenhuma busca realizada ainda</p>
        <p className="text-sm text-[var(--text-muted)] mt-1">
          Suas buscas aparecerão aqui
        </p>
      </div>
    );
  }

  return (
    <div className="card">
      <div className="flex items-center justify-between mb-4">
        <h3 className="font-semibold flex items-center gap-2">
          <Clock className="w-4 h-4" />
          Histórico de Buscas
        </h3>
        <span className="text-xs text-[var(--text-muted)]">{history.length} busca(s)</span>
      </div>

      <div className="space-y-2">
        {history.map((item) => (
          <Link
            key={item.id}
            href={`/scan/${item.id}`}
            className="block p-3 rounded-lg bg-[var(--surface-hover)] hover:bg-[var(--surface-hover)]/80 transition-colors group"
          >
            <div className="flex items-center justify-between">
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2">
                  <span className="font-medium truncate">{item.businessName}</span>
                  <span className={`text-xs px-2 py-0.5 rounded-full ${item.status === 'completed'
                      ? 'bg-[var(--rank-green)]/20 text-[var(--rank-green)]'
                      : item.status === 'failed'
                        ? 'bg-[var(--rank-red)]/20 text-[var(--rank-red)]'
                        : 'bg-[var(--rank-yellow)]/20 text-[var(--rank-yellow)]'
                    }`}>
                    {item.status === 'completed' ? 'Concluído' : item.status === 'failed' ? 'Falhou' : 'Pendente'}
                  </span>
                </div>
                <div className="flex items-center gap-3 mt-1 text-sm text-[var(--text-muted)]">
                  <span className="flex items-center gap-1">
                    <Search className="w-3 h-3" />
                    {item.keyword}
                  </span>
                  <span className="flex items-center gap-1">
                    <MapPin className="w-3 h-3" />
                    {item.gridSize}x{item.gridSize}
                  </span>
                </div>
                <p className="text-xs text-[var(--text-muted)] mt-1">
                  {formatDate(item.createdAt)}
                </p>
              </div>
              <div className="flex items-center gap-2">
                <button
                  onClick={(e) => handleDelete(item.id, e)}
                  className="p-2 rounded-lg opacity-0 group-hover:opacity-100 hover:bg-[var(--rank-red)]/10 text-[var(--text-muted)] hover:text-[var(--rank-red)] transition-all"
                  title="Excluir"
                >
                  <Trash2 className="w-4 h-4" />
                </button>
                <ChevronRight className="w-4 h-4 text-[var(--text-muted)]" />
              </div>
            </div>
          </Link>
        ))}
      </div>
    </div>
  );
}
