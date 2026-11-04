import axios from 'axios';
import { AuthResponse, Paper, ExtractedContent, PaperAnalysisState } from '@/types';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Attach JWT token from localStorage to outgoing requests
apiClient.interceptors.request.use(
  (config) => {
    if (typeof window !== 'undefined') {
      const token = localStorage.getItem('researchiq_token');
      if (token && config.headers) {
        config.headers.Authorization = `Bearer ${token}`;
      }
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Redirect to login on 401 Unauthorized
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401 && typeof window !== 'undefined') {
      if (!window.location.pathname.includes('/login') && !window.location.pathname.includes('/register')) {
        localStorage.removeItem('researchiq_token');
        localStorage.removeItem('researchiq_user');
        window.location.href = '/login';
      }
    }
    return Promise.reject(error);
  }
);

export const authService = {
  async register(data: { email: string; full_name: string; password: string }) {
    const res = await apiClient.post('/api/auth/register', data);
    return res.data;
  },

  async login(formData: FormData) {
    const res = await apiClient.post<AuthResponse>('/api/auth/login', formData, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    });
    if (res.data.access_token) {
      localStorage.setItem('researchiq_token', res.data.access_token);
      localStorage.setItem('researchiq_user', JSON.stringify(res.data.user));
    }
    return res.data;
  },

  logout() {
    if (typeof window !== 'undefined') {
      localStorage.removeItem('researchiq_token');
      localStorage.removeItem('researchiq_user');
      window.location.href = '/login';
    }
  },

  getCurrentUser() {
    if (typeof window !== 'undefined') {
      const userStr = localStorage.getItem('researchiq_user');
      return userStr ? JSON.parse(userStr) : null;
    }
    return null;
  },

  isAuthenticated(): boolean {
    if (typeof window !== 'undefined') {
      return !!localStorage.getItem('researchiq_token');
    }
    return false;
  },
};

export const paperService = {
  async uploadPaper(file: File, onProgress?: (percent: number) => void): Promise<Paper> {
    const formData = new FormData();
    formData.append('file', file);

    const res = await apiClient.post<Paper>('/api/papers/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
      onUploadProgress: (progressEvent) => {
        if (progressEvent.total && onProgress) {
          const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total);
          onProgress(percentCompleted);
        }
      },
    });
    return res.data;
  },

  async getPapers(): Promise<{ papers: Paper[]; total: number }> {
    const res = await apiClient.get('/api/papers');
    return res.data;
  },

  async getPaper(paperId: number): Promise<Paper> {
    const res = await apiClient.get<Paper>(`/api/papers/${paperId}`);
    return res.data;
  },

  async getExtractedContent(paperId: number): Promise<ExtractedContent> {
    const res = await apiClient.get<ExtractedContent>(`/api/papers/${paperId}/extracted`);
    return res.data;
  },

  async deletePaper(paperId: number): Promise<void> {
    await apiClient.delete(`/api/papers/${paperId}`);
  },
};

export const analysisService = {
  async getResults(paperId: number): Promise<PaperAnalysisState> {
    const res = await apiClient.get<PaperAnalysisState>(`/api/analysis/${paperId}/results`);
    return res.data;
  },

  async getHistory(): Promise<{ history: any[]; total: number }> {
    const res = await apiClient.get('/api/analysis/history');
    return res.data;
  },

  async triggerFeature(paperId: number, featureSlug: string) {
    const res = await apiClient.post(`/api/analysis/${paperId}/${featureSlug}`);
    return res.data;
  },

  async downloadReport(paperId: number): Promise<Blob> {
    const res = await apiClient.get(`/api/analysis/${paperId}/report`, {
      responseType: 'blob',
    });
    return res.data;
  },
};
