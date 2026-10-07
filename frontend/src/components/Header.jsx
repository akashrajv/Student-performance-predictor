import React from 'react';
import { Sparkles, Bell, ShieldAlert, Cpu } from 'lucide-react';

export default function Header({ title, subtitle, onQuickPredict }) {
  return (
    <header className="h-16 border-b border-slate-200 bg-white/90 backdrop-blur-md px-6 flex items-center justify-between sticky top-0 z-20">
      <div>
        <h2 className="text-lg font-bold text-slate-900 tracking-tight leading-none">
          {title}
        </h2>
        {subtitle && (
          <p className="text-xs text-slate-500 mt-1 leading-none">{subtitle}</p>
        )}
      </div>

      <div className="flex items-center gap-3">
        <div className="hidden sm:flex items-center gap-2 px-3 py-1.5 rounded-lg bg-blue-50 border border-blue-200 text-xs text-blue-950 font-medium">
          <Cpu className="w-3.5 h-3.5 text-blue-700" />
          <span>Logistic Regression • Random Forest • XGBoost • LLM</span>
        </div>

        {onQuickPredict && (
          <button
            onClick={onQuickPredict}
            className="flex items-center gap-1.5 px-3.5 py-1.5 rounded-lg bg-blue-900 hover:bg-blue-950 text-white text-xs font-semibold shadow-sm shadow-blue-900/20 transition-all cursor-pointer"
          >
            <Sparkles className="w-3.5 h-3.5" />
            <span>New Prediction</span>
          </button>
        )}
      </div>
    </header>
  );
}
