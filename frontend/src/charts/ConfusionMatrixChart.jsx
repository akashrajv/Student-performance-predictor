import React from 'react';

export default function ConfusionMatrixChart({ matrix = [], classes = ['High', 'Low', 'Medium'], modelName = 'Model' }) {
  if (!matrix || matrix.length === 0) {
    return (
      <div className="p-6 text-center text-slate-500 text-xs">
        No confusion matrix data available.
      </div>
    );
  }

  // Calculate totals and max value for color intensity
  const flatValues = matrix.flat();
  const maxVal = Math.max(...flatValues, 1);
  const totalSamples = flatValues.reduce((a, b) => a + b, 0);

  // Calculate correct predictions (diagonal sum)
  let correctSum = 0;
  for (let i = 0; i < matrix.length; i++) {
    if (matrix[i] && matrix[i][i] !== undefined) {
      correctSum += matrix[i][i];
    }
  }
  const accuracyPct = totalSamples > 0 ? Math.round((correctSum / totalSamples) * 100) : 0;

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between text-xs">
        <span className="text-slate-300 font-medium">
          Diagonal Accuracy: <span className="text-emerald-400 font-bold">{accuracyPct}%</span>
        </span>
        <span className="text-slate-400 text-[11px]">
          Evaluated on {totalSamples} test cases
        </span>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-center border-collapse text-xs">
          <thead>
            <tr>
              <th className="p-2 text-left text-slate-400 font-normal text-[11px]">
                Actual \ Pred
              </th>
              {classes.map((cls, idx) => (
                <th key={idx} className="p-2 text-slate-300 font-semibold border-b border-slate-700">
                  {cls}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {matrix.map((row, rIdx) => (
              <tr key={rIdx}>
                <td className="p-2 text-left font-semibold text-slate-300 border-r border-slate-700 bg-slate-900/40">
                  {classes[rIdx] || `Class ${rIdx}`}
                </td>
                {row.map((val, cIdx) => {
                  const isDiagonal = rIdx === cIdx;
                  const ratio = val / maxVal;
                  
                  let cellBg = 'bg-slate-800/40';
                  let textColor = 'text-slate-300';
                  if (isDiagonal && val > 0) {
                    cellBg = ratio > 0.6 ? 'bg-indigo-600/80' : 'bg-indigo-600/40';
                    textColor = 'text-white font-bold';
                  } else if (val > 0) {
                    cellBg = 'bg-rose-500/20';
                    textColor = 'text-rose-300';
                  }

                  return (
                    <td
                      key={cIdx}
                      className={`p-3 border border-slate-800 ${cellBg} ${textColor} transition-colors`}
                    >
                      <div className="font-mono text-sm">{val}</div>
                      <div className="text-[10px] opacity-70">
                        {totalSamples > 0 ? `${Math.round((val / totalSamples) * 100)}%` : ''}
                      </div>
                    </td>
                  );
                })}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
