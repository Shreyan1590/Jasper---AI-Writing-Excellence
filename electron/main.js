const { app, BrowserWindow, ipcMain, session } = require('electron');
const path = require('path');
const fs = require('fs');

let mainWindow = null;
const BACKEND_URL = 'https://jasper.info-skillxpress.workers.dev';
const IS_DEV = process.env.ELECTRON_DEV === '1';
const VITE_DEV_URL = 'http://localhost:5173';

/* ================================================================
   WINDOW
   ================================================================ */
function createWindow() {
    mainWindow = new BrowserWindow({
        width: 1360,
        height: 900,
        minWidth: 1000,
        minHeight: 680,
        title: 'Jasper — AI Writing Excellence',
        icon: path.join(__dirname, '..', 'assets', 'icon.ico'),
        backgroundColor: '#080c18',
        show: false,
        webPreferences: {
            preload: path.join(__dirname, 'preload.js'),
            contextIsolation: true,
            nodeIntegration: false,
            sandbox: true,
            backgroundThrottling: false,
        },
    });

    if (IS_DEV) {
        mainWindow.loadURL(VITE_DEV_URL);
    } else {
        mainWindow.loadFile(path.join(__dirname, '..', 'frontend', 'dist', 'index.html'));
    }

    mainWindow.once('ready-to-show', () => {
        mainWindow.show();
        mainWindow.focus();
    });

    mainWindow.on('closed', () => {
        mainWindow = null;
    });
}

/* ================================================================
   CSP
   ================================================================ */
function setCSP() {
    session.defaultSession.webRequest.onHeadersReceived((details, cb) => {
        cb({
            responseHeaders: {
                ...details.responseHeaders,
                'Content-Security-Policy': [
                    [
                        "default-src 'self'",
                        "script-src 'self'",
                        "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com",
                        "font-src 'self' https://fonts.gstatic.com",
                        `connect-src 'self' ${BACKEND_URL}`,
                        "img-src 'self' data:",
                    ].join('; '),
                ],
            },
        });
    });
}

/* ================================================================
   IPC HANDLERS
   ================================================================ */
ipcMain.handle('dialog:openFile', async () => {
    const { dialog } = require('electron');
    if (!mainWindow) return null;
    const { canceled, filePaths } = await dialog.showOpenDialog(mainWindow, {
        title: 'Open Text File',
        filters: [
            { name: 'Text Files', extensions: ['txt', 'md', 'csv', 'json'] },
            { name: 'All Files', extensions: ['*'] },
        ],
        properties: ['openFile'],
    });
    if (canceled || !filePaths.length) return null;
    const content = fs.readFileSync(filePaths[0], 'utf-8');
    return { path: filePaths[0], content };
});

ipcMain.handle('get-backend-url', () => BACKEND_URL);
ipcMain.handle('get-platform', () => process.platform);

/* ================================================================
   APP LIFECYCLE
   ================================================================ */
app.whenReady().then(() => {
    setCSP();
    createWindow();

    app.on('activate', () => {
        if (BrowserWindow.getAllWindows().length === 0) createWindow();
    });
});

app.on('window-all-closed', () => {
    if (process.platform !== 'darwin') app.quit();
});
