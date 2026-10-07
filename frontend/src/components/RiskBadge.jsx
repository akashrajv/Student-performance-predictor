import React from 'react';
import { AlertTriangle, CheckCircle2, AlertCircle, ShieldAlert } from 'lucide-react';

export default function RiskBadge({ risk, size = 'md', showIcon = true }) {
  const norm = (risk || '').toLowerCase();

  let bg = 'bg-slate-800 text-slate-300 border-slate-700';
  let icon = <AlertCircle className="w-4 h-4" />;
  let label = risk || 'Unknown';

  if (norm.includes('high') || norm === 'low') {
    // High Risk / Low Performance
    bg = 'bg-rose-500/15 text-rose-400 border-rose-500/30';
    icon = <ShieldAlert className={size === 'lg' ? 'w-5 h-5' : 'w-3.5 h-3.5'} />;
    label = risk || 'High Risk';
  } else if (norm.includes('mod') || norm === 'medium') {
    // Moderate Risk / Medium Performance
    bg = 'bg-amber-500/15 text-amber-400 border-amber-500/30';
    icon = <AlertTriangle className={size === 'lg' ? 'w-5 h-5' : 'w-3.5 h-3.5'} />;
    label = risk || 'Moderate Risk';
  } else if (norm.includes('low') || norm === 'high') {
    // Low Risk / High Performance
    bg = 'bg-emerald-500/15 text-emerald-400 border-emerald-500/30';
    icon = <CheckCircle2 className={size === 'lg' ? 'w-5 h-5' : 'w-3.5 h-3.5'} />;
    label = risk || 'Low Risk';
  }

  const sizeClasses = {
    sm: 'text-xs px-2 py-0.5 gap-1 font-medium',
    md: 'text-xs px-2.5 py-1 gap-1.5 font-semibold',
    lg: 'text-sm px-3.5 py-1.5 gap-2 font-bold',
  };

  return (
    <span
      className={`inline-flex items-center rounded-full border ${bg} ${sizeClasses[size] || sizeClasses.md} transition-colors`}
    >
      {showIcon && icon}
      <span>{label}</span>
    </span>
  );
}
