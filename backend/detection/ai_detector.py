"""
AI Content Detection Engine
Real detection using perplexity, burstiness, and transformer classification.
"""

import os
import numpy as np
from typing import Dict, List
import torch
from transformers import (
    GPT2LMHeadModel, 
    GPT2TokenizerFast,
    RobertaTokenizer,
    RobertaForSequenceClassification
)
from nltk.tokenize import sent_tokenize
import nltk

# Configure NLTK to use local data directory
LOCAL_NLTK_DATA = os.path.join(os.path.dirname(__file__), '..', 'models_local', 'nltk_data')
if os.path.exists(LOCAL_NLTK_DATA):
    nltk.data.path.insert(0, LOCAL_NLTK_DATA)

try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt', quiet=True)


class AIContentDetector:
    def __init__(self):
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        
        # GPT-2 for perplexity
        self.gpt2_model = None
        self.gpt2_tokenizer = None
        
        # RoBERTa for classification (using base model as fallback)
        self.roberta_model = None
        self.roberta_tokenizer = None
        
        self._load_models()
    
    def _load_models(self):
        """Load GPT-2 and RoBERTa models from local paths."""
        # Local model paths
        gpt2_path = os.path.join(os.path.dirname(__file__), '..', 'models_local', 'gpt2')
        roberta_path = os.path.join(os.path.dirname(__file__), '..', 'models_local', 'roberta-base')
        
        # Load GPT-2 for perplexity calculation
        if os.path.exists(gpt2_path):
            print(f"Loading GPT-2 from local path: {gpt2_path}")
            self.gpt2_tokenizer = GPT2TokenizerFast.from_pretrained(gpt2_path)
            self.gpt2_model = GPT2LMHeadModel.from_pretrained(gpt2_path).to(self.device)
        else:
            print("WARNING: Local GPT-2 not found. Downloading (requires internet)...")
            self.gpt2_tokenizer = GPT2TokenizerFast.from_pretrained('gpt2')
            self.gpt2_model = GPT2LMHeadModel.from_pretrained('gpt2').to(self.device)
        
        self.gpt2_model.eval()
        
        # Load RoBERTa base (or fine-tuned if available)
        try:
            if os.path.exists(roberta_path):
                print(f"Loading RoBERTa from local path: {roberta_path}")
                self.roberta_tokenizer = RobertaTokenizer.from_pretrained(roberta_path)
                self.roberta_model = RobertaForSequenceClassification.from_pretrained(
                    roberta_path, 
                    num_labels=2
                ).to(self.device)
            else:
                print("WARNING: Local RoBERTa not found. Downloading (requires internet)...")
                self.roberta_tokenizer = RobertaTokenizer.from_pretrained('roberta-base')
                self.roberta_model = RobertaForSequenceClassification.from_pretrained(
                    'roberta-base', 
                    num_labels=2
                ).to(self.device)
            
            self.roberta_model.eval()
        except Exception as e:
            print(f"RoBERTa loading failed: {e}")
            # Fallback: use RoBERTa base without fine-tuning
            self.roberta_model = None
    
    def calculate_perplexity(self, text: str) -> float:
        """
        Calculate perplexity using GPT-2.
        Lower perplexity often indicates AI-generated text.
        """
        encodings = self.gpt2_tokenizer(text, return_tensors='pt', truncation=True, max_length=1024)
        input_ids = encodings.input_ids.to(self.device)
        
        with torch.no_grad():
            outputs = self.gpt2_model(input_ids, labels=input_ids)
            loss = outputs.loss
            perplexity = torch.exp(loss).item()
        
        return perplexity
    
    def calculate_burstiness(self, text: str) -> float:
        """
        Calculate burstiness (sentence length variance).
        AI text tends to have lower variance (more consistent length).
        """
        sentences = sent_tokenize(text)
        if len(sentences) < 2:
            return 0.0
        
        lengths = [len(s.split()) for s in sentences]
        variance = np.var(lengths)
        return float(variance)
    
    def classify_with_roberta(self, text: str) -> float:
        """
        Classify text using RoBERTa.
        Returns probability of AI-generated (0-1).
        """
        if self.roberta_model is None:
            return 0.5  # Neutral if model not available
        
        inputs = self.roberta_tokenizer(
            text, 
            return_tensors='pt', 
            truncation=True, 
            max_length=512,
            padding=True
        ).to(self.device)
        
        with torch.no_grad():
            outputs = self.roberta_model(**inputs)
            probabilities = torch.softmax(outputs.logits, dim=1)
            ai_prob = probabilities[0][1].item()  # Probability of class 1 (AI)
        
        return ai_prob
    
    def detect(self, text: str) -> Dict:
        """
        Detect AI-generated content using ensemble of methods.
        Returns AI probability (0-100%) and confidence level.
        """
        if not text.strip():
            return {
                'ai_probability': 0.0,
                'ai_confidence': 'Low',
                'perplexity': None,
                'burstiness': None,
                'method': 'ensemble'
            }
        
        # Calculate metrics
        perplexity = self.calculate_perplexity(text)
        burstiness = self.calculate_burstiness(text)
        
        # Perplexity score (lower = more AI-like)
        # Normalize: typical human text has perplexity 50-200, AI text 10-50
        perplexity_score = max(0, min(1, (200 - perplexity) / 150))
        
        # Burstiness score (lower = more AI-like)
        # Normalize: human text variance ~30-100, AI text ~5-30
        burstiness_score = max(0, min(1, (50 - burstiness) / 45))
        
        # RoBERTa classification
        classifier_score = self.classify_with_roberta(text)
        
        # Weighted ensemble (if all available)
        # 35% perplexity, 25% burstiness, 40% classifier
        ai_probability = (
            0.35 * perplexity_score + 
            0.25 * burstiness_score + 
            0.40 * classifier_score
        ) * 100
        
        # Confidence level
        if ai_probability > 70:
            confidence = 'High'
        elif ai_probability > 40:
            confidence = 'Moderate'
        else:
            confidence = 'Low'
        
        return {
            'ai_probability': round(ai_probability, 2),
            'ai_confidence': confidence,
            'perplexity': round(perplexity, 2),
            'burstiness': round(burstiness, 2),
            'method': 'ensemble (Perplexity + Burstiness + RoBERTa)',
            'details': {
                'perplexity_score': round(perplexity_score * 100, 2),
                'burstiness_score': round(burstiness_score * 100, 2),
                'classifier_score': round(classifier_score * 100, 2)
            }
        }
