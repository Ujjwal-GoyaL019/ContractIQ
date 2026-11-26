'use client';

import React from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import {
  LayoutDashboard,
  Boxes,
  TrendingUp,
  ShieldAlert,
  Building2,
  Scale,
  Sparkles,
  FileSearch,
  LogOut,
  LogIn,
  User as UserIcon,
} from 'lucide-react';
import { useAuth } from '@/lib/auth-context';

const NAV_ITEMS = [
  { label: 'Overview', href: '/', icon: LayoutDashboard },
  { label: 'Inventory', href: '/inventory', icon: Boxes },
  { label: 'Forecasting', href: '/forecast/SKU-MCU-32B', icon: TrendingUp },
  { label: 'Risk Advisory', href: '/risk', icon: ShieldAlert },
  { label: 'Optimizer', href: '/optimize', icon: Scale },
  { label: 'Suppliers', href: '/suppliers', icon: Building2 },
];

export const Navbar: React.FC = () => {
  const pathname = usePathname();
  const { user, logout } = useAuth();
  const isChatActive = pathname.startsWith('/chat');

  const getRoleBadge = (role: string) => {
    switch (role.toLowerCase()) {
      case 'admin':
        return <span className="text-[10px] uppercase font-bold tracking-wider px-1.5 py-0.5 rounded bg-brand-cyan/20 text-brand-cyan border border-brand-cyan/40">Admin</span>;
      case 'procurement_analyst':
        return <span className="text-[10px] uppercase font-bold tracking-wider px-1.5 py-0.5 rounded bg-brand-sky/20 text-brand-sky border border-brand-sky/40">Analyst</span>;
      default:
        return <span className="text-[10px] uppercase font-bold tracking-wider px-1.5 py-0.5 rounded bg-brand-indigo/20 text-brand-indigo border border-brand-indigo/40">Viewer</span>;
    }
  };

  return (
    <header className="sticky top-0 z-50 border-b border-white/[0.06] bg-[#070a12]/80 backdrop-blur-xl">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Brand Logo */}
          <Link href="/" className="flex items-center gap-3 group">
            <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-cyan-500 via-sky-500 to-indigo-600 flex items-center justify-center shadow-lg shadow-sky-500/20 group-hover:scale-105 transition-transform duration-200">
              <FileSearch className="w-5 h-5 text-white fill-white/15" />
            </div>
            <div>
              <span className="text-base font-bold text-white tracking-tight flex items-center gap-1.5">
                Contract<span className="text-transparent bg-clip-text bg-gradient-to-r from-sky-400 to-indigo-400">IQ</span>
              </span>
              <p className="text-[10px] text-slate-400 font-medium leading-none">Supplier & Risk Advisor</p>
            </div>
          </Link>

          {/* Navigation Links */}
          <nav className="hidden md:flex items-center gap-1 bg-slate-900/60 p-1 rounded-xl border border-white/[0.05] backdrop-blur-md">
            {NAV_ITEMS.map((item) => {
              const Icon = item.icon;
              const isActive =
                item.href === '/'
                  ? pathname === '/'
                  : pathname.startsWith(item.href) ||
                    (item.href.startsWith('/forecast') && pathname.startsWith('/forecast'));

              return (
                <Link
                  key={item.href}
                  href={item.href}
                  className={`flex items-center gap-2 px-3.5 py-1.5 rounded-lg text-xs font-semibold transition-all duration-150 ${
                    isActive
                      ? 'bg-sky-500/15 text-sky-300 border border-sky-500/30 shadow-sm'
                      : 'text-slate-400 hover:text-slate-200 hover:bg-white/[0.04]'
                  }`}
                >
                  <Icon className={`w-3.5 h-3.5 ${isActive ? 'text-sky-400' : 'text-slate-400'}`} />
                  {item.label}
                </Link>
              );
            })}
          </nav>

          {/* Right Action: AI Assistant & User Auth Controls */}
          <div className="flex items-center gap-2.5">
            <Link
              href="/chat"
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-semibold transition-all duration-200 ${
                isChatActive
                  ? 'bg-gradient-to-r from-cyan-500 via-sky-500 to-indigo-600 text-white shadow-glow-cyan'
                  : 'bg-sky-500/10 hover:bg-sky-500/20 text-sky-300 border border-sky-500/30 hover:border-sky-500/50'
              }`}
            >
              <Sparkles className="w-3.5 h-3.5 text-sky-400" />
              <span className="hidden sm:inline">Contract RAG AI</span>
              <span className="sm:hidden">RAG</span>
            </Link>

            {user ? (
              <div className="flex items-center gap-2 pl-1 border-l border-slate-800">
                <div className="flex items-center gap-2 px-2.5 py-1 rounded-xl bg-slate-900/80 border border-slate-800">
                  <div className="w-6 h-6 rounded-lg bg-gradient-to-tr from-brand-cyan/20 to-brand-sky/20 border border-brand-cyan/30 flex items-center justify-center text-[11px] font-bold text-brand-cyan">
                    {(user.full_name || user.email)[0].toUpperCase()}
                  </div>
                  <div className="hidden lg:flex flex-col text-left">
                    <span className="text-xs font-medium text-slate-200 leading-none truncate max-w-[100px]">
                      {user.full_name || user.email.split('@')[0]}
                    </span>
                    <div className="mt-0.5">{getRoleBadge(user.role)}</div>
                  </div>
                  <div className="lg:hidden">{getRoleBadge(user.role)}</div>
                </div>

                <button
                  onClick={logout}
                  title="Sign Out"
                  className="p-1.5 rounded-lg text-slate-400 hover:text-rose-400 hover:bg-rose-500/10 border border-transparent hover:border-rose-500/20 transition-all"
                >
                  <LogOut className="w-4 h-4" />
                </button>
              </div>
            ) : (
              <Link
                href="/login"
                className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-semibold text-white bg-slate-800 hover:bg-slate-700 border border-slate-700 hover:border-slate-600 transition-all"
              >
                <LogIn className="w-3.5 h-3.5 text-brand-cyan" />
                <span>Sign In</span>
              </Link>
            )}
          </div>
        </div>
      </div>
    </header>
  );
};
