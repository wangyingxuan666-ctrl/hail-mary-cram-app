// Use relative paths — Vite proxy handles forwarding to backend
const API_BASE = '';

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: { 'Content-Type': 'application/json', ...options?.headers },
    ...options,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || `HTTP ${res.status}`);
  }
  return res.json();
}

// Upload
export async function uploadFile(file: File, type: 'materials' | 'exams') {
  const form = new FormData();
  form.append('file', file);
  const res = await fetch(`${API_BASE}/api/upload/${type}`, {
    method: 'POST',
    body: form,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || `Upload failed`);
  }
  return res.json();
}

// Documents
export const getDocuments = () => request<{ documents: Document[]; total: number }>('/api/documents');
export const deleteDocument = (id: string) => request<{ status: string }>(`/api/documents/${id}`, { method: 'DELETE' });
export const rebuildIndex = () => request<{ status: string; chunk_count: number }>('/api/documents/rebuild-index', { method: 'POST' });

// Analysis
export const generateFrequency = (courseName = '') =>
  request('/api/analysis/frequency', { method: 'POST', body: JSON.stringify({ course_name: courseName }) });
export const getFrequency = () => request('/api/analysis/frequency');
export const generateStrategy = (courseName = '') =>
  request('/api/analysis/strategy', { method: 'POST', body: JSON.stringify({ course_name: courseName }) });
export const getStrategy = () => request('/api/analysis/strategy');

// Chat
export const startSession = (examPaper = '') =>
  request('/api/chat/start', { method: 'POST', body: JSON.stringify({ exam_paper: examPaper }) });
export const getSessions = () => request<Array<{ id: string; exam_paper: string; message_count: number; created_at: string }>>('/api/chat/sessions');
export const getChatHistory = (sessionId: string) => request(`/api/chat/${sessionId}/history`);
export const deleteChatSession = (sessionId: string) =>
  request(`/api/chat/sessions/${sessionId}`, { method: 'DELETE' });
export const explainTopic = (topic: string, includeRag = true) =>
  request('/api/chat/explain-topic', { method: 'POST', body: JSON.stringify({ topic, include_rag: includeRag }) });

// Memory
export const getMemoryStatus = () => request('/api/memory/status');
export const updateMemory = (topic: string, status: string, notes = '') =>
  request('/api/memory/update', { method: 'POST', body: JSON.stringify({ topic, status, notes }) });
export const getMemorySummary = () => request('/api/memory/summary');

// Export
export const exportSingleExam = (examYear = '') =>
  request('/api/export/single-exam', { method: 'POST', body: JSON.stringify(examYear) });
export const exportCrossYear = () =>
  request('/api/export/cross-year', { method: 'POST' });
export const exportGapPrediction = (year = '') =>
  request('/api/export/gap-prediction', { method: 'POST', body: JSON.stringify(year) });
export const listExports = () => request('/api/export/list');
export const getDownloadUrl = (filename: string) => `/api/export/download/${encodeURIComponent(filename)}`;

// SSE streaming
export function streamAskQuestion(
  sessionId: string,
  message: string,
  questionRef: string | null,
  onChunk: (text: string) => void,
  onDone: () => void,
  onError: (err: Error) => void,
): AbortController {
  const controller = new AbortController();
  fetch(`${API_BASE}/api/chat/send`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ session_id: sessionId, message, question_ref: questionRef }),
    signal: controller.signal,
  })
    .then(async (res) => {
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const reader = res.body?.getReader();
      if (!reader) throw new Error('No response body');
      const decoder = new TextDecoder();
      let buffer = '';
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');
        buffer = lines.pop() || '';
        for (const line of lines) {
          if (line.startsWith('data: ') && line !== 'data: [DONE]') {
            onChunk(line.slice(6));
          }
        }
      }
      onDone();
    })
    .catch((err) => {
      if (err.name !== 'AbortError') onError(err);
    });
  return controller;
}
