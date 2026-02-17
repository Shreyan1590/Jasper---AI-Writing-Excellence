/// <reference types="vite/client" />

interface ElectronAPI {
    openFile: () => Promise<{ path: string; content: string } | null>;
    getBackendUrl: () => Promise<string>;
    getPlatform: () => Promise<string>;
}

interface Window {
    electronAPI?: ElectronAPI;
}
