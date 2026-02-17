import { ReactNode } from 'react';

interface StatCardProps {
    icon: ReactNode;
    label: string;
    value: string | number;
    trend?: {
        value: string;
        direction: 'positive' | 'negative';
    };
    onClick?: () => void;
}

export default function StatCard({ icon, label, value, trend, onClick }: StatCardProps) {
    return (
        <div className="stat-card" onClick={onClick} role={onClick ? 'button' : undefined}>
            <div className="stat-card-header">
                <div className="stat-card-icon">{icon}</div>
            </div>
            <div className="stat-card-value">{value}</div>
            <div className="stat-card-label">{label}</div>
            {trend && (
                <div className={`stat-card-trend ${trend.direction}`}>
                    <span>{trend.direction === 'positive' ? '↑' : '↓'}</span>
                    <span>{trend.value}</span>
                </div>
            )}
        </div>
    );
}
