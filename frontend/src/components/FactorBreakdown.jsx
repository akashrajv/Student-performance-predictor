import React from 'react';
import { TrendingDown, TrendingUp, Minus, HelpCircle, ArrowUpRight, ArrowDownRight } from 'lucide-react';

export default function FactorBreakdown({ factors = [], predictedClass, riskCategory }) {
  if (!factors || factors.length === 0) {
    return (
      <div className="p-6 text-center text-slate-400 text-sm glass-card rounded-2xl">
        No factor attribution data available.
      </div>
    );
  }

  const negativeFactors = factors.filter((f) => f.impact === 'Negative');
  const positiveFactors = factors.filter((f) => f.impact === 'Positive');

  return (
    <div className="space-y-4">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-slate-800 pb-3">
        <div>
          <h3 className="text-base font-bold text-slate-100 flex items-center gap-2">
            <span>Explainable AI (XAI) Attribution</span>
          </h3>
          <p className="text-xs text-slate-400">
            Feature contributions indicating why the model predicted{' '}
            <strong className="text-slate-200">{predictedClass}</strong> ({riskCategory})
          </p>
        </div>
        <div className="flex items-center gap-2 text-xs">
          <span className="flex items-center gap-1 text-rose-400 bg-rose-500/10 px-2 py-0.5 rounded-full border border-rose-500/20">
            <TrendingDown className="w-3 h-3" /> Risk Drivers ({negativeFactors.length})
          </span>
          <span className="flex items-center gap-1 text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded-full border border-emerald-500/20">
            <TrendingUp className="w-3 h-3" /> Strengths ({positiveFactors.length})
          </span>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
        {factors.map((factor, index) => {
          const isNegative = factor.impact === 'Negative';
          const isPositive = factor.impact === 'Positive';

          const cardBorder = isNegative
            ? 'border-rose-500/25 bg-rose-500/5'
            : isPositive
            ? 'border-emerald-500/25 bg-emerald-500/5'
            : 'border-slate-800 bg-slate-900/40';

          const badgeBg = isNegative
            ? 'bg-rose-500/20 text-rose-300'
            : isPositive
            ? 'bg-emerald-500/20 text-emerald-300'
            : 'bg-slate-800 text-slate-400';

          return (
            <div
              key={index}
              className={`p-3.5 rounded-xl border ${cardBorder} transition-all duration-200 hover:border-slate-600`}
            >
              <div className="flex items-start justify-between gap-2 mb-1.5">
                <div>
                  <div className="text-xs font-semibold text-slate-200">
                    {factor.feature_name_clean}
                  </div>
                  <div className="text-[11px] text-slate-400">
                    Student: <span className="font-mono font-semibold text-slate-100">{factor.value}</span> • Cohort Avg: <span className="font-mono text-slate-400">{factor.benchmark}</span>
                  </div>
                </div>

                <div className={`px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider flex items-center gap-1 ${badgeBg}`}>
                  {isNegative ? (
                    <>
                      <ArrowDownRight className="w-3 h-3 text-rose-400" />
                      Risk Factor
                    </>
                  ) : isPositive ? (
                    <>
                      <ArrowUpRight className="w-3 h-3 text-emerald-400" />
                      Strength
                    </>
                  ) : (
                    <>
                      <Minus className="w-3 h-3 text-slate-400" />
                      Neutral
                    </>
                  )}
                </div>
              </div>

              <p className="text-xs text-slate-300 leading-relaxed mt-2 pt-2 border-t border-slate-800/60">
                {factor.description}
              </p>
            </div>
          );
        })}
      </div>
    </div>
  );
}
