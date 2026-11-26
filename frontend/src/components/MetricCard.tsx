import React from 'react';
import { LucideIcon } from 'lucide-react';

interface MetricCardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  icon: LucideIcon;
  trend?: {
    value: string;
    isPositive: boolean;
  };
  variant?: 'default' | 'critical' | 'warning' | 'success' | 'sky';
}

export const MetricCard: React.FC<MetricCardProps> = ({
  title,
  value,
  subtitle,
  icon: Icon,
  trend,
  variant = 'default',
}) => {
  let borderClass = 'border-white/[0.07] bg-slate-900/40 hover:border-white/[0.12]';
  let iconBg = 'bg-sky-500/10 text-sky-400 border-sky-500/20';
  let glowGradient = 'from-sky-500/5 to-transparent';

  if (variant === 'critical') {
    borderClass = 'border-rose-500/20 bg-rose-950/10 hover:border-rose-500/40';
    iconBg = 'bg-rose-500/15 text-rose-400 border-rose-500/30';
    glowGradient = 'from-rose-500/10 to-transparent';
  } else if (variant === 'warning') {
    borderClass = 'border-amber-500/20 bg-amber-950/10 hover:border-amber-500/40';
    iconBg = 'bg-amber-500/15 text-amber-400 border-amber-500/30';
    glowGradient = 'from-amber-500/10 to-transparent';
  } else if (variant === 'success') {
    borderClass = 'border-emerald-500/20 bg-emerald-950/10 hover:border-emerald-500/40';
    iconBg = 'bg-emerald-500/15 text-emerald-400 border-emerald-500/30';
    glowGradient = 'from-emerald-500/10 to-transparent';
  } else if (variant === 'sky') {
    borderClass = 'border-sky-500/20 bg-sky-950/10 hover:border-sky-500/40';
    iconBg = 'bg-sky-500/15 text-sky-400 border-sky-500/30';
    glowGradient = 'from-sky-500/10 to-transparent';
  }

  return (
    <div
      className={`relative overflow-hidden p-5 rounded-2xl border ${borderClass} backdrop-blur-md transition-all duration-200 group shadow-card-subtle`}
    >
      {/* Top subtle highlight gradient */}
      <div
        className={`absolute top-0 left-0 right-0 h-1 bg-gradient-to-r ${glowGradient} opacity-0 group-hover:opacity-100 transition-opacity`}
      />

      <div className="flex items-center justify-between">
        <span className="text-xs font-semibold uppercase tracking-wider text-slate-400">{title}</span>
        <div className={`p-2 rounded-xl border ${iconBg} shadow-sm group-hover:scale-105 transition-transform duration-200`}>
          <Icon className="w-4 h-4" />
        </div>
      </div>

      <div className="mt-4">
        <div className="text-2xl sm:text-3xl font-bold text-white tracking-tight">{value}</div>
        {(subtitle || trend) && (
          <div className="mt-1.5 flex items-center gap-2 text-xs text-slate-400">
            {trend && (
              <span
                className={`font-semibold px-1.5 py-0.5 rounded-md ${
                  trend.isPositive ? 'bg-emerald-500/10 text-emerald-400' : 'bg-rose-500/10 text-rose-400'
                }`}
              >
                {trend.value}
              </span>
            )}
            {subtitle && <span className="line-clamp-1">{subtitle}</span>}
          </div>
        )}
      </div>
    </div>
  );
};
