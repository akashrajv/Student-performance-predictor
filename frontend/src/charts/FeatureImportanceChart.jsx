import React from 'react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Cell,
} from 'recharts';

export default function FeatureImportanceChart({ importances = {} }) {
  if (!importances || Object.keys(importances).length === 0) {
    return (
      <div className="h-64 flex items-center justify-center text-slate-500 text-xs">
        No feature importance data available.
      </div>
    );
  }

  // Convert to sorted array
  const data = Object.entries(importances)
    .map(([feature, val]) => ({
      feature: feature.replace(/_/g, ' '),
      rawName: feature,
      importance: Number((val * 100).toFixed(2)),
    }))
    .sort((a, b) => b.importance - a.importance)
    .slice(0, 10); // top 10

  const colors = [
    '#6366f1', '#8b5cf6', '#a855f7', '#d946ef', '#ec4899',
    '#f43f5e', '#f97316', '#eab308', '#22c55e', '#06b6d4'
  ];

  return (
    <div className="h-72 w-full">
      <ResponsiveContainer width="100%" height="100%">
        <BarChart
          data={data}
          layout="vertical"
          margin={{ top: 5, right: 30, left: 40, bottom: 5 }}
        >
          <CartesianGrid strokeDasharray="3 3" stroke="#334155" opacity={0.4} />
          <XAxis
            type="number"
            stroke="#94a3b8"
            fontSize={11}
            tickFormatter={(v) => `${v}%`}
          />
          <YAxis
            dataKey="feature"
            type="category"
            stroke="#94a3b8"
            fontSize={11}
            width={120}
            tickLine={false}
          />
          <Tooltip
            contentStyle={{
              backgroundColor: '#0f172a',
              borderColor: '#334155',
              borderRadius: '8px',
              fontSize: '12px',
              color: '#f8fafc',
            }}
            formatter={(value) => [`${value}% Importance`, 'Relative Weight']}
          />
          <Bar dataKey="importance" radius={[0, 4, 4, 0]}>
            {data.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={colors[index % colors.length]} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
