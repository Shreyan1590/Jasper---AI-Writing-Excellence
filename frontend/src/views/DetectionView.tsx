import { useState } from 'react';
import { useToast } from '../components/Toast';
import Button from '../components/Button';
import apiService from '../services/api';

interface DetectionResults {
    plagiarism?: {
        plagiarism_score: number;
        plagiarism_level: string;
        matched_sentences: Array<{
            input_sentence: string;
            matched_source: string;
            similarity: number;
            source_url?: string;
        }>;
        corpus_size: number;
        method: string;
        note?: string;
    };
    ai_detection?: {
        ai_probability: number;
        ai_confidence: string;
        perplexity?: number;
        burstiness?: number;
        method: string;
        details?: {
            perplexity_score: number;
            burstiness_score: number;
            classifier_score: number;
        };
    };
}

export default function DetectionView() {
    const [inputText, setInputText] = useState('');
    const [detectionType, setDetectionType] = useState<'plagiarism' | 'ai' | 'both'>('both');
    const [results, setResults] = useState<DetectionResults | null>(null);
    const [isLoading, setIsLoading] = useState(false);
    const { showToast } = useToast();

    const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
        const file = e.target.files?.[0];
        if (!file) return;

        if (file.size > 10 * 1024 * 1024) {
            showToast('File too large. Max 10MB', 'error');
            return;
        }

        try {
            setIsLoading(true);
            const formData = new FormData();
            formData.append('file', file);

            const response = await fetch(`${await apiService.getBackendUrl()}/api/upload/extract`, {
                method: 'POST',
                body: formData,
            });

            if (!response.ok) throw new Error('Upload failed');

            const data = await response.json();
            setInputText(data.text);
            showToast(`Loaded ${file.name}`, 'success');
        } catch (error: any) {
            showToast(error.message || 'Upload failed', 'error');
        } finally {
            setIsLoading(false);
        }
    };

    const handleDetect = async () => {
        if (!inputText.trim()) {
            showToast('Please enter text to analyze', 'warning');
            return;
        }

        if (inputText.length < 50) {
            showToast('Text too short. Minimum 50 characters', 'warning');
            return;
        }

        try {
            setIsLoading(true);
            setResults(null);

            if (detectionType === 'plagiarism') {
                const res = await apiService.detectPlagiarism(inputText);
                setResults({ plagiarism: res.data });
            } else if (detectionType === 'ai') {
                const res = await apiService.detectAI(inputText);
                setResults({ ai_detection: res.data });
            } else {
                const res = await apiService.detectHybrid(inputText);
                setResults(res.data);
            }

            showToast('Analysis complete', 'success');
        } catch (error: any) {
            showToast(error.response?.data?.detail || 'Detection failed', 'error');
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="animate-fade">
            <div className="mb-6">
                <h1>AI + Plagiarism Detection</h1>
                <p className="text-secondary">Real similarity and AI probability analysis</p>
            </div>

            <div className="grid gap-4">
                {/* Input Card */}
                <div className="card">
                    <div className="card-header">
                        <h2 className="card-title">Input Text</h2>
                        <label className="btn btn-secondary btn-sm" style={{ cursor: 'pointer' }}>
                            <input
                                type="file"
                                accept=".txt,.pdf,.docx"
                                onChange={handleFileUpload}
                                style={{ display: 'none' }}
                            />
                            📁 Load File
                        </label>
                    </div>
                    <div className="input-group">
                        <textarea
                            className="input textarea"
                            value={inputText}
                            onChange={(e) => setInputText(e.target.value)}
                            placeholder="Paste text or load file (PDF, DOCX, TXT)..."
                            rows={10}
                        />
                        <p className="text-secondary" style={{ fontSize: 'var(--text-xs)' }}>
                            {inputText.length} characters
                        </p>
                    </div>
                </div>

                {/* Options Card */}
                <div className="card">
                    <div className="flex items-center justify-between">
                        <div className="input-group" style={{ marginBottom: 0, flex: 1 }}>
                            <label className="input-label">Detection Type</label>
                            <select
                                className="input"
                                value={detectionType}
                                onChange={(e) => setDetectionType(e.target.value as any)}
                            >
                                <option value="both">Both (Plagiarism + AI)</option>
                                <option value="plagiarism">Plagiarism Only</option>
                                <option value="ai">AI Detection Only</option>
                            </select>
                        </div>
                        <Button
                            variant="primary"
                            size="lg"
                            onClick={handleDetect}
                            loading={isLoading}
                        >
                            🔍 Analyze
                        </Button>
                    </div>
                </div>

                {/* Results */}
                {results && (
                    <div className="grid gap-4">
                        {results.plagiarism && (
                            <div className="card">
                                <h2 className="card-title mb-4">📄 Plagiarism Analysis</h2>

                                <div className="flex items-center justify-between mb-6" style={{ padding: 'var(--space-6)', background: 'var(--surface)', borderRadius: 'var(--radius-md)' }}>
                                    <div style={{ textAlign: 'center', flex: 1 }}>
                                        <div style={{ fontSize: '48px', fontWeight: 700, color: getSeverityColor(results.plagiarism.plagiarism_score) }}>
                                            {results.plagiarism.plagiarism_score}%
                                        </div>
                                        <div style={{ fontSize: 'var(--text-base)', color: 'var(--text-secondary)', marginTop: 'var(--space-2)' }}>
                                            {results.plagiarism.plagiarism_level} Similarity
                                        </div>
                                        <div className="badge badge-primary" style={{ marginTop: 'var(--space-2)' }}>
                                            {results.plagiarism.method}
                                        </div>
                                    </div>
                                </div>

                                {results.plagiarism.note && (
                                    <div style={{ background: 'var(--primary-light)', padding: 'var(--space-4)', borderRadius: 'var(--radius-sm)', marginBottom: 'var(--space-4)', fontSize: 'var(--text-sm)' }}>
                                        ℹ️ {results.plagiarism.note}
                                    </div>
                                )}

                                {results.plagiarism.matched_sentences.length > 0 && (
                                    <div>
                                        <h3 style={{ fontSize: 'var(--text-lg)', marginBottom: 'var(--space-4)' }}>
                                            Matched Sentences ({results.plagiarism.matched_sentences.length})
                                        </h3>
                                        <div className="grid gap-4">
                                            {results.plagiarism.matched_sentences.map((match, i) => (
                                                <div key={i} className="card" style={{ background: 'var(--surface)' }}>
                                                    <div className="badge badge-warning" style={{ marginBottom: 'var(--space-2)' }}>
                                                        {(match.similarity * 100).toFixed(1)}% similar
                                                    </div>
                                                    <p style={{ marginBottom: 'var(--space-2)', lineHeight: 1.6 }}>
                                                        "{match.input_sentence}"
                                                    </p>
                                                    <p className="text-secondary" style={{ fontSize: 'var(--text-sm)' }}>
                                                        Source: <strong style={{ color: 'var(--primary)' }}>{match.matched_source}</strong>
                                                        {match.source_url && (
                                                            <a href={match.source_url} target="_blank" rel="noopener noreferrer" style={{ marginLeft: 'var(--space-2)', color: 'var(--primary)' }}>
                                                                🔗
                                                            </a>
                                                        )}
                                                    </p>
                                                </div>
                                            ))}
                                        </div>
                                    </div>
                                )}

                                <p className="text-secondary" style={{ fontSize: 'var(--text-xs)', marginTop: 'var(--space-4)', textAlign: 'center' }}>
                                    Corpus size: {results.plagiarism.corpus_size} documents
                                </p>
                            </div>
                        )}

                        {results.ai_detection && (
                            <div className="card">
                                <h2 className="card-title mb-4">🤖 AI Content Detection</h2>

                                <div className="flex items-center justify-between mb-6" style={{ padding: 'var(--space-6)', background: 'var(--surface)', borderRadius: 'var(--radius-md)' }}>
                                    <div style={{ textAlign: 'center', flex: 1 }}>
                                        <div style={{ fontSize: '48px', fontWeight: 700, color: getAIColor(results.ai_detection.ai_probability) }}>
                                            {results.ai_detection.ai_probability}%
                                        </div>
                                        <div style={{ fontSize: 'var(--text-base)', color: 'var(--text-secondary)', marginTop: 'var(--space-2)' }}>
                                            {results.ai_detection.ai_confidence} Confidence
                                        </div>
                                        <div className="badge badge-primary" style={{ marginTop: 'var(--space-2)' }}>
                                            {results.ai_detection.method}
                                        </div>
                                    </div>
                                </div>

                                {results.ai_detection.details && (
                                    <div className="grid grid-cols-4 gap-4">
                                        <div className="card" style={{ background: 'var(--surface)', textAlign: 'center' }}>
                                            <div style={{ fontSize: 'var(--text-2xl)', fontWeight: 700, color: 'var(--primary)' }}>
                                                {results.ai_detection.details.perplexity_score}%
                                            </div>
                                            <div className="text-secondary" style={{ fontSize: 'var(--text-xs)', marginTop: 'var(--space-1)' }}>
                                                Perplexity Score
                                            </div>
                                        </div>
                                        <div className="card" style={{ background: 'var(--surface)', textAlign: 'center' }}>
                                            <div style={{ fontSize: 'var(--text-2xl)', fontWeight: 700, color: 'var(--primary)' }}>
                                                {results.ai_detection.details.burstiness_score}%
                                            </div>
                                            <div className="text-secondary" style={{ fontSize: 'var(--text-xs)', marginTop: 'var(--space-1)' }}>
                                                Burstiness Score
                                            </div>
                                        </div>
                                        <div className="card" style={{ background: 'var(--surface)', textAlign: 'center' }}>
                                            <div style={{ fontSize: 'var(--text-2xl)', fontWeight: 700, color: 'var(--primary)' }}>
                                                {results.ai_detection.details.classifier_score}%
                                            </div>
                                            <div className="text-secondary" style={{ fontSize: 'var(--text-xs)', marginTop: 'var(--space-1)' }}>
                                                Classifier Score
                                            </div>
                                        </div>
                                        <div className="card" style={{ background: 'var(--surface)', textAlign: 'center' }}>
                                            <div style={{ fontSize: 'var(--text-2xl)', fontWeight: 700, color: 'var(--primary)' }}>
                                                {results.ai_detection.perplexity?.toFixed(1)}
                                            </div>
                                            <div className="text-secondary" style={{ fontSize: 'var(--text-xs)', marginTop: 'var(--space-1)' }}>
                                                Perplexity
                                            </div>
                                        </div>
                                    </div>
                                )}
                            </div>
                        )}
                    </div>
                )}
            </div>
        </div>
    );
}

function getSeverityColor(score: number): string {
    if (score < 10) return 'var(--success)';
    if (score < 25) return 'var(--warning)';
    return 'var(--error)';
}

function getAIColor(prob: number): string {
    if (prob > 70) return 'var(--error)';
    if (prob > 40) return 'var(--warning)';
    return 'var(--success)';
}
