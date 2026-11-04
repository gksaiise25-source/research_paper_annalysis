export interface User {
  id: number;
  email: string;
  full_name: string;
  is_active: boolean;
  created_at: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user: User;
}

export type AnalysisStatus = 'pending' | 'processing' | 'completed' | 'failed';

export interface Paper {
  id: number;
  title: string | null;
  filename: string;
  file_type: string;
  file_size_bytes: number | null;
  page_count: number | null;
  status: AnalysisStatus;
  created_at: string;
}

export interface ExtractedContent {
  abstract: string | null;
  introduction: string | null;
  methodology: string | null;
  conclusion: string | null;
  keywords: string[] | null;
  word_count: number | null;
  figures_count: number;
  tables_count: number;
}

export interface TechnicalReviewResult {
  overall_score: number;
  sections_present: string[];
  sections_missing: string[];
  section_analyses: Record<string, {
    present: boolean;
    score: number;
    word_count: number;
    feedback: string[];
    issues: string[];
    strengths: string[];
  }>;
  strengths: string[];
  weaknesses: string[];
  word_count: number;
  recommendations: string[];
}

export interface SimilarPaper {
  title: string;
  abstract_snippet: string;
  year?: number;
  doi?: string;
  venue?: string;
  citations?: number;
  similarity_percentage: number;
  overlap_level: string;
}

export interface NoveltyResult {
  overall_novelty_score: number;
  assessment: string;
  similar_papers: SimilarPaper[];
  research_gaps: string[];
  novelty_indicators: string[];
  papers_compared: number;
  data_source: string;
}

export interface CitationIssue {
  type: string;
  description: string;
  citation?: string;
  reference_index?: number;
  reference_snippet?: string;
}

export interface CitationResult {
  detected_style: string;
  total_references: number;
  total_intext_citations: number;
  issues: {
    cross_reference_issues: CitationIssue[];
    doi_issues: CitationIssue[];
    duplicates: CitationIssue[];
    incomplete_references: CitationIssue[];
  };
  total_issue_count: number;
  citation_score: number;
  sample_references: string[];
  recommendations: string[];
}

export interface GrammarSuggestion {
  type: string;
  original: string;
  suggestion: string;
  reason: string;
  severity: 'minor' | 'moderate' | 'major';
}

export interface GrammarResult {
  grammar_score: number;
  readability_score: { score: number | null; level: string };
  academic_tone_score: number;
  total_suggestions: number;
  suggestions: GrammarSuggestion[];
  summary: {
    wordy_phrases_found: number;
    informal_words_found: number;
    passive_voice_issues: number;
    sentence_length_issues: number;
    repeated_words: number;
  };
  recommendations: string[];
}

export interface PlagiarismResult {
  overall_risk_level: 'Minimal Risk' | 'Low Risk' | 'Moderate Risk' | 'High Risk';
  similarity_score: number;
  originality_indicator: number;
  internal_repetition: {
    total_paragraphs: number;
    duplicate_paragraphs: number;
    duplication_rate: number;
    duplicates: Array<{ paragraph_index: number; duplicate_of: number; snippet: string }>;
  };
  external_comparisons: Array<{
    source_title: string;
    source: string;
    similarity_percentage: number;
    risk_level: string;
  }>;
  ngram_analysis: {
    total_5grams?: number;
    unique_5grams?: number;
    uniqueness_ratio?: number;
    interpretation?: string;
  };
  disclaimer: string;
  recommendations: string[];
}

export interface FigureTableResult {
  validation_score: number;
  summary: {
    detected_figures_count: number;
    detected_tables_count: number;
    figure_issues_count: number;
    table_issues_count: number;
  };
  figure_captions: Array<{ type: string; number: string; caption: string }>;
  table_captions: Array<{ type: string; number: string; caption: string }>;
  issues: Array<{
    element: string;
    severity: 'low' | 'medium' | 'high';
    type: string;
    message: string;
  }>;
  recommendations: string[];
}

export interface ReviewerCommentsResult {
  overall_assessment: string;
  recommendation: string;
  paper_strengths: string[];
  paper_weaknesses: string[];
  major_revisions: string[];
  minor_revisions: string[];
  methodology_critique: string;
  experimental_suggestions: string;
  conclusion_improvements: string;
  generator_mode: string;
}

export interface JournalRecommendation {
  name: string;
  type: string;
  publisher: string;
  website: string;
  issn?: string;
  is_oa?: boolean;
  scope: string;
  suitability_score: number;
  matching_explanation: string;
  indexing_status: string;
}

export interface JournalResult {
  search_query_used: string;
  total_venues_found: number;
  recommendations: JournalRecommendation[];
  disclaimer: string;
}

export interface PatentabilityResult {
  overall_patentability_score: number;
  readiness_tier: string;
  criteria_breakdown: {
    industrial_applicability: { score: number; detected_elements: string[]; status: string };
    inventive_step_novelty: { score: number; claims_found: number; status: string };
    technical_enablement: { score: number; status: string };
  };
  eligibility_concerns: string[];
  potential_patent_claims: string[];
  disclaimer: string;
  recommended_next_steps: string[];
}

export interface ReadinessCategoryScore {
  score: number | null;
  weight?: number;
  status: string;
  label?: string;
}

export interface ReadinessResult {
  overall_score: number;
  readiness_category: 'Ready for Submission' | 'Minor Revision' | 'Major Revision' | 'Not Ready for Submission';
  summary_assessment: string;
  weights_normalization_factor: number;
  category_scores: Record<string, ReadinessCategoryScore>;
  strengths: string[];
  weaknesses: string[];
  priority_improvements: string[];
  disclaimer: string;
}

export interface FullPaperAnalyses {
  technical_review?: { status: AnalysisStatus; score: number | null; result_data: TechnicalReviewResult };
  novelty?: { status: AnalysisStatus; score: number | null; result_data: NoveltyResult };
  citations?: { status: AnalysisStatus; score: number | null; result_data: CitationResult };
  grammar?: { status: AnalysisStatus; score: number | null; result_data: GrammarResult };
  plagiarism?: { status: AnalysisStatus; score: number | null; result_data: PlagiarismResult };
  figures_tables?: { status: AnalysisStatus; score: number | null; result_data: FigureTableResult };
  reviewer_comments?: { status: AnalysisStatus; score: number | null; result_data: ReviewerCommentsResult };
  journals?: { status: AnalysisStatus; score: number | null; result_data: JournalResult };
  patentability?: { status: AnalysisStatus; score: number | null; result_data: PatentabilityResult };
  readiness?: { status: AnalysisStatus; score: number | null; result_data: ReadinessResult };
}

export interface PaperAnalysisState {
  paper_id: number;
  title: string | null;
  status: AnalysisStatus;
  analyses: FullPaperAnalyses;
}
