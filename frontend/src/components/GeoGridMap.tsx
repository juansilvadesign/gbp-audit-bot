'use client';

import { MapContainer, TileLayer, CircleMarker, Tooltip, useMap } from 'react-leaflet';
import { useEffect } from 'react';
import 'leaflet/dist/leaflet.css';

export interface GridPoint {
  id: number;
  lat: number;
  lng: number;
  rank: number | null;
  status: 'success' | 'warning' | 'danger';
  color: string;
}

interface GeoGridMapProps {
  points: GridPoint[];
  center?: [number, number];
  zoom?: number;
}

// Component to fit map bounds to points
function FitBounds({ points }: { points: GridPoint[] }) {
  const map = useMap();

  useEffect(() => {
    if (points.length > 0) {
      const bounds = points.map(p => [p.lat, p.lng] as [number, number]);
      map.fitBounds(bounds, { padding: [50, 50] });
    }
  }, [map, points]);

  return null;
}

export default function GeoGridMap({ points, center, zoom = 13 }: GeoGridMapProps) {
  // Calculate center from points if not provided
  const mapCenter = center || (points.length > 0
    ? [
      points.reduce((sum, p) => sum + p.lat, 0) / points.length,
      points.reduce((sum, p) => sum + p.lng, 0) / points.length,
    ] as [number, number]
    : [-23.5505, -46.6333] as [number, number] // São Paulo default
  );

  return (
    <MapContainer
      center={mapCenter}
      zoom={zoom}
      className="w-full h-full min-h-[400px] rounded-xl"
      scrollWheelZoom={true}
    >
      <TileLayer
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      />

      <FitBounds points={points} />

      {points.map((point) => (
        <CircleMarker
          key={point.id}
          center={[point.lat, point.lng]}
          pathOptions={{
            fillColor: point.color,
            color: 'white',
            weight: 2,
            fillOpacity: 0.85,
          }}
          radius={18}
        >
          <Tooltip
            permanent
            direction="center"
            className="rank-tooltip"
          >
            <span className="font-bold text-white text-sm">
              {point.rank !== null ? point.rank : '—'}
            </span>
          </Tooltip>
        </CircleMarker>
      ))}
    </MapContainer>
  );
}
