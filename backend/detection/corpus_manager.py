"""
Corpus Manager for FAISS indexing and document management.
"""

import os
import json
import numpy as np
from pathlib import Path
from typing import List, Dict
from sentence_transformers import SentenceTransformer
import faiss
import nltk
from nltk.tokenize import sent_tokenize

# Configure NLTK to use local data directory
LOCAL_NLTK_DATA = os.path.join(os.path.dirname(__file__), '..', 'models_local', 'nltk_data')
if os.path.exists(LOCAL_NLTK_DATA):
    nltk.data.path.insert(0, LOCAL_NLTK_DATA)


class CorpusManager:
    def __init__(self, corpus_dir: str = "data/corpus"):
        self.corpus_dir = Path(corpus_dir)
        self.index_path = self.corpus_dir / "index.faiss"
        self.metadata_path = self.corpus_dir / "metadata.json"
        self.texts_dir = self.corpus_dir / "texts"
        
        # Create directories
        self.corpus_dir.mkdir(parents=True, exist_ok=True)
        self.texts_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize embedding model from local path
        model_path = os.path.join(os.path.dirname(__file__), '..', 'models_local', 'sentence-transformers', 'all-MiniLM-L6-v2')
        if os.path.exists(model_path):
            self.embedding_model = SentenceTransformer(model_path)
        else:
            self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Load or create index
        if self.index_path.exists():
            self.index = faiss.read_index(str(self.index_path))
            with open(self.metadata_path, 'r', encoding='utf-8') as f:
                self.metadata = json.load(f)
        else:
            self.index = faiss.IndexFlatL2(384)  # all-MiniLM-L6-v2 dimension
            self.metadata = []
    
    def add_document(self, doc_id: str, title: str, text: str, source: str = "", url: str = ""):
        """Add a document to the corpus and index it."""
        # Save text file
        text_file = self.texts_dir / f"{doc_id}.txt"
        with open(text_file, 'w', encoding='utf-8') as f:
            f.write(text)
        
        # Split into sentences and encode
        sentences = sent_tokenize(text)
        if not sentences:
            return
        
        embeddings = self.embedding_model.encode(sentences)
        
        # Add to FAISS index
        self.index.add(embeddings.astype('float32'))
        
        # Add metadata
        self.metadata.append({
            'id': doc_id,
            'title': title,
            'source': source,
            'url': url,
            'num_sentences': len(sentences)
        })
        
        print(f"Added document '{title}' with {len(sentences)} sentences")
    
    def save(self):
        """Save FAISS index and metadata to disk."""
        faiss.write_index(self.index, str(self.index_path))
        with open(self.metadata_path, 'w', encoding='utf-8') as f:
            json.dump(self.metadata, f, indent=2)
        print(f"Saved corpus: {self.index.ntotal} vectors, {len(self.metadata)} documents")
    
    def get_stats(self) -> Dict:
        """Get corpus statistics."""
        return {
            'total_documents': len(self.metadata),
            'total_vectors': self.index.ntotal,
            'index_size_mb': os.path.getsize(self.index_path) / (1024*1024) if self.index_path.exists() else 0
        }
