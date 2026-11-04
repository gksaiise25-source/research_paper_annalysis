'use client';

import React, { useState, useRef } from 'react';
import { useRouter } from 'next/navigation';
import {
  UploadCloud,
  FileCheck,
  AlertCircle,
  Loader2,
  FileText,
  ShieldCheck,
  ArrowRight,
  Info,
} from 'lucide-react';
import { paperService, authService } from '@/services/api';

export default function UploadPage() {
  const router = useRouter();
  const fileInputRef = useRef<HTMLInputElement>(null);

  const [dragActive, setDragActive] = useState(false);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [uploadProgress, setUploadProgress] = useState<number>(0);
  const [isUploading, setIsUploading] = useState(false);
  const [statusMessage, setStatusMessage] = useState<string>('');
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const validateFile = (file: File): boolean => {
    const validExtensions = ['.pdf', '.docx'];
    const ext = file.name.substring(file.name.lastIndexOf('.')).toLowerCase();

    if (!validExtensions.includes(ext)) {
      setErrorMessage('Unsupported file format. Please upload a PDF (.pdf) or Word document (.docx).');
      return false;
    }

    if (file.size > 50 * 1024 * 1024) {
      setErrorMessage('File size exceeds the 50MB limit.');
      return false;
    }

    setErrorMessage(null);
    return true;
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const file = e.dataTransfer.files[0];
      if (validateFile(file)) {
        setSelectedFile(file);
      }
    }
  };

  const handleFileInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0];
      if (validateFile(file)) {
        setSelectedFile(file);
      }
    }
  };

  const handleUploadAndAnalyze = async () => {
    if (!selectedFile) return;

    if (!authService.isAuthenticated()) {
      router.push('/login');
      return;
    }

    setIsUploading(true);
    setUploadProgress(10);
    setStatusMessage('Uploading manuscript to secure processing sandbox...');

    try {
      const paper = await paperService.uploadPaper(selectedFile, (percent) => {
        setUploadProgress(Math.min(90, Math.max(15, percent)));
        if (percent >= 100) {
          setStatusMessage('Extracting document sections, tables, and references...');
        }
      });

      setUploadProgress(100);
      setStatusMessage('Manuscript successfully ingested. Initializing 10 AI evaluation modules...');

      // Redirect to analysis dashboard
      setTimeout(() => {
        router.push(`/analysis?id=${paper.id}`);
      }, 1200);
    } catch (err: any) {
      console.error(err);
      setIsUploading(false);
      setErrorMessage(
        err.response?.data?.detail || 'Failed to upload manuscript. Please try again.'
      );
    }
  };

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 py-12">
      <div className="text-center mb-10">
        <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-blue-50 border border-blue-200 text-blue-800 text-xs font-semibold mb-3">
          <ShieldCheck className="w-4 h-4 text-accent-600" />
          <span>Real Document Extraction & Verification</span>
        </div>
        <h1 className="text-3xl font-extrabold text-navy-950 sm:text-4xl">
          Submit Manuscript for Evaluation
        </h1>
        <p className="mt-2 text-sm text-slate-600 max-w-xl mx-auto">
          Upload your research paper to trigger the full 10-module peer review and publication readiness pipeline.
        </p>
      </div>

      {errorMessage && (
        <div className="mb-6 p-4 rounded-xl bg-red-50 border border-red-200 flex items-start space-x-3 text-red-700 text-xs">
          <AlertCircle className="w-4 h-4 flex-shrink-0 mt-0.5" />
          <span>{errorMessage}</span>
        </div>
      )}

      {/* Upload Box */}
      <div className="bg-white border border-slate-200 rounded-3xl p-8 shadow-sm">
        <div
          onDragEnter={handleDrag}
          onDragLeave={handleDrag}
          onDragOver={handleDrag}
          onDrop={handleDrop}
          onClick={() => !isUploading && fileInputRef.current?.click()}
          className={`border-2 border-dashed rounded-2xl p-10 text-center transition-all cursor-pointer ${
            dragActive
              ? 'border-accent-500 bg-accent-50/50'
              : 'border-slate-300 hover:border-navy-700 bg-slate-50/60'
          } ${isUploading ? 'pointer-events-none opacity-60' : ''}`}
        >
          <input
            ref={fileInputRef}
            type="file"
            accept=".pdf,.docx"
            onChange={handleFileInput}
            className="hidden"
          />

          <div className="w-16 h-16 rounded-2xl bg-white border border-slate-200 shadow-sm flex items-center justify-center mx-auto mb-4 text-navy-800">
            <UploadCloud className="w-8 h-8 text-accent-600" />
          </div>

          <h3 className="text-base font-bold text-navy-950 mb-1">
            {selectedFile ? selectedFile.name : 'Choose a file or drag & drop here'}
          </h3>

          <p className="text-xs text-slate-500 max-w-md mx-auto mb-4">
            Supports standard academic research formats: PDF (.pdf) or Microsoft Word (.docx). Max file size: 50MB.
          </p>

          {!selectedFile ? (
            <button
              type="button"
              className="px-5 py-2 rounded-xl text-xs font-semibold text-white bg-navy-800 hover:bg-navy-900 transition-colors shadow-sm"
            >
              Browse Files
            </button>
          ) : (
            <div className="inline-flex items-center space-x-2 text-xs font-semibold text-emerald-700 bg-emerald-50 px-3 py-1.5 rounded-full border border-emerald-200">
              <FileCheck className="w-4 h-4" />
              <span>{(selectedFile.size / (1024 * 1024)).toFixed(2)} MB — Ready to analyze</span>
            </div>
          )}
        </div>

        {/* Progress & Upload Button */}
        {isUploading && (
          <div className="mt-6 space-y-3">
            <div className="flex justify-between text-xs font-semibold text-slate-700">
              <span className="flex items-center space-x-2">
                <Loader2 className="w-3.5 h-3.5 animate-spin text-accent-600" />
                <span>{statusMessage}</span>
              </span>
              <span>{uploadProgress}%</span>
            </div>
            <div className="w-full bg-slate-100 rounded-full h-2.5 overflow-hidden">
              <div
                className="bg-navy-800 h-2.5 rounded-full transition-all duration-300"
                style={{ width: `${uploadProgress}%` }}
              ></div>
            </div>
          </div>
        )}

        <div className="mt-8 flex flex-col sm:flex-row justify-between items-center gap-4 pt-6 border-t border-slate-100">
          <div className="flex items-center space-x-2 text-xs text-slate-500">
            <Info className="w-4 h-4 text-slate-400" />
            <span>Documents are processed in memory and untrusted input is safely isolated.</span>
          </div>

          <button
            onClick={handleUploadAndAnalyze}
            disabled={!selectedFile || isUploading}
            className="w-full sm:w-auto inline-flex items-center justify-center space-x-2 px-8 py-3 rounded-xl text-sm font-semibold text-white bg-navy-800 hover:bg-navy-900 transition-colors shadow-md disabled:opacity-40 disabled:cursor-not-allowed"
          >
            {isUploading ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin" />
                <span>Processing Manuscript...</span>
              </>
            ) : (
              <>
                <span>Launch Comprehensive Evaluation</span>
                <ArrowRight className="w-4 h-4" />
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  );
}
