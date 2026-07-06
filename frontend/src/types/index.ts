export interface DocumentItem {
  id: string;
  filename: string;
  doc_type: 'material' | 'exam';
  page_count: number;
  chunk_count: number;
  content_preview: string;
  uploaded_at: string;
  processed: boolean;
}

export interface TopicFrequency {
  topic_name: string;
  years: string[];
  frequency_count: number;
  total_years: number;
  frequency_pct: number;
  priority: '🔴' | '🟠' | '🟡' | '🟢';
  related_questions: string[];
}

export interface FrequencyTable {
  course_name: string;
  total_exam_years: number;
  topics: TopicFrequency[];
  generated_at: string;
}

export interface ExamStrategy {
  questions: Record<string, unknown>[];
  best_combination: string;
  expected_total: string;
  skip_recommendation: string;
}

export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  question_ref?: string;
  timestamp: string;
}

export interface ChatSession {
  id: string;
  exam_paper: string;
  messages: ChatMessage[];
  created_at: string;
}

export interface MemoryEntry {
  topic: string;
  status: 'mastered' | 'confused' | 'learning';
  notes: string;
  last_reviewed: string;
}

export interface MemoryStatus {
  entries: MemoryEntry[];
  mastered_count: number;
  confused_count: number;
  total_topics: number;
}

export interface ExportItem {
  filename: string;
  size: number;
  created_at: string;
}
