const { app, BrowserWindow, dialog, ipcMain, session } = require('electron');
const path = require('path');
const fs = require('fs');
const { spawn } = require('child_process');
const http = require('http');

let mainWindow = null;
let pythonProcess = null;
let backendRestarts = 0;
const MAX_RESTARTS = 3;
const BACKEND_PORT = 5123;
const BACKEND_URL = `http://127.0.0.1:${BACKEND_PORT}`;
const IS_DEV = process.env.ELECTRON_DEV === '1';
const VITE_DEV_URL = 'http://localhost:5173';

/* ================================================================
   PYTHON BACKEND MANAGEMENT
   ================================================================ */
function findPython() {
    // In production, use bundled Python from resources
    if (!IS_DEV) {
        const bundledPython = path.join(process.resourcesPath, 'python', 'python.exe');
        if (fs.existsSync(bundledPython)) {
            console.log('[Electron] Using bundled Python runtime');
            return bundledPython;
        }
    }

    // In development, use venv
    const root = path.join(__dirname, '..');
    const candidates = [
        path.join(root, 'venv', 'Scripts', 'python.exe'),
        path.join(root, 'venv', 'bin', 'python3'),
        path.join(root, 'venv', 'bin', 'python'),
    ];
    for (const p of candidates) {
        if (fs.existsSync(p)) return p;
    }

    console.warn('[Electron] WARNING: No Python found in venv or bundled resources');
    return process.platform === 'win32' ? 'python' : 'python3';
}

function startBackend() {
    if (pythonProcess) return;
    const pythonCmd = findPython();

    // Determine server path based on dev/prod mode
    const serverPath = IS_DEV
        ? path.join(__dirname, '..', 'backend', 'server.py')
        : path.join(process.resourcesPath, 'app.asar.unpacked', 'backend', 'server.py');

    console.log(`[Electron] Mode: ${IS_DEV ? 'DEVELOPMENT' : 'PRODUCTION'}`);
    console.log(`[Electron] Starting backend: ${pythonCmd} ${serverPath}`);
    console.log(`[Electron] Working directory: ${path.join(__dirname, '..')}`);

    pythonProcess = spawn(pythonCmd, [serverPath], {
        cwd: path.join(__dirname, '..'),
        stdio: ['pipe', 'pipe', 'pipe'],
        windowsHide: true,
    });

    pythonProcess.stdout.on('data', (d) => console.log(`[Backend] ${d.toString().trim()}`));
    pythonProcess.stderr.on('data', (d) => console.log(`[Backend] ${d.toString().trim()}`));
    pythonProcess.on('error', (err) => console.error('[Electron] Backend spawn error:', err.message));

    pythonProcess.on('close', (code) => {
        console.log(`[Electron] Backend exited (code ${code})`);
        pythonProcess = null;
        if (code !== 0 && code !== null && backendRestarts < MAX_RESTARTS) {
            backendRestarts++;
            console.log(`[Electron] Restarting backend (attempt ${backendRestarts}/${MAX_RESTARTS})…`);
            setTimeout(startBackend, 2000);
        }
    });
}

function killBackend() {
    if (!pythonProcess) return;
    try {
        if (process.platform === 'win32') {
            spawn('taskkill', ['/pid', String(pythonProcess.pid), '/f', '/t']);
        } else {
            pythonProcess.kill('SIGTERM');
        }
    } catch (_) { /* ignore */ }
    pythonProcess = null;
}

function waitForBackend(retries = 40, delay = 1000) {
    return new Promise((resolve, reject) => {
        const attempt = (n) => {
            http.get(`${BACKEND_URL}/api/health`, (res) => {
                let body = '';
                res.on('data', (c) => (body += c));
                res.on('end', () => {
                    try { if (JSON.parse(body).status === 'ok') return resolve(); } catch (_) { }
                    n < retries ? setTimeout(() => attempt(n + 1), delay) : reject(new Error('Backend timeout'));
                });
            }).on('error', () => {
                n < retries ? setTimeout(() => attempt(n + 1), delay) : reject(new Error('Backend unreachable'));
            });
        };
        attempt(1);
    });
}

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
        },
    });

    if (IS_DEV) {
        mainWindow.loadURL(VITE_DEV_URL);
    } else {
        mainWindow.loadFile(path.join(__dirname, '..', 'frontend', 'dist', 'index.html'));
    }

    mainWindow.once('ready-to-show', () => mainWindow.show());
    mainWindow.on('closed', () => { mainWindow = null; });
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
app.whenReady().then(async () => {
    setCSP();
    startBackend();

    try {
        await waitForBackend();
        console.log('[Electron] Backend healthy — creating window');
    } catch (e) {
        console.warn('[Electron] Backend slow, opening window anyway:', e.message);
    }

    createWindow();
    app.on('activate', () => { if (!BrowserWindow.getAllWindows().length) createWindow(); });
});

app.on('window-all-closed', () => {
    killBackend();
    if (process.platform !== 'darwin') app.quit();
});

app.on('before-quit', killBackend);
