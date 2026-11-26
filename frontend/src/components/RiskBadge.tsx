import React from 'react';

interface RiskBadgeProps {
  severity: 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW' | 'HEALTHY' | 'OVERSTOCKED' | string;
  score?: number;
}

export const RiskBadge: React.FC<RiskBadgeProps> = ({ severity, score }) => {
  const sev = (severity || 'HEALTHY').toUpperCase();

  let bgClass = 'bg-slate-800/80 text-slate-300 border-white/10';
  let dotClass = 'bg-slate-400';

  if (sev === 'CRITICAL') {
    bgClass = 'bg-rose-500/10 text-rose-300 border-rose-500/30';
    dotClass = 'bg-rose-500 animate-pulse';
  } else if (sev === 'HIGH') {
    bgClass = 'bg-amber-500/10 text-amber-300 border-amber-500/30';
    dotClass = 'bg-amber-400';
  } else if (sev === 'MEDIUM' || sev === 'WARNING') {
    bgClass = 'bg-amber-500/10 text-amber-300 border-amber-500/20';
    dotClass = 'bg-amber-400';
  } else if (sev === 'LOW' || sev === 'HEALTHY') {
    bgClass = 'bg-emerald-500/10 text-emerald-300 border-emerald-500/30';
    dotClass = 'bg-emerald-400';
  } else if (sev === 'OVERSTOCKED') {
    bgClass = 'bg-sky-500/10 text-sky-300 border-sky-500/30';
    dotClass = 'bg-sky-400';
  }

  return (
    <span
      className={`inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-[11px] font-semibold tracking-wide border ${bgClass} backdrop-blur-sm`}
    >
      <span className={`w-1.5 h-1.5 rounded-full ${dotClass}`}></span>
      <span>{severity}</span>
      {score !== undefined && (
        <span className="opacity-75 font-mono text-[10px] pl-0.5 font-normal">({Math.round(score)})</span>
      )}
    </span>
  );
};
