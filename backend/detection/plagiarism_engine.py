"""
Plagiarism Detection Engine
Real similarity detection using TF-IDF, sentence embeddings, and FAISS.
"""

import os
import re
import json
import numpy as np
from typing import List, Dict, Tuple, Optional
from pathlib import Path

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer
import faiss
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import sent_tokenize, word_tokenize

# Configure NLTK to use local data directory
LOCAL_NLTK_DATA = os.path.join(os.path.dirname(__file__), '..', 'models_local', 'nltk_data')
if os.path.exists(LOCAL_NLTK_DATA):
    nltk.data.path.insert(0, LOCAL_NLTK_DATA)

# Download NLTK data if not present
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt', quiet=True)
try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords', quiet=True)


class PlagiarismDetector:
    def __init__(self, corpus_dir: str = "data/corpus"):
        self.corpus_dir = Path(corpus_dir)
        self.index_path = self.corpus_dir / "index.faiss"
        self.metadata_path = self.corpus_dir / "metadata.json"
        self.texts_dir = self.corpus_dir / "texts"
        
        self.embedding_model = None
        self.index = None
        self.metadata = []
        self.corpus_docs = []
        self.stop_words = set(stopwords.words('english'))
        
        self._load_resources()
    
    def _load_resources(self):
        """Load embedding model, FAISS index, and corpus metadata."""
        # Load sentence transformer from local path
        model_path = os.path.join(os.path.dirname(__file__), '..', 'models_local', 'sentence-transformers', 'all-MiniLM-L6-v2')
        
        if os.path.exists(model_path):
            print(f"Loading model from local path: {model_path}")
            self.embedding_model = SentenceTransformer(model_path)
        else:
            print("WARNING: Local model not found. Downloading (requires internet)...")
            self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Load FAISS index if exists
        if self.index_path.exists():
            self.index = faiss.read_index(str(self.index_path))
            with open(self.metadata_path, 'r', encoding='utf-8') as f:
                self.metadata = json.load(f)
            
            # Load corpus documents
            for meta in self.metadata:
                text_file = self.texts_dir / f"{meta['id']}.txt"
                if text_file.exists():
                    with open(text_file, 'r', encoding='utf-8') as f:
                        self.corpus_docs.append(f.read())
        else:
            # Initialize empty index
            self.index = faiss.IndexFlatL2(384)  # all-MiniLM-L6-v2 dimension
    
    def preprocess_text(self, text: str) -> str:
        """Preprocess text: lowercase, remove punctuation, remove stopwords."""
        # Lowercase
        text = text.lower()
        # Remove URLs
        text = re.sub(r'http\S+|www\S+', '', text)
        # Remove special characters but keep sentence structure
        text = re.sub(r'[^a-z0-9\s\.\,\!\?]', '', text)
        return text
    
    def create_ngrams(self, text: str, n: int = 5) -> List[str]:
        """Create n-word shingles for fingerprinting."""
        words = word_tokenize(text.lower())
        words = [w for w in words if w.isalnum() and w not in self.stop_words]
        ngrams = []
        for i in range(len(words) - n + 1):
            ngrams.append(' '.join(words[i:i+n]))
        return ngrams
    
    def compute_tfidf_similarity(self, input_text: str, corpus_texts: List[str]) -> np.ndarray:
        """Compute TF-IDF based cosine similarity."""
        if not corpus_texts:
            return np.array([])
        
        all_texts = [input_text] + corpus_texts
        vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')
        
        try:
            tfidf_matrix = vectorizer.fit_transform(all_texts)
            input_vector = tfidf_matrix[0:1]
            corpus_vectors = tfidf_matrix[1:]
            similarities = cosine_similarity(input_vector, corpus_vectors)[0]
            return similarities
        except Exception:
            return np.zeros(len(corpus_texts))
    
    def compute_embedding_similarity(self, input_sentences: List[str]) -> List[Dict]:
        """Compute sentence embedding similarity using FAISS."""
        if not input_sentences or self.index.ntotal == 0:
            return []
        
        # Encode input sentences
        embeddings = self.embedding_model.encode(input_sentences)
        
        # Search FAISS index
        k = min(3, self.index.ntotal)  # Top-3 matches per sentence
        distances, indices = self.index.search(embeddings.astype('float32'), k)
        
        matches = []
        for i, sentence in enumerate(input_sentences):
            for j in range(k):
                if indices[i][j] != -1:
                    similarity = 1.0 / (1.0 + distances[i][j])  # Convert distance to similarity
                    if similarity > 0.7:  # Threshold
                        doc_idx = indices[i][j] // 10  # Approximate doc index
                        if doc_idx < len(self.metadata):
                            matches.append({
                                'input_sentence': sentence,
                                'matched_source': self.metadata[doc_idx].get('title', 'Unknown'),
                                'similarity': float(similarity),
                                'source_url': self.metadata[doc_idx].get('url', '')
                            })
        
        return matches
    
    def detect(self, text: str) -> Dict:
        """
        Detect plagiarism using hybrid approach.
        Returns plagiarism score, level, and matched sentences.
        """
        if not text.strip():
            return {
                'plagiarism_score': 0.0,
                'plagiarism_level': 'None',
                'matched_sentences': [],
                'corpus_size': len(self.corpus_docs),
                'method': 'hybrid'
            }
        
        # Preprocess
        processed_text = self.preprocess_text(text)
        
        # Sentence tokenization
        sentences = sent_tokenize(text)
        
        # TF-IDF similarity (document-level)
        tfidf_scores = self.compute_tfidf_similarity(processed_text, self.corpus_docs)
        avg_tfidf_similarity = float(np.mean(tfidf_scores)) if len(tfidf_scores) > 0 else 0.0
        
        # Sentence-level embedding similarity
        matched_sentences = self.compute_embedding_similarity(sentences)
        
        # Calculate overall score
        if len(matched_sentences) > 0:
            avg_embedding_similarity = np.mean([m['similarity'] for m in matched_sentences])
            # Weighted average: 40% TF-IDF, 60% Embeddings
            plagiarism_score = (0.4 * avg_tfidf_similarity + 0.6 * avg_embedding_similarity) * 100
        else:
            plagiarism_score = avg_tfidf_similarity * 100
        
        # Determine level
        if plagiarism_score < 10:
            level = 'Low'
        elif plagiarism_score < 25:
            level = 'Moderate'
        else:
            level = 'High'
        
        return {
            'plagiarism_score': round(plagiarism_score, 2),
            'plagiarism_level': level,
            'matched_sentences': matched_sentences[:10],  # Top 10 matches
            'corpus_size': len(self.corpus_docs),
            'method': 'hybrid (TF-IDF + Embeddings + FAISS)',
            'note': 'Results based on indexed corpus. Expand corpus for better accuracy.' if len(self.corpus_docs) < 100 else None
        }
