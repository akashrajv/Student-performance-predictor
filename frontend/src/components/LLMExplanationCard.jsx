import React, { useState } from 'react';
import {
  Sparkles,
  AlertCircle,
  Target,
  BookOpen,
  UserCheck,
  Printer,
  Copy,
  Check,
  Bot,
} from 'lucide-react';

export default function LLMExplanationCard({
  explanationData,
  loading = false,
  onGenerate,
}) {
  const [copied, setCopied] = useState(false);

  if (loading) {
    return (
      <div className="p-8 rounded-2xl glass-card border border-indigo-500/30 text-center space-y-4">
        <div className="w-12 h-12 rounded-2xl bg-indigo-600/20 border border-indigo-500/40 mx-auto flex items-center justify-center animate-pulse">
          <Sparkles className="w-6 h-6 text-indigo-400 animate-spin" />
        </div>
        <div>
          <h4 className="text-base font-bold text-slate-100">
            Synthesizing Grounded Pedagogical Analysis...
          </h4>
          <p className="text-xs text-slate-400 mt-1 max-w-md mx-auto">
            The LLM is analyzing the model's prediction, probability distribution, and feature attributions to formulate structured academic recommendations.
          </p>
        </div>
      </div>
    );
  }

  if (!explanationData) {
    return (
      <div className="p-6 rounded-2xl glass-card border border-dashed border-slate-700 text-center space-y-3">
        <div className="w-10 h-10 rounded-xl bg-slate-800 text-slate-400 mx-auto flex items-center justify-center">
          <Bot className="w-5 h-5" />
        </div>
        <div>
          <h4 className="text-sm font-semibold text-slate-200">
            AI Academic Advisor & Explanation
          </h4>
          <p className="text-xs text-slate-400 max-w-sm mx-auto mt-1">
            Generate simple explanations, root causes of underperformance, and personalized early interventions.
          </p>
        </div>
        {onGenerate && (
          <button
            onClick={onGenerate}
            className="px-4 py-2 rounded-xl bg-gradient-to-r from-indigo-600 to-violet-600 hover:from-indigo-500 hover:to-violet-500 text-white text-xs font-semibold shadow-md shadow-indigo-500/20 transition-all cursor-pointer inline-flex items-center gap-2"
          >
            <Sparkles className="w-3.5 h-3.5" />
            <span>Generate AI Explanation & Action Plan</span>
          </button>
        )}
      </div>
    );
  }

  const {
    explanation,
    possible_causes = [],
    attention_areas = [],
    personalized_recommendations = [],
    early_interventions = [],
    model_used,
  } = explanationData;

  const handleCopy = () => {
    const text = `
ACADEMIC INTERVENTION REPORT
${explanation}

POSSIBLE CAUSES:
${possible_causes.map((c) => `- ${c}`).join('\n')}

AREAS NEEDING ATTENTION:
${attention_areas.map((a) => `- ${a}`).join('\n')}

PERSONALIZED RECOMMENDATIONS:
${personalized_recommendations.map((r) => `- ${r}`).join('\n')}

EARLY INTERVENTIONS FOR EDUCATORS:
${early_interventions.map((i) => `- ${i}`).join('\n')}
    `.trim();

    navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handlePrint = () => {
    window.print();
  };

  return (
    <div className="rounded-2xl glass-card border border-indigo-500/25 p-6 space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-slate-800 pb-4">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-indigo-500 to-purple-500 flex items-center justify-center text-white shadow-md shadow-indigo-500/20">
            <Sparkles className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-base font-bold text-slate-100 flex items-center gap-2">
              <span>AI Academic Advisor Report</span>
              <span className="text-[10px] px-2 py-0.5 rounded-full bg-indigo-500/20 text-indigo-300 font-mono font-medium">
                {model_used || 'AI Engine'}
              </span>
            </h3>
            <p className="text-xs text-slate-400">
              Grounded, transparent reasoning powered by ML attribution
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2 no-print">
          <button
            onClick={handleCopy}
            className="px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-medium border border-slate-700 transition-colors inline-flex items-center gap-1.5 cursor-pointer"
          >
            {copied ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
            <span>{copied ? 'Copied' : 'Copy Report'}</span>
          </button>
          <button
            onClick={handlePrint}
            className="px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-medium border border-slate-700 transition-colors inline-flex items-center gap-1.5 cursor-pointer"
          >
            <Printer className="w-3.5 h-3.5" />
            <span>Print Report</span>
          </button>
        </div>
      </div>

      {/* 1. Simple Natural Language Explanation */}
      <div className="p-4 rounded-xl bg-indigo-950/30 border border-indigo-500/20 space-y-1.5">
        <div className="text-xs font-bold text-indigo-300 uppercase tracking-wider flex items-center gap-1.5">
          <Bot className="w-3.5 h-3.5" />
          Executive Academic Summary
        </div>
        <p className="text-sm text-slate-200 leading-relaxed font-normal">
          {explanation}
        </p>
      </div>

      {/* 2. Grid: Possible Causes & Areas Needing Attention */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Possible Causes */}
        <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800 space-y-2.5">
          <h4 className="text-xs font-bold text-rose-300 uppercase tracking-wider flex items-center gap-1.5">
            <AlertCircle className="w-3.5 h-3.5 text-rose-400" />
            Identified Factors & Causes
          </h4>
          <ul className="space-y-2">
            {possible_causes.map((cause, idx) => (
              <li key={idx} className="text-xs text-slate-300 flex items-start gap-2">
                <span className="w-1.5 h-1.5 rounded-full bg-rose-400 mt-1.5 shrink-0" />
                <span>{cause}</span>
              </li>
            ))}
          </ul>
        </div>

        {/* Areas Needing Attention */}
        <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800 space-y-2.5">
          <h4 className="text-xs font-bold text-amber-300 uppercase tracking-wider flex items-center gap-1.5">
            <Target className="w-3.5 h-3.5 text-amber-400" />
            Areas Requiring Immediate Attention
          </h4>
          <ul className="space-y-2">
            {attention_areas.map((area, idx) => (
              <li key={idx} className="text-xs text-slate-300 flex items-start gap-2">
                <span className="w-1.5 h-1.5 rounded-full bg-amber-400 mt-1.5 shrink-0" />
                <span>{area}</span>
              </li>
            ))}
          </ul>
        </div>
      </div>

      {/* 3. Actionable Personalized Recommendations & Early Interventions */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Student Recommendations */}
        <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800 space-y-2.5">
          <h4 className="text-xs font-bold text-indigo-300 uppercase tracking-wider flex items-center gap-1.5">
            <BookOpen className="w-3.5 h-3.5 text-indigo-400" />
            Personalized Academic Recommendations
          </h4>
          <ul className="space-y-2.5">
            {personalized_recommendations.map((rec, idx) => (
              <li key={idx} className="text-xs text-slate-200 flex items-start gap-2 bg-slate-800/40 p-2 rounded-lg">
                <span className="text-indigo-400 font-bold text-xs">#{idx + 1}</span>
                <span>{rec}</span>
              </li>
            ))}
          </ul>
        </div>

        {/* Educator Early Interventions */}
        <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800 space-y-2.5">
          <h4 className="text-xs font-bold text-emerald-300 uppercase tracking-wider flex items-center gap-1.5">
            <UserCheck className="w-3.5 h-3.5 text-emerald-400" />
            Early Interventions for Educators & Counselors
          </h4>
          <ul className="space-y-2.5">
            {early_interventions.map((action, idx) => (
              <li key={idx} className="text-xs text-slate-200 flex items-start gap-2 bg-emerald-950/20 border border-emerald-500/20 p-2 rounded-lg">
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 mt-1.5 shrink-0" />
                <span>{action}</span>
              </li>
            ))}
          </ul>
        </div>
      </div>
    </div>
  );
}
