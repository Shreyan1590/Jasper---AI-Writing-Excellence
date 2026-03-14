import { createContext, useContext, useState, useCallback, ReactNode } from 'react';
import { MdCheckCircle, MdError, MdWarning, MdInfo } from 'react-icons/md';

type ToastType = 'success' | 'error' | 'info' | 'warning';

interface Toast {
    id: number;
    message: string;
    type: ToastType;
}

interface ToastCtx {
    showToast: (message: string, type?: ToastType) => void;
    addToast: (message: string, type?: ToastType) => void;
}

const Ctx = createContext<ToastCtx>({ showToast: () => { }, addToast: () => { } });

export const useToast = () => useContext(Ctx);

let _id = 0;

export function ToastProvider({ children }: { children: ReactNode }) {
    const [toasts, setToasts] = useState<Toast[]>([]);

    const showToast = useCallback((message: string, type: ToastType = 'info') => {
        const id = ++_id;
        setToasts((prev) => [...prev, { id, message, type }]);
        setTimeout(() => setToasts((prev) => prev.filter((t) => t.id !== id)), 3500);
    }, []);

    return (
        <Ctx.Provider value={{ showToast, addToast: showToast }}>
            {children}
            <div className="toast-container">
                {toasts.map((t) => (
                    <div key={t.id} className={`toast toast-${t.type}`}>
                        <span className="toast-icon">
                            {t.type === 'success' && <MdCheckCircle size={20} />}
                            {t.type === 'error' && <MdError size={20} />}
                            {t.type === 'warning' && <MdWarning size={20} />}
                            {t.type === 'info' && <MdInfo size={20} />}
                        </span>
                        <span className="toast-content">{t.message}</span>
                    </div>
                ))}
            </div>
        </Ctx.Provider>
    );
}
