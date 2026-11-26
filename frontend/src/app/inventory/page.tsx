'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { api } from '@/lib/api-client';
import { InventoryItem } from '@/types/api';
import { RiskBadge } from '@/components/RiskBadge';
import { useAuth } from '@/lib/auth-context';
import {
  Search,
  LineChart,
  ShieldAlert,
  Package,
  ArrowUpRight,
  Sliders,
  X,
  CheckCircle2,
  AlertCircle,
  Loader2,
  Lock,
} from 'lucide-react';

export default function InventoryPage() {
  const queryClient = useQueryClient();
  const { user } = useAuth();
  const isViewer = user?.role?.toLowerCase() === 'viewer';

  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState('ALL');

  // Modal State
  const [selectedItem, setSelectedItem] = useState<InventoryItem | null>(null);
  const [editCurrentStock, setEditCurrentStock] = useState<number>(0);
  const [editIncomingStock, setEditIncomingStock] = useState<number>(0);
  const [editReorderPoint, setEditReorderPoint] = useState<number>(0);
  const [editReorderQty, setEditReorderQty] = useState<number>(0);
  const [feedback, setFeedback] = useState<{ type: 'success' | 'error'; message: string } | null>(null);

  const { data: inventory, isLoading } = useQuery<InventoryItem[]>({
    queryKey: ['inventory'],
    queryFn: () => api.getInventory(),
  });

  const updateMutation = useMutation({
    mutationFn: async () => {
      if (!selectedItem || !selectedItem.product) throw new Error('No SKU selected');
      return api.updateInventory(selectedItem.product.sku, {
        current_stock: editCurrentStock,
        incoming_stock: editIncomingStock,
        reorder_point: editReorderPoint,
        reorder_quantity: editReorderQty,
      });
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['inventory'] });
      queryClient.invalidateQueries({ queryKey: ['riskSummary'] });
      setFeedback({ type: 'success', message: 'Inventory levels updated successfully!' });
      setTimeout(() => {
        setFeedback(null);
        setSelectedItem(null);
      }, 1500);
    },
    onError: (err: any) => {
      const msg = err.response?.data?.detail || 'Failed to update inventory. Make sure you have Analyst or Admin permissions.';
      setFeedback({ type: 'error', message: msg });
    },
  });

  const handleOpenAdjustModal = (item: InventoryItem) => {
    setSelectedItem(item);
    setEditCurrentStock(item.current_stock);
    setEditIncomingStock(item.incoming_stock);
    setEditReorderPoint(item.reorder_point);
    setEditReorderQty(item.reorder_quantity);
    setFeedback(null);
  };

  const filteredItems = (inventory || []).filter((item) => {
    const p = item.product;
    const matchesSearch =
      !search ||
      (p?.sku.toLowerCase().includes(search.toLowerCase()) ||
        p?.name.toLowerCase().includes(search.toLowerCase()) ||
        p?.category.toLowerCase().includes(search.toLowerCase()));

    const matchesStatus =
      statusFilter === 'ALL' ||
      (statusFilter === 'CRITICAL' && item.urgency_status === 'CRITICAL') ||
      (statusFilter === 'HIGH' && item.urgency_status === 'HIGH') ||
      (statusFilter === 'HEALTHY' && item.urgency_status === 'HEALTHY');

    return matchesSearch && matchesStatus;
  });

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="inline-flex items-center gap-1.5 text-xs font-semibold text-sky-400 mb-1">
            <Package className="w-3.5 h-3.5" />
            Stock Ledger &amp; Warehouse Controls
          </div>
          <h1 className="text-2xl font-extrabold text-white tracking-tight">
            Inventory Management
          </h1>
          <p className="text-xs sm:text-sm text-slate-400">
            Real-time warehouse on-hand balances, buffer health, and replenishment runway.
          </p>
        </div>

        {isViewer && (
          <div className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-indigo-500/10 border border-indigo-500/20 text-indigo-300 text-xs">
            <Lock className="w-3.5 h-3.5 text-indigo-400" />
            <span>Viewer Mode: Read-Only Telemetry</span>
          </div>
        )}
      </div>

      {/* Filter & Search Bar */}
      <div className="flex flex-col sm:flex-row items-center justify-between gap-4 p-3.5 rounded-2xl bg-slate-900/40 border border-white/[0.07] backdrop-blur-md">
        <div className="relative w-full sm:w-80">
          <Search className="absolute left-3 top-2.5 w-4 h-4 text-slate-400" />
          <input
            type="text"
            placeholder="Search SKU, item name, or category..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full pl-9 pr-4 py-2 rounded-xl bg-slate-800/50 border border-white/[0.08] text-xs text-white placeholder-slate-400 focus:outline-none focus:border-sky-500/60 transition-colors"
          />
        </div>

        <div className="flex items-center gap-1.5 w-full sm:w-auto overflow-x-auto pb-1 sm:pb-0">
          <span className="text-xs text-slate-400 font-medium mr-1 hidden sm:inline">Status:</span>
          {['ALL', 'CRITICAL', 'HIGH', 'HEALTHY'].map((st) => (
            <button
              key={st}
              onClick={() => setStatusFilter(st)}
              className={`px-3 py-1.5 rounded-xl text-xs font-semibold transition-all duration-150 shrink-0 ${
                statusFilter === st
                  ? 'bg-sky-500 text-white shadow-glow-cyan'
                  : 'bg-slate-800/40 text-slate-400 hover:text-slate-200 hover:bg-slate-800/80'
              }`}
            >
              {st}
            </button>
          ))}
        </div>
      </div>

      {/* Inventory Table */}
      <div className="rounded-2xl border border-white/[0.07] bg-slate-900/40 backdrop-blur-md overflow-hidden shadow-card-subtle">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs text-slate-300">
            <thead className="text-[11px] uppercase tracking-wider bg-slate-950/60 text-slate-400 border-b border-white/[0.06]">
              <tr>
                <th className="px-6 py-4 font-bold">SKU &amp; Product</th>
                <th className="px-6 py-4 font-bold">Category</th>
                <th className="px-6 py-4 font-bold">On-Hand</th>
                <th className="px-6 py-4 font-bold">In-Transit</th>
                <th className="px-6 py-4 font-bold">Safety Buffer</th>
                <th className="px-6 py-4 font-bold">Days of Supply</th>
                <th className="px-6 py-4 font-bold">Status</th>
                <th className="px-6 py-4 font-bold text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-white/[0.05]">
              {isLoading ? (
                <tr>
                  <td colSpan={8} className="px-6 py-12 text-center text-slate-400">
                    Loading inventory telemetry...
                  </td>
                </tr>
              ) : filteredItems.length === 0 ? (
                <tr>
                  <td colSpan={8} className="px-6 py-12 text-center text-slate-400">
                    No SKUs matched your search filter.
                  </td>
                </tr>
              ) : (
                filteredItems.map((item) => {
                  const p = item.product;
                  const days = item.days_of_supply;
                  const barWidth = Math.min(100, Math.max(8, (days / 45) * 100));

                  return (
                    <tr key={item.id} className="hover:bg-white/[0.02] transition-colors group">
                      <td className="px-6 py-4">
                        <Link
                          href={`/forecast/${p?.sku}`}
                          className="font-bold text-sm text-white hover:text-sky-400 transition-colors flex items-center gap-1"
                        >
                          {p?.sku}
                          <ArrowUpRight className="w-3 h-3 text-slate-500 group-hover:text-sky-400 transition-colors" />
                        </Link>
                        <div className="text-xs text-slate-400 line-clamp-1">{p?.name}</div>
                      </td>

                      <td className="px-6 py-4 text-slate-300">
                        <span className="px-2 py-0.5 rounded-md bg-slate-800/80 text-slate-300 text-[11px] border border-white/[0.05]">
                          {p?.category}
                        </span>
                      </td>

                      <td className="px-6 py-4 font-bold text-white text-sm">
                        {item.current_stock.toLocaleString()}
                        <span className="text-[10px] text-slate-400 font-normal pl-1">units</span>
                      </td>

                      <td className="px-6 py-4 text-sky-300 font-semibold">
                        +{item.incoming_stock.toLocaleString()}
                      </td>

                      <td className="px-6 py-4 text-slate-400">{p?.min_safety_stock.toLocaleString()}</td>

                      <td className="px-6 py-4 min-w-[140px]">
                        <div className="space-y-1">
                          <div className="flex items-center justify-between text-xs font-semibold">
                            <span
                              className={
                                days < 10
                                  ? 'text-rose-400'
                                  : days < 20
                                  ? 'text-amber-400'
                                  : 'text-emerald-400'
                              }
                            >
                              {days} days
                            </span>
                          </div>
                          {/* Mini Progress Bar */}
                          <div className="w-full h-1.5 rounded-full bg-slate-800 overflow-hidden">
                            <div
                              className={`h-full rounded-full ${
                                days < 10
                                  ? 'bg-rose-500'
                                  : days < 20
                                  ? 'bg-amber-500'
                                  : 'bg-emerald-500'
                              }`}
                              style={{ width: `${barWidth}%` }}
                            />
                          </div>
                        </div>
                      </td>

                      <td className="px-6 py-4">
                        <RiskBadge severity={item.urgency_status} />
                      </td>

                      <td className="px-6 py-4 text-right">
                        <div className="flex items-center justify-end gap-1.5">
                          {!isViewer && (
                            <button
                              onClick={() => handleOpenAdjustModal(item)}
                              className="p-1.5 rounded-lg bg-brand-cyan/10 hover:bg-brand-cyan/20 text-brand-cyan border border-brand-cyan/20 transition-colors"
                              title="Adjust Stock & Runway"
                            >
                              <Sliders className="w-4 h-4" />
                            </button>
                          )}
                          <Link
                            href={`/forecast/${p?.sku}`}
                            className="p-1.5 rounded-lg bg-sky-500/10 hover:bg-sky-500/20 text-sky-300 border border-sky-500/20 transition-colors"
                            title="Forecast Demand"
                          >
                            <LineChart className="w-4 h-4" />
                          </Link>
                          <Link
                            href="/risk"
                            className="p-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 transition-colors border border-white/[0.06]"
                            title="Risk Analysis"
                          >
                            <ShieldAlert className="w-4 h-4" />
                          </Link>
                        </div>
                      </td>
                    </tr>
                  );
                })
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Stock Adjustment Modal */}
      {selectedItem && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm animate-fadeIn">
          <div className="w-full max-w-lg rounded-3xl border border-white/[0.12] bg-slate-900/95 p-6 shadow-2xl space-y-5">
            {/* Modal Header */}
            <div className="flex items-center justify-between border-b border-white/[0.08] pb-4">
              <div>
                <div className="inline-flex items-center gap-1.5 text-xs font-semibold text-brand-cyan">
                  <Sliders className="w-3.5 h-3.5" />
                  Inventory Level Calibration
                </div>
                <h3 className="text-lg font-bold text-white mt-0.5">
                  {selectedItem.product?.name} ({selectedItem.product?.sku})
                </h3>
              </div>
              <button
                onClick={() => setSelectedItem(null)}
                className="p-1.5 rounded-xl text-slate-400 hover:text-white hover:bg-slate-800 transition-colors"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* Alert Feedback */}
            {feedback && (
              <div
                className={`flex items-start gap-2.5 p-3 rounded-xl text-xs ${
                  feedback.type === 'success'
                    ? 'bg-emerald-500/10 border border-emerald-500/30 text-emerald-300'
                    : 'bg-rose-500/10 border border-rose-500/30 text-rose-300'
                }`}
              >
                {feedback.type === 'success' ? (
                  <CheckCircle2 className="w-4 h-4 shrink-0 text-emerald-400 mt-0.5" />
                ) : (
                  <AlertCircle className="w-4 h-4 shrink-0 text-rose-400 mt-0.5" />
                )}
                <span>{feedback.message}</span>
              </div>
            )}

            {/* Form Fields */}
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">
                  On-Hand Current Stock
                </label>
                <input
                  type="number"
                  min={0}
                  value={editCurrentStock}
                  onChange={(e) => setEditCurrentStock(Math.max(0, parseInt(e.target.value) || 0))}
                  className="w-full px-3.5 py-2.5 rounded-xl bg-slate-950/60 border border-slate-700 text-sm text-white focus:outline-none focus:border-brand-cyan"
                />
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">
                  In-Transit Incoming Stock
                </label>
                <input
                  type="number"
                  min={0}
                  value={editIncomingStock}
                  onChange={(e) => setEditIncomingStock(Math.max(0, parseInt(e.target.value) || 0))}
                  className="w-full px-3.5 py-2.5 rounded-xl bg-slate-950/60 border border-slate-700 text-sm text-white focus:outline-none focus:border-brand-cyan"
                />
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">
                  Reorder Trigger Point
                </label>
                <input
                  type="number"
                  min={0}
                  value={editReorderPoint}
                  onChange={(e) => setEditReorderPoint(Math.max(0, parseInt(e.target.value) || 0))}
                  className="w-full px-3.5 py-2.5 rounded-xl bg-slate-950/60 border border-slate-700 text-sm text-white focus:outline-none focus:border-brand-cyan"
                />
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">
                  Batch Reorder Quantity
                </label>
                <input
                  type="number"
                  min={1}
                  value={editReorderQty}
                  onChange={(e) => setEditReorderQty(Math.max(1, parseInt(e.target.value) || 1))}
                  className="w-full px-3.5 py-2.5 rounded-xl bg-slate-950/60 border border-slate-700 text-sm text-white focus:outline-none focus:border-brand-cyan"
                />
              </div>
            </div>

            {/* Quick Preview Pill */}
            <div className="p-3.5 rounded-2xl bg-slate-950/60 border border-white/[0.06] flex items-center justify-between text-xs">
              <span className="text-slate-400">Total Available Pipeline:</span>
              <span className="font-bold text-white">
                {(editCurrentStock + editIncomingStock - selectedItem.allocated_stock).toLocaleString()} units
              </span>
            </div>

            {/* Actions */}
            <div className="flex items-center justify-end gap-3 pt-2">
              <button
                type="button"
                onClick={() => setSelectedItem(null)}
                className="px-4 py-2 rounded-xl text-xs font-medium text-slate-400 hover:text-white bg-slate-800/60 hover:bg-slate-800 transition-colors"
              >
                Cancel
              </button>
              <button
                type="button"
                disabled={updateMutation.isPending}
                onClick={() => updateMutation.mutate()}
                className="flex items-center gap-2 px-5 py-2 rounded-xl bg-gradient-to-r from-brand-cyan to-brand-sky hover:from-cyan-400 hover:to-sky-400 text-slate-950 font-bold text-xs shadow-glow-cyan transition-all disabled:opacity-50"
              >
                {updateMutation.isPending ? (
                  <>
                    <Loader2 className="w-3.5 h-3.5 animate-spin" />
                    <span>Saving...</span>
                  </>
                ) : (
                  <span>Commit Inventory Update</span>
                )}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
