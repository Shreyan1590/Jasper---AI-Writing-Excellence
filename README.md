# Jasper — AI Writing Excellence

Production Electron desktop application with FastAPI backend and React+TypeScript frontend.

## Project Structure

```
/Jasper
  /assets
    icon.ico          # Custom application icon (multi-resolution)
  /backend
    models.py         # Pydantic request/response models
    server.py         # FastAPI with async endpoints
    processor.py      # TextProcessor (NLP engine)
  /electron
    main.js           # Electron main process (CSP, sandbox, backend manager)
    preload.js        # Secure IPC bridge
  /frontend
    /src
      App.tsx         # React root component
      /components     # UI components
      /views          # Tool views
      /services       # API service layer
    package.json
    vite.config.ts
  package.json        # Root Electron config
  electron-builder.json  # Build configuration
  requirements.txt    # Python dependencies
```

## Setup

### 1. Python Dependencies

```bash
venv\Scripts\python.exe -m pip install -r requirements.txt
```

### 2. Node.js Dependencies

```bash
# Root Electron dependencies
npm install

# Frontend dependencies
cd frontend
npm install
cd ..
```

### 3. Build Frontend

```bash
cd frontend
npx vite build
cd ..
```

## Development

### Dev Mode (Vite HMR)

Terminal 1:
```bash
cd frontend
npm run dev
```

Terminal 2:
```bash
npm run dev
```

### Production Mode

```bash
npm start
```

## Build Windows Installer

```bash
npm run build
```

Output: `dist/Jasper-2.0.0-win-x64.exe`

## Branding

- **Application Icon**: `assets/icon.ico` (multi-resolution: 16x16, 32x32, 64x64, 128x128, 256x256)
- **Window Title**: "Jasper — AI Writing Excellence"
- **Product Name**: Jasper
- **App ID**: com.shreyan.jasper
- **Executable**: Jasper.exe

All Electron default branding removed. Custom icon appears in:
- Application window
- Taskbar
- Desktop shortcut
- Start menu shortcut
- Installer
- Uninstaller

## Architecture

```
Electron Main → FastAPI Backend (uvicorn :5123) → TextProcessor (NLP)
             ↓
       React Frontend (Vite build) → Axios REST API
```

## Security

- `sandbox: true`
- `contextIsolation: true`
- `nodeIntegration: false`
- CSP headers
- Secure IPC via preload script

## Features

- AI → Human Converter
- Text Summarizer
- Paraphraser
- Grammar Checker
- AI Content Detector
- Plagiarism Checker
