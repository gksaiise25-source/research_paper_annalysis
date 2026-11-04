'use client';

import React, { useEffect, useState, Suspense } from 'react';
import { useSearchParams, useRouter } from 'next/navigation';
import {
  FileSearch,
  Sparkles,
  Quote,
  Languages,
  CopyCheck,
  Image as ImageIcon,
  MessageSquare,
  Compass,
  Lightbulb,
  Award,
  Download,
  RotateCw,
  AlertCircle,
  CheckCircle2,
  AlertTriangle,
  ExternalLink,
  ChevronRight,
  Loader2,
  FileText,
  ShieldCheck,
  Check,
  X,
} from 'lucide-react';
import {
  ResponsiveContainer,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
} from 'recharts';
import { analysisService, paperService, authService } from '@/services/api';
import { PaperAnalysisState, Paper } from '@/types';

function AnalysisContent() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const paperId = Number(searchParams.get('id'));

  const [activeTab, setActiveTab] = useState<string>('readiness');
  const [analysisData, setAnalysisData] = useState<PaperAnalysisState | null>(null);
  const [paperDetails, setPaperDetails] = useState<Paper | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [isDownloading, setIsDownloading] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  const tabs = [
    { id: 'readiness', label: '10. Readiness Score', icon: Award },
    { id: 'technical_review', label: '1. Technical Review', icon: FileSearch },
    { id: 'novelty', label: '2. Novelty & Gaps', icon: Sparkles },
    { id: 'citations', label: '3. Citations', icon: Quote },
    { id: 'grammar', label: '4. Writing Quality', icon: Languages },
    { id: 'plagiarism', label: '5. Plagiarism Risk', icon: CopyCheck },
    { id: 'figures_tables', label: '6. Figures & Tables', icon: ImageIcon },
    { id: 'reviewer_comments', label: '7. AI Peer Review', icon: MessageSquare },
    { id: 'journals', label: '8. Journal Matching', icon: Compass },
    { id: 'patentability', label: '9. Patentability', icon: Lightbulb },
  ];

  useEffect(() => {
    if (!authService.isAuthenticated()) {
      router.push('/login');
      return;
    }
    if (!paperId) {
      router.push('/dashboard');
      return;
    }
    loadAnalysis();
  }, [paperId]);

  const loadAnalysis = async () => {
    setIsLoading(true);
    setErrorMsg(null);
    try {
      const [paper, analyses] = await Promise.all([
        paperService.getPaper(paperId),
        analysisService.getResults(paperId),
      ]);
      setPaperDetails(paper);
      setAnalysisData(analyses);
    } catch (err: any) {
      console.error(err);
      setErrorMsg('Failed to load analysis results. Please refresh or re-run modules.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleRefresh = async () => {
    setIsRefreshing(true);
    try {
      const analyses = await analysisService.getResults(paperId);
      setAnalysisData(analyses);
    } catch (err) {
      console.error(err);
    } finally {
      setIsRefreshing(false);
    }
  };

  const handleDownloadPDF = async () => {
    setIsDownloading(true);
    try {
      const blob = await analysisService.downloadReport(paperId);
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `ResearchIQ_Evaluation_Report_${paperId}.pdf`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
    } catch (err) {
      console.error('PDF download error:', err);
      alert('Failed to generate PDF report. Ensure all modules have completed analysis.');
    } finally {
      setIsDownloading(false);
    }
  };

  const handleRerunModule = async (slug: string) => {
    setIsRefreshing(true);
    try {
      await analysisService.triggerFeature(paperId, slug.replace('_', '-'));
      await handleRefresh();
    } catch (err) {
      console.error(err);
      alert('Could not re-run module.');
    } finally {
      setIsRefreshing(false);
    }
  };

  if (isLoading) {
    return (
      <div className="min-h-[70vh] flex flex-col items-center justify-center">
        <Loader2 className="w-10 h-10 animate-spin text-navy-800 mb-4" />
        <p className="text-sm font-semibold text-slate-700">Loading ResearchIQ Evaluation Dashboard...</p>
        <p className="text-xs text-slate-400 mt-1">Grounded analysis across 10 analytical dimensions</p>
      </div>
    );
  }

  const analyses = analysisData?.analyses || {};
  const readiness = analyses.readiness?.result_data;
  const tech = analyses.technical_review?.result_data;
  const novelty = analyses.novelty?.result_data;
  const citations = analyses.citations?.result_data;
  const grammar = analyses.grammar?.result_data;
  const plagiarism = analyses.plagiarism?.result_data;
  const figures = analyses.figures_tables?.result_data;
  const reviewer = analyses.reviewer_comments?.result_data;
  const journals = analyses.journals?.result_data;
  const patent = analyses.patentability?.result_data;

  // Radar chart data for publication readiness breakdown
  const radarData = [
    { dimension: 'Methodology', score: tech?.overall_score || 0 },
    { dimension: 'Novelty', score: novelty?.overall_novelty_score || 0 },
    { dimension: 'Citations', score: citations?.citation_score || 0 },
    { dimension: 'Writing', score: grammar?.grammar_score || 0 },
    { dimension: 'Figures', score: figures?.validation_score || 0 },
    { dimension: 'Originality', score: plagiarism?.originality_indicator || 0 },
  ];

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Top Header Card */}
      <div className="bg-white border border-slate-200 rounded-3xl p-6 sm:p-8 shadow-sm mb-8">
        <div className="flex flex-col lg:flex-row justify-between items-start lg:items-center gap-6">
          <div className="space-y-2">
            <div className="flex flex-wrap items-center gap-2">
              <span className="px-2.5 py-1 rounded-full text-[11px] font-bold uppercase tracking-wider bg-navy-100 text-navy-800">
                Manuscript #{paperId}
              </span>
              <span className="px-2.5 py-1 rounded-full text-[11px] font-semibold bg-slate-100 text-slate-600 uppercase">
                {paperDetails?.file_type} format
              </span>
              <span className="text-xs text-slate-400">
                Uploaded {paperDetails ? new Date(paperDetails.created_at).toLocaleDateString() : ''}
              </span>
            </div>
            <h1 className="text-xl sm:text-2xl font-extrabold text-navy-950 max-w-4xl leading-tight">
              {paperDetails?.title || paperDetails?.filename || 'Untitled Manuscript'}
            </h1>
          </div>

          {/* Action Buttons */}
          <div className="flex flex-wrap items-center gap-3">
            <button
              onClick={handleRefresh}
              disabled={isRefreshing}
              className="inline-flex items-center space-x-1.5 px-4 py-2.5 rounded-xl border border-slate-300 text-xs font-semibold text-slate-700 hover:bg-slate-50 transition-colors disabled:opacity-50"
            >
              <RotateCw className={`w-3.5 h-3.5 ${isRefreshing ? 'animate-spin' : ''}`} />
              <span>Refresh Results</span>
            </button>

            <button
              onClick={handleDownloadPDF}
              disabled={isDownloading}
              className="inline-flex items-center space-x-2 px-5 py-2.5 rounded-xl text-xs font-semibold text-white bg-navy-800 hover:bg-navy-900 shadow-md transition-colors disabled:opacity-50"
            >
              {isDownloading ? (
                <Loader2 className="w-3.5 h-3.5 animate-spin" />
              ) : (
                <Download className="w-3.5 h-3.5" />
              )}
              <span>Download Official PDF Report</span>
            </button>
          </div>
        </div>
      </div>

      {/* Tabs Navigation */}
      <div className="flex overflow-x-auto space-x-2 border-b border-slate-200 pb-2 mb-8 scrollbar-none">
        {tabs.map((tab) => {
          const Icon = tab.icon;
          const isActive = activeTab === tab.id;
          return (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`flex items-center space-x-2 px-4 py-2.5 rounded-xl text-xs font-bold whitespace-nowrap transition-all ${
                isActive
                  ? 'bg-navy-800 text-white shadow-sm'
                  : 'text-slate-600 hover:bg-slate-100 hover:text-navy-900'
              }`}
            >
              <Icon className="w-4 h-4" />
              <span>{tab.label}</span>
            </button>
          );
        })}
      </div>

      {/* TAB 10: Publication Readiness Score */}
      {activeTab === 'readiness' && (
        <div className="space-y-8">
          {/* Executive Score Card */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div className="lg:col-span-1 p-6 bg-white border border-slate-200 rounded-3xl shadow-sm flex flex-col justify-between text-center sm:text-left">
              <div>
                <span className="text-xs font-bold text-slate-400 uppercase tracking-widest">
                  Readiness Verdict
                </span>
                <div className="mt-4 flex items-center justify-center sm:justify-start space-x-4">
                  <div className="text-5xl font-black text-navy-950">
                    {readiness?.overall_score || 0}
                    <span className="text-2xl text-slate-400 font-normal">/100</span>
                  </div>
                </div>
                <div className="mt-3">
                  <span
                    className={`inline-flex items-center px-3 py-1 rounded-full text-xs font-extrabold ${
                      readiness?.overall_score && readiness.overall_score >= 80
                        ? 'bg-emerald-100 text-emerald-800'
                        : readiness?.overall_score && readiness.overall_score >= 60
                        ? 'bg-amber-100 text-amber-800'
                        : 'bg-rose-100 text-rose-800'
                    }`}
                  >
                    {readiness?.readiness_category || 'Pending Assessment'}
                  </span>
                </div>
                <p className="mt-4 text-xs text-slate-600 leading-relaxed">
                  {readiness?.summary_assessment ||
                    'Multi-module analytical pipeline is processing your manuscript sections.'}
                </p>
              </div>

              <div className="mt-6 pt-4 border-t border-slate-100 text-[11px] text-slate-400">
                Evaluation weights normalized dynamically across completed analytical engines.
              </div>
            </div>

            {/* Radar Dimension Chart */}
            <div className="lg:col-span-2 p-6 bg-white border border-slate-200 rounded-3xl shadow-sm">
              <h3 className="text-sm font-bold text-navy-950 mb-2">
                Multi-Dimensional Metric Alignment
              </h3>
              <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <RadarChart data={radarData}>
                    <PolarGrid stroke="#e2e8f0" />
                    <PolarAngleAxis dataKey="dimension" fontSize={11} stroke="#64748b" />
                    <PolarRadiusAxis domain={[0, 100]} angle={30} stroke="#94a3b8" />
                    <Radar
                      name="Score"
                      dataKey="score"
                      stroke="#0284c7"
                      fill="#38bdf8"
                      fillOpacity={0.4}
                    />
                    <Tooltip />
                  </RadarChart>
                </ResponsiveContainer>
              </div>
            </div>
          </div>

          {/* Dimension Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
            {readiness?.category_scores &&
              Object.entries(readiness.category_scores).map(([key, item]: [string, any]) => (
                <div
                  key={key}
                  className="p-5 bg-white border border-slate-200 rounded-2xl shadow-sm flex flex-col justify-between"
                >
                  <div>
                    <div className="flex justify-between items-center mb-2">
                      <span className="text-xs font-bold text-navy-950">
                        {item.label || key.replace('_', ' ').toUpperCase()}
                      </span>
                      <span className="text-xs font-semibold text-slate-400">
                        {item.weight ? `${Math.round(item.weight * 100)}% wt` : ''}
                      </span>
                    </div>
                    <div className="text-2xl font-black text-navy-900">
                      {item.score !== null ? `${item.score}%` : 'Unavailable'}
                    </div>
                  </div>
                  <div className="mt-4 pt-3 border-t border-slate-100 flex justify-between items-center text-[11px]">
                    <span className="text-slate-500">Status</span>
                    <span className="font-semibold text-emerald-600">{item.status}</span>
                  </div>
                </div>
              ))}
          </div>

          {/* Action Checklist & Strengths */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="p-6 bg-white border border-slate-200 rounded-3xl shadow-sm">
              <h3 className="text-sm font-bold text-navy-950 mb-4 flex items-center space-x-2">
                <CheckCircle2 className="w-4 h-4 text-emerald-600" />
                <span>Verified Manuscript Strengths</span>
              </h3>
              <ul className="space-y-3">
                {readiness?.strengths && readiness.strengths.length > 0 ? (
                  readiness.strengths.map((str: string, i: number) => (
                    <li key={i} className="text-xs text-slate-700 flex items-start space-x-2">
                      <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 mt-1.5 flex-shrink-0" />
                      <span>{str}</span>
                    </li>
                  ))
                ) : (
                  <p className="text-xs text-slate-400">No strengths recorded yet.</p>
                )}
              </ul>
            </div>

            <div className="p-6 bg-white border border-slate-200 rounded-3xl shadow-sm">
              <h3 className="text-sm font-bold text-navy-950 mb-4 flex items-center space-x-2">
                <AlertTriangle className="w-4 h-4 text-amber-500" />
                <span>Priority Action Checklist Before Submission</span>
              </h3>
              <ul className="space-y-3">
                {readiness?.priority_improvements && readiness.priority_improvements.length > 0 ? (
                  readiness.priority_improvements.map((imp: string, i: number) => (
                    <li key={i} className="text-xs text-slate-700 flex items-start space-x-2">
                      <span className="w-1.5 h-1.5 rounded-full bg-amber-500 mt-1.5 flex-shrink-0" />
                      <span>{imp}</span>
                    </li>
                  ))
                ) : (
                  <p className="text-xs text-slate-400">No action items flagged.</p>
                )}
              </ul>
            </div>
          </div>
        </div>
      )}

      {/* TAB 1: Technical Review */}
      {activeTab === 'technical_review' && (
        <div className="space-y-6">
          <div className="p-6 bg-white border border-slate-200 rounded-3xl shadow-sm flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
            <div>
              <span className="text-xs font-bold text-slate-400 uppercase tracking-widest">
                Structural Completeness
              </span>
              <div className="text-3xl font-black text-navy-950 mt-1">
                {tech?.overall_score || 0}%
              </div>
              <p className="text-xs text-slate-500 mt-1">
                Analyzed {tech?.word_count || 0} total words across recognized research sections.
              </p>
            </div>
            <button
              onClick={() => handleRerunModule('technical-review')}
              className="px-4 py-2 rounded-xl text-xs font-semibold bg-navy-50 text-navy-800 hover:bg-navy-100"
            >
              Re-run Technical Review
            </button>
          </div>

          {/* Section-by-section breakdown */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
            {tech?.section_analyses &&
              Object.entries(tech.section_analyses).map(([secName, sec]: [string, any]) => (
                <div key={secName} className="p-5 bg-white border border-slate-200 rounded-2xl shadow-sm">
                  <div className="flex justify-between items-center mb-3">
                    <h4 className="text-sm font-bold text-navy-950 capitalize">{secName.replace('_', ' ')}</h4>
                    <span
                      className={`px-2 py-0.5 rounded-full text-[10px] font-bold ${
                        sec.present
                          ? 'bg-emerald-50 text-emerald-700'
                          : 'bg-rose-50 text-rose-700'
                      }`}
                    >
                      {sec.present ? `${Math.round(sec.score * 100)}% Score` : 'Missing Section'}
                    </span>
                  </div>
                  <div className="text-xs text-slate-500 mb-3">
                    {sec.word_count} words analyzed
                  </div>
                  <div className="space-y-1.5">
                    {sec.feedback &&
                      sec.feedback.map((fb: string, i: number) => (
                        <p key={i} className="text-xs text-slate-700 leading-relaxed">
                          {fb}
                        </p>
                      ))}
                  </div>
                </div>
              ))}
          </div>
        </div>
      )}

      {/* TAB 2: Novelty Analysis */}
      {activeTab === 'novelty' && (
        <div className="space-y-6">
          <div className="p-6 bg-white border border-slate-200 rounded-3xl shadow-sm flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
            <div>
              <span className="text-xs font-bold text-slate-400 uppercase tracking-widest">
                Novelty Assessment
              </span>
              <div className="text-3xl font-black text-navy-950 mt-1">
                {novelty?.overall_novelty_score || 0}%
              </div>
              <p className="text-xs text-slate-600 mt-1 max-w-xl">
                {novelty?.assessment}
              </p>
            </div>
            <button
              onClick={() => handleRerunModule('novelty')}
              className="px-4 py-2 rounded-xl text-xs font-semibold bg-navy-50 text-navy-800 hover:bg-navy-100"
            >
              Re-run Novelty Search
            </button>
          </div>

          {/* Comparison with OpenAlex / Crossref */}
          <div className="bg-white border border-slate-200 rounded-2xl p-6 shadow-sm">
            <h3 className="text-sm font-bold text-navy-950 mb-4 flex items-center space-x-2">
              <Sparkles className="w-4 h-4 text-accent-600" />
              <span>Thematically Related Published Literature (OpenAlex Registry)</span>
            </h3>

            {novelty?.similar_papers && novelty.similar_papers.length > 0 ? (
              <div className="space-y-4">
                {novelty.similar_papers.map((paper: any, idx: number) => (
                  <div
                    key={idx}
                    className="p-4 rounded-xl border border-slate-100 bg-slate-50/70 hover:bg-slate-50 transition-colors"
                  >
                    <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-2 mb-2">
                      <h4 className="text-xs font-bold text-navy-950">{paper.title}</h4>
                      <span className="px-2.5 py-1 rounded-full text-[10px] font-bold bg-navy-100 text-navy-800 whitespace-nowrap">
                        {paper.similarity_percentage}% Thematic Overlap
                      </span>
                    </div>
                    <p className="text-xs text-slate-600 line-clamp-2 mb-2">
                      {paper.abstract_snippet || 'Abstract text registered in index.'}
                    </p>
                    <div className="flex items-center space-x-4 text-[11px] text-slate-400">
                      <span>Venue: {paper.venue || 'Scholarly Publication'}</span>
                      {paper.year && <span>Year: {paper.year}</span>}
                      {paper.citations !== undefined && <span>Citations: {paper.citations}</span>}
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-xs text-slate-500">
                No overlapping publications retrieved. Ensure keywords are clearly defined in the abstract.
              </p>
            )}
          </div>
        </div>
      )}

      {/* TAB 3: Citations */}
      {activeTab === 'citations' && (
        <div className="space-y-6">
          <div className="p-6 bg-white border border-slate-200 rounded-3xl shadow-sm flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
            <div>
              <span className="text-xs font-bold text-slate-400 uppercase tracking-widest">
                Citation Integrity Score
              </span>
              <div className="text-3xl font-black text-navy-950 mt-1">
                {citations?.citation_score || 0}%
              </div>
              <p className="text-xs text-slate-500 mt-1">
                Style Detected: <b>{citations?.detected_style || 'IEEE'}</b> | Total References: <b>{citations?.total_references || 0}</b> | In-text Mentions: <b>{citations?.total_intext_citations || 0}</b>
              </p>
            </div>
            <button
              onClick={() => handleRerunModule('citations')}
              className="px-4 py-2 rounded-xl text-xs font-semibold bg-navy-50 text-navy-800 hover:bg-navy-100"
            >
              Re-run Citation Analysis
            </button>
          </div>

          {/* Issues Card */}
          <div className="bg-white border border-slate-200 rounded-2xl p-6 shadow-sm">
            <h3 className="text-sm font-bold text-navy-950 mb-4">Bibliographic Consistency Checks</h3>
            <div className="space-y-3">
              {citations?.issues?.cross_reference_issues && citations.issues.cross_reference_issues.length > 0 ? (
                citations.issues.cross_reference_issues.map((iss: any, i: number) => (
                  <div key={i} className="p-3 rounded-xl bg-amber-50 border border-amber-200 text-xs text-amber-800 flex items-start space-x-2">
                    <AlertTriangle className="w-4 h-4 flex-shrink-0 mt-0.5" />
                    <span>{iss.description}</span>
                  </div>
                ))
              ) : (
                <div className="p-3 rounded-xl bg-emerald-50 border border-emerald-200 text-xs text-emerald-800 flex items-center space-x-2">
                  <CheckCircle2 className="w-4 h-4" />
                  <span>No orphaned or missing cross-references detected.</span>
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* TAB 4: Grammar & Language */}
      {activeTab === 'grammar' && (
        <div className="space-y-6">
          <div className="p-6 bg-white border border-slate-200 rounded-3xl shadow-sm flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
            <div>
              <span className="text-xs font-bold text-slate-400 uppercase tracking-widest">
                Academic Language Score
              </span>
              <div className="text-3xl font-black text-navy-950 mt-1">
                {grammar?.grammar_score || 0}%
              </div>
              <p className="text-xs text-slate-500 mt-1">
                Academic Tone: <b>{grammar?.academic_tone_score || 0}%</b> | Readability Level: <b>{grammar?.readability_score?.level || 'Standard'}</b>
              </p>
            </div>
            <button
              onClick={() => handleRerunModule('grammar')}
              className="px-4 py-2 rounded-xl text-xs font-semibold bg-navy-50 text-navy-800 hover:bg-navy-100"
            >
              Re-run Grammar Check
            </button>
          </div>

          <div className="bg-white border border-slate-200 rounded-2xl p-6 shadow-sm">
            <h3 className="text-sm font-bold text-navy-950 mb-4">Academic Writing Suggestions</h3>
            <div className="space-y-3">
              {grammar?.suggestions && grammar.suggestions.length > 0 ? (
                grammar.suggestions.map((sug: any, i: number) => (
                  <div key={i} className="p-3.5 rounded-xl border border-slate-200 bg-slate-50/50 flex flex-col sm:flex-row justify-between items-start sm:items-center gap-2">
                    <div className="text-xs">
                      <p className="text-slate-600 line-through mb-1">"{sug.original}"</p>
                      <p className="font-semibold text-navy-950">&rarr; {sug.suggestion}</p>
                      <p className="text-[11px] text-slate-400 mt-1">{sug.reason}</p>
                    </div>
                    <span className="px-2 py-0.5 rounded text-[10px] font-bold uppercase bg-slate-200 text-slate-700">
                      {sug.severity}
                    </span>
                  </div>
                ))
              ) : (
                <p className="text-xs text-slate-500">Writing quality meets high academic standards.</p>
              )}
            </div>
          </div>
        </div>
      )}

      {/* TAB 5: Plagiarism Risk */}
      {activeTab === 'plagiarism' && (
        <div className="space-y-6">
          <div className="p-6 bg-white border border-slate-200 rounded-3xl shadow-sm flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
            <div>
              <span className="text-xs font-bold text-slate-400 uppercase tracking-widest">
                Similarity Risk Level
              </span>
              <div className="text-3xl font-black text-navy-950 mt-1">
                {plagiarism?.overall_risk_level || 'Minimal Risk'}
              </div>
              <p className="text-xs text-slate-500 mt-1">
                Originality Indicator: <b>{plagiarism?.originality_indicator || 100}%</b> | Similarity Score: <b>{plagiarism?.similarity_score || 0}%</b>
              </p>
            </div>
            <button
              onClick={() => handleRerunModule('plagiarism')}
              className="px-4 py-2 rounded-xl text-xs font-semibold bg-navy-50 text-navy-800 hover:bg-navy-100"
            >
              Re-run Plagiarism Screening
            </button>
          </div>

          <div className="p-4 rounded-2xl bg-amber-50/70 border border-amber-200 text-xs text-amber-900 leading-relaxed">
            <span className="font-bold">Notice & Disclaimer: </span>
            {plagiarism?.disclaimer}
          </div>
        </div>
      )}

      {/* TAB 6: Figures & Tables */}
      {activeTab === 'figures_tables' && (
        <div className="space-y-6">
          <div className="p-6 bg-white border border-slate-200 rounded-3xl shadow-sm flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
            <div>
              <span className="text-xs font-bold text-slate-400 uppercase tracking-widest">
                Figure & Table Validation
              </span>
              <div className="text-3xl font-black text-navy-950 mt-1">
                {figures?.validation_score || 0}%
              </div>
              <p className="text-xs text-slate-500 mt-1">
                Figures Detected: <b>{figures?.summary?.detected_figures_count || 0}</b> | Tables Detected: <b>{figures?.summary?.detected_tables_count || 0}</b>
              </p>
            </div>
            <button
              onClick={() => handleRerunModule('figures-tables')}
              className="px-4 py-2 rounded-xl text-xs font-semibold bg-navy-50 text-navy-800 hover:bg-navy-100"
            >
              Re-run Figure Check
            </button>
          </div>

          <div className="bg-white border border-slate-200 rounded-2xl p-6 shadow-sm">
            <h3 className="text-sm font-bold text-navy-950 mb-4">Diagnostics & Warnings</h3>
            <div className="space-y-3">
              {figures?.issues && figures.issues.length > 0 ? (
                figures.issues.map((iss: any, i: number) => (
                  <div key={i} className="p-3.5 rounded-xl border border-slate-200 bg-slate-50 flex items-start space-x-3 text-xs">
                    <AlertTriangle className="w-4 h-4 text-amber-500 flex-shrink-0 mt-0.5" />
                    <div>
                      <span className="font-bold text-navy-950">{iss.element}: </span>
                      <span className="text-slate-600">{iss.message}</span>
                    </div>
                  </div>
                ))
              ) : (
                <p className="text-xs text-emerald-700 font-semibold">
                  All figures and tables are properly numbered, captioned, and referenced.
                </p>
              )}
            </div>
          </div>
        </div>
      )}

      {/* TAB 7: AI Reviewer Comments */}
      {activeTab === 'reviewer_comments' && (
        <div className="space-y-6">
          <div className="p-6 bg-white border border-slate-200 rounded-3xl shadow-sm flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
            <div>
              <span className="text-xs font-bold text-slate-400 uppercase tracking-widest">
                Peer Reviewer Recommendation
              </span>
              <div className="text-3xl font-black text-navy-950 mt-1">
                {reviewer?.recommendation || 'Minor Revision'}
              </div>
              <p className="text-xs text-slate-500 mt-1">
                Mode: <b>{reviewer?.generator_mode || 'Academic Rubric Model'}</b>
              </p>
            </div>
            <button
              onClick={() => handleRerunModule('reviewer-comments')}
              className="px-4 py-2 rounded-xl text-xs font-semibold bg-navy-50 text-navy-800 hover:bg-navy-100"
            >
              Regenerate Review
            </button>
          </div>

          <div className="p-6 bg-white border border-slate-200 rounded-3xl shadow-sm space-y-6">
            <div>
              <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">Overall Assessment</h4>
              <p className="text-xs text-slate-700 leading-relaxed bg-slate-50 p-4 rounded-xl border border-slate-200">
                {reviewer?.overall_assessment}
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <h4 className="text-xs font-bold text-emerald-700 uppercase tracking-wider mb-2 flex items-center space-x-1.5">
                  <CheckCircle2 className="w-3.5 h-3.5" />
                  <span>Paper Strengths</span>
                </h4>
                <ul className="space-y-2">
                  {reviewer?.paper_strengths?.map((str: string, i: number) => (
                    <li key={i} className="text-xs text-slate-600 flex items-start space-x-2">
                      <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 mt-1.5 flex-shrink-0" />
                      <span>{str}</span>
                    </li>
                  ))}
                </ul>
              </div>

              <div>
                <h4 className="text-xs font-bold text-rose-700 uppercase tracking-wider mb-2 flex items-center space-x-1.5">
                  <AlertCircle className="w-3.5 h-3.5" />
                  <span>Major Revisions Required</span>
                </h4>
                <ul className="space-y-2">
                  {reviewer?.major_revisions?.map((rev: string, i: number) => (
                    <li key={i} className="text-xs text-slate-600 flex items-start space-x-2">
                      <span className="w-1.5 h-1.5 rounded-full bg-rose-500 mt-1.5 flex-shrink-0" />
                      <span>{rev}</span>
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* TAB 8: Journal Recommendations */}
      {activeTab === 'journals' && (
        <div className="space-y-6">
          <div className="p-6 bg-white border border-slate-200 rounded-3xl shadow-sm flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
            <div>
              <span className="text-xs font-bold text-slate-400 uppercase tracking-widest">
                Publication Venue Matching
              </span>
              <div className="text-3xl font-black text-navy-950 mt-1">
                {journals?.total_venues_found || 0} Venues Sourced
              </div>
              <p className="text-xs text-slate-500 mt-1">
                Queried via OpenAlex Scholarly Registry based on manuscript keywords.
              </p>
            </div>
            <button
              onClick={() => handleRerunModule('journals')}
              className="px-4 py-2 rounded-xl text-xs font-semibold bg-navy-50 text-navy-800 hover:bg-navy-100"
            >
              Re-run Venue Search
            </button>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
            {journals?.recommendations?.map((venue: any, idx: number) => (
              <div key={idx} className="p-5 bg-white border border-slate-200 rounded-2xl shadow-sm flex flex-col justify-between">
                <div>
                  <div className="flex justify-between items-start gap-2 mb-2">
                    <h4 className="text-sm font-bold text-navy-950">{venue.name}</h4>
                    <span className="px-2.5 py-1 rounded-full text-[10px] font-bold bg-navy-100 text-navy-800 whitespace-nowrap">
                      {venue.suitability_score}% Fit
                    </span>
                  </div>
                  <p className="text-xs text-slate-500 mb-2">Publisher: <b>{venue.publisher}</b> | {venue.type}</p>
                  <p className="text-xs text-slate-600 leading-relaxed mb-3">{venue.matching_explanation}</p>
                </div>
                <div className="pt-3 border-t border-slate-100 flex justify-between items-center text-xs">
                  <span className="text-slate-400 text-[11px]">{venue.indexing_status}</span>
                  {venue.website && (
                    <a
                      href={venue.website}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="inline-flex items-center space-x-1 text-accent-600 font-semibold hover:text-accent-700"
                    >
                      <span>Visit Venue</span>
                      <ExternalLink className="w-3.5 h-3.5" />
                    </a>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* TAB 9: Patentability */}
      {activeTab === 'patentability' && (
        <div className="space-y-6">
          <div className="p-6 bg-white border border-slate-200 rounded-3xl shadow-sm flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
            <div>
              <span className="text-xs font-bold text-slate-400 uppercase tracking-widest">
                Patentability Screening
              </span>
              <div className="text-3xl font-black text-navy-950 mt-1">
                {patent?.overall_patentability_score || 0}%
              </div>
              <p className="text-xs text-slate-500 mt-1">
                Classification: <b>{patent?.readiness_tier}</b>
              </p>
            </div>
            <button
              onClick={() => handleRerunModule('patentability')}
              className="px-4 py-2 rounded-xl text-xs font-semibold bg-navy-50 text-navy-800 hover:bg-navy-100"
            >
              Re-run Patent Screening
            </button>
          </div>

          <div className="p-6 bg-white border border-slate-200 rounded-3xl shadow-sm space-y-4">
            <h3 className="text-sm font-bold text-navy-950">Statutory Subject Matter Eligibility</h3>
            <div className="space-y-2">
              {patent?.eligibility_concerns?.map((con: string, i: number) => (
                <div key={i} className="p-3 bg-slate-50 rounded-xl border border-slate-200 text-xs text-slate-700">
                  {con}
                </div>
              ))}
            </div>

            <div className="mt-4 pt-4 border-t border-slate-100 text-[11px] text-slate-400">
              {patent?.disclaimer}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default function AnalysisPage() {
  return (
    <Suspense
      fallback={
        <div className="min-h-[70vh] flex flex-col items-center justify-center">
          <Loader2 className="w-8 h-8 animate-spin text-navy-800" />
          <p className="text-xs text-slate-500 mt-2">Loading analysis dashboard...</p>
        </div>
      }
    >
      <AnalysisContent />
    </Suspense>
  );
}
