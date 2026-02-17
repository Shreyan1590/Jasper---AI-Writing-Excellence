import { useState, useRef, ReactNode } from 'react';
import { useToast } from './Toast';

interface Props {
    title: string;
    subtitle: string;
    processLabel: string;
    options?: ReactNode;
    resultContent: ReactNode;
    onProcess: (text: string) => Promise<void>;
    isLoading: boolean;
}

export default function ToolView({
    title, subtitle, processLabel, options, resultContent, onProcess, isLoading,
}: Props) {
    const [input, setInput] = useState('');
    const { addToast } = useToast();
    const fileRef = useRef<HTMLInputElement>(null);

    const handleProcess = () => {
        if (!input.trim()) { addToast('Please enter some text first', 'warning'); return; }
        onProcess(input);
    };

    const handleLoadFile = async () => {
        if (window.electronAPI?.openFile) {
            const res = await window.electronAPI.openFile();
            if (res) { setInput(res.content); addToast(`Loaded ${res.path.split(/[\\/]/).pop()}`, 'success'); }
        } else {
            fileRef.current?.click();
        }
    };

    const handleFileInput = (e: React.ChangeEvent<HTMLInputElement>) => {
        const file = e.target.files?.[0];
        if (!file) return;
        const reader = new FileReader();
        reader.onload = () => { setInput(reader.result as string); addToast(`Loaded ${file.name}`, 'success'); };
        reader.readAsText(file);
    };

    return (
        <section className="section-animate">
            <div className="section-header">
                <h1>{title.split(' ').map((w, i, a) =>
                    i === a.length - 1 ? <span key={i} className="gradient-text">{w}</span> : w + ' '
                )}</h1>
                <p className="subtitle">{subtitle}</p>
            </div>

            <div className="tool-layout">
                <div className="glass-card">
                    <div className="panel-header">
                        <h3>Input Text</h3>
                        <div className="panel-actions">
                            <button className="btn btn-sm btn-ghost" onClick={handleLoadFile}>Load File</button>
                            <button className="btn btn-sm btn-ghost" onClick={() => setInput('')}>Clear</button>
                        </div>
                    </div>
                    <textarea
                        className="text-area"
                        placeholder="Paste your text here…"
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                    />
                    <input ref={fileRef} type="file" accept=".txt,.md,.csv,.json" hidden onChange={handleFileInput} />
                </div>

                <div className="action-bar">
                    {options}
                    <button className={`btn btn-primary btn-lg${isLoading ? ' loading' : ''}`} onClick={handleProcess} disabled={isLoading}>
                        <span className="btn-content">{processLabel}</span>
                        <span className="btn-loader" />
                    </button>
                </div>

                <div className="glass-card">
                    <div className="panel-header"><h3>Result</h3></div>
                    <div className="result-area">
                        {resultContent || <span className="text-muted">Results will appear here…</span>}
                    </div>
                </div>
            </div>
        </section>
    );
}
