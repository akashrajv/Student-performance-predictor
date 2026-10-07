import React from 'react';
import { Bot, CheckCircle2, AlertTriangle, ShieldAlert, Info } from 'lucide-react';
import RiskBadge from './RiskBadge';

export default function ModelConsensusCard({ consensus }) {
  if (!consensus) return null;

  const {
    final_prediction = 'Unknown',
    models_agree_display = 'N/A',
    consensus_percentage = 0,
    consensus_status = 'N/A',
    average_confidence_display = 'Confidence unavailable',
    model_predictions = {},
  } = consensus;

  const isStrong = consensus_status.includes('Strong');
  const isModerate = consensus_status.includes('Moderate');
  const isUncertain = consensus_status.includes('Uncertain') || consensus_status.includes('Disagreement');

  const modelsList = ['Logistic Regression', 'Random Forest', 'XGBoost'];

  return (
    <div className="p-6 rounded-2xl glass-card border border-blue-500/40 bg-gradient-to-br from-slate-900 via-blue-950/20 to-slate-900 shadow-xl space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-slate-800 pb-4">
        <div className="flex items-center gap-3">
          <div className="p-2.5 rounded-xl bg-blue-500/10 border border-blue-500/30 text-blue-400">
            <Bot className="w-6 h-6" />
          </div>
          <div>
            <h3 className="text-lg font-black text-white flex items-center gap-2">
              <span>MODEL CONSENSUS</span>
              <span className="text-xs px-2.5 py-0.5 rounded-full font-semibold bg-blue-500/15 text-blue-300 border border-blue-500/30">
                Multi-Model Agreement
              </span>
            </h3>
            <p className="text-xs text-slate-400 mt-0.5">
              Simultaneous majority-voting across Logistic Regression, Random Forest & XGBoost
            </p>
          </div>
        </div>

        {/* Status Badge */}
        <div>
          {isStrong && (
            <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold bg-emerald-500/20 text-emerald-300 border border-emerald-500/40">
              <CheckCircle2 className="w-3.5 h-3.5" /> Strong Model Consensus
            </span>
          )}
          {isModerate && (
            <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold bg-amber-500/20 text-amber-300 border border-amber-500/40">
              <AlertTriangle className="w-3.5 h-3.5" /> Moderate Model Consensus
            </span>
          )}
          {isUncertain && (
            <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold bg-rose-500/20 text-rose-300 border border-rose-500/40">
              <ShieldAlert className="w-3.5 h-3.5" /> Model Disagreement – Prediction Uncertain
            </span>
          )}
        </div>
      </div>

      {/* 3 Model Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {modelsList.map((mName) => {
          const mData = model_predictions[mName] || {};
          const pred = mData.prediction || 'Unknown';
          const conf = mData.confidence_display || 'Confidence unavailable';

          return (
            <div
              key={mName}
              className="p-4 rounded-xl bg-slate-900/80 border border-slate-800 hover:border-slate-700 transition-colors space-y-3"
            >
              <div className="flex items-center justify-between">
                <span className="text-xs font-bold text-slate-300">{mName}</span>
                <span className="text-[10px] text-slate-500 font-mono">Algorithm</span>
              </div>

              <div>
                <span className="text-[11px] text-slate-400 block mb-1">Prediction:</span>
                <RiskBadge risk={pred} size="sm" />
              </div>

              <div className="pt-2 border-t border-slate-800/80 flex items-center justify-between text-xs">
                <span className="text-slate-400">Confidence:</span>
                <span className="font-semibold text-slate-200">{conf}</span>
              </div>
            </div>
          );
        })}
      </div>

      {/* Consensus Summary Metrics */}
      <div className="p-4 rounded-xl bg-slate-950/70 border border-slate-800 grid grid-cols-2 sm:grid-cols-4 gap-4 text-center">
        <div>
          <div className="text-[10px] uppercase font-semibold text-slate-400">Final Prediction</div>
          <div className="text-base sm:text-lg font-black text-white mt-1">
            {final_prediction.toUpperCase()}
          </div>
        </div>

        <div>
          <div className="text-[10px] uppercase font-semibold text-slate-400">Models Agree</div>
          <div className="text-base sm:text-lg font-black text-blue-400 mt-1">
            {models_agree_display}
          </div>
        </div>

        <div>
          <div className="text-[10px] uppercase font-semibold text-slate-400">Consensus</div>
          <div className="text-base sm:text-lg font-black text-purple-400 mt-1">
            {typeof consensus_percentage === 'number'
              ? `${consensus_percentage.toFixed(2)}%`
              : `${consensus_percentage}%`}
          </div>
        </div>

        <div>
          <div className="text-[10px] uppercase font-semibold text-slate-400">Average Confidence</div>
          <div className="text-base sm:text-lg font-black text-emerald-400 mt-1">
            {average_confidence_display}
          </div>
        </div>
      </div>

      {/* Disclaimer */}
      <div className="flex items-start gap-2 text-[11px] text-slate-400 bg-slate-900/50 p-2.5 rounded-lg border border-slate-800">
        <Info className="w-4 h-4 text-blue-400 shrink-0 mt-0.5" />
        <span>
          <strong>Important Note:</strong> Model consensus indicates agreement across 3 independent
          machine learning algorithms and is distinct from classification accuracy. 100% consensus
          does not imply 100% accuracy.
        </span>
      </div>
    </div>
  );
}
