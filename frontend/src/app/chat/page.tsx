'use client';

import React, { useState, useEffect, useRef, Suspense } from 'react';
import { useSearchParams } from 'next/navigation';
import {
  Send,
  Bot,
  User,
  FileText,
  AlertTriangle,
  RefreshCw,
  Zap,
  ShieldCheck,
} from 'lucide-react';

interface GroundingInfo {
  is_grounded: boolean;
  abstained: boolean;
  faithfulness_score: number;
  verified_claims_count: number;
  unsupported_claims?: string[];
  abstention_reason?: string | null;
}

interface Citation {
  doc_title: string;
  supplier_name?: string;
  page_number?: number;
  quote?: string;
  score?: number;
  dense_score?: number;
  bm25_score?: number;
  rrf_score?: number;
  retrieval_method?: string;
}

interface Message {
  role: 'user' | 'assistant';
  content: string;
  citations?: Citation[];
  grounding?: GroundingInfo;
  risk_flags?: string[];
  suggested_actions?: string[];
  isStreaming?: boolean;
}

const STARTER_PROMPTS = [
  'Which suppliers have force majeure or lead-time risk notices?',
  'What are the contractual surcharges for expedited MCU orders?',
  'Which SKUs are impacted by Pacific Optics delivery delays?',
  'Compare delivery lead times and payment terms across suppliers.',
];

function ChatContent() {
  const searchParams = useSearchParams();
  const initialQuery = searchParams.get('q') || '';

  const [messages, setMessages] = useState<Message[]>([
    {
      role: 'assistant',
      content:
        'Hello! I am your **ContractIQ Intelligence Advisor**. Ask me anything about supplier contracts, SLA terms, lead-time amendments, or impending stockout risks.',
    },
  ]);
  const [input, setInput] = useState(initialQuery);
  const [retrievalMode, setRetrievalMode] = useState<'hybrid' | 'dense' | 'bm25'>('hybrid');
  const [isStreaming, setIsStreaming] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isStreaming]);

  // Handle auto-send if URL has query param 'q'
  useEffect(() => {
    if (initialQuery && messages.length === 1) {
      sendMessage(initialQuery);
    }
  }, [initialQuery]);

  const sendMessage = async (textToSend?: string) => {
    const query = textToSend || input;
    if (!query.trim() || isStreaming) return;

    const userMessage: Message = { role: 'user', content: query };
    const tempAssistantMessage: Message = {
      role: 'assistant',
      content: '',
      isStreaming: true,
    };

    setMessages((prev) => [...prev, userMessage, tempAssistantMessage]);
    setInput('');
    setIsStreaming(true);

    try {
      const apiBase = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000/api/v1';
      const token = typeof window !== 'undefined' ? localStorage.getItem('contractiq_token') : null;

      const headers: Record<string, string> = {
        'Content-Type': 'application/json',
      };
      if (token) {
        headers['Authorization'] = `Bearer ${token}`;
      }

      // Stream SSE from backend
      const response = await fetch(`${apiBase}/chat`, {
        method: 'POST',
        headers,
        body: JSON.stringify({
          query: query,
          question: query,
          retrieval_mode: retrievalMode,
          stream: true,
        }),
      });

      if (!response.body) throw new Error('No readable stream received.');

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let accumulatedContent = '';
      let citations: Citation[] = [];
      let grounding: GroundingInfo | undefined = undefined;
      let risk_flags: string[] = [];

      while (true) {
        const { value, done } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value);
        const lines = chunk.split('\n');

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const dataStr = line.replace('data: ', '').trim();
            if (dataStr === '[DONE]' || !dataStr) continue;

            try {
              const parsed = JSON.parse(dataStr);
              if (parsed.event === 'token' && typeof parsed.data === 'string') {
                accumulatedContent += parsed.data;
              } else if (parsed.event === 'citations' && Array.isArray(parsed.data)) {
                citations = parsed.data.map((c: any) => ({
                  doc_title: c.document_title || c.doc_title || 'Document',
                  supplier_name: c.supplier_name,
                  page_number: c.page_number || 1,
                  quote: c.snippet || c.quote,
                  score: c.score,
                  dense_score: c.dense_score,
                  bm25_score: c.bm25_score,
                  rrf_score: c.rrf_score,
                  retrieval_method: c.retrieval_method,
                }));
              } else if (parsed.event === 'grounding' && parsed.data) {
                grounding = parsed.data;
              } else if (parsed.token) {
                accumulatedContent += parsed.token;
              } else if (parsed.citations) {
                citations = parsed.citations;
              } else if (parsed.risk_flags) {
                risk_flags = parsed.risk_flags;
              }

              setMessages((prev) => {
                const updated = [...prev];
                const last = updated[updated.length - 1];
                if (last.role === 'assistant') {
                  last.content = accumulatedContent;
                  if (citations.length > 0) last.citations = citations;
                  if (grounding) last.grounding = grounding;
                }
                return updated;
              });
            } catch {
              accumulatedContent += dataStr;
              setMessages((prev) => {
                const updated = [...prev];
                const last = updated[updated.length - 1];
                if (last.role === 'assistant') {
                  last.content = accumulatedContent;
                }
                return updated;
              });
            }
          }
        }
      }

      // Finalize message with citations
      setMessages((prev) => {
        const updated = [...prev];
        const last = updated[updated.length - 1];
        if (last.role === 'assistant') {
          last.content = accumulatedContent || 'No grounded information found in supplier documents.';
          last.citations = citations;
          last.grounding = grounding;
          last.risk_flags = risk_flags;
          last.isStreaming = false;
        }
        return updated;
      });
    } catch (err: any) {
      console.error('Streaming error:', err);
      setMessages((prev) => {
        const updated = [...prev];
        const last = updated[updated.length - 1];
        if (last.role === 'assistant') {
          last.content =
            'Sorry, an error occurred communicating with the RAG inference service. Please check your backend connection.';
          last.isStreaming = false;
        }
        return updated;
      });
    } finally {
      setIsStreaming(false);
    }
  };

  return (
    <div className="flex flex-col h-[calc(100vh-10rem)] max-w-5xl mx-auto">
      {/* Header */}
      <div className="flex items-center justify-between pb-4 mb-4 border-b border-white/[0.06]">
        <div>
          <div className="inline-flex items-center gap-1.5 text-xs font-semibold text-sky-400 mb-0.5">
            <Zap className="w-3.5 h-3.5" />
            Groq Llama 3.3 70B • Hybrid Search (BGE Dense + Okapi BM25 + RRF Reranker)
          </div>
          <h1 className="text-xl sm:text-2xl font-extrabold text-white tracking-tight flex items-center gap-2">
            ContractIQ RAG Studio
          </h1>
        </div>

        <div className="flex items-center gap-2">
          <select
            value={retrievalMode}
            onChange={(e) => setRetrievalMode(e.target.value as 'hybrid' | 'dense' | 'bm25')}
            aria-label="Retrieval Mode"
            className="px-2.5 py-1.5 rounded-xl bg-slate-900 border border-sky-500/30 text-sky-300 text-xs font-semibold focus:outline-none"
          >
            <option value="hybrid">Hybrid RRF + Rerank</option>
            <option value="dense">Dense Vector Only</option>
            <option value="bm25">BM25 Sparse Only</option>
          </select>

          <button
            onClick={() =>
              setMessages([
                {
                  role: 'assistant',
                  content:
                    'Chat session reset. Ask me about supplier contracts, lead times, or stockout mitigation plans.',
                },
              ])
            }
            className="px-3 py-1.5 rounded-xl bg-slate-800/80 hover:bg-slate-700 text-slate-300 text-xs font-semibold border border-white/[0.06] transition-all flex items-center gap-1.5"
          >
            <RefreshCw className="w-3 h-3" />
            Reset Chat
          </button>
        </div>
      </div>

      {/* Messages Scroll Area */}
      <div className="flex-1 overflow-y-auto space-y-4 pr-2">
        {messages.map((msg, idx) => (
          <div
            key={idx}
            className={`flex items-start gap-3 ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            {msg.role === 'assistant' && (
              <div className="w-8 h-8 rounded-xl bg-gradient-to-tr from-cyan-500 via-sky-500 to-indigo-600 flex items-center justify-center shrink-0 shadow-md shadow-sky-500/20 mt-1">
                <Bot className="w-4 h-4 text-white" />
              </div>
            )}

            <div
              className={`max-w-2xl rounded-2xl p-4 text-xs sm:text-sm leading-relaxed ${
                msg.role === 'user'
                  ? 'bg-gradient-to-r from-cyan-500 via-sky-500 to-indigo-600 text-white shadow-glow-cyan ml-8'
                  : 'bg-slate-900/60 border border-white/[0.08] text-slate-200 backdrop-blur-md mr-8'
              }`}
            >
              <div className="whitespace-pre-wrap">{msg.content}</div>

              {msg.isStreaming && (
                <span className="inline-block w-1.5 h-4 ml-1 bg-sky-400 animate-pulse align-middle" />
              )}

              {/* Anti-Hallucination Grounding Verification Badge */}
              {msg.role === 'assistant' && msg.grounding && !msg.isStreaming && (
                <div
                  className={`mt-3 inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg text-[11px] font-semibold border ${
                    msg.grounding.abstained
                      ? 'bg-amber-500/15 border-amber-500/30 text-amber-300'
                      : msg.grounding.is_grounded
                      ? 'bg-emerald-500/15 border-emerald-500/30 text-emerald-300'
                      : 'bg-rose-500/15 border-rose-500/30 text-rose-300'
                  }`}
                >
                  <ShieldCheck className="w-3.5 h-3.5 shrink-0" />
                  {msg.grounding.abstained
                    ? 'Abstained — Clause Not Specified (Zero Hallucination Guard)'
                    : `${Math.round(msg.grounding.faithfulness_score * 100)}% Verified Grounded • ${msg.grounding.verified_claims_count} numeric/entity claim(s) audited`}
                </div>
              )}

              {/* Citations Card Section */}
              {msg.citations && msg.citations.length > 0 && (
                <div className="mt-4 pt-3 border-t border-white/[0.08] space-y-2">
                  <div className="flex items-center gap-1.5 text-[11px] font-bold text-sky-300 uppercase tracking-wider">
                    <FileText className="w-3 h-3" />
                    Verified Document Citations ({msg.citations.length})
                  </div>
                  <div className="grid grid-cols-1 gap-2">
                    {msg.citations.map((c, cIdx) => (
                      <div
                        key={cIdx}
                        className="p-2.5 rounded-xl bg-slate-800/60 border border-white/[0.06] text-xs space-y-1"
                      >
                        <div className="flex items-center justify-between gap-2">
                          <span className="font-bold text-white line-clamp-1">{c.doc_title}</span>
                          <div className="flex items-center gap-1.5 shrink-0">
                            {typeof c.score === 'number' && (
                              <span className="px-1.5 py-0.5 rounded bg-emerald-500/15 text-emerald-300 text-[10px] font-mono">
                                score {c.score.toFixed(2)}
                              </span>
                            )}
                            {typeof c.bm25_score === 'number' && c.bm25_score > 0 && (
                              <span className="px-1.5 py-0.5 rounded bg-indigo-500/15 text-indigo-300 text-[10px] font-mono">
                                BM25 {c.bm25_score.toFixed(1)}
                              </span>
                            )}
                            {c.page_number && (
                              <span className="px-1.5 py-0.5 rounded bg-sky-500/20 text-sky-300 text-[10px] font-mono">
                                p.{c.page_number}
                              </span>
                            )}
                          </div>
                        </div>
                        {c.quote && (
                          <p className="text-slate-400 italic text-[11px] line-clamp-2">
                            &ldquo;{c.quote}&rdquo;
                          </p>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Risk Flags Warning Badge */}
              {msg.risk_flags && msg.risk_flags.length > 0 && (
                <div className="mt-3 flex items-center gap-1.5 p-2 rounded-xl bg-rose-500/10 border border-rose-500/20 text-rose-300 text-xs">
                  <AlertTriangle className="w-3.5 h-3.5 shrink-0" />
                  <span>Risk Flags Identified: {msg.risk_flags.join(', ')}</span>
                </div>
              )}
            </div>

            {msg.role === 'user' && (
              <div className="w-8 h-8 rounded-xl bg-slate-800 border border-white/10 flex items-center justify-center shrink-0 mt-1">
                <User className="w-4 h-4 text-slate-300" />
              </div>
            )}
          </div>
        ))}
        <div ref={messagesEndRef} />
      </div>

      {/* Suggested Starter Chips */}
      {messages.length <= 2 && (
        <div className="pt-3 pb-2 flex items-center gap-2 overflow-x-auto">
          <span className="text-[11px] text-slate-500 font-semibold uppercase tracking-wider shrink-0">Try:</span>
          {STARTER_PROMPTS.map((prompt, pIdx) => (
            <button
              key={pIdx}
              onClick={() => sendMessage(prompt)}
              className="px-3 py-1 rounded-xl bg-slate-900/60 hover:bg-slate-800/80 text-slate-300 hover:text-white text-xs border border-white/[0.06] hover:border-sky-500/30 transition-all shrink-0"
            >
              {prompt}
            </button>
          ))}
        </div>
      )}

      {/* Input Form Bar */}
      <form
        onSubmit={(e) => {
          e.preventDefault();
          sendMessage();
        }}
        className="mt-3 relative flex items-center"
      >
        <input
          type="text"
          placeholder="Ask about contract clauses, surcharges, lead-time changes, or supplier risks..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
          disabled={isStreaming}
          className="w-full pl-4 pr-12 py-3.5 rounded-2xl bg-slate-900/80 border border-white/[0.08] focus:border-sky-500 text-xs sm:text-sm text-white placeholder-slate-500 shadow-card-subtle backdrop-blur-md focus:outline-none transition-all"
        />
        <button
          type="submit"
          disabled={!input.trim() || isStreaming}
          className="absolute right-2 p-2.5 rounded-xl bg-gradient-to-r from-cyan-500 via-sky-500 to-indigo-600 hover:from-cyan-400 hover:to-indigo-500 text-white disabled:opacity-40 transition-all shadow-glow-cyan"
        >
          <Send className="w-4 h-4" />
        </button>
      </form>
    </div>
  );
}

export default function ChatPage() {
  return (
    <Suspense
      fallback={
        <div className="flex items-center justify-center h-80 text-slate-400 text-xs">
          Loading ContractIQ RAG Studio...
        </div>
      }
    >
      <ChatContent />
    </Suspense>
  );
}
