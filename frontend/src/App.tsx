import { useState, useEffect } from 'react';
import ErrorBoundary from './components/ErrorBoundary';
import { ToastProvider } from './components/Toast';
import AppBar from './components/AppBar';
import Sidebar from './components/Sidebar';
import Dashboard from './components/Dashboard';
import { HumanizeView, SummarizeView, ParaphraseView } from './views/SimpleViews';
import { GrammarView, AIDetectView, PlagiarismView } from './views/AnalysisViews';
import DetectionView from './views/DetectionView';
import apiService from './services/api';

export default function App() {
    const [view, setView] = useState('dashboard');
    const [online, setOnline] = useState(false);

    useEffect(() => {
        const check = async () => {
            try { await apiService.health(); setOnline(true); } catch { setOnline(false); }
        };
        check();
        const id = setInterval(check, 15000);
        return () => clearInterval(id);
    }, []);

    const renderView = () => {
        switch (view) {
            case 'dashboard': return <Dashboard onNavigate={setView} />;
            case 'detection': return <DetectionView />;
            case 'humanize': return <HumanizeView />;
            case 'summarize': return <SummarizeView />;
            case 'paraphrase': return <ParaphraseView />;
            case 'grammar': return <GrammarView />;
            case 'ai-detect': return <AIDetectView />;
            case 'plagiarism': return <PlagiarismView />;
            default: return <Dashboard onNavigate={setView} />;
        }
    };

    return (
        <ErrorBoundary>
            <ToastProvider>
                <div className="app-layout">
                    <AppBar />
                    <div className="app-content">
                        <Sidebar active={view} onNavigate={setView} backendOnline={online} />
                        <main className="main-content">{renderView()}</main>
                    </div>
                </div>
            </ToastProvider>
        </ErrorBoundary>
    );
}
