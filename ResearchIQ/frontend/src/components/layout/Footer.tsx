import React from 'react';
import Link from 'next/link';
import { BookOpen, ShieldCheck, Database, Award } from 'lucide-react';

export default function Footer() {
  return (
    <footer className="bg-slate-900 text-slate-400 py-12 border-t border-slate-800">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8 mb-8">
          {/* Brand */}
          <div className="space-y-4 md:col-span-1">
            <div className="flex items-center space-x-2">
              <div className="w-8 h-8 rounded-lg bg-accent-600 text-white flex items-center justify-center font-bold">
                <BookOpen className="w-4 h-4 text-white" />
              </div>
              <span className="text-xl font-bold tracking-tight text-white">
                Research<span className="text-accent-400">IQ</span>
              </span>
            </div>
            <p className="text-xs leading-relaxed text-slate-400">
              AI-powered research paper analysis, quality assessment, and publication readiness platform grounded in verified scholarly data.
            </p>
          </div>

          {/* Core Modules */}
          <div>
            <h4 className="text-xs font-semibold uppercase tracking-wider text-slate-200 mb-3">
              Analytical Modules
            </h4>
            <ul className="space-y-2 text-xs">
              <li>Automated Technical Review</li>
              <li>Novelty & Semantic Similarity</li>
              <li>Citation Cross-Checking</li>
              <li>Grammar & Academic Tone</li>
              <li>Plagiarism Risk Detection</li>
            </ul>
          </div>

          {/* Publication Readiness */}
          <div>
            <h4 className="text-xs font-semibold uppercase tracking-wider text-slate-200 mb-3">
              Decision Intelligence
            </h4>
            <ul className="space-y-2 text-xs">
              <li>Figure & Table Validation</li>
              <li>AI Peer Reviewer Comments</li>
              <li>Journal Recommendations (OpenAlex)</li>
              <li>Patentability Screening</li>
              <li>Publication Readiness Score</li>
            </ul>
          </div>

          {/* Scholarly Integrity */}
          <div>
            <h4 className="text-xs font-semibold uppercase tracking-wider text-slate-200 mb-3">
              Scholarly Standards
            </h4>
            <div className="space-y-2 text-xs text-slate-400">
              <div className="flex items-center space-x-2">
                <Database className="w-4 h-4 text-accent-400" />
                <span>OpenAlex & Crossref Metadata</span>
              </div>
              <div className="flex items-center space-x-2">
                <ShieldCheck className="w-4 h-4 text-emerald-400" />
                <span>Zero Metric Fabrication</span>
              </div>
              <div className="flex items-center space-x-2">
                <Award className="w-4 h-4 text-amber-400" />
                <span>Explainable AI Evaluation</span>
              </div>
            </div>
          </div>
        </div>

        <div className="pt-8 border-t border-slate-800 text-xs text-center text-slate-500 flex flex-col sm:flex-row justify-between items-center space-y-4 sm:space-y-0">
          <p>© {new Date().getFullYear()} ResearchIQ. Built for students, research scholars, and academic faculty.</p>
          <div className="flex space-x-6 text-slate-400">
            <Link href="/" className="hover:text-white transition-colors">Platform Overview</Link>
            <Link href="/upload" className="hover:text-white transition-colors">Submit Manuscript</Link>
            <Link href="/dashboard" className="hover:text-white transition-colors">Author Dashboard</Link>
          </div>
        </div>
      </div>
    </footer>
  );
}
