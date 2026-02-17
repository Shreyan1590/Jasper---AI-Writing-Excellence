const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('electronAPI', {
    openFile: () => ipcRenderer.invoke('dialog:openFile'),
    getBackendUrl: () => ipcRenderer.invoke('get-backend-url'),
    getPlatform: () => ipcRenderer.invoke('get-platform'),
});
