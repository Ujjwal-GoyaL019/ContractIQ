import type { Metadata } from 'next';
import { Plus_Jakarta_Sans } from 'next/font/google';
import './globals.css';
import Providers from '@/components/Providers';
import { Navbar } from '@/components/Navbar';

const font = Plus_Jakarta_Sans({
  subsets: ['latin'],
  weight: ['400', '500', '600', '700', '800'],
  variable: '--font-sans',
});

export const metadata: Metadata = {
  title: 'ContractIQ • Smart Supplier & Risk Advisor',
  description: 'AI-driven supplier contract RAG intelligence combined with dual time-series demand forecasting.',
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="dark">
      <body className={`${font.className} bg-[#070a12] text-slate-100 antialiased min-h-screen flex flex-col relative selection:bg-sky-500 selection:text-white`}>
        {/* Ambient background lighting glow */}
        <div className="fixed inset-0 pointer-events-none z-0 overflow-hidden">
          <div className="absolute -top-40 left-1/2 -translate-x-1/2 w-[850px] h-[450px] bg-gradient-to-b from-sky-500/12 via-indigo-600/6 to-transparent rounded-full blur-3xl opacity-75" />
          <div className="absolute top-1/3 -left-40 w-[450px] h-[450px] bg-sky-600/8 rounded-full blur-3xl opacity-50" />
          <div className="absolute top-2/3 -right-40 w-[450px] h-[450px] bg-indigo-600/8 rounded-full blur-3xl opacity-50" />
        </div>

        <Providers>
          <div className="relative z-10 flex flex-col min-h-screen">
            <Navbar />
            <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8">{children}</main>
            <footer className="border-t border-white/[0.06] py-6 text-center text-xs text-slate-500">
              <p>ContractIQ • Smart Supplier & Risk Advisor • Prophet & LightGBM • FastEmbed & Qdrant RAG</p>
            </footer>
          </div>
        </Providers>
      </body>
    </html>
  );
}
