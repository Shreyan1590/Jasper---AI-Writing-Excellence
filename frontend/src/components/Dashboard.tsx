import StatCard from './StatCard';
import Button from './Button';

interface DashboardProps {
    onNavigate: (view: string) => void;
}

export default function Dashboard({ onNavigate }: DashboardProps) {
    const tools = [
        {
            id: 'detection',
            label: 'AI + Plagiarism Detection',
            description: 'Advanced detection with real algorithms',
            icon: '🔍'
        },
        {
            id: 'humanize',
            label: 'AI to Human Text',
            description: 'Convert AI-generated text to human-like',
            icon: '👤'
        },
        {
            id: 'summarize',
            label: 'Text Summarizer',
            description: 'Intelligent document summarization',
            icon: '📝'
        },
        {
            id: 'paraphrase',
            label: 'Paraphraser',
            description: 'Rephrase with multiple variations',
            icon: '🔄'
        },
        {
            id: 'grammar',
            label: 'Grammar Checker',
            description: 'Fix grammar and improve writing',
            icon: '✓'
        },
        {
            id: 'ai-detect',
            label: 'AI Detector',
            description: 'Detect AI-generated content',
            icon: '🤖'
        }
    ];

    return (
        <div className="animate-fade">
            <div className="mb-6">
                <h1>Welcome to Jasper</h1>
                <p className="text-secondary">Professional AI writing and detection tools</p>
            </div>

            {/* Statistics */}
            <div className="grid grid-cols-4 gap-4 mb-6">
                <StatCard
                    icon={
                        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                            <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
                            <polyline points="14 2 14 8 20 8" />
                        </svg>
                    }
                    label="Documents Processed"
                    value="1,247"
                    trend={{ value: '12%', direction: 'positive' }}
                />
                <StatCard
                    icon={
                        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                            <circle cx="11" cy="11" r="8" />
                            <line x1="21" y1="21" x2="16.65" y2="16.65" />
                        </svg>
                    }
                    label="Detections Run"
                    value="523"
                    trend={{ value: '8%', direction: 'positive' }}
                />
                <StatCard
                    icon={
                        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                            <polyline points="22 12 18 12 15 21 9 3 6 12 2 12" />
                        </svg>
                    }
                    label="Avg. Accuracy"
                    value="96.8%"
                />
                <StatCard
                    icon={
                        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                            <path d="M12 2v20M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6" />
                        </svg>
                    }
                    label="Time Saved"
                    value="142h"
                    trend={{ value: '24%', direction: 'positive' }}
                />
            </div>

            {/* Tools Grid */}
            <div className="card mb-6">
                <div className="card-header">
                    <h2 className="card-title">Available Tools</h2>
                </div>
                <div className="grid grid-cols-3 gap-4">
                    {tools.map((tool) => (
                        <div
                            key={tool.id}
                            className="card"
                            style={{ cursor: 'pointer' }}
                            onClick={() => onNavigate(tool.id)}
                        >
                            <div style={{ fontSize: '32px', marginBottom: 'var(--space-3)' }}>
                                {tool.icon}
                            </div>
                            <h3 style={{ fontSize: 'var(--text-base)', marginBottom: 'var(--space-1)' }}>
                                {tool.label}
                            </h3>
                            <p className="text-secondary" style={{ fontSize: 'var(--text-sm)' }}>
                                {tool.description}
                            </p>
                        </div>
                    ))}
                </div>
            </div>

            {/* Quick Actions */}
            <div className="card">
                <div className="card-header">
                    <h2 className="card-title">Quick Actions</h2>
                </div>
                <div className="flex gap-4">
                    <Button variant="primary" onClick={() => onNavigate('detection')}>
                        🔍 Run Detection
                    </Button>
                    <Button variant="secondary" onClick={() => onNavigate('humanize')}>
                        👤 Humanize Text
                    </Button>
                    <Button variant="ghost">
                        📊 View Reports
                    </Button>
                </div>
            </div>
        </div>
    );
}
