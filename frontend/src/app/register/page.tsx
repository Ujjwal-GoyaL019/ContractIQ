'use client';

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { UserPlus, Lock, Mail, User, Shield, ArrowRight, AlertCircle, Loader2, CheckCircle2 } from 'lucide-react';
import { useAuth } from '@/lib/auth-context';

export default function RegisterPage() {
  const router = useRouter();
  const { register } = useAuth();

  const [fullName, setFullName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [role, setRole] = useState<'admin' | 'procurement_analyst' | 'viewer'>('procurement_analyst');
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!email || !password || !fullName) {
      setError('Please fill in all required fields.');
      return;
    }
    if (password.length < 6) {
      setError('Password must be at least 6 characters long.');
      return;
    }

    try {
      setLoading(true);
      setError(null);
      await register({
        email,
        password,
        full_name: fullName,
        role,
      });
      router.push('/');
    } catch (err: any) {
      const msg = err.response?.data?.detail || 'Registration failed. Please try again.';
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
            <UserPlus className="h-9 w-9 text-brand-cyan" />
          </div>
          <h2 className="text-3xl font-extrabold tracking-tight text-white">
            Create an Account
          </h2>
          <p className="mt-2 text-sm text-slate-400">
            Join <span className="text-brand-cyan font-semibold">ContractIQ</span> intelligent supply operations
          </p>
        </div>

        {/* Register Form */}
        <div className="glass-panel p-8 rounded-2xl border border-slate-800 shadow-2xl bg-slate-900/80">
          <form onSubmit={handleSubmit} className="space-y-4">
            {error && (
              <div className="flex items-start gap-2.5 p-3 rounded-lg bg-rose-500/10 border border-rose-500/30 text-rose-300 text-xs animate-shake">
                <AlertCircle className="w-4 h-4 shrink-0 mt-0.5 text-rose-400" />
                <span>{error}</span>
              </div>
            )}

            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1.5">
                Full Name
              </label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-slate-500">
                  <User className="h-4 w-4" />
                </div>
                <input
                  type="text"
                  required
                  value={fullName}
                  onChange={(e) => setFullName(e.target.value)}
                  placeholder="e.g. Alex Morgan"
                  className="block w-full pl-10 pr-3 py-2.5 text-sm bg-slate-950/60 border border-slate-700/80 rounded-xl text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-brand-cyan focus:border-transparent transition-all"
                />
              </div>
            </div>

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
                  placeholder="alex.morgan@contractiq.ai"
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
                  minLength={6}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="Minimum 6 characters"
                  className="block w-full pl-10 pr-3 py-2.5 text-sm bg-slate-950/60 border border-slate-700/80 rounded-xl text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-brand-cyan focus:border-transparent transition-all"
                />
              </div>
            </div>

            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1.5">
                Account Role
              </label>
              <div className="grid grid-cols-3 gap-2">
                <button
                  type="button"
                  onClick={() => setRole('procurement_analyst')}
                  className={`p-2.5 rounded-xl border text-center transition-all ${
                    role === 'procurement_analyst'
                      ? 'bg-brand-sky/20 border-brand-sky text-brand-sky font-semibold'
                      : 'bg-slate-950/40 border-slate-800 text-slate-400 hover:border-slate-700'
                  }`}
                >
                  <div className="text-xs">Analyst</div>
                  <div className="text-[10px] opacity-75 mt-0.5">Operations</div>
                </button>

                <button
                  type="button"
                  onClick={() => setRole('admin')}
                  className={`p-2.5 rounded-xl border text-center transition-all ${
                    role === 'admin'
                      ? 'bg-brand-cyan/20 border-brand-cyan text-brand-cyan font-semibold'
                      : 'bg-slate-950/40 border-slate-800 text-slate-400 hover:border-slate-700'
                  }`}
                >
                  <div className="text-xs">Admin</div>
                  <div className="text-[10px] opacity-75 mt-0.5">Full Access</div>
                </button>

                <button
                  type="button"
                  onClick={() => setRole('viewer')}
                  className={`p-2.5 rounded-xl border text-center transition-all ${
                    role === 'viewer'
                      ? 'bg-brand-indigo/20 border-brand-indigo text-brand-indigo font-semibold'
                      : 'bg-slate-950/40 border-slate-800 text-slate-400 hover:border-slate-700'
                  }`}
                >
                  <div className="text-xs">Viewer</div>
                  <div className="text-[10px] opacity-75 mt-0.5">Read-Only</div>
                </button>
              </div>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full flex items-center justify-center gap-2 py-2.5 px-4 rounded-xl font-medium text-sm text-slate-950 bg-gradient-to-r from-brand-cyan to-brand-sky hover:from-cyan-400 hover:to-sky-400 shadow-glow-cyan transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed font-semibold mt-4"
            >
              {loading ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin text-slate-950" />
                  <span>Creating Account...</span>
                </>
              ) : (
                <>
                  <span>Complete Registration</span>
                  <ArrowRight className="w-4 h-4" />
                </>
              )}
            </button>
          </form>

          <div className="mt-6 pt-5 border-t border-slate-800 text-center">
            <p className="text-xs text-slate-400">
              Already have an account?{' '}
              <Link href="/login" className="font-semibold text-brand-cyan hover:text-cyan-300 transition-colors">
                Sign in here
              </Link>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
