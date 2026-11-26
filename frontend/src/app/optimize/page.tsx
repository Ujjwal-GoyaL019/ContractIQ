'use client';

import React, { useState, useEffect } from 'react';
import {
  Scale,
  Cpu,
  CheckCircle2,
  AlertTriangle,
  TrendingDown,
  Clock,
  ShieldCheck,
  RefreshCw,
  BarChart3,
  Layers,
  Sparkles,
} from 'lucide-react';
import { api } from '@/lib/api-client';

interface AllocationItem {
  supplier_id: string;
  supplier_code: string;
  supplier_name: string;
  country: string;
  allocated_units: number;
  allocation_share_pct: number;
  base_unit_cost: number;
  surcharge_pct: number;
  effective_unit_cost: number;
  direct_procurement_cost: number;
  risk_adjusted_cost: number;
  lead_time_days: number;
  reliability_score: number;
  disruption_risk_score: number;
  moq: number;
}

interface OptimizationResult {
  sku: string;
  product_name?: string;
  category?: string;
  requested_quantity: number;
  total_allocated_quantity: number;
  solver_engine: string;
  solver_status: string;
  solve_time_ms: number;
  parameters: {
    risk_aversion_lambda: number;
    max_single_supplier_share_pct: number;
    target_lead_time_days: number;
  };
  summary: {
    total_direct_cost: number;
    total_risk_adjusted_cost: number;
    naive_single_source_supplier: string;
    naive_direct_cost: number;
    naive_risk_adjusted_cost: number;
    expected_risk_cost_savings: number;
    disruption_risk_reduction_pct: number;
    weighted_lead_time_days: number;
    weighted_reliability_pct: number;
    weighted_disruption_risk: number;
    active_suppliers_count: number;
  };
  allocations: AllocationItem[];
  solver_notes: string[];
}

const SKU_OPTIONS = [
  { sku: 'SKU-LENS-4K', label: 'SKU-LENS-4K — 4K Optical Lens Array (High Maritime Risk)' },
  { sku: 'SKU-MCU-32B', label: 'SKU-MCU-32B — 32-Bit Cortex-M4 MCU (Dual-Source)' },
  { sku: 'SKU-BLE-SOC', label: 'SKU-BLE-SOC — BLE 5.3 SoC Module' },
  { sku: 'SKU-ENC-IP67', label: 'SKU-ENC-IP67 — IP67 Ruggedized Enclosure' },
];

export default function OptimizeAndBenchmarksPage() {
  const [activeTab, setActiveTab] = useState<'optimizer' | 'benchmarks'>('optimizer');

  // Optimizer Form State
  const [selectedSku, setSelectedSku] = useState('SKU-LENS-4K');
  const [quantity, setQuantity] = useState(600);
  const [riskLambda, setRiskLambda] = useState(1.5);
  const [maxShare, setMaxShare] = useState(0.7);
  const [targetLead, setTargetLead] = useState(18);
  const [optLoading, setOptLoading] = useState(false);
  const [optError, setOptError] = useState<string | null>(null);
  const [optResult, setOptResult] = useState<OptimizationResult | null>(null);

  // Benchmarks State
  const [benchLoading, setBenchLoading] = useState(false);
  const [benchError, setBenchError] = useState<string | null>(null);
  const [benchData, setBenchData] = useState<any>(null);

  const runOptimization = async () => {
    setOptLoading(true);
    setOptError(null);
    try {
      const res = await api.optimizeAllocation({
        sku: selectedSku,
        required_quantity: quantity,
        risk_aversion_lambda: riskLambda,
        max_single_supplier_share: maxShare,
        target_lead_time_days: targetLead,
      });
      setOptResult(res);
    } catch (err: any) {
      setOptError(err?.response?.data?.detail || err?.message || 'Failed to solve MILP optimization.');
    } finally {
      setOptLoading(false);
    }
  };

  const runBenchmarks = async (forceRefresh = false) => {
    setBenchLoading(true);
    setBenchError(null);
    try {
      const res = await api.getAIBenchmarks({
        include_forecasting: true,
        test_days: 14,
        force_refresh: forceRefresh,
      });
      setBenchData(res);
    } catch (err: any) {
      setBenchError(err?.response?.data?.detail || err?.message || 'Failed to run AI evaluation benchmarks.');
    } finally {
      setBenchLoading(false);
    }
  };

  useEffect(() => {
    runOptimization();
  }, []);

  useEffect(() => {
    if (activeTab === 'benchmarks' && !benchData && !benchLoading) {
      runBenchmarks(false);
    }
  }, [activeTab]);

  return (
    <div className="max-w-7xl mx-auto space-y-6">
      {/* Page Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-white/[0.06] pb-5">
        <div>
          <div className="inline-flex items-center gap-1.5 text-xs font-semibold text-cyan-400 mb-1">
            <Cpu className="w-3.5 h-3.5" />
            Prescriptive Operations Research & Empirical AI Evaluation
          </div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight">
            MILP Sourcing Optimizer & AI Benchmarks
          </h1>
          <p className="text-xs sm:text-sm text-slate-400 mt-1">
            Solve multi-supplier split-order allocations with SciPy HiGHS MILP and inspect live Hybrid RAG + Forecasting backtest proofs.
          </p>
        </div>

        {/* Mode Switcher */}
        <div className="flex items-center gap-1.5 bg-slate-900/70 p-1 rounded-xl border border-white/[0.06] self-start">
          <button
            onClick={() => setActiveTab('optimizer')}
            className={`flex items-center gap-2 px-4 py-2 rounded-lg text-xs font-semibold transition-all ${
              activeTab === 'optimizer'
                ? 'bg-gradient-to-r from-cyan-500 to-indigo-600 text-white shadow-md'
                : 'text-slate-400 hover:text-white'
            }`}
          >
            <Scale className="w-3.5 h-3.5" />
            MILP Order Optimizer
          </button>
          <button
            onClick={() => setActiveTab('benchmarks')}
            className={`flex items-center gap-2 px-4 py-2 rounded-lg text-xs font-semibold transition-all ${
              activeTab === 'benchmarks'
                ? 'bg-gradient-to-r from-cyan-500 to-indigo-600 text-white shadow-md'
                : 'text-slate-400 hover:text-white'
            }`}
          >
            <BarChart3 className="w-3.5 h-3.5" />
            Empirical AI Benchmarks
          </button>
        </div>
      </div>

      {/* TAB 1: MULTI-SUPPLIER MILP OPTIMIZER */}
      {activeTab === 'optimizer' && (
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
          {/* Controls Panel */}
          <div className="lg:col-span-4 rounded-2xl bg-slate-900/60 border border-white/[0.08] p-5 space-y-5 h-fit">
            <div className="flex items-center justify-between">
              <h2 className="text-sm font-bold text-white uppercase tracking-wider flex items-center gap-2">
                <Layers className="w-4 h-4 text-cyan-400" />
                MILP Constraints
              </h2>
              <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-cyan-500/15 text-cyan-300 border border-cyan-500/30">
                HiGHS Solver
              </span>
            </div>

            <div className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1.5">Target SKU</label>
                <select
                  value={selectedSku}
                  onChange={(e) => setSelectedSku(e.target.value)}
                  className="w-full rounded-xl bg-slate-950 border border-white/10 px-3 py-2.5 text-xs text-white focus:outline-none focus:border-cyan-500"
                >
                  {SKU_OPTIONS.map((o) => (
                    <option key={o.sku} value={o.sku}>
                      {o.label}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <div className="flex justify-between text-xs mb-1">
                  <span className="font-semibold text-slate-300">Replenishment Quantity</span>
                  <span className="font-bold text-cyan-300">{quantity.toLocaleString()} units</span>
                </div>
                <input
                  type="range"
                  min={200}
                  max={2000}
                  step={50}
                  value={quantity}
                  onChange={(e) => setQuantity(Number(e.target.value))}
                  className="w-full accent-cyan-400"
                />
              </div>

              <div>
                <div className="flex justify-between text-xs mb-1">
                  <span className="font-semibold text-slate-300">Risk Aversion (λ)</span>
                  <span className="font-bold text-indigo-300">{riskLambda.toFixed(1)}×</span>
                </div>
                <input
                  type="range"
                  min={0}
                  max={3.5}
                  step={0.1}
                  value={riskLambda}
                  onChange={(e) => setRiskLambda(Number(e.target.value))}
                  className="w-full accent-indigo-400"
                />
                <p className="text-[10px] text-slate-500 mt-1">
                  0.0 = pure unit cost; 1.5 = balanced SLA/risk; 3.0+ = maximum disruption avoidance.
                </p>
              </div>

              <div>
                <div className="flex justify-between text-xs mb-1">
                  <span className="font-semibold text-slate-300">Max Single-Vendor Cap</span>
                  <span className="font-bold text-emerald-300">{Math.round(maxShare * 100)}%</span>
                </div>
                <input
                  type="range"
                  min={0.5}
                  max={1.0}
                  step={0.05}
                  value={maxShare}
                  onChange={(e) => setMaxShare(Number(e.target.value))}
                  className="w-full accent-emerald-400"
                />
              </div>

              <div>
                <div className="flex justify-between text-xs mb-1">
                  <span className="font-semibold text-slate-300">Target Lead Time Window</span>
                  <span className="font-bold text-amber-300">{targetLead} days</span>
                </div>
                <input
                  type="range"
                  min={7}
                  max={35}
                  step={1}
                  value={targetLead}
                  onChange={(e) => setTargetLead(Number(e.target.value))}
                  className="w-full accent-amber-400"
                />
              </div>

              <button
                onClick={runOptimization}
                disabled={optLoading}
                className="w-full py-2.5 rounded-xl bg-gradient-to-r from-cyan-500 via-sky-500 to-indigo-600 text-white text-xs font-bold shadow-lg shadow-cyan-500/20 hover:opacity-95 transition-all disabled:opacity-50 flex items-center justify-center gap-2"
              >
                {optLoading ? (
                  <>
                    <RefreshCw className="w-3.5 h-3.5 animate-spin" />
                    Solving MILP Program...
                  </>
                ) : (
                  <>
                    <Sparkles className="w-3.5 h-3.5" />
                    Solve Optimal Split Allocation
                  </>
                )}
              </button>
            </div>
          </div>

          {/* Results Panel */}
          <div className="lg:col-span-8 space-y-5">
            {optError && (
              <div className="rounded-xl bg-rose-500/10 border border-rose-500/30 p-4 text-xs text-rose-300 flex items-center gap-2">
                <AlertTriangle className="w-4 h-4 shrink-0" />
                {optError}
              </div>
            )}

            {optResult && (
              <>
                {/* KPI Cards */}
                <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                  <div className="rounded-2xl bg-slate-900/60 border border-white/[0.08] p-4">
                    <div className="text-[11px] text-slate-400 flex items-center gap-1.5">
                      <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
                      Solver Status
                    </div>
                    <div className="text-lg font-extrabold text-emerald-400 mt-1">
                      {optResult.solver_status}
                    </div>
                    <div className="text-[10px] text-slate-500 mt-0.5">
                      Solved in {optResult.solve_time_ms} ms
                    </div>
                  </div>

                  <div className="rounded-2xl bg-slate-900/60 border border-white/[0.08] p-4">
                    <div className="text-[11px] text-slate-400 flex items-center gap-1.5">
                      <TrendingDown className="w-3.5 h-3.5 text-cyan-400" />
                      Risk-Cost Savings
                    </div>
                    <div className="text-lg font-extrabold text-cyan-300 mt-1">
                      ${optResult.summary.expected_risk_cost_savings.toLocaleString()}
                    </div>
                    <div className="text-[10px] text-slate-500 mt-0.5">
                      vs. naive single-source
                    </div>
                  </div>

                  <div className="rounded-2xl bg-slate-900/60 border border-white/[0.08] p-4">
                    <div className="text-[11px] text-slate-400 flex items-center gap-1.5">
                      <ShieldCheck className="w-3.5 h-3.5 text-indigo-400" />
                      Risk Reduction
                    </div>
                    <div className="text-lg font-extrabold text-indigo-300 mt-1">
                      -{optResult.summary.disruption_risk_reduction_pct}%
                    </div>
                    <div className="text-[10px] text-slate-500 mt-0.5">
                      Reliability {optResult.summary.weighted_reliability_pct}%
                    </div>
                  </div>

                  <div className="rounded-2xl bg-slate-900/60 border border-white/[0.08] p-4">
                    <div className="text-[11px] text-slate-400 flex items-center gap-1.5">
                      <Clock className="w-3.5 h-3.5 text-amber-400" />
                      Weighted Lead Time
                    </div>
                    <div className="text-lg font-extrabold text-amber-300 mt-1">
                      {optResult.summary.weighted_lead_time_days} days
                    </div>
                    <div className="text-[10px] text-slate-500 mt-0.5">
                      Across {optResult.summary.active_suppliers_count} supplier(s)
                    </div>
                  </div>
                </div>

                {/* Comparison Banner: Naive vs MILP */}
                <div className="rounded-2xl bg-slate-900/60 border border-white/[0.08] p-5">
                  <div className="flex flex-wrap items-center justify-between gap-2 mb-4">
                    <div>
                      <h3 className="text-sm font-bold text-white">
                        Optimal Purchase Order Allocation — {optResult.sku}
                      </h3>
                      <p className="text-xs text-slate-400">
                        {optResult.product_name} • Naive ERP Single-Source ({optResult.summary.naive_single_source_supplier}) Risk Cost:{' '}
                        <span className="text-rose-300 font-semibold">
                          ${optResult.summary.naive_risk_adjusted_cost.toLocaleString()}
                        </span>{' '}
                        → MILP Optimized:{' '}
                        <span className="text-emerald-300 font-semibold">
                          ${optResult.summary.total_risk_adjusted_cost.toLocaleString()}
                        </span>
                      </p>
                    </div>
                  </div>

                  {/* Allocation Bars & Cards */}
                  <div className="space-y-3">
                    {optResult.allocations.map((alloc) => (
                      <div
                        key={alloc.supplier_id}
                        className="rounded-xl bg-slate-950/70 border border-white/[0.06] p-4"
                      >
                        <div className="flex flex-wrap items-center justify-between gap-2 mb-2">
                          <div>
                            <div className="flex items-center gap-2">
                              <span className="text-sm font-bold text-white">{alloc.supplier_name}</span>
                              <span className="text-[10px] font-semibold px-2 py-0.5 rounded bg-slate-800 text-slate-300">
                                {alloc.country}
                              </span>
                              {alloc.surcharge_pct > 0 && (
                                <span className="text-[10px] font-semibold px-2 py-0.5 rounded bg-rose-500/15 text-rose-300 border border-rose-500/30">
                                  +{alloc.surcharge_pct}% Surcharge
                                </span>
                              )}
                            </div>
                          </div>
                          <div className="text-right">
                            <span className="text-sm font-extrabold text-cyan-300">
                              {alloc.allocated_units.toLocaleString()} units
                            </span>
                            <span className="text-xs text-slate-400 ml-2">
                              ({alloc.allocation_share_pct}%)
                            </span>
                          </div>
                        </div>

                        {/* Visual progress bar */}
                        <div className="w-full h-2 rounded-full bg-slate-800 overflow-hidden mb-3">
                          <div
                            className="h-full bg-gradient-to-r from-cyan-400 via-sky-500 to-indigo-500 rounded-full"
                            style={{ width: `${Math.min(100, alloc.allocation_share_pct)}%` }}
                          />
                        </div>

                        <div className="grid grid-cols-2 sm:grid-cols-5 gap-2 text-[11px] text-slate-400">
                          <div>
                            Eff. Unit Cost:{' '}
                            <span className="text-white font-semibold">${alloc.effective_unit_cost}</span>
                          </div>
                          <div>
                            Direct Cost:{' '}
                            <span className="text-white font-semibold">
                              ${alloc.direct_procurement_cost.toLocaleString()}
                            </span>
                          </div>
                          <div>
                            Lead Time:{' '}
                            <span className="text-amber-300 font-semibold">{alloc.lead_time_days}d</span>
                          </div>
                          <div>
                            Reliability:{' '}
                            <span className="text-emerald-300 font-semibold">{alloc.reliability_score}%</span>
                          </div>
                          <div>
                            Disruption:{' '}
                            <span
                              className={`font-semibold ${
                                alloc.disruption_risk_score > 40 ? 'text-rose-400' : 'text-sky-300'
                              }`}
                            >
                              {alloc.disruption_risk_score}/100
                            </span>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>

                  {optResult.solver_notes && optResult.solver_notes.length > 0 && (
                    <div className="mt-4 text-[11px] text-amber-300/90 bg-amber-500/10 border border-amber-500/20 rounded-xl p-3">
                      {optResult.solver_notes.join(' ')}
                    </div>
                  )}
                </div>
              </>
            )}
          </div>
        </div>
      )}

      {/* TAB 2: EMPIRICAL AI BENCHMARKS */}
      {activeTab === 'benchmarks' && (
        <div className="space-y-6">
          <div className="flex items-center justify-between">
            <p className="text-xs text-slate-400">
              Live reproducible ablation benchmarks across the indexed multi-PDF contract corpus and 400-day historical SKU demand series.
            </p>
            <button
              onClick={() => runBenchmarks(true)}
              disabled={benchLoading}
              className="px-3.5 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-xs font-semibold text-white border border-white/10 flex items-center gap-2"
            >
              <RefreshCw className={`w-3.5 h-3.5 ${benchLoading ? 'animate-spin' : ''}`} />
              {benchLoading ? 'Running Benchmarks...' : 'Re-Run Full Evaluation'}
            </button>
          </div>

          {benchError && (
            <div className="rounded-xl bg-rose-500/10 border border-rose-500/30 p-4 text-xs text-rose-300">
              {benchError}
            </div>
          )}

          {benchLoading && !benchData && (
            <div className="rounded-2xl bg-slate-900/60 border border-white/[0.08] p-10 text-center text-sm text-slate-400">
              Running RAG Retrieval Ablation (Dense vs BM25 vs Hybrid RRF) & 14-Day Holdout Forecasting Backtest...
            </div>
          )}

          {benchData && (
            <>
              {/* 1. RAG Retrieval Ablation Table */}
              <div className="rounded-2xl bg-slate-900/60 border border-white/[0.08] p-5 space-y-4">
                <div className="flex flex-wrap items-center justify-between gap-2">
                  <div>
                    <h2 className="text-base font-bold text-white">
                      1. RAG Retrieval Ablation — Dense HNSW vs. BM25 Sparse vs. Hybrid RRF + Reranker
                    </h2>
                    <p className="text-xs text-slate-400">
                      Evaluated on 10 multi-PDF legal queries across {benchData.rag_evaluation.corpus_chunks_indexed} indexed chunks
                    </p>
                  </div>
                  <span className="text-xs font-bold px-3 py-1 rounded-full bg-emerald-500/15 text-emerald-300 border border-emerald-500/30">
                    MRR Gain vs Dense: {benchData.rag_evaluation.hybrid_vs_dense_mrr_gain >= 0 ? '+' : ''}
                    {benchData.rag_evaluation.hybrid_vs_dense_mrr_gain}
                  </span>
                </div>

                <div className="overflow-x-auto">
                  <table className="w-full text-left text-xs">
                    <thead>
                      <tr className="border-b border-white/[0.08] text-slate-400 uppercase text-[10px]">
                        <th className="py-2.5 pr-4">Retrieval Engine</th>
                        <th className="py-2.5 px-4">Hit@1 (%)</th>
                        <th className="py-2.5 px-4">Hit@3 (%)</th>
                        <th className="py-2.5 px-4">MRR</th>
                        <th className="py-2.5 px-4">Precision@3</th>
                        <th className="py-2.5 pl-4">Avg Latency</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-white/[0.05]">
                      {[
                        { key: 'dense', label: 'Dense Vector Only (Qdrant HNSW BGE)', highlight: false },
                        { key: 'bm25', label: 'Sparse Lexical Only (Okapi BM25)', highlight: false },
                        { key: 'hybrid', label: 'Hybrid RRF + Cross-Reranker (Production)', highlight: true },
                      ].map((row) => {
                        const m = benchData.rag_evaluation.modes[row.key];
                        return (
                          <tr
                            key={row.key}
                            className={row.highlight ? 'bg-cyan-500/10 font-semibold' : ''}
                          >
                            <td className="py-3 pr-4 text-white">{row.label}</td>
                            <td className="py-3 px-4 text-emerald-300">{m.hit_at_1_pct}%</td>
                            <td className="py-3 px-4 text-sky-300">{m.hit_at_3_pct}%</td>
                            <td className="py-3 px-4 text-cyan-300">{m.mrr}</td>
                            <td className="py-3 px-4 text-slate-200">{m.precision_at_3}</td>
                            <td className="py-3 pl-4 text-slate-400">{m.avg_latency_ms} ms</td>
                          </tr>
                        );
                      })}
                    </tbody>
                  </table>
                </div>
              </div>

              {/* 2. Adversarial Zero-Hallucination & Faithfulness Audit */}
              {benchData.hallucination_audit && (
                <div className="rounded-2xl bg-slate-900/60 border border-white/[0.08] p-5 space-y-4">
                  <div className="flex flex-wrap items-center justify-between gap-2">
                    <div>
                      <h2 className="text-base font-bold text-white flex items-center gap-2">
                        <ShieldCheck className="w-4 h-4 text-emerald-400" />
                        2. Zero-Hallucination & Adversarial Faithfulness Audit
                      </h2>
                      <p className="text-xs text-slate-400">
                        Audited {benchData.hallucination_audit.total_queries_audited} queries (10 legal QA + 6 adversarial trap prompts) + synthetic LLM fabrication injection
                      </p>
                    </div>
                    <span className="text-xs font-bold px-3 py-1 rounded-full bg-emerald-500/15 text-emerald-300 border border-emerald-500/30">
                      Hallucination Rate: {benchData.hallucination_audit.hallucination_rate_pct}%
                    </span>
                  </div>

                  <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                    <div className="rounded-xl bg-slate-950/70 border border-emerald-500/20 p-3.5">
                      <div className="text-[10px] text-slate-400 uppercase font-bold">Hallucination Rate</div>
                      <div className="text-xl font-extrabold text-emerald-400 mt-1">
                        {benchData.hallucination_audit.hallucination_rate_pct}%
                      </div>
                    </div>
                    <div className="rounded-xl bg-slate-950/70 border border-cyan-500/20 p-3.5">
                      <div className="text-[10px] text-slate-400 uppercase font-bold">Faithfulness Score</div>
                      <div className="text-xl font-extrabold text-cyan-300 mt-1">
                        {benchData.hallucination_audit.avg_faithfulness_score_pct}%
                      </div>
                    </div>
                    <div className="rounded-xl bg-slate-950/70 border border-amber-500/20 p-3.5">
                      <div className="text-[10px] text-slate-400 uppercase font-bold">Trap Abstention Acc.</div>
                      <div className="text-xl font-extrabold text-amber-300 mt-1">
                        {benchData.hallucination_audit.adversarial_abstention_accuracy_pct}%
                      </div>
                    </div>
                    <div className="rounded-xl bg-slate-950/70 border border-indigo-500/20 p-3.5">
                      <div className="text-[10px] text-slate-400 uppercase font-bold">Fabrication Interception</div>
                      <div className="text-xl font-extrabold text-indigo-300 mt-1">
                        {benchData.hallucination_audit.synthetic_fabrication_interception?.passed ? 'PASS' : 'FAIL'}
                      </div>
                    </div>
                  </div>

                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                    {benchData.hallucination_audit.adversarial_traps?.map((t: any, idx: number) => (
                      <div
                        key={idx}
                        className="rounded-xl bg-slate-950/60 border border-white/[0.05] px-3 py-2 flex items-center justify-between gap-2 text-[11px]"
                      >
                        <span className="text-slate-300 truncate">{t.query}</span>
                        <span
                          className={`shrink-0 px-2 py-0.5 rounded font-bold text-[10px] ${
                            t.safely_abstained
                              ? 'bg-emerald-500/15 text-emerald-300 border border-emerald-500/30'
                              : 'bg-rose-500/15 text-rose-300 border border-rose-500/30'
                          }`}
                        >
                          {t.safely_abstained ? 'Abstained ✓' : 'Leaked ✗'}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* 3. Multi-Model AI Forecasting Leaderboard (7 Distinct Models) */}
              {benchData.forecasting_evaluation && (
                <div className="rounded-2xl bg-slate-900/60 border border-white/[0.08] p-5 space-y-4">
                  <div className="flex flex-wrap items-center justify-between gap-2">
                    <div>
                      <h2 className="text-base font-bold text-white">
                        3. Multi-Model AI Forecasting Leaderboard ({benchData.forecasting_evaluation.models_tested} Models × {benchData.forecasting_evaluation.skus_evaluated} SKUs)
                      </h2>
                      <p className="text-xs text-slate-400">
                        14-day out-of-sample holdout comparison ranked by MAPE & RMSE across statistical, linear, tree-ensemble, and stacked models
                      </p>
                    </div>
                    <span className="text-xs font-bold px-3 py-1 rounded-full bg-indigo-500/15 text-indigo-300 border border-indigo-500/30">
                      Best Model: {benchData.forecasting_evaluation.best_model_by_mape}
                    </span>
                  </div>

                  <div className="overflow-x-auto">
                    <table className="w-full text-left text-xs">
                      <thead>
                        <tr className="border-b border-white/[0.08] text-slate-400 uppercase text-[10px]">
                          <th className="py-2.5 pr-4">Rank & AI Model</th>
                          <th className="py-2.5 px-3">MAPE (%)</th>
                          <th className="py-2.5 px-3">RMSE</th>
                          <th className="py-2.5 px-3">MAE</th>
                          <th className="py-2.5 px-3">WAPE (%)</th>
                          <th className="py-2.5 px-3">P90 Cov.</th>
                          <th className="py-2.5 pl-3">Fit Latency</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-white/[0.05]">
                        {benchData.forecasting_evaluation.leaderboard?.map((row: any, idx: number) => (
                          <tr
                            key={row.model_key}
                            className={idx === 0 ? 'bg-emerald-500/10 font-semibold' : ''}
                          >
                            <td className="py-3 pr-4 text-white flex items-center gap-2">
                              <span
                                className={`w-5 h-5 rounded-md flex items-center justify-center text-[10px] font-bold ${
                                  idx === 0
                                    ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/40'
                                    : 'bg-slate-800 text-slate-400'
                                }`}
                              >
                                #{idx + 1}
                              </span>
                              {row.model_name}
                            </td>
                            <td className="py-3 px-3 text-cyan-300 font-bold">{row.avg_mape}%</td>
                            <td className="py-3 px-3 text-slate-200">{row.avg_rmse}</td>
                            <td className="py-3 px-3 text-slate-300">{row.avg_mae}</td>
                            <td className="py-3 px-3 text-slate-300">{row.avg_wape}%</td>
                            <td className="py-3 px-3 text-emerald-300">{row.avg_p90_coverage_pct}%</td>
                            <td className="py-3 pl-3 text-slate-400">{row.avg_latency_ms} ms</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              )}
            </>
          )}
        </div>
      )}
    </div>
  );
}
