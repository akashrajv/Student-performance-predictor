import React from 'react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';

export default function ModelComparisonChart({ metrics = {} }) {
  if (!metrics || Object.keys(metrics).length === 0) {
    return (
      <div className="h-64 flex items-center justify-center text-slate-500 text-xs">
        No model evaluation metrics available.
      </div>
    );
  }

  // Filter out any legacy ensemble
  const filteredKeys = Object.keys(metrics).filter(
    (k) => !k.toLowerCase().includes('ensemble')
  );

  const data = filteredKeys.map((modelName) => {
    const m = metrics[modelName];
    const trainAcc = Math.round((m.train_accuracy != null ? m.train_accuracy : m.accuracy || 0) * 1000) / 10;
    const testAcc = Math.round((m.accuracy || 0) * 1000) / 10;
    const isBest = m.is_best_model ? ' ★ (Best)' : '';

    return {
      name: `${modelName.replace('Classifier', '').replace('(L2 Regularized)', '(L2)').trim()}${isBest}`,
      'Training Accuracy': trainAcc,
      'Test Accuracy': testAcc,
      'F1 Score': Math.round((m.f1_score || 0) * 1000) / 10,
      'Precision': Math.round((m.precision || 0) * 1000) / 10,
      'Recall': Math.round((m.recall || 0) * 1000) / 10,
    };
  });

  return (
    <div className="h-72 w-full">
      <ResponsiveContainer width="100%" height="100%">
        <BarChart
          data={data}
          margin={{ top: 15, right: 10, left: -20, bottom: 5 }}
        >
          <CartesianGrid strokeDasharray="3 3" stroke="#334155" opacity={0.5} />
          <XAxis
            dataKey="name"
            stroke="#94a3b8"
            fontSize={11}
            tickLine={false}
          />
          <YAxis
            stroke="#94a3b8"
            fontSize={11}
            domain={[60, 100]}
            tickFormatter={(v) => `${v}%`}
          />
          <Tooltip
            contentStyle={{
              backgroundColor: '#0f172a',
              borderColor: '#334155',
              borderRadius: '8px',
              fontSize: '12px',
              color: '#f8fafc',
            }}
            formatter={(value) => [`${value}%`]}
          />
          <Legend
            wrapperStyle={{ fontSize: '11px', paddingTop: '10px' }}
          />
          <Bar dataKey="Training Accuracy" fill="#10b981" radius={[4, 4, 0, 0]} />
          <Bar dataKey="Test Accuracy" fill="#6366f1" radius={[4, 4, 0, 0]} />
          <Bar dataKey="F1 Score" fill="#a855f7" radius={[4, 4, 0, 0]} />
          <Bar dataKey="Precision" fill="#38bdf8" radius={[4, 4, 0, 0]} />
          <Bar dataKey="Recall" fill="#f59e0b" radius={[4, 4, 0, 0]} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
