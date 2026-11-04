'use client';

import React, { useEffect, useState } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { BookOpen, FileUp, History, LayoutDashboard, LogOut, User } from 'lucide-react';
import { authService } from '@/services/api';

export default function Navbar() {
  const pathname = usePathname();
  const [currentUser, setCurrentUser] = useState<any>(null);
  const [isMounted, setIsMounted] = useState(false);

  useEffect(() => {
    setIsMounted(true);
    setCurrentUser(authService.getCurrentUser());
  }, [pathname]);

  if (!isMounted) return null;

  const isAuthPage = pathname === '/login' || pathname === '/register';
  if (isAuthPage) return null;

  return (
    <header className="sticky top-0 z-50 bg-white/90 backdrop-blur-md border-b border-slate-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          {/* Logo & Brand */}
          <Link href="/" className="flex items-center space-x-3 group">
            <div className="w-10 h-10 rounded-xl bg-navy-800 text-white flex items-center justify-center shadow-md group-hover:bg-navy-900 transition-colors">
              <BookOpen className="w-5 h-5 text-accent-400" />
            </div>
            <div>
              <span className="text-xl font-bold tracking-tight text-navy-900">
                Research<span className="text-accent-600">IQ</span>
              </span>
              <span className="block text-[10px] uppercase tracking-wider font-semibold text-slate-500">
                Peer Review & Publication AI
              </span>
            </div>
          </Link>

          {/* Navigation Links */}
          <nav className="hidden md:flex items-center space-x-1">
            <Link
              href="/dashboard"
              className={`flex items-center space-x-1.5 px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                pathname === '/dashboard'
                  ? 'bg-navy-50 text-navy-800 font-semibold'
                  : 'text-slate-600 hover:text-navy-900 hover:bg-slate-50'
              }`}
            >
              <LayoutDashboard className="w-4 h-4" />
              <span>Dashboard</span>
            </Link>

            <Link
              href="/upload"
              className={`flex items-center space-x-1.5 px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                pathname === '/upload'
                  ? 'bg-navy-50 text-navy-800 font-semibold'
                  : 'text-slate-600 hover:text-navy-900 hover:bg-slate-50'
              }`}
            >
              <FileUp className="w-4 h-4" />
              <span>Upload Paper</span>
            </Link>

            <Link
              href="/history"
              className={`flex items-center space-x-1.5 px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                pathname === '/history'
                  ? 'bg-navy-50 text-navy-800 font-semibold'
                  : 'text-slate-600 hover:text-navy-900 hover:bg-slate-50'
              }`}
            >
              <History className="w-4 h-4" />
              <span>Evaluation History</span>
            </Link>
          </nav>

          {/* User Profile / Auth buttons */}
          <div className="flex items-center space-x-3">
            {currentUser ? (
              <div className="flex items-center space-x-3">
                <div className="flex items-center space-x-2 pl-3 pr-2 py-1.5 bg-slate-100 rounded-full text-xs font-medium text-slate-700">
                  <User className="w-3.5 h-3.5 text-navy-700" />
                  <span className="max-w-[120px] truncate">{currentUser.full_name || currentUser.email}</span>
                </div>
                <button
                  onClick={() => authService.logout()}
                  className="p-2 text-slate-500 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                  title="Sign Out"
                >
                  <LogOut className="w-4 h-4" />
                </button>
              </div>
            ) : (
              <div className="flex items-center space-x-2">
                <Link
                  href="/login"
                  className="px-4 py-2 text-sm font-medium text-navy-800 hover:bg-slate-100 rounded-lg transition-colors"
                >
                  Sign In
                </Link>
                <Link
                  href="/register"
                  className="px-4 py-2 text-sm font-medium text-white bg-navy-800 hover:bg-navy-900 rounded-lg shadow-sm transition-colors"
                >
                  Get Started
                </Link>
              </div>
            )}
          </div>
        </div>
      </div>
    </header>
  );
}
