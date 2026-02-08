'use client';

import { useState } from 'react';
import { Search, MapPin, Building2, Loader2, Zap, Grid3X3, Link2, CheckCircle2 } from 'lucide-react';

interface SearchFormProps {
  onSearch: (data: SearchFormData) => void;
  isLoading?: boolean;
  creditsBalance?: number;
}

export interface SearchFormData {
  businessName: string;
  keyword: string;
  lat: number;
  lng: number;
  radiusKm: number;
  gridSize: 3 | 5 | 7;
}

/**
 * Extract latitude and longitude from a Google Maps URL.
 * Prioritizes the actual entity location (data param) over the viewport center (@ param).
 */
function extractCoordsFromGoogleMapsUrl(url: string): { lat: number; lng: number } | null {
  try {
    const decodedUrl = decodeURIComponent(url);

    // 1. Priority: Entity location in 'data' param (hex/protobuf format)
    // Structure: !3d-22.1234567!4d-43.1234567
    // This is the most accurate location for a specific place/pin
    const entityPattern = /!3d(-?\d+\.\d+)!4d(-?\d+\.\d+)/;
    const entityMatch = decodedUrl.match(entityPattern);
    if (entityMatch) {
      return {
        lat: parseFloat(entityMatch[1]),
        lng: parseFloat(entityMatch[2]),
      };
    }

    // 2. Priority: 'll' parameter (often used in static maps or older links)
    try {
      const urlObj = new URL(url);
      const ll = urlObj.searchParams.get('ll');
      if (ll) {
        const [lat, lng] = ll.split(',');
        if (lat && lng) {
          return { lat: parseFloat(lat), lng: parseFloat(lng) };
        }
      }

      // 3. Priority: 'q' or 'query' parameter (search query) - often contains coords 
      // Format: q=-22.123,-43.123 or query=-22.123,-43.123
      const q = urlObj.searchParams.get('q') || urlObj.searchParams.get('query');
      if (q) {
        const qMatch = q.match(/^(-?\d+\.\d+),(-?\d+\.\d+)$/);
        if (qMatch) {
          return { lat: parseFloat(qMatch[1]), lng: parseFloat(qMatch[2]) };
        }
      }
    } catch {
      // Not a valid URL object, continue to regex fallback
    }

    // 4. Fallback: Viewport center (@lat,lng)
    // This is less accurate for specific places as it just shows where the camera is looking
    // Format: @-22.123,-43.123
    const viewportPattern = /@(-?\d+\.\d+),(-?\d+\.\d+)/;
    const viewportMatch = decodedUrl.match(viewportPattern);
    if (viewportMatch) {
      return {
        lat: parseFloat(viewportMatch[1]),
        lng: parseFloat(viewportMatch[2]),
      };
    }

    return null;
  } catch {
    return null;
  }
}

export default function SearchForm({ onSearch, isLoading = false, creditsBalance = 0 }: SearchFormProps) {
  const [businessName, setBusinessName] = useState('');
  const [keyword, setKeyword] = useState('');
  const [mapsUrl, setMapsUrl] = useState('');
  const [radiusKm, setRadiusKm] = useState('2');
  const [gridSize, setGridSize] = useState<3 | 5 | 7>(5);

  const [errors, setErrors] = useState<Record<string, string>>({});
  const [extractedCoords, setExtractedCoords] = useState<{ lat: number; lng: number } | null>(null);

  // Calculate credits needed
  const creditsNeeded = gridSize * gridSize;
  const hasEnoughCredits = creditsBalance >= creditsNeeded;

  // Handle Maps URL change and extract coordinates
  const handleMapsUrlChange = (url: string) => {
    setMapsUrl(url);
    if (url.trim()) {
      const coords = extractCoordsFromGoogleMapsUrl(url);
      setExtractedCoords(coords);
      if (!coords && url.length > 10) {
        setErrors(prev => ({ ...prev, mapsUrl: 'Não foi possível extrair coordenadas do link' }));
      } else {
        setErrors(prev => {
          const { mapsUrl, ...rest } = prev;
          return rest;
        });
      }
    } else {
      setExtractedCoords(null);
    }
  };

  const validate = (): boolean => {
    const newErrors: Record<string, string> = {};

    if (!businessName.trim()) {
      newErrors.businessName = 'Nome do negócio é obrigatório';
    }

    if (!keyword.trim()) {
      newErrors.keyword = 'Palavra-chave é obrigatória';
    }

    if (!mapsUrl.trim()) {
      newErrors.mapsUrl = 'Link do Google Maps é obrigatório';
    } else if (!extractedCoords) {
      newErrors.mapsUrl = 'Não foi possível extrair coordenadas do link';
    }

    const radiusNum = parseFloat(radiusKm);
    if (isNaN(radiusNum) || radiusNum <= 0 || radiusNum > 50) {
      newErrors.radius = 'Raio deve ser entre 0.1 e 50 km';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    if (!validate()) return;
    if (!hasEnoughCredits) return;
    if (!extractedCoords) return;

    onSearch({
      businessName: businessName.trim(),
      keyword: keyword.trim(),
      lat: extractedCoords.lat,
      lng: extractedCoords.lng,
      radiusKm: parseFloat(radiusKm),
      gridSize,
    });
  };

  return (
    <form onSubmit={handleSubmit} className="card space-y-6">
      <div className="flex items-center gap-3 pb-4 border-b border-[var(--surface-hover)]">
        <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-[var(--accent)] to-[var(--rank-green)] flex items-center justify-center">
          <Search className="w-5 h-5 text-white" />
        </div>
        <div>
          <h2 className="text-lg font-semibold">Nova Busca Geogrid</h2>
          <p className="text-sm text-[var(--text-muted)]">Configure os parâmetros da análise</p>
        </div>
      </div>

      {/* Business Name */}
      <div>
        <label className="block text-sm font-medium mb-2">
          <Building2 className="w-4 h-4 inline mr-2" />
          Nome do Negócio
        </label>
        <input
          type="text"
          value={businessName}
          onChange={(e) => setBusinessName(e.target.value)}
          placeholder="Ex: Clínica Sorriso Real"
          className={`w-full px-4 py-3 rounded-lg bg-[var(--surface-hover)] border ${errors.businessName ? 'border-[var(--rank-red)]' : 'border-transparent'
            } focus:border-[var(--accent)] focus:outline-none transition-colors`}
        />
        {errors.businessName && (
          <p className="text-sm text-[var(--rank-red)] mt-1">{errors.businessName}</p>
        )}
      </div>

      {/* Keyword */}
      <div>
        <label className="block text-sm font-medium mb-2">
          <Search className="w-4 h-4 inline mr-2" />
          Palavra-chave
        </label>
        <input
          type="text"
          value={keyword}
          onChange={(e) => setKeyword(e.target.value)}
          placeholder="Ex: dentista em copacabana"
          className={`w-full px-4 py-3 rounded-lg bg-[var(--surface-hover)] border ${errors.keyword ? 'border-[var(--rank-red)]' : 'border-transparent'
            } focus:border-[var(--accent)] focus:outline-none transition-colors`}
        />
        {errors.keyword && (
          <p className="text-sm text-[var(--rank-red)] mt-1">{errors.keyword}</p>
        )}
      </div>

      {/* Google Maps URL */}
      <div>
        <label className="block text-sm font-medium mb-2">
          <Link2 className="w-4 h-4 inline mr-2" />
          Link do Google Maps
        </label>
        <input
          type="text"
          value={mapsUrl}
          onChange={(e) => handleMapsUrlChange(e.target.value)}
          placeholder="Cole o link do Google Maps aqui..."
          className={`w-full px-4 py-3 rounded-lg bg-[var(--surface-hover)] border ${errors.mapsUrl ? 'border-[var(--rank-red)]' : extractedCoords ? 'border-[var(--rank-green)]' : 'border-transparent'
            } focus:border-[var(--accent)] focus:outline-none transition-colors`}
        />
        {errors.mapsUrl && (
          <p className="text-sm text-[var(--rank-red)] mt-1">{errors.mapsUrl}</p>
        )}
        {extractedCoords && (
          <div className="flex items-center gap-2 mt-2 text-sm text-[var(--rank-green)]">
            <CheckCircle2 className="w-4 h-4" />
            <span>Coordenadas extraídas: ({extractedCoords.lat}, {extractedCoords.lng})</span>
          </div>
        )}
        <p className="text-xs text-[var(--text-muted)] mt-1">
          Abra o local no Google Maps, copie o link da barra de endereços e cole aqui
        </p>
      </div>

      {/* Radius */}
      <div>
        <label className="block text-sm font-medium mb-2">
          Raio da Busca
        </label>
        <div className="flex items-center gap-3">
          <input
            type="range"
            min="0.5"
            max="10"
            step="0.5"
            value={radiusKm}
            onChange={(e) => setRadiusKm(e.target.value)}
            className="flex-1 accent-[var(--accent)]"
          />
          <span className="text-sm font-medium w-16 text-center bg-[var(--surface-hover)] px-3 py-1 rounded-lg">
            {radiusKm} km
          </span>
        </div>
      </div>

      {/* Grid Size */}
      <div>
        <label className="block text-sm font-medium mb-2">
          <Grid3X3 className="w-4 h-4 inline mr-2" />
          Tamanho da Grade
        </label>
        <div className="grid grid-cols-3 gap-3">
          {([3, 5, 7] as const).map((size) => {
            const credits = size * size;
            const isSelected = gridSize === size;
            return (
              <button
                key={size}
                type="button"
                onClick={() => setGridSize(size)}
                className={`py-3 rounded-lg text-center transition-all ${isSelected
                  ? 'bg-[var(--accent)] text-white'
                  : 'bg-[var(--surface-hover)] text-[var(--text-muted)] hover:text-white'
                  }`}
              >
                <div className="font-semibold">{size}x{size}</div>
                <div className="text-xs mt-1 opacity-75">{credits} créditos</div>
              </button>
            );
          })}
        </div>
      </div>

      {/* Credit Warning */}
      {!hasEnoughCredits && (
        <div className="flex items-center gap-3 p-4 rounded-lg bg-[var(--rank-red)]/10 border border-[var(--rank-red)]/30">
          <Zap className="w-5 h-5 text-[var(--rank-red)]" />
          <div>
            <p className="text-sm font-medium text-[var(--rank-red)]">Créditos insuficientes</p>
            <p className="text-xs text-[var(--text-muted)]">
              Necessário: {creditsNeeded} | Disponível: {creditsBalance}
            </p>
          </div>
        </div>
      )}

      {/* Submit Button */}
      <button
        type="submit"
        disabled={isLoading || !hasEnoughCredits}
        className={`w-full py-4 rounded-lg font-semibold text-white transition-all flex items-center justify-center gap-2 ${isLoading || !hasEnoughCredits
          ? 'bg-[var(--surface-hover)] cursor-not-allowed opacity-60'
          : 'bg-gradient-to-r from-[var(--accent)] to-[var(--rank-green)] hover:opacity-90'
          }`}
      >
        {isLoading ? (
          <>
            <Loader2 className="w-5 h-5 animate-spin" />
            Executando busca...
          </>
        ) : (
          <>
            <Search className="w-5 h-5" />
            Iniciar Análise ({creditsNeeded} créditos)
          </>
        )}
      </button>

      {/* Helper Text */}
      <p className="text-xs text-[var(--text-muted)] text-center">
        A busca irá consultar {creditsNeeded} pontos na API do Google Local
      </p>
    </form>
  );
}
