"""
Jasper — FastAPI Backend Server
Production-grade REST API for text processing.
"""

import os
import sys
import logging
import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI, UploadFile, File, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from models import (
    TextRequest, SummarizeRequest, ParaphraseRequest,
    TextResponse, ParaphraseResponse, GrammarResponse,
    AIDetectResponse, PlagiarismResponse, UploadResponse,
    HealthResponse, ErrorResponse,
)
from processor import TextProcessor
from detection.plagiarism_engine import PlagiarismDetector
from detection.ai_detector import AIContentDetector
from detection.models import (
    DetectionRequest, PlagiarismResult, AIDetectionResult, 
    HybridDetectionResult, CorpusStats
)
from detection.corpus_manager import CorpusManager
import PyPDF2
import docx
from io import BytesIO

# ── Logging ───────────────────────────────────────────────────────
LOG_DIR = os.path.join(os.path.expanduser("~"), ".jasper", "logs")
os.makedirs(LOG_DIR, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(os.path.join(LOG_DIR, "backend.log"), encoding="utf-8"),
    ],
)
logger = logging.getLogger("jasper")

# ── Application Lifespan ─────────────────────────────────────────
processor: TextProcessor | None = None
plagiarism_detector: PlagiarismDetector | None = None
ai_detector: AIContentDetector | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global processor, plagiarism_detector, ai_detector
    logger.info("Initializing Jasper TextProcessor …")
    loop = asyncio.get_event_loop()
    processor = await loop.run_in_executor(None, TextProcessor)
    logger.info("TextProcessor ready.")
    
    logger.info("Initializing Detection Engines …")
    plagiarism_detector = await loop.run_in_executor(None, PlagiarismDetector)
    ai_detector = await loop.run_in_executor(None, AIContentDetector)
    logger.info("Detection engines ready.")
    
    yield
    logger.info("Shutting down Jasper backend.")


app = FastAPI(
    title="Jasper API",
    version="2.0.0",
    lifespan=lifespan,
)

# ── CORS ──────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Global Exception Handler ─────────────────────────────────────
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled exception")
    return JSONResponse(
        status_code=500,
        content={"error": str(exc), "detail": type(exc).__name__},
    )


# ── Helper to run blocking code ──────────────────────────────────
async def run_blocking(func, *args):
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, func, *args)


# ── Health ────────────────────────────────────────────────────────
@app.get("/api/health", response_model=HealthResponse)
async def health():
    return HealthResponse(status="ok")


# ── Humanize ──────────────────────────────────────────────────────
@app.post("/api/humanize", response_model=TextResponse, responses={400: {"model": ErrorResponse}})
async def humanize(req: TextRequest):
    result = await run_blocking(processor.ai_to_human_converter, req.text)
    return TextResponse(result=result)


# ── Summarize ─────────────────────────────────────────────────────
@app.post("/api/summarize", response_model=TextResponse, responses={400: {"model": ErrorResponse}})
async def summarize(req: SummarizeRequest):
    result = await run_blocking(processor.summarize_text, req.text, req.max_length, req.min_length)
    return TextResponse(result=result)


# ── Paraphrase ────────────────────────────────────────────────────
@app.post("/api/paraphrase", response_model=ParaphraseResponse, responses={400: {"model": ErrorResponse}})
async def paraphrase(req: ParaphraseRequest):
    result = await run_blocking(processor.paraphrase_text, req.text, req.variations)
    return ParaphraseResponse(result=result)


# ── Grammar ───────────────────────────────────────────────────────
@app.post("/api/grammar", response_model=GrammarResponse, responses={400: {"model": ErrorResponse}})
async def grammar(req: TextRequest):
    result = await run_blocking(processor.check_grammar, req.text)
    return GrammarResponse(**result)


# ── AI Detect ─────────────────────────────────────────────────────
@app.post("/api/ai-detect", response_model=AIDetectResponse, responses={400: {"model": ErrorResponse}})
async def ai_detect(req: TextRequest):
    result = await run_blocking(processor.detect_ai_content, req.text)
    return AIDetectResponse(**result)


# ── Plagiarism ────────────────────────────────────────────────────
@app.post("/api/plagiarism", response_model=PlagiarismResponse, responses={400: {"model": ErrorResponse}})
async def plagiarism(req: TextRequest):
    result = await run_blocking(processor.check_plagiarism, req.text)
    return PlagiarismResponse(**result)


# ── File Upload ───────────────────────────────────────────────────
@app.post("/api/upload", response_model=UploadResponse, responses={400: {"model": ErrorResponse}})
async def upload_file(file: UploadFile = File(...)):
    if not file.filename:
        raise HTTPException(status_code=400, detail="Empty filename")
    content = await file.read()
    text = content.decode("utf-8", errors="replace")
    return UploadResponse(text=text, filename=file.filename)


# ── Detection: Plagiarism ─────────────────────────────────────────
@app.post("/api/detect/plagiarism", response_model=PlagiarismResult)
async def detect_plagiarism(req: DetectionRequest):
    result = await run_blocking(plagiarism_detector.detect, req.text)
    return PlagiarismResult(**result)


# ── Detection: AI Content ─────────────────────────────────────────
@app.post("/api/detect/ai", response_model=AIDetectionResult)
async def detect_ai_content(req: DetectionRequest):
    result = await run_blocking(ai_detector.detect, req.text)
    return AIDetectionResult(**result)


# ── Detection: Hybrid (Both) ──────────────────────────────────────
@app.post("/api/detect/hybrid", response_model=HybridDetectionResult)
async def detect_hybrid(req: DetectionRequest):
    plag_result = await run_blocking(plagiarism_detector.detect, req.text)
    ai_result = await run_blocking(ai_detector.detect, req.text)
    return HybridDetectionResult(
        plagiarism=PlagiarismResult(**plag_result),
        ai_detection=AIDetectionResult(**ai_result)
    )


# ── Corpus Stats ──────────────────────────────────────────────────
@app.get("/api/corpus/stats", response_model=CorpusStats)
async def get_corpus_stats():
    corpus_mgr = CorpusManager()
    stats = await run_blocking(corpus_mgr.get_stats)
    return CorpusStats(**stats)


# ── File Upload with Extraction ───────────────────────────────────
@app.post("/api/upload/extract")
async def upload_extract(file: UploadFile = File(...)):
    if not file.filename:
        raise HTTPException(status_code=400, detail="Empty filename")
    
    content = await file.read()
    text = ""
    
    # Extract based on file type
    if file.filename.endswith('.pdf'):
        try:
            pdf = PyPDF2.PdfReader(BytesIO(content))
            text = "\n".join([page.extract_text() for page in pdf.pages])
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"PDF extraction failed: {str(e)}")
    
    elif file.filename.endswith('.docx'):
        try:
            doc = docx.Document(BytesIO(content))
            text = "\n".join([p.text for p in doc.paragraphs])
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"DOCX extraction failed: {str(e)}")
    
    else:  # TXT or other
        text = content.decode("utf-8", errors="replace")
    
    return {"text": text, "filename": file.filename, "length": len(text)}


# ── Entry Point ───────────────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=5123, log_level="info")
