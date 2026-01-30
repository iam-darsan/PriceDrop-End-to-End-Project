import React from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, ReferenceLine } from 'recharts';
import { PriceHistory, PriceAlert } from '@/types';
import { format } from 'date-fns';
import { formatCurrency } from '@/utils/formatters';

interface PriceHistoryChartProps {
  history: PriceHistory[];
  alerts: PriceAlert[];
  currency: string;
}

const PriceHistoryChart: React.FC<PriceHistoryChartProps> = ({ history, alerts, currency }) => {
  const data = history
    .map(h => ({
      date: new Date(h.recorded_at).getTime(),
      price: parseFloat(h.price.toString()),
      dateStr: format(new Date(h.recorded_at), 'MMM dd, HH:mm'),
    }))
    .sort((a, b) => a.date - b.date);

  if (data.length === 0) {
    return (
      <div className="text-center py-12 text-gray-500">
        No price history available yet
      </div>
    );
  }

  const activeAlerts = alerts.filter(a => a.is_active && !a.triggered_at);

  return (
    <div className="w-full h-80">
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={data} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis
            dataKey="dateStr"
            tick={{ fontSize: 12 }}
            angle={-45}
            textAnchor="end"
            height={80}
          />
          <YAxis
            tick={{ fontSize: 12 }}
            tickFormatter={(value) => `$${value}`}
          />
          <Tooltip
            formatter={(value: any) => [formatCurrency(value, currency), 'Price']}
            labelFormatter={(label) => `Time: ${label}`}
          />
          <Line
            type="monotone"
            dataKey="price"
            stroke="#2563eb"
            strokeWidth={2}
            dot={{ r: 3 }}
            activeDot={{ r: 5 }}
          />
          {activeAlerts.map((alert) => (
            <ReferenceLine
              key={alert.id}
              y={parseFloat(alert.target_price.toString())}
              stroke="#ef4444"
              strokeDasharray="5 5"
              label={{
                value: `Target: ${formatCurrency(parseFloat(alert.target_price.toString()), currency)}`,
                position: 'right',
                fill: '#ef4444',
                fontSize: 12,
              }}
            />
          ))}
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
};

export default PriceHistoryChart;
