'use client';

import React, { useEffect, useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import {
  FileText,
  Award,
  AlertTriangle,
  Upload,
  ArrowRight,
  TrendingUp,
  Clock,
  CheckCircle2,
  FileCheck2,
  Layers,
} from 'lucide-react';
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  PieChart,
  Pie,
  Cell,
} from 'recharts';
import { paperService, analysisService, authService } from '@/services/api';
import { Paper } from '@/types';

export default function DashboardPage() {
  const router = useRouter();
  const [papers, setPapers] = useState<Paper[]>([]);
  const [history, setHistory] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    if (!authService.isAuthenticated()) {
      router.push('/login');
      return;
    }
    loadDashboardData();
  }, [router]);

  const loadDashboardData = async () => {
    setIsLoading(true);
    try {
      const [papersRes, historyRes] = await Promise.all([
        paperService.getPapers(),
        analysisService.getHistory(),
      ]);
      setPapers(papersRes.papers || []);
      setHistory(historyRes.history || []);
    } catch (err) {
      console.error('Failed to load dashboard data:', err);
    } finally {
      setIsLoading(false);
    }
  };

  // Compute metrics
  const totalPapers = papers.length;
  const scoredPapers = history.filter((h) => h.readiness_score !== null);
  const avgReadiness =
    scoredPapers.length > 0
      ? Math.round(
          scoredPapers.reduce((acc, curr) => acc + (curr.readiness_score || 0), 0) /
            scoredPapers.length
        )
      : 0;

  const requiringRevision = history.filter(
    (h) =>
      h.readiness_category === 'Major Revision' ||
      h.readiness_category === 'Minor Revision' ||
      (h.readiness_score !== null && h.readiness_score < 80)
  ).length;

  const readyForSubmission = history.filter(
    (h) => h.readiness_category === 'Ready for Submission' || (h.readiness_score && h.readiness_score >= 80)
  ).length;

  // Chart Data
  const readinessTrendData = history.slice(0, 6).reverse().map((h, i) => ({
    name: `Paper #${h.paper_id}`,
    score: h.readiness_score || 0,
    title: h.title ? h.title.slice(0, 20) + '...' : `Paper #${h.paper_id}`,
  }));

  const pieData = [
    { name: 'Ready for Submission', value: readyForSubmission || (totalPapers > 0 ? 1 : 0), color: '#16a34a' },
    { name: 'Minor Revision', value: requiringRevision || 0, color: '#ca8a04' },
    { name: 'Under Processing', value: totalPapers - (readyForSubmission + requiringRevision) > 0 ? totalPapers - (readyForSubmission + requiringRevision) : 0, color: '#0284c7' },
  ].filter(d => d.value > 0);

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 mb-8">
        <div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-navy-950">Scholar Dashboard</h1>
          <p className="text-xs sm:text-sm text-slate-500 mt-1">
            Overview of uploaded manuscripts, readiness trends, and evaluation history.
          </p>
        </div>
        <Link
          href="/upload"
          className="inline-flex items-center space-x-2 px-5 py-2.5 rounded-xl font-semibold text-white bg-navy-800 hover:bg-navy-900 shadow-sm transition-colors text-sm"
        >
          <Upload className="w-4 h-4" />
          <span>Upload Manuscript</span>
        </Link>
      </div>

      {/* KPI Metrics Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5 mb-8">
        <div className="p-5 bg-white border border-slate-200 rounded-2xl shadow-sm">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">
              Total Manuscripts
            </span>
            <div className="w-9 h-9 rounded-xl bg-blue-50 text-blue-600 flex items-center justify-center">
              <FileText className="w-5 h-5" />
            </div>
          </div>
          <div className="mt-3 text-3xl font-extrabold text-navy-950">{totalPapers}</div>
          <div className="mt-1 text-xs text-slate-500">Evaluated in ResearchIQ</div>
        </div>

        <div className="p-5 bg-white border border-slate-200 rounded-2xl shadow-sm">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">
              Avg. Readiness Score
            </span>
            <div className="w-9 h-9 rounded-xl bg-emerald-50 text-emerald-600 flex items-center justify-center">
              <Award className="w-5 h-5" />
            </div>
          </div>
          <div className="mt-3 text-3xl font-extrabold text-navy-950">
            {avgReadiness > 0 ? `${avgReadiness}%` : '—'}
          </div>
          <div className="mt-1 text-xs text-slate-500">Across evaluated papers</div>
        </div>

        <div className="p-5 bg-white border border-slate-200 rounded-2xl shadow-sm">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">
              Revisions Required
            </span>
            <div className="w-9 h-9 rounded-xl bg-amber-50 text-amber-600 flex items-center justify-center">
              <AlertTriangle className="w-5 h-5" />
            </div>
          </div>
          <div className="mt-3 text-3xl font-extrabold text-navy-950">{requiringRevision}</div>
          <div className="mt-1 text-xs text-slate-500">Action items flagged</div>
        </div>

        <div className="p-5 bg-white border border-slate-200 rounded-2xl shadow-sm">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">
              Submission Ready
            </span>
            <div className="w-9 h-9 rounded-xl bg-teal-50 text-teal-600 flex items-center justify-center">
              <FileCheck2 className="w-5 h-5" />
            </div>
          </div>
          <div className="mt-3 text-3xl font-extrabold text-navy-950">{readyForSubmission}</div>
          <div className="mt-1 text-xs text-slate-500">Met quality threshold</div>
        </div>
      </div>

      {/* Analytics Charts */}
      {totalPapers > 0 && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
          <div className="lg:col-span-2 p-6 bg-white border border-slate-200 rounded-2xl shadow-sm">
            <h3 className="text-sm font-bold text-navy-950 mb-4 flex items-center space-x-2">
              <TrendingUp className="w-4 h-4 text-accent-600" />
              <span>Publication Readiness Trend by Manuscript</span>
            </h3>
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={readinessTrendData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                  <XAxis dataKey="name" fontSize={11} stroke="#94a3b8" />
                  <YAxis domain={[0, 100]} fontSize={11} stroke="#94a3b8" />
                  <Tooltip
                    content={({ active, payload }) => {
                      if (active && payload && payload.length) {
                        return (
                          <div className="bg-navy-900 text-white p-2.5 rounded-lg text-xs shadow-lg">
                            <p className="font-semibold">{payload[0].payload.title}</p>
                            <p className="text-accent-300">Readiness: {payload[0].value}%</p>
                          </div>
                        );
                      }
                      return null;
                    }}
                  />
                  <Bar dataKey="score" fill="#1e3a8a" radius={[6, 6, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>

          <div className="p-6 bg-white border border-slate-200 rounded-2xl shadow-sm flex flex-col justify-between">
            <h3 className="text-sm font-bold text-navy-950 mb-2 flex items-center space-x-2">
              <Layers className="w-4 h-4 text-accent-600" />
              <span>Readiness Distribution</span>
            </h3>
            <div className="h-52 flex items-center justify-center">
              {pieData.length > 0 ? (
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie data={pieData} innerRadius={45} outerRadius={70} paddingAngle={4} dataKey="value">
                      {pieData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.color} />
                      ))}
                    </Pie>
                    <Tooltip />
                  </PieChart>
                </ResponsiveContainer>
              ) : (
                <p className="text-xs text-slate-400">No data available</p>
              )}
            </div>
            <div className="space-y-1.5 pt-2 border-t border-slate-100 text-xs">
              {pieData.map((d, i) => (
                <div key={i} className="flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    <span className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: d.color }}></span>
                    <span className="text-slate-600">{d.name}</span>
                  </div>
                  <span className="font-semibold text-navy-900">{d.value}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Recent Manuscripts Table */}
      <div className="bg-white border border-slate-200 rounded-2xl shadow-sm overflow-hidden">
        <div className="px-6 py-4 border-b border-slate-200 flex justify-between items-center">
          <h2 className="text-sm font-bold text-navy-950">Recent Manuscripts</h2>
          <Link href="/history" className="text-xs font-semibold text-accent-600 hover:text-accent-700">
            View All History &rarr;
          </Link>
        </div>

        {papers.length === 0 ? (
          <div className="text-center py-16 px-4">
            <FileText className="w-12 h-12 text-slate-300 mx-auto mb-3" />
            <h3 className="text-sm font-bold text-navy-900">No manuscripts uploaded yet</h3>
            <p className="text-xs text-slate-500 max-w-sm mx-auto mt-1 mb-6">
              Upload your research paper (PDF or DOCX) to get a multi-module technical review and publication readiness report.
            </p>
            <Link
              href="/upload"
              className="inline-flex items-center space-x-2 px-5 py-2.5 rounded-xl text-xs font-semibold text-white bg-navy-800 hover:bg-navy-900 transition-colors"
            >
              <Upload className="w-3.5 h-3.5" />
              <span>Upload First Paper</span>
            </Link>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-slate-200 text-left text-xs">
              <thead className="bg-slate-50 text-slate-600 font-semibold uppercase tracking-wider">
                <tr>
                  <th className="px-6 py-3">Manuscript Title</th>
                  <th className="px-6 py-3">Format</th>
                  <th className="px-6 py-3">Uploaded</th>
                  <th className="px-6 py-3">Readiness Category</th>
                  <th className="px-6 py-3 text-right">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 bg-white">
                {papers.slice(0, 8).map((p) => {
                  const historyItem = history.find((h) => h.paper_id === p.id);
                  const score = historyItem?.readiness_score;
                  const cat = historyItem?.readiness_category || 'In Progress';

                  return (
                    <tr key={p.id} className="hover:bg-slate-50/80 transition-colors">
                      <td className="px-6 py-4 font-medium text-navy-900 max-w-xs truncate">
                        <Link href={`/analysis?id=${p.id}`} className="hover:text-accent-600">
                          {p.title || p.filename}
                        </Link>
                      </td>
                      <td className="px-6 py-4 uppercase text-slate-500 font-medium">
                        {p.file_type}
                      </td>
                      <td className="px-6 py-4 text-slate-500">
                        {new Date(p.created_at).toLocaleDateString()}
                      </td>
                      <td className="px-6 py-4">
                        <span
                          className={`inline-flex items-center px-2.5 py-1 rounded-full text-[11px] font-semibold ${
                            score && score >= 80
                              ? 'bg-emerald-50 text-emerald-700'
                              : score && score >= 60
                              ? 'bg-amber-50 text-amber-700'
                              : 'bg-blue-50 text-blue-700'
                          }`}
                        >
                          {score ? `${score}% — ${cat}` : 'Analyzing...'}
                        </span>
                      </td>
                      <td className="px-6 py-4 text-right">
                        <Link
                          href={`/analysis?id=${p.id}`}
                          className="inline-flex items-center space-x-1 text-accent-600 font-semibold hover:text-accent-700"
                        >
                          <span>Open Report</span>
                          <ArrowRight className="w-3.5 h-3.5" />
                        </Link>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
