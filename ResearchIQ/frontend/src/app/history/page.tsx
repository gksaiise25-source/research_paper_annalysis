'use client';

import React, { useEffect, useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import {
  History,
  FileText,
  Search,
  Download,
  Trash2,
  ArrowRight,
  Loader2,
  AlertCircle,
  FileCheck2,
} from 'lucide-react';
import { analysisService, paperService, authService } from '@/services/api';

export default function HistoryPage() {
  const router = useRouter();
  const [historyItems, setHistoryItems] = useState<any[]>([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [isLoading, setIsLoading] = useState(true);
  const [deletingId, setDeletingId] = useState<number | null>(null);

  useEffect(() => {
    if (!authService.isAuthenticated()) {
      router.push('/login');
      return;
    }
    loadHistory();
  }, [router]);

  const loadHistory = async () => {
    setIsLoading(true);
    try {
      const res = await analysisService.getHistory();
      setHistoryItems(res.history || []);
    } catch (err) {
      console.error('Failed to load history:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleDelete = async (paperId: number, e: React.MouseEvent) => {
    e.stopPropagation();
    if (!confirm('Are you sure you want to delete this manuscript and its evaluation results?')) {
      return;
    }
    setDeletingId(paperId);
    try {
      await paperService.deletePaper(paperId);
      setHistoryItems((prev) => prev.filter((item) => item.paper_id !== paperId));
    } catch (err) {
      console.error('Failed to delete paper:', err);
      alert('Could not delete manuscript.');
    } finally {
      setDeletingId(null);
    }
  };

  const handleDownloadPDF = async (paperId: number, e: React.MouseEvent) => {
    e.stopPropagation();
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
      console.error('Download error:', err);
      alert('Report not yet available for this paper.');
    }
  };

  const filteredItems = historyItems.filter((item) => {
    const text = (item.title || item.filename || '').toLowerCase();
    return text.includes(searchQuery.toLowerCase());
  });

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 mb-8">
        <div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-navy-950">Evaluation History</h1>
          <p className="text-xs sm:text-sm text-slate-500 mt-1">
            Access previous manuscript analyses, review reports, and publication readiness scores.
          </p>
        </div>

        {/* Search Bar */}
        <div className="relative w-full sm:w-72">
          <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
            <Search className="h-4 w-4 text-slate-400" />
          </div>
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search manuscripts..."
            className="block w-full pl-9 pr-3 py-2 text-xs border border-slate-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-navy-800"
          />
        </div>
      </div>

      {isLoading ? (
        <div className="min-h-[50vh] flex flex-col items-center justify-center">
          <Loader2 className="w-8 h-8 animate-spin text-navy-800 mb-2" />
          <p className="text-xs text-slate-500">Loading evaluation archive...</p>
        </div>
      ) : filteredItems.length === 0 ? (
        <div className="bg-white border border-slate-200 rounded-3xl p-12 text-center">
          <History className="w-12 h-12 text-slate-300 mx-auto mb-3" />
          <h3 className="text-sm font-bold text-navy-950">No manuscript evaluations found</h3>
          <p className="text-xs text-slate-500 max-w-sm mx-auto mt-1 mb-6">
            Upload a research paper to generate multi-dimensional peer reviewer feedback and publication scores.
          </p>
          <Link
            href="/upload"
            className="inline-flex items-center space-x-2 px-5 py-2.5 rounded-xl text-xs font-semibold text-white bg-navy-800 hover:bg-navy-900 transition-colors"
          >
            <span>Upload New Manuscript</span>
          </Link>
        </div>
      ) : (
        <div className="bg-white border border-slate-200 rounded-2xl shadow-sm overflow-hidden">
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-slate-200 text-left text-xs">
              <thead className="bg-slate-50 text-slate-600 font-semibold uppercase tracking-wider">
                <tr>
                  <th className="px-6 py-3.5">Manuscript</th>
                  <th className="px-6 py-3.5">Date Analyzed</th>
                  <th className="px-6 py-3.5">Readiness Score</th>
                  <th className="px-6 py-3.5">Status</th>
                  <th className="px-6 py-3.5 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 bg-white">
                {filteredItems.map((item) => {
                  const score = item.readiness_score;
                  const cat = item.readiness_category || 'Processing';

                  return (
                    <tr
                      key={item.paper_id}
                      onClick={() => router.push(`/analysis?id=${item.paper_id}`)}
                      className="hover:bg-slate-50/80 cursor-pointer transition-colors"
                    >
                      <td className="px-6 py-4 font-semibold text-navy-950 max-w-sm">
                        <div className="truncate">{item.title || item.filename}</div>
                        <div className="text-[11px] font-normal text-slate-400 mt-0.5">
                          {item.filename}
                        </div>
                      </td>
                      <td className="px-6 py-4 text-slate-500 whitespace-nowrap">
                        {new Date(item.created_at).toLocaleDateString()}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span
                          className={`inline-flex items-center px-2.5 py-1 rounded-full text-[11px] font-bold ${
                            score && score >= 80
                              ? 'bg-emerald-50 text-emerald-700'
                              : score && score >= 60
                              ? 'bg-amber-50 text-amber-700'
                              : 'bg-blue-50 text-blue-700'
                          }`}
                        >
                          {score ? `${score}% — ${cat}` : 'Evaluating...'}
                        </span>
                      </td>
                      <td className="px-6 py-4 uppercase text-slate-500 font-medium">
                        {item.status}
                      </td>
                      <td className="px-6 py-4 text-right space-x-2 whitespace-nowrap">
                        <button
                          onClick={(e) => handleDownloadPDF(item.paper_id, e)}
                          title="Download PDF Report"
                          className="p-1.5 text-slate-500 hover:text-navy-900 hover:bg-slate-100 rounded-lg transition-colors"
                        >
                          <Download className="w-4 h-4" />
                        </button>
                        <button
                          onClick={(e) => handleDelete(item.paper_id, e)}
                          disabled={deletingId === item.paper_id}
                          title="Delete Manuscript"
                          className="p-1.5 text-slate-500 hover:text-rose-600 hover:bg-rose-50 rounded-lg transition-colors"
                        >
                          {deletingId === item.paper_id ? (
                            <Loader2 className="w-4 h-4 animate-spin text-rose-600" />
                          ) : (
                            <Trash2 className="w-4 h-4" />
                          )}
                        </button>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}
