import { 
    MdSearch, 
    MdPerson, 
    MdDescription, 
    MdAutorenew, 
    MdCheckCircle, 
    MdSmartToy,
    MdTrendingUp,
    MdInsertDriveFile,
    MdQueryStats,
    MdTimer,
    MdAttachMoney
} from 'react-icons/md';
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
            icon: <MdSearch size={32} color="var(--primary)" />
        },
        {
            id: 'humanize',
            label: 'AI to Human Text',
            description: 'Convert AI-generated text to human-like',
            icon: <MdPerson size={32} color="var(--primary)" />
        },
        {
            id: 'summarize',
            label: 'Text Summarizer',
            description: 'Intelligent document summarization',
            icon: <MdDescription size={32} color="var(--primary)" />
        },
        {
            id: 'paraphrase',
            label: 'Paraphraser',
            description: 'Rephrase with multiple variations',
            icon: <MdAutorenew size={32} color="var(--primary)" />
        },
        {
            id: 'grammar',
            label: 'Grammar Checker',
            description: 'Fix grammar and improve writing',
            icon: <MdCheckCircle size={32} color="var(--primary)" />
        },
        {
            id: 'ai-detect',
            label: 'AI Detector',
            description: 'Detect AI-generated content',
            icon: <MdSmartToy size={32} color="var(--primary)" />
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
                    icon={<MdInsertDriveFile size={20} />}
                    label="Documents Processed"
                    value="1,247"
                    trend={{ value: '12%', direction: 'positive' }}
                />
                <StatCard
                    icon={<MdSearch size={20} />}
                    label="Detections Run"
                    value="523"
                    trend={{ value: '8%', direction: 'positive' }}
                />
                <StatCard
                    icon={<MdQueryStats size={20} />}
                    label="Avg. Accuracy"
                    value="96.8%"
                />
                <StatCard
                    icon={<MdTimer size={20} />}
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
                            <div style={{ marginBottom: 'var(--space-3)' }}>
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
                        Run Detection
                    </Button>
                    <Button variant="secondary" onClick={() => onNavigate('humanize')}>
                        Humanize Text
                    </Button>
                    <Button variant="ghost">
                        View Reports
                    </Button>
                </div>
            </div>
        </div>
    );
}
