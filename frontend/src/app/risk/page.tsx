'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import { useQuery } from '@tanstack/react-query';
import { api } from '@/lib/api-client';
import { RiskSummaryResponse } from '@/types/api';
import { RiskBadge } from '@/components/RiskBadge';
import { MetricCard } from '@/components/MetricCard';
import {
  AlertOctagon,
  DollarSign,
  AlertTriangle,
  Sparkles,
  CheckCircle2,
  ShieldX,
  ExternalLink,
} from 'lucide-react';

export default function RiskAdvisoryPage() {
  const [severityFilter, setSeverityFilter] = useState('ALL');

  const { data: riskSummary, isLoading } = useQuery<RiskSummaryResponse>({
    queryKey: ['riskSummary', severityFilter],
    queryFn: () => api.getRiskSummary(severityFilter !== 'ALL' ? { severity: severityFilter } : {}),
  });

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="inline-flex items-center gap-1.5 text-xs font-semibold text-rose-400 mb-1">
            <ShieldX className="w-3.5 h-3.5" />
            Supply Chain Vulnerability Matrix
          </div>
          <h1 className="text-2xl font-extrabold text-white tracking-tight">
            Risk & Disruption Advisory
          </h1>
          <p className="text-xs sm:text-sm text-slate-400">
            Multi-factor composite scoring combining forecast velocity, safety buffers, and supplier contractual risk clauses.
          </p>
        </div>
      </div>

      {/* KPI Highlights */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <MetricCard
          title="Critical Vulnerabilities"
          value={riskSummary?.critical_risk_count || 0}
          subtitle="Immediate stockout threat"
          icon={AlertOctagon}
          variant="critical"
        />
        <MetricCard
          title="High Risk SKUs"
          value={riskSummary?.high_risk_count || 0}
          subtitle="Safety buffer breached"
          icon={AlertTriangle}
          variant="warning"
        />
        <MetricCard
          title="Capital at Risk"
          value={`$${(riskSummary?.total_capital_at_risk || 0).toLocaleString()}`}
          subtitle="Uncovered lead-time demand"
          icon={DollarSign}
          variant="sky"
        />
        <MetricCard
          title="Supplier Health Index"
          value={`${riskSummary?.average_supplier_reliability || 95}%`}
          subtitle="Contractual on-time SLA"
          icon={CheckCircle2}
          variant="success"
        />
      </div>

      {/* Filter Tabs */}
      <div className="flex items-center gap-1.5 p-1.5 rounded-2xl bg-slate-900/40 border border-white/[0.07] backdrop-blur-md w-fit overflow-x-auto">
        {['ALL', 'CRITICAL', 'HIGH', 'MEDIUM', 'LOW'].map((sev) => (
          <button
            key={sev}
            onClick={() => setSeverityFilter(sev)}
            className={`px-3.5 py-1.5 rounded-xl text-xs font-semibold transition-all duration-150 ${
              severityFilter === sev
                ? 'bg-sky-500 text-white shadow-glow-cyan'
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/40'
            }`}
          >
            {sev}
          </button>
        ))}
      </div>

      {/* Detailed Risk Ledger */}
      <div className="rounded-2xl border border-white/[0.07] bg-slate-900/40 backdrop-blur-md overflow-hidden shadow-card-subtle">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs text-slate-300">
            <thead className="text-[11px] uppercase tracking-wider bg-slate-950/60 text-slate-400 border-b border-white/[0.06]">
              <tr>
                <th className="px-6 py-4 font-bold">SKU & Item</th>
                <th className="px-6 py-4 font-bold">Supplier / Region</th>
                <th className="px-6 py-4 font-bold">Risk Breakdown</th>
                <th className="px-6 py-4 font-bold">Stock vs Lead Demand</th>
                <th className="px-6 py-4 font-bold">Financial Exposure</th>
                <th className="px-6 py-4 font-bold">Contract & Lead-Time Factors</th>
                <th className="px-6 py-4 font-bold text-right">RAG Advisory</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-white/[0.05]">
              {isLoading ? (
                <tr>
                  <td colSpan={7} className="px-6 py-12 text-center text-slate-400">
                    Computing multi-factor risk models...
                  </td>
                </tr>
              ) : riskSummary?.items?.length === 0 ? (
                <tr>
                  <td colSpan={7} className="px-6 py-12 text-center text-slate-400">
                    No SKUs matched the selected risk severity filter.
                  </td>
                </tr>
              ) : (
                riskSummary?.items?.map((item) => (
                  <tr key={item.sku} className="hover:bg-white/[0.02] transition-colors group">
                    <td className="px-6 py-4">
                      <Link
                        href={`/forecast/${item.sku}`}
                        className="font-bold text-sm text-white hover:text-sky-400 flex items-center gap-1 transition-colors"
                      >
                        {item.sku}
                        <ExternalLink className="w-3 h-3 text-slate-500 group-hover:text-sky-400 transition-colors" />
                      </Link>
                      <div className="text-xs text-slate-400 line-clamp-1">{item.product_name}</div>
                    </td>

                    <td className="px-6 py-4">
                      <div className="text-white font-medium">{item.supplier_name}</div>
                      <div className="text-[11px] text-slate-400">
                        {item.supplier_country} • {item.lead_time_days}d lead time
                      </div>
                    </td>

                    <td className="px-6 py-4">
                      <div className="space-y-1.5">
                        <div className="flex items-center gap-2">
                          <RiskBadge
                            severity={item.risk_breakdown.severity}
                            score={item.risk_breakdown.composite_risk_score}
                          />
                        </div>
                        <div className="text-[10px] text-slate-400 flex items-center gap-3">
                          <span>
                            Stockout: <strong className="text-slate-200">{item.risk_breakdown.stockout_risk_score}</strong>
                          </span>
                          <span>
                            Supplier: <strong className="text-slate-200">{item.risk_breakdown.supplier_disruption_risk}</strong>
                          </span>
                        </div>
                      </div>
                    </td>

                    <td className="px-6 py-4 text-xs">
                      <div>
                        On-Hand: <strong className="text-white">{item.current_stock}</strong>
                      </div>
                      <div className="text-slate-400">
                        Demand in Lead: <strong className="text-slate-200">{item.forecasted_demand_lead_time}</strong>
                      </div>
                      <div
                        className={`font-semibold mt-0.5 ${
                          item.projected_net_stock < 0 ? 'text-rose-400' : 'text-emerald-400'
                        }`}
                      >
                        Net: {item.projected_net_stock} units
                      </div>
                    </td>

                    <td className="px-6 py-4 font-bold text-white text-sm">
                      ${item.financial_impact_risk.toLocaleString()}
                    </td>

                    <td className="px-6 py-4 max-w-xs">
                      <div className="space-y-1">
                        {item.risk_reasons.slice(0, 2).map((reason, idx) => (
                          <div
                            key={idx}
                            className="text-[11px] text-slate-300 flex items-start gap-1.5 bg-slate-800/40 px-2 py-1 rounded-md border border-white/[0.04]"
                          >
                            <span className="text-amber-400 shrink-0 mt-0.5">•</span>
                            <span className="line-clamp-2">{reason}</span>
                          </div>
                        ))}
                      </div>
                    </td>

                    <td className="px-6 py-4 text-right">
                      <Link
                        href={`/chat?q=What+mitigation+steps+should+we+take+for+${item.sku}+from+${encodeURIComponent(
                          item.supplier_name
                        )}%3F`}
                        className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-sky-500/10 hover:bg-sky-500/20 text-sky-300 border border-sky-500/30 text-xs font-semibold transition-all shadow-sm"
                      >
                        <Sparkles className="w-3.5 h-3.5" />
                        Mitigate
                      </Link>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
