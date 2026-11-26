'use client';

import React from 'react';
import {
  ResponsiveContainer,
  ComposedChart,
  Line,
  Area,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  Legend,
} from 'recharts';

interface ForecastChartProps {
  data: Array<{
    date: string;
    actual?: number;
    forecast?: number;
    lower?: number;
    upper?: number;
  }>;
  modelType: string;
}

const CustomTooltip = ({ active, payload, label }: any) => {
  if (active && payload && payload.length) {
    return (
      <div className="rounded-xl border border-white/10 bg-slate-900/90 p-3.5 shadow-2xl backdrop-blur-xl text-xs space-y-1.5 min-w-[170px]">
        <div className="font-bold text-white border-b border-white/[0.08] pb-1.5 flex items-center justify-between">
          <span>{label}</span>
        </div>
        {payload.map((entry: any, index: number) => {
          if (entry.dataKey === 'lower' || entry.dataKey === 'upper') return null;
          return (
            <div key={index} className="flex items-center justify-between gap-3">
              <span className="text-slate-400 flex items-center gap-1.5">
                <span className="w-2 h-2 rounded-full" style={{ backgroundColor: entry.color }} />
                {entry.name}:
              </span>
              <span className="font-mono font-bold text-white">
                {entry.value !== undefined ? Math.round(entry.value) : '—'} units
              </span>
            </div>
          );
        })}
        {payload.find((p: any) => p.dataKey === 'lower') && payload.find((p: any) => p.dataKey === 'upper') && (
          <div className="text-[10px] text-indigo-300/80 pt-1 border-t border-white/[0.05] flex justify-between font-mono">
            <span>95% CI:</span>
            <span>
              {Math.round(payload.find((p: any) => p.dataKey === 'lower')?.value || 0)} -{' '}
              {Math.round(payload.find((p: any) => p.dataKey === 'upper')?.value || 0)}
            </span>
          </div>
        )}
      </div>
    );
  }
  return null;
};

export default function ForecastChart({ data, modelType }: ForecastChartProps) {
  return (
    <div className="w-full h-80 sm:h-96">
      <ResponsiveContainer width="100%" height="100%">
        <ComposedChart data={data} margin={{ top: 10, right: 10, left: -15, bottom: 0 }}>
          <defs>
            <linearGradient id="forecastGlow" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="#6366f1" stopOpacity={0.25} />
              <stop offset="100%" stopColor="#6366f1" stopOpacity={0.0} />
            </linearGradient>
            <linearGradient id="confidenceArea" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="#38bdf8" stopOpacity={0.15} />
              <stop offset="100%" stopColor="#38bdf8" stopOpacity={0.02} />
            </linearGradient>
          </defs>

          <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.04)" vertical={false} />
          <XAxis
            dataKey="date"
            stroke="#64748b"
            tick={{ fill: '#64748b', fontSize: 11 }}
            tickLine={false}
            axisLine={{ stroke: 'rgba(255,255,255,0.08)' }}
          />
          <YAxis
            stroke="#64748b"
            tick={{ fill: '#64748b', fontSize: 11 }}
            tickLine={false}
            axisLine={false}
          />
          <Tooltip content={<CustomTooltip />} />
          <Legend
            verticalAlign="top"
            align="right"
            iconType="circle"
            wrapperStyle={{ paddingBottom: '12px', fontSize: '12px', color: '#94a3b8' }}
          />

          {/* 95% Confidence Interval Area */}
          <Area
            type="monotone"
            dataKey="upper"
            stroke="transparent"
            fill="url(#confidenceArea)"
            name="Upper Bound (95%)"
          />
          <Area
            type="monotone"
            dataKey="lower"
            stroke="transparent"
            fill="transparent"
            name="Lower Bound (5%)"
          />

          {/* Historical Demand Line */}
          <Line
            type="monotone"
            dataKey="actual"
            stroke="#94a3b8"
            strokeWidth={2}
            dot={false}
            activeDot={{ r: 4, stroke: '#94a3b8', fill: '#0f172a' }}
            name="Historical Demand"
          />

          {/* Predicted Demand Line */}
          <Line
            type="monotone"
            dataKey="forecast"
            stroke="#6366f1"
            strokeWidth={3}
            dot={false}
            activeDot={{ r: 5, stroke: '#818cf8', fill: '#080c14', strokeWidth: 2 }}
            name={`${modelType === 'lightgbm' ? 'LightGBM' : 'Prophet'} Forecast`}
          />
        </ComposedChart>
      </ResponsiveContainer>
    </div>
  );
}
