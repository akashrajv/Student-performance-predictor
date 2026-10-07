import React from 'react';
import {
  LayoutDashboard,
  UserCheck,
  FileSpreadsheet,
  BarChart3,
  Users,
  Database,
  BrainCircuit,
  GraduationCap,
  Sparkles,
  FileText,
} from 'lucide-react';

export default function Sidebar({ activeTab, setActiveTab, modelsReady = true }) {
  const navItems = [
    {
      id: 'dashboard',
      label: 'Dashboard',
      icon: LayoutDashboard,
      desc: 'Overview & Statistics',
    },
    {
      id: 'predict',
      label: 'Predict Performance',
      icon: UserCheck,
      desc: 'Single Student Inference',
      badge: 'Core',
    },
    {
      id: 'batch',
      label: 'Batch Prediction',
      icon: FileSpreadsheet,
      desc: 'Upload CSV & Batch Score',
    },
    {
      id: 'analysis',
      label: 'Model Analysis',
      icon: BarChart3,
      desc: 'Metrics & Comparisons',
    },
    {
      id: 'students',
      label: 'Student Directory',
      icon: Users,
      desc: 'Profiles & History',
    },
    {
      id: 'resume',
      label: 'Resume Analyzer',
      icon: FileText,
      desc: 'AI Matching & Placement',
      badge: 'New',
    },
    {
      id: 'dataset',
      label: 'Dataset & Training',
      icon: Database,
      desc: 'Retrain Models & Data',
    },
  ];

  return (
    <aside className="w-64 bg-slate-900/90 border-r border-slate-800 flex flex-col h-screen sticky top-0 z-30 select-none backdrop-blur-md">
      {/* Brand Header */}
      <div className="p-5 border-b border-slate-800/80">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-indigo-600 to-violet-500 flex items-center justify-center shadow-lg shadow-indigo-500/25">
            <BrainCircuit className="w-6 h-6 text-white" />
          </div>
          <div>
            <h1 className="font-bold text-slate-100 text-sm tracking-tight leading-tight">
              Student Performance
            </h1>
            <span className="text-xs text-indigo-400 font-semibold flex items-center gap-1">
              <Sparkles className="w-3 h-3 inline" /> AI Predictor
            </span>
          </div>
        </div>
      </div>

      {/* Navigation List */}
      <nav className="flex-1 p-3 space-y-1.5 overflow-y-auto">
        <div className="px-3 pt-2 pb-1 text-[11px] font-semibold uppercase tracking-wider text-slate-400">
          Navigation
        </div>
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = activeTab === item.id;
          return (
            <button
              key={item.id}
              onClick={() => setActiveTab(item.id)}
              className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-left text-sm transition-all duration-150 group relative ${
                isActive
                  ? 'bg-indigo-600 text-white font-medium shadow-md shadow-indigo-600/30'
                  : 'text-slate-300 hover:text-white hover:bg-slate-800/60'
              }`}
            >
              <Icon
                className={`w-4 h-4 transition-colors ${
                  isActive ? 'text-white' : 'text-slate-400 group-hover:text-indigo-400'
                }`}
              />
              <div className="flex-1 truncate">
                <div className="leading-tight">{item.label}</div>
                <div
                  className={`text-[11px] truncate ${
                    isActive ? 'text-indigo-200' : 'text-slate-400'
                  }`}
                >
                  {item.desc}
                </div>
              </div>
              {item.badge && (
                <span
                  className={`text-[10px] px-1.5 py-0.5 rounded font-bold uppercase tracking-wider ${
                    isActive
                      ? 'bg-white/20 text-white'
                      : 'bg-indigo-500/20 text-indigo-300'
                  }`}
                >
                  {item.badge}
                </span>
              )}
            </button>
          );
        })}
      </nav>

      {/* Models Status and Project Footer */}
      <div className="p-3 border-t border-slate-800/80 bg-slate-950/40 space-y-2">
        <div className="px-2 py-1.5 rounded-lg bg-slate-800/60 border border-slate-700/50 flex items-center justify-between text-xs">
          <span className="text-slate-400 flex items-center gap-1.5">
            <span
              className={`w-2 h-2 rounded-full ${
                modelsReady ? 'bg-emerald-400 animate-pulse' : 'bg-amber-400'
              }`}
            />
            ML Pipeline
          </span>
          <span className="font-semibold text-emerald-400">
            {modelsReady ? 'Active (4 Models)' : 'Untrained'}
          </span>
        </div>

        <div className="px-2 pt-1 text-[11px] text-slate-400 leading-snug">
          <div className="font-medium text-slate-300 flex items-center gap-1">
            <GraduationCap className="w-3.5 h-3.5 text-indigo-400 inline" />
            Project Presentation Spec
          </div>
          <div>Akashraj (61782324110006)</div>
        </div>
      </div>
    </aside>
  );
}
