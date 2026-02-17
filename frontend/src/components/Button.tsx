import { ReactNode, ButtonHTMLAttributes } from 'react';

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
    variant?: 'primary' | 'secondary' | 'ghost';
    size?: 'sm' | 'md' | 'lg';
    loading?: boolean;
    children: ReactNode;
}

export default function Button({
    variant = 'primary',
    size = 'md',
    loading = false,
    children,
    className = '',
    disabled,
    ...props
}: ButtonProps) {
    const baseClass = 'btn';
    const variantClass = `btn-${variant}`;
    const sizeClass = size !== 'md' ? `btn-${size}` : '';
    const loadingClass = loading ? 'loading' : '';

    const classes = [baseClass, variantClass, sizeClass, loadingClass, className]
        .filter(Boolean)
        .join(' ');

    return (
        <button
            className={classes}
            disabled={disabled || loading}
            {...props}
        >
            <span className="btn-content">{children}</span>
            <div className="btn-loader" />
        </button>
    );
}
