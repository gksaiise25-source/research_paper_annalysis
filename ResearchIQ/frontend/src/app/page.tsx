'use client';

import React from 'react';
import Link from 'next/link';
import {
  BookOpen,
  CheckCircle2,
  Sparkles,
  FileSearch,
  Quote,
  Languages,
  CopyCheck,
  Image as ImageIcon,
  MessageSquare,
  Compass,
  Lightbulb,
  Award,
  ArrowRight,
  ShieldCheck,
  Download,
} from 'lucide-react';

export default function LandingPage() {
  const features = [
    {
      icon: <FileSearch className="w-6 h-6 text-accent-600" />,
      title: "1. Automated Technical Review",
      desc: "Evaluates Abstract, Methodology, Results, and Conclusions for completeness, logical cohesion, and experimental depth.",
    },
    {
      icon: <Sparkles className="w-6 h-6 text-amber-500" />,
      title: "2. Novelty Analysis",
      desc: "Queries OpenAlex & Crossref in real-time, computing semantic embeddings to uncover overlapping prior research and gaps.",
    },
    {
      icon: <Quote className="w-6 h-6 text-indigo-500" />,
      title: "3. Citation & Reference Verification",
      desc: "Cross-checks in-text citations against the bibliography for IEEE, APA, and MLA styles, detecting orphaned or duplicate entries.",
    },
    {
      icon: <Languages className="w-6 h-6 text-emerald-500" />,
      title: "4. Academic Writing Quality",
      desc: "Identifies passive voice overuse, wordiness, and informal vocabulary while providing academic rewrite suggestions.",
    },
    {
      icon: <CopyCheck className="w-6 h-6 text-rose-500" />,
      title: "5. Plagiarism Risk Detection",
      desc: "N-gram fingerprinting and TF-IDF cosine similarity analysis against indexed literature to flag similarity risks.",
    },
    {
      icon: <ImageIcon className="w-6 h-6 text-cyan-500" />,
      title: "6. Figure & Table Validation",
      desc: "Detects sequential numbering gaps, missing captions, low-resolution figures (<300 DPI), and unreferenced assets.",
    },
    {
      icon: <MessageSquare className="w-6 h-6 text-violet-500" />,
      title: "7. AI Peer Reviewer Critique",
      desc: "Grounded peer reviewer assessment delivering major/minor revisions, experimental design critique, and manuscript weaknesses.",
    },
    {
      icon: <Compass className="w-6 h-6 text-blue-500" />,
      title: "8. Journal Recommendations",
      desc: "Live OpenAlex scholarly venue matching with verified publishers, ISSNs, and suitability scoring without fabricated rankings.",
    },
    {
      icon: <Lightbulb className="w-6 h-6 text-yellow-500" />,
      title: "9. Patentability Indicator",
      desc: "Preliminary evaluation of industrial applicability, technical enablement, and statutory subject matter eligibility.",
    },
    {
      icon: <Award className="w-6 h-6 text-teal-500" />,
      title: "10. Publication Readiness Score",
      desc: "Transparent weighted readiness score categorizing submissions into Ready, Minor Revision, or Major Revision.",
    },
  ];

  return (
    <div className="flex flex-col min-h-screen">
      {/* Hero Section */}
      <section className="relative overflow-hidden bg-gradient-to-b from-navy-950 via-navy-900 to-slate-900 text-white py-24 sm:py-32">
        <div className="absolute inset-0 bg-[radial-gradient(#38bdf8_1px,transparent_1px)] [background-size:16px_16px] opacity-15"></div>
        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <div className="inline-flex items-center space-x-2 px-3 py-1.5 rounded-full bg-accent-500/10 border border-accent-400/20 text-accent-300 text-xs font-semibold tracking-wide uppercase mb-8">
            <ShieldCheck className="w-4 h-4 text-accent-400" />
            <span>AI-Powered Manuscript Quality Intelligence</span>
          </div>

          <h1 className="text-4xl sm:text-6xl font-extrabold tracking-tight text-white max-w-4xl mx-auto leading-tight">
            Analyze, Enhance, and Validate Your Research Paper Before Submission
          </h1>

          <p className="mt-6 text-lg sm:text-xl text-slate-300 max-w-3xl mx-auto leading-relaxed">
            ResearchIQ provides scholars, professors, and postgraduate researchers with
            rigorous multi-module technical review, novelty assessment, citation verification, and publication readiness scoring.
          </p>

          <div className="mt-10 flex flex-col sm:flex-row items-center justify-center gap-4">
            <Link
              href="/upload"
              className="w-full sm:w-auto inline-flex items-center justify-center space-x-2 px-8 py-4 rounded-xl text-base font-semibold text-navy-950 bg-white hover:bg-slate-100 shadow-lg hover:shadow-xl transition-all"
            >
              <span>Upload Your Manuscript</span>
              <ArrowRight className="w-5 h-5 text-navy-900" />
            </Link>
            <Link
              href="/dashboard"
              className="w-full sm:w-auto inline-flex items-center justify-center space-x-2 px-8 py-4 rounded-xl text-base font-semibold text-white bg-slate-800/80 hover:bg-slate-700/80 border border-slate-700 transition-all"
            >
              <span>Explore Dashboard</span>
            </Link>
          </div>

          {/* Quick Stats Banner */}
          <div className="mt-16 pt-10 border-t border-slate-800 grid grid-cols-2 md:grid-cols-4 gap-6 text-left">
            <div>
              <div className="text-3xl font-extrabold text-accent-400">10 Core</div>
              <div className="text-xs text-slate-400 mt-1">Multi-Dimensional Modules</div>
            </div>
            <div>
              <div className="text-3xl font-extrabold text-emerald-400">100% Real</div>
              <div className="text-xs text-slate-400 mt-1">Extracted Manuscript Analysis</div>
            </div>
            <div>
              <div className="text-3xl font-extrabold text-amber-400">OpenAlex</div>
              <div className="text-xs text-slate-400 mt-1">Scholarly Metadata Integration</div>
            </div>
            <div>
              <div className="text-3xl font-extrabold text-teal-400">PDF Report</div>
              <div className="text-xs text-slate-400 mt-1">Executive Summary Export</div>
            </div>
          </div>
        </div>
      </section>

      {/* 10 Core Features Grid */}
      <section className="py-24 bg-white border-b border-slate-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center max-w-3xl mx-auto mb-16">
            <h2 className="text-xs uppercase tracking-widest font-bold text-accent-600 mb-2">
              Comprehensive Scholarly Evaluation
            </h2>
            <h3 className="text-3xl sm:text-4xl font-extrabold text-navy-950">
              Ten AI Modules Delivering Actionable Peer-Review Insights
            </h3>
            <p className="mt-4 text-slate-600 text-sm leading-relaxed">
              Every check is grounded in your manuscript’s text. No fabricated impact factors,
              no artificial score inflations, and no generic placeholders.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {features.map((feat, idx) => (
              <div
                key={idx}
                className="p-6 bg-slate-50 border border-slate-200/80 rounded-2xl hover:border-slate-300 hover:shadow-md transition-all group"
              >
                <div className="w-12 h-12 rounded-xl bg-white border border-slate-200 shadow-sm flex items-center justify-center mb-4 group-hover:scale-105 transition-transform">
                  {feat.icon}
                </div>
                <h4 className="text-base font-bold text-navy-900 mb-2">{feat.title}</h4>
                <p className="text-xs leading-relaxed text-slate-600">{feat.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* How it Works Section */}
      <section className="py-24 bg-slate-50 border-b border-slate-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center max-w-3xl mx-auto mb-16">
            <h2 className="text-xs uppercase tracking-widest font-bold text-accent-600 mb-2">
              Streamlined Evaluation Workflow
            </h2>
            <h3 className="text-3xl font-extrabold text-navy-950">
              From Upload to Publication-Ready Manuscript in 3 Steps
            </h3>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div className="bg-white p-8 rounded-2xl border border-slate-200 shadow-sm relative">
              <div className="w-10 h-10 rounded-full bg-navy-800 text-white font-bold flex items-center justify-center mb-6">
                1
              </div>
              <h4 className="text-lg font-bold text-navy-900 mb-2">Upload Manuscript</h4>
              <p className="text-xs text-slate-600 leading-relaxed">
                Submit your paper in PDF or Word (.docx) format. ResearchIQ parses structural sections, figures, tables, and bibliographies.
              </p>
            </div>

            <div className="bg-white p-8 rounded-2xl border border-slate-200 shadow-sm relative">
              <div className="w-10 h-10 rounded-full bg-navy-800 text-white font-bold flex items-center justify-center mb-6">
                2
              </div>
              <h4 className="text-lg font-bold text-navy-900 mb-2">Multi-Engine AI Analysis</h4>
              <p className="text-xs text-slate-600 leading-relaxed">
                Ten specialized engines evaluate your work in parallel: technical review, novelty against OpenAlex, grammar, citations, and reviewer critique.
              </p>
            </div>

            <div className="bg-white p-8 rounded-2xl border border-slate-200 shadow-sm relative">
              <div className="w-10 h-10 rounded-full bg-navy-800 text-white font-bold flex items-center justify-center mb-6">
                3
              </div>
              <h4 className="text-lg font-bold text-navy-900 mb-2">Readiness Score & PDF Report</h4>
              <p className="text-xs text-slate-600 leading-relaxed">
                Review the multi-attribute dashboard, resolve specific suggestions, and export an executive publication readiness report.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 bg-navy-900 text-white text-center">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
          <h2 className="text-3xl sm:text-4xl font-extrabold tracking-tight">
            Ready to Evaluate Your Manuscript?
          </h2>
          <p className="mt-4 text-slate-300 text-sm max-w-2xl mx-auto">
            Increase your acceptance rate by spotting critical methodology flaws, citation gaps, and formatting inconsistencies before journal editors do.
          </p>
          <div className="mt-8 flex justify-center">
            <Link
              href="/upload"
              className="inline-flex items-center space-x-2 px-8 py-3.5 rounded-xl font-semibold bg-accent-500 hover:bg-accent-600 text-white shadow-md transition-colors"
            >
              <span>Get Started Free</span>
              <ArrowRight className="w-4 h-4" />
            </Link>
          </div>
        </div>
      </section>
    </div>
  );
}
