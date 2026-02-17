import { useState } from 'react';
import ToolView from '../components/ToolView';
import { useToast } from '../components/Toast';
import apiService from '../services/api';

/* ================================================================
   HUMANIZE VIEW
   ================================================================ */
export function HumanizeView() {
    const [result, setResult] = useState('');
    const [loading, setLoading] = useState(false);
    const { addToast } = useToast();

    const process = async (text: string) => {
        setLoading(true);
        try {
            const { data } = await apiService.humanize(text);
            setResult(data.result);
            addToast('Text humanized!', 'success');
        } catch (e: any) { addToast(e.response?.data?.error ?? e.message, 'error'); }
        finally { setLoading(false); }
    };

    return (
        <ToolView
            title="AI → Human Converter"
            subtitle="Transform AI-generated text into natural, human-like writing"
            processLabel="Humanize Text"
            isLoading={loading}
            onProcess={process}
            resultContent={result ? <p className="whitespace-pre">{result}</p> : null}
        />
    );
}

/* ================================================================
   SUMMARIZE VIEW
   ================================================================ */
export function SummarizeView() {
    const [result, setResult] = useState('');
    const [loading, setLoading] = useState(false);
    const [maxLen, setMaxLen] = useState(130);
    const { addToast } = useToast();

    const process = async (text: string) => {
        setLoading(true);
        try {
            const { data } = await apiService.summarize(text, maxLen);
            setResult(data.result);
            addToast('Summarization complete!', 'success');
        } catch (e: any) { addToast(e.response?.data?.error ?? e.message, 'error'); }
        finally { setLoading(false); }
    };

    return (
        <ToolView
            title="Text Summarizer"
            subtitle="Condense long documents into concise summaries"
            processLabel="Summarize"
            isLoading={loading}
            onProcess={process}
            options={
                <div className="options-row">
                    <label className="option-label">Length</label>
                    <select className="select-input" value={maxLen} onChange={(e) => setMaxLen(Number(e.target.value))}>
                        <option value={80}>Short</option>
                        <option value={130}>Medium</option>
                        <option value={200}>Long</option>
                    </select>
                </div>
            }
            resultContent={result ? <p className="whitespace-pre">{result}</p> : null}
        />
    );
}

/* ================================================================
   PARAPHRASE VIEW
   ================================================================ */
export function ParaphraseView() {
    const [results, setResults] = useState<string[]>([]);
    const [loading, setLoading] = useState(false);
    const [vars, setVars] = useState(2);
    const { addToast } = useToast();

    const process = async (text: string) => {
        setLoading(true);
        try {
            const { data } = await apiService.paraphrase(text, vars);
            setResults(data.result);
            addToast('Paraphrasing complete!', 'success');
        } catch (e: any) { addToast(e.response?.data?.error ?? e.message, 'error'); }
        finally { setLoading(false); }
    };

    return (
        <ToolView
            title="Text Paraphraser"
            subtitle="Generate multiple unique variations of your text"
            processLabel="Paraphrase"
            isLoading={loading}
            onProcess={process}
            options={
                <div className="options-row">
                    <label className="option-label">Variations</label>
                    <select className="select-input" value={vars} onChange={(e) => setVars(Number(e.target.value))}>
                        {[1, 2, 3, 4, 5].map(n => <option key={n} value={n}>{n}</option>)}
                    </select>
                </div>
            }
            resultContent={results.length ? (
                <div>{results.map((t, i) => (
                    <div key={i} className="variation-card">
                        <div className="variation-badge">Variation {i + 1}</div>
                        <p>{t}</p>
                    </div>
                ))}</div>
            ) : null}
        />
    );
}
