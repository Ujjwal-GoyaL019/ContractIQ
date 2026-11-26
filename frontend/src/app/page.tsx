'use client';

import React from 'react';
import Link from 'next/link';
import { useQuery } from '@tanstack/react-query';
import { api } from '@/lib/api-client';
import { MetricCard } from '@/components/MetricCard';
import { RiskBadge } from '@/components/RiskBadge';
import {
  Boxes,
  TrendingUp,
  Building2,
  ArrowRight,
  AlertTriangle,
  Sparkles,
  ExternalLink,
  ShieldCheck,
  ChevronRight,
  Activity,
  FileSearch,
} from 'lucide-react';
import { RiskSummaryResponse } from '@/types/api';
import { useAuth } from '@/lib/auth-context';

export default function DashboardPage() {
  const { user } = useAuth();
  const { data: riskData, isLoading: isRiskLoading } = useQuery<RiskSummaryResponse>({
    queryKey: ['riskSummary'],
    queryFn: () => api.getRiskSummary(),
  });

  const totalSKUs = riskData?.total_skus || 0;
  const criticalCount = riskData?.critical_risk_count || 0;
  const capitalAtRisk = riskData?.total_capital_at_risk || 0;
  const supplierReliability = riskData?.average_supplier_reliability || 95;

  return (
    <div className="space-y-8">
      {/* Hero Welcome Banner */}
      <div className="relative overflow-hidden rounded-3xl border border-white/[0.08] bg-gradient-to-br from-slate-900/90 via-slate-900/60 to-slate-950 p-6 sm:p-8 backdrop-blur-xl shadow-card-subtle">
        {/* Glow ambient circle */}
        <div className="absolute -right-20 -top-20 w-80 h-80 bg-sky-500/10 rounded-full blur-3xl pointer-events-none" />
        <div className="absolute -left-20 -bottom-20 w-80 h-80 bg-indigo-500/10 rounded-full blur-3xl pointer-events-none" />

        <div className="relative z-10 flex flex-col md:flex-row md:items-center justify-between gap-6">
          <div className="space-y-2 max-w-2xl">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-sky-500/10 border border-sky-500/20 text-sky-300 text-xs font-semibold">
              <Sparkles className="w-3.5 h-3.5 text-sky-400" />
              {user ? `Welcome, ${user.full_name || user.email.split('@')[0]} (${user.role.toUpperCase()})` : 'ContractIQ Supply Intelligence'}
            </div>
            <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight">
              Executive Supplier &amp; Risk Overview
            </h1>
            <p className="text-sm text-slate-400 leading-relaxed">
              Unifying dual time-series demand forecasting (Prophet &amp; LightGBM) with grounded supplier contract RAG intelligence.
            </p>
          </div>

          <div className="flex flex-wrap items-center gap-3">
            <Link
              href="/chat"
              className="flex items-center gap-2 px-4 py-2.5 rounded-xl bg-gradient-to-r from-cyan-500 via-sky-500 to-indigo-600 hover:from-cyan-400 hover:to-indigo-500 text-white text-xs font-semibold shadow-glow-cyan transition-all duration-200"
            >
              <Sparkles className="w-4 h-4" />
              Ask Contract RAG
            </Link>
            <Link
              href="/risk"
              className="flex items-center gap-2 px-4 py-2.5 rounded-xl bg-slate-800/80 hover:bg-slate-700/80 text-slate-200 text-xs font-medium border border-white/10 hover:border-white/20 transition-all duration-200"
            >
              Risk Matrix
              <ArrowRight className="w-3.5 h-3.5" />
            </Link>
          </div>
        </div>
      </div>

      {/* KPI Cards Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <MetricCard
          title="Critical Stockouts"
          value={criticalCount}
          subtitle="SKUs requiring urgent order"
          icon={AlertTriangle}
          variant={criticalCount > 0 ? 'critical' : 'success'}
        />
        <MetricCard
          title="Capital at Risk"
          value={`$${capitalAtRisk.toLocaleString()}`}
          subtitle="Unbuffered lead-time demand"
          icon={TrendingUp}
          variant="warning"
        />
        <MetricCard
          title="Managed SKUs"
          value={totalSKUs}
          subtitle="Across active warehouses"
          icon={Boxes}
          variant="sky"
        />
        <MetricCard
          title="Supplier Reliability"
          value={`${supplierReliability}%`}
          subtitle="On-time fulfillment index"
          icon={Building2}
          variant="success"
        />
      </div>

      {/* Main Grid: Action Queue (2/3) + AI Advisor Assistant (1/3) */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Urgent Procurement Action Queue */}
        <div className="lg:col-span-2 space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-base font-bold text-white flex items-center gap-2">
                <Activity className="w-4 h-4 text-sky-400" />
                Urgent Procurement Action Queue
              </h2>
              <p className="text-xs text-slate-400">Ranked by composite stockout risk & financial exposure</p>
            </div>
            <Link
              href="/risk"
              className="text-xs text-sky-400 hover:text-sky-300 font-semibold flex items-center gap-1 group"
            >
              View all ({riskData?.items?.length || 0})
              <ChevronRight className="w-3.5 h-3.5 group-hover:translate-x-0.5 transition-transform" />
            </Link>
          </div>

          <div className="rounded-2xl border border-white/[0.07] bg-slate-900/40 backdrop-blur-md overflow-hidden divide-y divide-white/[0.05]">
            {isRiskLoading ? (
              <div className="p-8 text-center text-xs text-slate-400">Loading risk assessments...</div>
            ) : riskData?.items?.length === 0 ? (
              <div className="p-10 text-center text-xs text-slate-400 flex flex-col items-center gap-3">
                <div className="w-10 h-10 rounded-full bg-emerald-500/10 flex items-center justify-center border border-emerald-500/20 text-emerald-400">
                  <ShieldCheck className="w-5 h-5" />
                </div>
                <span>All SKU inventory buffers are currently healthy!</span>
              </div>
            ) : (
              riskData?.items?.slice(0, 4).map((item) => (
                <div
                  key={item.sku}
                  className="p-5 hover:bg-white/[0.02] transition-colors flex flex-col sm:flex-row sm:items-center justify-between gap-4"
                >
                  <div className="space-y-2 flex-1">
                    <div className="flex items-center gap-2.5 flex-wrap">
                      <Link
                        href={`/forecast/${item.sku}`}
                        className="font-bold text-sm text-white hover:text-sky-300 transition-colors"
                      >
                        {item.sku}
                      </Link>
                      <span className="text-xs text-slate-400">• {item.product_name}</span>
                      <RiskBadge
                        severity={item.risk_breakdown.severity}
                        score={item.risk_breakdown.composite_risk_score}
                      />
                    </div>

                    {/* Micro info pills */}
                    <div className="flex items-center gap-4 text-xs text-slate-400 flex-wrap">
                      <span>
                        On-Hand: <strong className="text-slate-200">{item.current_stock}</strong>
                      </span>
                      <span>
                        Lead Time: <strong className="text-slate-200">{item.lead_time_days}d</strong>
                      </span>
                      <span>
                        Runway:{' '}
                        <strong
                          className={
                            item.days_until_stockout < 10
                              ? 'text-rose-400'
                              : item.days_until_stockout < 20
                              ? 'text-amber-400'
                              : 'text-emerald-400'
                          }
                        >
                          {item.days_until_stockout} days left
                        </strong>
                      </span>
                    </div>

                    <div className="text-xs text-slate-300 bg-slate-800/40 rounded-lg px-3 py-1.5 border border-white/[0.04]">
                      💡 <span className="text-sky-200 font-medium">{item.suggested_action}</span>
                    </div>
                  </div>

                  <div className="flex sm:flex-col items-end justify-between sm:justify-center gap-2">
                    <div className="text-right">
                      <span className="text-[10px] uppercase tracking-wider text-slate-500 font-semibold">Exposure</span>
                      <div className="text-sm font-bold text-white">${item.financial_impact_risk.toLocaleString()}</div>
                    </div>
                    <Link
                      href={`/forecast/${item.sku}`}
                      className="px-3 py-1.5 rounded-lg bg-sky-500/10 hover:bg-sky-500/20 text-sky-300 border border-sky-500/30 text-xs font-semibold transition-all flex items-center gap-1"
                    >
                      Forecast
                      <ExternalLink className="w-3 h-3" />
                    </Link>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>

        {/* AI Assistant Quick Intelligence Box */}
        <div className="space-y-4">
          <div>
            <h2 className="text-base font-bold text-white flex items-center gap-2">
              <FileSearch className="w-4 h-4 text-sky-400" />
              Contract Document RAG
            </h2>
            <p className="text-xs text-slate-400">Ask natural language questions to contracts</p>
          </div>

          <div className="p-5 rounded-2xl border border-white/[0.07] bg-slate-900/40 backdrop-blur-md space-y-4">
            <p className="text-xs text-slate-300 leading-relaxed">
              Qdrant vector engine searches across active supplier agreements, SLAs, and lead-time amendments.
            </p>

            <div className="space-y-2">
              <span className="text-[10px] uppercase tracking-wider text-slate-500 font-bold">Suggested Prompts:</span>

              <Link
                href="/chat?q=Which+suppliers+have+force+majeure+or+lead-time+risk+notices?"
                className="block p-3 rounded-xl bg-slate-800/40 hover:bg-slate-800/80 border border-white/[0.05] hover:border-sky-500/30 text-xs text-slate-300 hover:text-white transition-all group"
              >
                <div className="flex items-center justify-between">
                  <span className="line-clamp-1 font-medium">⚠️ Which suppliers have force majeure notices?</span>
                  <ChevronRight className="w-3.5 h-3.5 text-slate-500 group-hover:text-sky-400 group-hover:translate-x-0.5 transition-all shrink-0" />
                </div>
              </Link>

              <Link
                href="/chat?q=What+are+the+contractual+surcharges+for+expedited+MCU+orders?"
                className="block p-3 rounded-xl bg-slate-800/40 hover:bg-slate-800/80 border border-white/[0.05] hover:border-sky-500/30 text-xs text-slate-300 hover:text-white transition-all group"
              >
                <div className="flex items-center justify-between">
                  <span className="line-clamp-1 font-medium">📦 What are surcharges for expedited MCU orders?</span>
                  <ChevronRight className="w-3.5 h-3.5 text-slate-500 group-hover:text-sky-400 group-hover:translate-x-0.5 transition-all shrink-0" />
                </div>
              </Link>

              <Link
                href="/chat?q=Which+SKUs+are+impacted+by+Pacific+Optics+delivery+delays?"
                className="block p-3 rounded-xl bg-slate-800/40 hover:bg-slate-800/80 border border-white/[0.05] hover:border-sky-500/30 text-xs text-slate-300 hover:text-white transition-all group"
              >
                <div className="flex items-center justify-between">
                  <span className="line-clamp-1 font-medium">🚢 Which SKUs have delivery delays from Pacific Optics?</span>
                  <ChevronRight className="w-3.5 h-3.5 text-slate-500 group-hover:text-sky-400 group-hover:translate-x-0.5 transition-all shrink-0" />
                </div>
              </Link>
            </div>

            <Link
              href="/chat"
              className="w-full flex items-center justify-center gap-2 py-2.5 rounded-xl bg-sky-500/15 hover:bg-sky-500/25 text-sky-300 border border-sky-500/30 text-xs font-semibold transition-all shadow-sm"
            >
              Open Interactive RAG Studio
              <ArrowRight className="w-3.5 h-3.5" />
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}
