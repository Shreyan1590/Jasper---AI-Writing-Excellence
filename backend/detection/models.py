"""Pydantic models for detection API."""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class DetectionRequest(BaseModel):
    text: str = Field(..., min_length=1, description="Text to analyze")


class MatchedSentence(BaseModel):
    input_sentence: str
    matched_source: str
    similarity: float
    source_url: Optional[str] = None


class PlagiarismResult(BaseModel):
    plagiarism_score: float
    plagiarism_level: str
    matched_sentences: List[MatchedSentence]
    corpus_size: int
    method: str
    note: Optional[str] = None


class AIDetectionDetails(BaseModel):
    perplexity_score: float
    burstiness_score: float
    classifier_score: float


class AIDetectionResult(BaseModel):
    ai_probability: float
    ai_confidence: str
    perplexity: Optional[float] = None
    burstiness: Optional[float] = None
    method: str
    details: Optional[AIDetectionDetails] = None


class HybridDetectionResult(BaseModel):
    plagiarism: PlagiarismResult
    ai_detection: AIDetectionResult


class CorpusStats(BaseModel):
    total_documents: int
    total_vectors: int
    index_size_mb: float
