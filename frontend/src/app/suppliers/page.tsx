'use client';

import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { api } from '@/lib/api-client';
import { Supplier, DocumentMetadata } from '@/types/api';
import {
  Building2,
  FileText,
  UploadCloud,
  CheckCircle2,
  Clock,
  Globe2,
  FileCheck2,
  Sparkles,
  Lock,
} from 'lucide-react';
import Link from 'next/link';
import { useAuth } from '@/lib/auth-context';

export default function SuppliersPage() {
  const queryClient = useQueryClient();
  const { user } = useAuth();
  const isViewer = user?.role?.toLowerCase() === 'viewer';

  const [selectedSupplier, setSelectedSupplier] = useState<string>('');
  const [docTitle, setDocTitle] = useState<string>('');
  const [docType, setDocType] = useState<string>('contract');
  const [file, setFile] = useState<File | null>(null);
  const [uploadSuccess, setUploadSuccess] = useState<boolean>(false);

  const { data: suppliers, isLoading: isSuppliersLoading } = useQuery<Supplier[]>({
    queryKey: ['suppliers'],
    queryFn: () => api.getSuppliers(),
  });

  const { data: documents, isLoading: isDocsLoading } = useQuery<DocumentMetadata[]>({
    queryKey: ['documents'],
    queryFn: () => api.getDocuments(),
  });

  const uploadMutation = useMutation({
    mutationFn: async () => {
      if (!file || !docTitle) throw new Error('File and Title are required');
      const formData = new FormData();
      formData.append('file', file);
      formData.append('title', docTitle);
      formData.append('doc_type', docType);
      if (selectedSupplier) formData.append('supplier_id', selectedSupplier);

      return api.uploadDocument(formData);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['documents'] });
      setFile(null);
      setDocTitle('');
      setUploadSuccess(true);
      setTimeout(() => setUploadSuccess(false), 4000);
    },
  });

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="inline-flex items-center gap-1.5 text-xs font-semibold text-sky-400 mb-1">
            <Building2 className="w-3.5 h-3.5" />
            Vendor Ecosystem & Contract Ingestion
          </div>
          <h1 className="text-2xl font-extrabold text-white tracking-tight">
            Supplier Scorecards & Document Intelligence
          </h1>
          <p className="text-xs sm:text-sm text-slate-400">
            Monitor vendor reliability indices, operational lead times, and ingest unstructured PDF contracts into Qdrant.
          </p>
        </div>
      </div>

      {/* Supplier Grid */}
      <div className="space-y-3">
        <h2 className="text-base font-bold text-white flex items-center gap-2">
          <Globe2 className="w-4 h-4 text-sky-400" />
          Active Strategic Suppliers ({suppliers?.length || 0})
        </h2>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
          {isSuppliersLoading ? (
            <div className="col-span-3 p-12 text-center text-xs text-slate-400">Loading supplier scorecards...</div>
          ) : (
            suppliers?.map((s) => {
              const reliabilityPct = Math.round(s.reliability_score * 100);
              const qualityPct = Math.round(s.quality_score * 100);

              return (
                <div
                  key={s.id}
                  className="p-5 rounded-3xl border border-white/[0.08] bg-slate-900/40 backdrop-blur-xl shadow-card-subtle flex flex-col justify-between space-y-4 hover:border-sky-500/30 transition-all duration-200 group"
                >
                  <div className="space-y-3">
                    <div className="flex items-start justify-between gap-2">
                      <div>
                        <span className="text-[10px] font-bold text-sky-400 uppercase tracking-wider">{s.code}</span>
                        <h3 className="text-base font-bold text-white group-hover:text-sky-300 transition-colors">
                          {s.name}
                        </h3>
                        <p className="text-xs text-slate-400 flex items-center gap-1 mt-0.5">
                          <Globe2 className="w-3 h-3 text-slate-500" />
                          {s.country} • Payment: {s.payment_terms}
                        </p>
                      </div>

                      <span
                        className={`px-2 py-0.5 rounded-full text-[10px] font-semibold uppercase tracking-wider border ${
                          s.status === 'active'
                            ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20'
                            : 'bg-amber-500/10 text-amber-400 border-amber-500/20'
                        }`}
                      >
                        {s.status}
                      </span>
                    </div>

                    {/* Progress bars for reliability & quality */}
                    <div className="space-y-2 pt-2 border-t border-white/[0.05]">
                      <div className="space-y-1">
                        <div className="flex justify-between text-xs">
                          <span className="text-slate-400">On-Time Reliability:</span>
                          <span className="font-bold text-emerald-400">{reliabilityPct}%</span>
                        </div>
                        <div className="w-full h-1.5 rounded-full bg-slate-800 overflow-hidden">
                          <div className="h-full rounded-full bg-emerald-500" style={{ width: `${reliabilityPct}%` }} />
                        </div>
                      </div>

                      <div className="space-y-1">
                        <div className="flex justify-between text-xs">
                          <span className="text-slate-400">Quality Score:</span>
                          <span className="font-bold text-sky-400">{qualityPct}%</span>
                        </div>
                        <div className="w-full h-1.5 rounded-full bg-slate-800 overflow-hidden">
                          <div className="h-full rounded-full bg-sky-500" style={{ width: `${qualityPct}%` }} />
                        </div>
                      </div>
                    </div>

                    <div className="flex items-center justify-between text-xs text-slate-400 pt-1">
                      <span className="flex items-center gap-1">
                        <Clock className="w-3.5 h-3.5 text-slate-500" />
                        Avg Lead Time: <strong className="text-white">{s.base_lead_time_days} days</strong>
                      </span>
                    </div>
                  </div>

                  <Link
                    href={`/chat?q=What+are+the+SLA+terms+and+penalties+for+${encodeURIComponent(s.name)}%3F`}
                    className="w-full flex items-center justify-center gap-1.5 py-2 rounded-xl bg-slate-800/80 hover:bg-sky-600/20 text-slate-300 hover:text-sky-300 text-xs font-semibold border border-white/[0.06] hover:border-sky-500/30 transition-all"
                  >
                    <Sparkles className="w-3.5 h-3.5 text-sky-400" />
                    Query Documents via RAG
                  </Link>
                </div>
              );
            })
          )}
        </div>
      </div>

      {/* Two Columns: PDF Uploader & Indexed Documents List */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 pt-2">
        {/* Upload Form Card */}
        <div className="p-6 rounded-3xl border border-white/[0.08] bg-slate-900/40 backdrop-blur-xl shadow-card-subtle space-y-4">
          <div>
            <h2 className="text-base font-bold text-white flex items-center gap-2">
              <UploadCloud className="w-4 h-4 text-sky-400" />
              Upload Supplier Contract / SLA
            </h2>
            <p className="text-xs text-slate-400">Parses text, chunks semantically, and embeds to Qdrant</p>
          </div>

          {uploadSuccess && (
            <div className="p-3 rounded-xl bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 text-xs flex items-center gap-2">
              <CheckCircle2 className="w-4 h-4 shrink-0" />
              Document ingested and indexed into vector store!
            </div>
          )}

          <div className="space-y-3">
            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1">Document Title</label>
              <input
                type="text"
                placeholder="e.g. Master Supply Agreement 2026"
                value={docTitle}
                onChange={(e) => setDocTitle(e.target.value)}
                className="w-full px-3.5 py-2 rounded-xl bg-slate-800/60 border border-white/[0.08] text-xs text-white placeholder-slate-500 focus:outline-none focus:border-sky-500"
              />
            </div>

            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1">Supplier Association</label>
              <select
                value={selectedSupplier}
                onChange={(e) => setSelectedSupplier(e.target.value)}
                className="w-full px-3.5 py-2 rounded-xl bg-slate-800/60 border border-white/[0.08] text-xs text-white focus:outline-none focus:border-sky-500"
              >
                <option value="">General (All Suppliers)</option>
                {suppliers?.map((s) => (
                  <option key={s.id} value={s.id}>
                    {s.name} ({s.code})
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1">Document Category</label>
              <select
                value={docType}
                onChange={(e) => setDocType(e.target.value)}
                className="w-full px-3.5 py-2 rounded-xl bg-slate-800/60 border border-white/[0.08] text-xs text-white focus:outline-none focus:border-sky-500"
              >
                <option value="contract">Master Contract</option>
                <option value="sla">SLA & Delivery Schedule</option>
                <option value="risk_notice">Risk / Force Majeure Notice</option>
                <option value="compliance">Compliance & Quality Spec</option>
              </select>
            </div>

            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1">Select PDF Document</label>
              <input
                type="file"
                accept=".pdf,.txt,.md"
                onChange={(e) => setFile(e.target.files?.[0] || null)}
                className="w-full text-xs text-slate-400 file:mr-3 file:py-2 file:px-3 file:rounded-xl file:border-0 file:text-xs file:font-semibold file:bg-sky-500/20 file:text-sky-300 hover:file:bg-sky-500/30 file:cursor-pointer"
              />
            </div>

            {isViewer ? (
              <div className="w-full mt-2 p-3 rounded-xl bg-indigo-500/10 border border-indigo-500/20 text-indigo-300 text-xs flex items-center justify-center gap-2">
                <Lock className="w-4 h-4 text-indigo-400" />
                <span>Document ingestion restricted to Analyst / Admin</span>
              </div>
            ) : (
              <button
                onClick={() => uploadMutation.mutate()}
                disabled={!file || !docTitle || uploadMutation.isPending}
                className="w-full mt-2 flex items-center justify-center gap-2 py-2.5 rounded-xl bg-gradient-to-r from-cyan-500 via-sky-500 to-indigo-600 hover:from-cyan-400 hover:to-indigo-500 text-white text-xs font-semibold shadow-glow-cyan disabled:opacity-50 transition-all"
              >
                <UploadCloud className="w-4 h-4" />
                {uploadMutation.isPending ? 'Ingesting to Vector Database...' : 'Ingest Document into RAG'}
              </button>
            )}
          </div>
        </div>

        {/* Indexed Documents Table (2 Cols) */}
        <div className="lg:col-span-2 space-y-4">
          <div>
            <h2 className="text-base font-bold text-white flex items-center gap-2">
              <FileCheck2 className="w-4 h-4 text-sky-400" />
              Indexed Vector Knowledge Base ({documents?.length || 0})
            </h2>
            <p className="text-xs text-slate-400">Active PDF documents partitioned into 384-d semantic vectors</p>
          </div>

          <div className="rounded-3xl border border-white/[0.08] bg-slate-900/40 backdrop-blur-xl shadow-card-subtle overflow-hidden">
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs text-slate-300">
                <thead className="text-[11px] uppercase tracking-wider bg-slate-950/60 text-slate-400 border-b border-white/[0.06]">
                  <tr>
                    <th className="px-6 py-4 font-bold">Document Title</th>
                    <th className="px-6 py-4 font-bold">Supplier</th>
                    <th className="px-6 py-4 font-bold">Doc Type</th>
                    <th className="px-6 py-4 font-bold">Vector Chunks</th>
                    <th className="px-6 py-4 font-bold text-right">Query</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-white/[0.05]">
                  {isDocsLoading ? (
                    <tr>
                      <td colSpan={5} className="px-6 py-8 text-center text-slate-400">
                        Loading indexed knowledge base...
                      </td>
                    </tr>
                  ) : documents?.length === 0 ? (
                    <tr>
                      <td colSpan={5} className="px-6 py-8 text-center text-slate-400">
                        No documents indexed yet.
                      </td>
                    </tr>
                  ) : (
                    documents?.map((doc) => (
                      <tr key={doc.id} className="hover:bg-white/[0.02] transition-colors">
                        <td className="px-6 py-4">
                          <div className="font-bold text-white flex items-center gap-1.5">
                            <FileText className="w-3.5 h-3.5 text-sky-400 shrink-0" />
                            {doc.title}
                          </div>
                          <div className="text-[11px] text-slate-400">{doc.filename}</div>
                        </td>

                        <td className="px-6 py-4 text-slate-300">
                          {doc.supplier_name || 'General Document'}
                        </td>

                        <td className="px-6 py-4">
                          <span className="px-2 py-0.5 rounded-md bg-slate-800 text-sky-300 text-[10px] font-semibold uppercase border border-white/[0.05]">
                            {doc.doc_type}
                          </span>
                        </td>

                        <td className="px-6 py-4 text-slate-300 font-mono">
                          {doc.chunk_count} chunks
                        </td>

                        <td className="px-6 py-4 text-right">
                          <Link
                            href={`/chat?q=What+are+the+key+terms+in+${encodeURIComponent(doc.title)}%3F`}
                            className="inline-flex items-center gap-1 px-3 py-1.5 rounded-xl bg-sky-500/10 hover:bg-sky-500/20 text-sky-300 border border-sky-500/20 text-xs font-semibold transition-all"
                          >
                            <Sparkles className="w-3 h-3" />
                            Ask
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
      </div>
    </div>
  );
}
