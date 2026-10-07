import React from 'react';
import {
  PieChart,
  Pie,
  Cell,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from 'recharts';

export default function RiskDistributionChart({ riskDistribution = {} }) {
  const data = [
    { name: 'Low Risk', value: riskDistribution['Low Risk'] || 0, color: '#10b981' },
    { name: 'Moderate Risk', value: riskDistribution['Moderate Risk'] || 0, color: '#f59e0b' },
    { name: 'High Risk', value: riskDistribution['High Risk'] || 0, color: '#f43f5e' },
  ].filter((d) => d.value > 0);

  if (data.length === 0) {
    return (
      <div className="h-64 flex items-center justify-center text-slate-500 text-xs">
        No student predictions recorded yet. Run predictions to see distribution.
      </div>
    );
  }

  return (
    <div className="h-64 w-full">
      <ResponsiveContainer width="100%" height="100%">
        <PieChart>
          <Pie
            data={data}
            cx="50%"
            cy="50%"
            innerRadius={55}
            outerRadius={80}
            paddingAngle={4}
            dataKey="value"
          >
            {data.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={entry.color} />
            ))}
          </Pie>
          <Tooltip
            contentStyle={{
              backgroundColor: '#0f172a',
              borderColor: '#334155',
              borderRadius: '8px',
              fontSize: '12px',
              color: '#f8fafc',
            }}
            formatter={(value, name) => [`${value} Students`, name]}
          />
          <Legend
            verticalAlign="bottom"
            height={36}
            wrapperStyle={{ fontSize: '11px' }}
          />
        </PieChart>
      </ResponsiveContainer>
    </div>
  );
}
