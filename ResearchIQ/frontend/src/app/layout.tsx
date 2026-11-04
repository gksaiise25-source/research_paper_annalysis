import type { Metadata } from 'next';
import '@/styles/globals.css';
import Navbar from '@/components/layout/Navbar';
import Footer from '@/components/layout/Footer';

export const metadata: Metadata = {
  title: 'ResearchIQ — AI Research Paper Analysis & Publication Readiness',
  description:
    'Comprehensive AI-powered academic paper analysis evaluating technical completeness, novelty, citations, language, plagiarism risk, figures, and publication readiness.',
  keywords: [
    'research paper analysis',
    'peer review AI',
    'publication readiness score',
    'novelty detection',
    'citation check',
    'journal recommendation',
    'academic writing',
  ],
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="min-h-screen flex flex-col bg-slate-50 text-slate-900">
        <Navbar />
        <main className="flex-1">{children}</main>
        <Footer />
      </body>
    </html>
  );
}
