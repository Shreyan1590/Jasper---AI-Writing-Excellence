"""Jasper — Pydantic request/response models for the FastAPI backend."""

from typing import List, Optional
from pydantic import BaseModel, Field


# ── Request Models ────────────────────────────────────────────────
class TextRequest(BaseModel):
    text: str = Field(..., min_length=1, description="Input text to process")


class SummarizeRequest(TextRequest):
    max_length: int = Field(130, ge=30, le=500, description="Maximum summary length")
    min_length: int = Field(30, ge=10, le=200, description="Minimum summary length")


class ParaphraseRequest(TextRequest):
    variations: int = Field(2, ge=1, le=5, description="Number of paraphrase variations")


# ── Response Models ───────────────────────────────────────────────
class TextResponse(BaseModel):
    result: str


class ParaphraseResponse(BaseModel):
    result: List[str]


class GrammarChange(BaseModel):
    type: str
    message: str
    original: str
    suggestions: List[str]
    position: int


class GrammarResponse(BaseModel):
    original: str
    corrected: str
    changes: List[GrammarChange]


class AIAnalysis(BaseModel):
    lexical_diversity: float
    sentence_length_variance: float
    avg_sentence_length: float
    pattern_matches: int


class AIDetectResponse(BaseModel):
    ai_score: float
    is_ai_generated: bool
    analysis: AIAnalysis


class PlagiarismMatch(BaseModel):
    phrase: str
    position: int
    length: int


class PlagiarismResponse(BaseModel):
    plagiarism_score: float
    originality_score: float
    matches: List[PlagiarismMatch]


class UploadResponse(BaseModel):
    text: str
    filename: str


class HealthResponse(BaseModel):
    status: str


class ErrorResponse(BaseModel):
    error: str
    detail: Optional[str] = None
