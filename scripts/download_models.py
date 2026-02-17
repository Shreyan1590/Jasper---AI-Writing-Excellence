"""
Download and save ML models locally for offline usage.
Run this ONCE during setup (requires internet).
"""

import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

print("=" * 60)
print("Jasper — Offline Model Downloader")
print("Downloading models to backend/models_local/")
print("=" * 60)

models_dir = Path(__file__).parent.parent / "backend" / "models_local"
models_dir.mkdir(parents=True, exist_ok=True)

# ── Sentence Transformers ─────────────────────────────────────
print("\n[1/4] Downloading sentence-transformers model...")
try:
    from sentence_transformers import SentenceTransformer
    
    model_path = models_dir / "sentence-transformers" / "all-MiniLM-L6-v2"
    model_path.parent.mkdir(parents=True, exist_ok=True)
    
    print("  Downloading all-MiniLM-L6-v2 (~90MB)...")
    model = SentenceTransformer('all-MiniLM-L6-v2')
    model.save(str(model_path))
    print(f"  ✓ Saved to: {model_path}")
except Exception as e:
    print(f"  ✗ Error: {e}")

# ── GPT-2 ─────────────────────────────────────────────────────
print("\n[2/4] Downloading GPT-2 for perplexity...")
try:
    from transformers import GPT2LMHeadModel, GPT2TokenizerFast
    
    model_path = models_dir / "gpt2"
    model_path.mkdir(parents=True, exist_ok=True)
    
    print("  Downloading GPT-2 model and tokenizer (~500MB)...")
    tokenizer = GPT2TokenizerFast.from_pretrained('gpt2')
    model = GPT2LMHeadModel.from_pretrained('gpt2')
    
    tokenizer.save_pretrained(str(model_path))
    model.save_pretrained(str(model_path))
    print(f"  ✓ Saved to: {model_path}")
except Exception as e:
    print(f"  ✗ Error: {e}")

# ── RoBERTa ───────────────────────────────────────────────────
print("\n[3/4] Downloading RoBERTa...")
try:
    from transformers import RobertaTokenizer, RobertaForSequenceClassification
    
    model_path = models_dir / "roberta-base"
    model_path.mkdir(parents=True, exist_ok=True)
    
    print("  Downloading RoBERTa model and tokenizer (~500MB)...")
    tokenizer = RobertaTokenizer.from_pretrained('roberta-base')
    model = RobertaForSequenceClassification.from_pretrained('roberta-base', num_labels=2)
    
    tokenizer.save_pretrained(str(model_path))
    model.save_pretrained(str(model_path))
    print(f"  ✓ Saved to: {model_path}")
except Exception as e:
    print(f"  ✗ Error: {e}")

# ── NLTK Data ─────────────────────────────────────────────────
print("\n[4/4] Downloading NLTK data...")
try:
    import nltk
    
    nltk_data_dir = models_dir / "nltk_data"
    nltk_data_dir.mkdir(parents=True, exist_ok=True)
    
    nltk.data.path.append(str(nltk_data_dir))
    nltk.download('punkt', download_dir=str(nltk_data_dir), quiet=False)
    nltk.download('stopwords', download_dir=str(nltk_data_dir), quiet=False)
    print(f"  ✓ Saved to: {nltk_data_dir}")
except Exception as e:
    print(f"  ✗ Error: {e}")

print("\n" + "=" * 60)
print("Model download complete!")
print(f"Total size: ~1.1GB")
print(f"Location: {models_dir}")
print("\nNext steps:")
print("1. Models are saved locally")
print("2. Application will load from these paths")
print("3. No internet required after this point")
print("=" * 60)
