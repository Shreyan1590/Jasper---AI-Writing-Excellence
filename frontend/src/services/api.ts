import axios from 'axios';

const BACKEND = 'http://127.0.0.1:5123';

const api = axios.create({
    baseURL: BACKEND,
    timeout: 120_000,
    headers: { 'Content-Type': 'application/json' },
});

// ── Retry interceptor (3 attempts) ──────────────────────────────
api.interceptors.response.use(undefined, async (error) => {
    const cfg = error.config;
    if (!cfg || cfg._retryCount >= 3) return Promise.reject(error);
    cfg._retryCount = (cfg._retryCount ?? 0) + 1;
    await new Promise((r) => setTimeout(r, 1000 * cfg._retryCount));
    return api(cfg);
});

// ── Response types ──────────────────────────────────────────────
export interface GrammarChange {
    type: string;
    message: string;
    original: string;
    suggestions: string[];
    position: number;
}

export interface GrammarResult {
    original: string;
    corrected: string;
    changes: GrammarChange[];
}

export interface AIAnalysis {
    lexical_diversity: number;
    sentence_length_variance: number;
    avg_sentence_length: number;
    pattern_matches: number;
}

export interface AIDetectResult {
    ai_score: number;
    is_ai_generated: boolean;
    analysis: AIAnalysis;
}

export interface PlagiarismMatch {
    phrase: string;
    position: number;
    length: number;
}

export interface PlagiarismResult {
    plagiarism_score: number;
    originality_score: number;
    matches: PlagiarismMatch[];
}

// ── Service methods ─────────────────────────────────────────────
const apiService = {
    health: () => api.get<{ status: string }>('/api/health'),

    humanize: (text: string) =>
        api.post<{ result: string }>('/api/humanize', { text }),

    summarize: (text: string, max_length: number) =>
        api.post<{ result: string }>('/api/summarize', { text, max_length }),

    paraphrase: (text: string, variations: number) =>
        api.post<{ result: string[] }>('/api/paraphrase', { text, variations }),

    grammar: (text: string) =>
        api.post<GrammarResult>('/api/grammar', { text }),

    aiDetect: (text: string) =>
        api.post<AIDetectResult>('/api/ai-detect', { text }),

    plagiarism: (text: string) =>
        api.post<PlagiarismResult>('/api/plagiarism', { text }),

    detectPlagiarism: (text: string) =>
        api.post('/api/detect/plagiarism', { text }),

    detectAI: (text: string) =>
        api.post('/api/detect/ai', { text }),

    detectHybrid: (text: string) =>
        api.post('/api/detect/hybrid', { text }),

    upload: (file: File) => {
        const fd = new FormData();
        fd.append('file', file);
        return api.post<{ text: string; filename: string }>('/api/upload', fd, {
            headers: { 'Content-Type': 'multipart/form-data' },
        });
    },

    getBackendUrl: async () => BACKEND,
};

export default apiService;
