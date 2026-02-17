# Jasper — Offline Setup Guide

## Prerequisites
- Windows 10/11
- 8GB+ RAM recommended
- **Internet connection required for initial setup only**

## One-Time Setup (Requires Internet)

### 1. Install Dependencies

```powershell
# Backend dependencies
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

```powershell
# Frontend dependencies
cd frontend
npm install
```

### 2. Download ML Models (~1.1GB)

```powershell
# Run model downloader (downloads to backend/models_local/)
venv\Scripts\python scripts\download_models.py
```

This will download:
- sentence-transformers/all-MiniLM-L6-v2 (~90MB)
- GPT-2 (~500MB)
- RoBERTa (~500MB)
- NLTK data (~5MB)

### 3. Download Fonts

Download Inter font from one of these sources:

**Option A: Google Fonts Helper**
1. Visit https://gwfh.mranftl.com/fonts/inter
2. Select weights: 400, 500, 600
3. Format: WOFF2
4. Download and extract to `assets/fonts/`

**Option B: Manual**
1. Visit https://fonts.google.com/specimen/Inter
2. Click "Download family"
3. Convert TTF to WOFF2 using https://cloudconvert.com/ttf-to-woff2
4. Copy files to `assets/fonts/`:
   - Inter-Regular.woff2
   - Inter-Medium.woff2
   - Inter-SemiBold.woff2

### 4. Build Local Corpus

```powershell
# Build offline corpus index
venv\Scripts\python scripts\build_corpus.py
```

This creates a local FAISS index with 30+ sample documents.

**To add custom documents:**
1. Add `.txt` files to `data/corpus_source/`
2. Re-run `python scripts\build_corpus.py`

### 5. Build Frontend

```powershell
cd frontend
npm run build
```

## Running in Development Mode

```powershell
# Terminal 1: Start backend
venv\Scripts\python backend\server.py

# Terminal 2: Start Electron
npm start
```

## Building Offline Installer

### 1. Bundle Python Runtime (Optional)

```powershell
# Download Python embeddable package
Invoke-WebRequest -Uri "https://www.python.org/ftp/python/3.11.7/python-3.11.7-embed-amd64.zip" -OutFile "python-embed.zip"

# Extract to resources/python
Expand-Archive -Path "python-embed.zip" -DestinationPath "resources\python"

# Install pip
resources\python\python.exe -m ensurepip

# Install requirements
resources\python\python.exe -m pip install -r requirements.txt --target resources\python\Lib\site-packages
```

### 2. Package Electron App

```powershell
npm run build
```

This will create:
- `dist/Jasper-2.0.0-win-x64.exe` (~520MB installer)

## Verifying Offline Functionality

1. **Disconnect internet**
2. Install `Jasper-2.0.0-win-x64.exe`
3. Run application
4. Test features:
   - Detection (plagiarism + AI)
   - All tool views
   - File upload

### Verification Checklist
- [ ] Fonts load (no CDN requests)
- [ ] Models load from local files
- [ ] Detection works without internet
- [ ] No network errors in console
- [ ] Backend starts automatically
- [ ] All features functional

## File Structure

```
Jasper/
├── assets/
│   ├── fonts/              # Bundled Inter fonts (500KB)
│   │   ├── Inter-Regular.woff2
│   │   ├── Inter-Medium.woff2
│   │   └── Inter-SemiBold.woff2
│   └── icon.ico
├── backend/
│   ├── models_local/       # Local ML models (1.1GB)
│   │   ├── sentence-transformers/
│   │   ├── gpt2/
│   │   ├── roberta-base/
│   │   └── nltk_data/
│   ├── database.py
│   ├── server.py
│   └── detection/
├── data/
│   ├── jasper.db           # SQLite database
│   ├── corpus/             # FAISS index + texts
│   └── corpus_source/      # Source .txt files (optional)
├── resources/
│   └── python/             # Bundled Python runtime (60MB)
└── frontend/dist/          # Built React app
```

## Installer Size Breakdown

- ML Models: ~1.1GB
- Python Runtime: ~60MB (if bundled)
- Application Code: ~10MB
- Fonts: ~500KB
- Corpus Data: ~50MB
- **Total: ~520MB** (without Python) or ~580MB (with Python)

## Troubleshooting

### Models not loading
- Verify `backend/models_local/` contains model folders
- Check console for "Loading model from local path" messages
- Re-run `python scripts/download_models.py`

### Fonts not showing
- Verify `assets/fonts/` contains `.woff2` files
- Check browser console for font loading errors
- Ensure paths in CSS match file names

### Backend won't start
- In dev: Ensure venv is activated
- In prod: Verify `resources/python/python.exe` exists
- Check Electron console for Python errors

### Detection not working
- Verify corpus is built: check `data/corpus/index.faiss` exists
- SQLite database initialized: check `data/jasper.db` exists
- Re-run `python scripts/build_corpus.py`

## Notes

- **First-time setup requires internet** (model downloads, font downloads, npm install)
- **After setup, application is 100% offline**
- Models are cached locally in `backend/models_local/`
- Corpus can be expanded by adding .txt files to `data/corpus_source/`
- No external API calls, no CDN dependencies
- All detection runs on local machine

## Performance Tips

- Close other applications to free RAM (models use ~3GB)
- SSD recommended for faster model loading
- Detection first run slower (model initialization)
- Subsequent detections much faster (models cached in RAM)
