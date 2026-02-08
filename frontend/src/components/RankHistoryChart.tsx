'use client';

import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

interface HistoryItem {
  date: string;
  avg_rank: number;
}

interface RankHistoryChartProps {
  history: HistoryItem[];
}

export default function RankHistoryChart({ history }: RankHistoryChartProps) {
  // Format date for display - handle both ISO dates and plain text
  const formattedData = history.map(item => {
    let displayDate = item.date;

    // Try to parse as date, if it fails use the original string
    const parsed = new Date(item.date);
    if (!isNaN(parsed.getTime())) {
      displayDate = parsed.toLocaleDateString('pt-BR', {
        day: '2-digit',
        month: '2-digit'
      });
    }

    return {
      ...item,
      displayDate,
    };
  });

  // If only one data point, show a simple display instead of chart
  if (history.length <= 1) {
    return (
      <div className="card">
        <h3 className="text-lg font-semibold mb-4">📈 Evolução do Ranking</h3>
        <div className="text-center py-8">
          <p className="text-3xl font-bold text-[var(--accent)]">
            {history[0]?.avg_rank?.toFixed(1) || '—'}
          </p>
          <p className="text-sm text-[var(--text-muted)] mt-2">
            Posição média atual
          </p>
          <p className="text-xs text-[var(--text-muted)] mt-4">
            Mais dados aparecerão após novas análises
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="card">
      <h3 className="text-lg font-semibold mb-4">📈 Evolução do Ranking</h3>
      <div className="h-[200px]">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={formattedData}>
            <CartesianGrid strokeDasharray="3 3" stroke="var(--surface-hover)" />
            <XAxis
              dataKey="displayDate"
              stroke="var(--text-muted)"
              fontSize={12}
            />
            <YAxis
              stroke="var(--text-muted)"
              fontSize={12}
              reversed // Lower rank is better, so reverse axis
              domain={['auto', 'auto']}
            />
            <Tooltip
              contentStyle={{
                backgroundColor: 'var(--surface)',
                border: '1px solid var(--surface-hover)',
                borderRadius: '8px',
                color: 'var(--foreground)',
              }}
              formatter={(value) => [`Posição ${Number(value).toFixed(1)}`, 'ARP']}
              labelFormatter={(label) => `Data: ${label}`}
            />
            <Line
              type="monotone"
              dataKey="avg_rank"
              stroke="var(--accent)"
              strokeWidth={3}
              dot={{ fill: 'var(--accent)', strokeWidth: 2, r: 4 }}
              activeDot={{ r: 6, fill: 'var(--rank-green)' }}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
      <p className="text-xs text-[var(--text-muted)] mt-2 text-center">
        ↓ Menor posição = Melhor ranking
      </p>
    </div>
  );
}
