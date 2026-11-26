'use client';

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { ShieldCheck, Lock, Mail, ArrowRight, Sparkles, CheckCircle2, AlertCircle, Loader2 } from 'lucide-react';
import { useAuth } from '@/lib/auth-context';

export default function LoginPage() {
  const router = useRouter();
  const { login } = useAuth();

  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!email || !password) {
      setError('Please enter both email and password.');
      return;
    }

    try {
      setLoading(true);
      setError(null);
      await login(email, password);
      router.push('/');
    } catch (err: any) {
      const msg = err.response?.data?.detail || 'Authentication failed. Please check your credentials.';
      setError(msg);
    } finally {
      setLoading(false);
    }
  };

  const handleDemoLogin = async (demoEmail: string, demoPass: string) => {
    setEmail(demoEmail);
    setPassword(demoPass);
    setError(null);
    setLoading(true);
    try {
      await login(demoEmail, demoPass);
      router.push('/');
    } catch (err: any) {
      const msg = err.response?.data?.detail || 'Demo login failed. Make sure backend is running.';
      setError(msg);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-[calc(100vh-5rem)] flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8 relative">
      {/* Background glow ambient effects */}
      <div className="absolute top-1/4 left-1/2 -translate-x-1/2 -translate-y-1/2 w-96 h-96 bg-brand-cyan/10 rounded-full blur-3xl pointer-events-none" />
      <div className="absolute bottom-1/4 left-1/3 -translate-x-1/2 w-80 h-80 bg-brand-indigo/10 rounded-full blur-3xl pointer-events-none" />

      <div className="w-full max-w-md space-y-8 relative z-10">
        {/* Header Branding */}
        <div className="text-center">
          <div className="inline-flex items-center justify-center p-3 rounded-2xl bg-gradient-to-tr from-brand-cyan/20 to-brand-sky/10 border border-brand-cyan/30 shadow-glow-cyan mb-4">
            <ShieldCheck className="h-9 w-9 text-brand-cyan" />
          </div>
          <h2 className="text-3xl font-extrabold tracking-tight text-white">
            Welcome to <span className="bg-gradient-to-r from-brand-cyan via-brand-sky to-brand-indigo bg-clip-text text-transparent">ContractIQ</span>
          </h2>
          <p className="mt-2 text-sm text-slate-400">
            Smart Supplier &amp; Risk Advisor platform
          </p>
        </div>

        {/* 1-Click Demo Login Panel */}
        <div className="glass-panel p-4 rounded-xl border border-brand-cyan/20 bg-slate-900/60 shadow-lg">
          <div className="flex items-center gap-2 mb-3">
            <Sparkles className="w-4 h-4 text-brand-cyan animate-pulse" />
            <span className="text-xs font-semibold uppercase tracking-wider text-brand-cyan">1-Click Demo Logins</span>
          </div>
          <div className="grid grid-cols-3 gap-2">
            <button
              type="button"
              disabled={loading}
              onClick={() => handleDemoLogin('admin@contractiq.ai', 'Admin@12345')}
              className="px-2.5 py-2 rounded-lg bg-slate-800/80 hover:bg-slate-800 border border-brand-cyan/30 hover:border-brand-cyan text-left transition-all duration-200 group"
            >
              <div className="text-xs font-semibold text-white group-hover:text-brand-cyan flex items-center justify-between">
                <span>Admin</span>
                <span className="text-[10px] px-1.5 py-0.5 rounded bg-brand-cyan/10 text-brand-cyan border border-brand-cyan/20">Full</span>
              </div>
              <div className="text-[10px] text-slate-400 truncate mt-0.5">admin@contractiq.ai</div>
            </button>

            <button
              type="button"
              disabled={loading}
              onClick={() => handleDemoLogin('analyst@contractiq.ai', 'Analyst@12345')}
              className="px-2.5 py-2 rounded-lg bg-slate-800/80 hover:bg-slate-800 border border-brand-sky/30 hover:border-brand-sky text-left transition-all duration-200 group"
            >
              <div className="text-xs font-semibold text-white group-hover:text-brand-sky flex items-center justify-between">
                <span>Analyst</span>
                <span className="text-[10px] px-1.5 py-0.5 rounded bg-brand-sky/10 text-brand-sky border border-brand-sky/20">Ops</span>
              </div>
              <div className="text-[10px] text-slate-400 truncate mt-0.5">analyst@contractiq.ai</div>
            </button>

            <button
              type="button"
              disabled={loading}
              onClick={() => handleDemoLogin('demo@contractiq.ai', 'Demo@12345')}
              className="px-2.5 py-2 rounded-lg bg-slate-800/80 hover:bg-slate-800 border border-brand-indigo/30 hover:border-brand-indigo text-left transition-all duration-200 group"
            >
              <div className="text-xs font-semibold text-white group-hover:text-brand-indigo flex items-center justify-between">
                <span>Viewer</span>
                <span className="text-[10px] px-1.5 py-0.5 rounded bg-brand-indigo/10 text-brand-indigo border border-brand-indigo/20">Read</span>
              </div>
              <div className="text-[10px] text-slate-400 truncate mt-0.5">demo@contractiq.ai</div>
            </button>
          </div>
        </div>

        {/* Login Form */}
        <div className="glass-panel p-8 rounded-2xl border border-slate-800 shadow-2xl bg-slate-900/80">
          <form onSubmit={handleSubmit} className="space-y-5">
            {error && (
              <div className="flex items-start gap-2.5 p-3 rounded-lg bg-rose-500/10 border border-rose-500/30 text-rose-300 text-xs animate-shake">
                <AlertCircle className="w-4 h-4 shrink-0 mt-0.5 text-rose-400" />
                <span>{error}</span>
              </div>
            )}

            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1.5">
                Work Email Address
              </label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-slate-500">
                  <Mail className="h-4 w-4" />
                </div>
                <input
                  type="email"
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="analyst@contractiq.ai"
                  className="block w-full pl-10 pr-3 py-2.5 text-sm bg-slate-950/60 border border-slate-700/80 rounded-xl text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-brand-cyan focus:border-transparent transition-all"
                />
              </div>
            </div>

            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1.5">
                Password
              </label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-slate-500">
                  <Lock className="h-4 w-4" />
                </div>
                <input
                  type="password"
                  required
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="••••••••••••"
                  className="block w-full pl-10 pr-3 py-2.5 text-sm bg-slate-950/60 border border-slate-700/80 rounded-xl text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-brand-cyan focus:border-transparent transition-all"
                />
              </div>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full flex items-center justify-center gap-2 py-2.5 px-4 rounded-xl font-medium text-sm text-slate-950 bg-gradient-to-r from-brand-cyan to-brand-sky hover:from-cyan-400 hover:to-sky-400 shadow-glow-cyan transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed font-semibold mt-2"
            >
              {loading ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin text-slate-950" />
                  <span>Authenticating...</span>
                </>
              ) : (
                <>
                  <span>Sign In</span>
                  <ArrowRight className="w-4 h-4" />
                </>
              )}
            </button>
          </form>

          <div className="mt-6 pt-5 border-t border-slate-800 text-center">
            <p className="text-xs text-slate-400">
              New team member?{' '}
              <Link href="/register" className="font-semibold text-brand-cyan hover:text-cyan-300 transition-colors">
                Create an account
              </Link>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
