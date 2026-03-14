import { 
    MdDashboard, 
    MdSearch, 
    MdPerson, 
    MdDescription, 
    MdAutorenew, 
    MdCheckCircle, 
    MdSmartToy,
    MdAssignment
} from 'react-icons/md';
import { ReactNode } from 'react';

interface NavItem {
    id: string;
    label: string;
    icon: ReactNode;
}

const NAV: NavItem[] = [
    { id: 'dashboard', label: 'Dashboard', icon: <MdDashboard size={20} /> },
    { id: 'detection', label: 'Detection', icon: <MdSearch size={20} /> },
    { id: 'humanize', label: 'AI → Human', icon: <MdPerson size={20} /> },
    { id: 'summarize', label: 'Summarizer', icon: <MdDescription size={20} /> },
    { id: 'paraphrase', label: 'Paraphraser', icon: <MdAutorenew size={20} /> },
    { id: 'grammar', label: 'Grammar', icon: <MdCheckCircle size={20} /> },
    { id: 'ai-detect', label: 'AI Detector', icon: <MdSmartToy size={20} /> },
    { id: 'plagiarism', label: 'Plagiarism', icon: <MdAssignment size={20} /> },
];

interface Props {
    active: string;
    onNavigate: (id: string) => void;
    backendOnline: boolean;
}

export default function Sidebar({ active, onNavigate, backendOnline }: Props) {
    return (
        <aside className="sidebar">
            <nav className="sidebar-nav">
                {NAV.map((item) => (
                    <button
                        key={item.id}
                        className={`nav-item${active === item.id ? ' active' : ''}`}
                        onClick={() => onNavigate(item.id)}
                    >
                        <span className="nav-icon">{item.icon}</span>
                        <span>{item.label}</span>
                    </button>
                ))}
            </nav>

            <div className="sidebar-footer">
                <div className="status-indicator">
                    <span className={`status-dot${backendOnline ? ' online' : ' offline'}`} />
                    <span>{backendOnline ? 'Backend Online' : 'Backend Offline'}</span>
                </div>
            </div>
        </aside>
    );
}
