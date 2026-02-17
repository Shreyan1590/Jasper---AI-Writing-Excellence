"""
Jasper - AI Writing Excellence
Text Processing Engine (extracted from PyQt5 monolith)
"""

import os
import re
import ssl
import urllib.request
import zipfile
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize

# Fix SSL certificate issues for NLTK downloads
try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context


def download_nltk_data():
    """Download all required NLTK data with error handling."""
    nltk_data_path = os.path.join(os.path.expanduser('~'), 'nltk_data')
    if not os.path.exists(nltk_data_path):
        os.makedirs(nltk_data_path)

    required_data = [
        'punkt', 'stopwords', 'punkt_tab',
        'averaged_perceptron_tagger', 'wordnet'
    ]

    for data in required_data:
        try:
            nltk.download(data, quiet=True)
        except Exception as e:
            print(f"Failed to download {data}: {e}")
            try:
                if data == 'punkt_tab':
                    url = "https://raw.githubusercontent.com/nltk/nltk_data/gh-pages/packages/tokenizers/punkt_tab.zip"
                    download_path = os.path.join(
                        nltk_data_path, 'tokenizers', 'punkt_tab.zip')
                    os.makedirs(os.path.dirname(download_path), exist_ok=True)
                    with urllib.request.urlopen(url) as response:
                        with open(download_path, 'wb') as out_file:
                            out_file.write(response.read())
                    with zipfile.ZipFile(download_path, 'r') as zip_ref:
                        zip_ref.extractall(os.path.join(
                            nltk_data_path, 'tokenizers'))
                    os.remove(download_path)
            except Exception as manual_error:
                print(f"Manual download also failed: {manual_error}")


# Download NLTK data on import
download_nltk_data()


class TextProcessor:
    """Core NLP engine for all text processing features."""

    def __init__(self):
        self.nlp = None
        self.summarizer = None
        self._initialize_models()

    def _initialize_models(self):
        """Initialize NLP models gracefully."""
        try:
            import spacy
            self.nlp = spacy.load("en_core_web_sm")
        except Exception:
            print("spaCy model not found, some features may be limited")

        try:
            from transformers import pipeline
            self.summarizer = pipeline(
                "summarization", model="facebook/bart-large-cnn")
        except ImportError:
            print("Transformers not available, using fallback summarization")
        except Exception as e:
            print(f"Summarization model could not be loaded: {e}")

    # ------------------------------------------------------------------
    # AI-to-Human Converter
    # ------------------------------------------------------------------
    def ai_to_human_converter(self, text):
        """Convert AI-generated text to more human-like text."""
        if not text.strip():
            return text

        contractions = [
            (r"\b(is not)\b", "isn't"),
            (r"\b(are not)\b", "aren't"),
            (r"\b(cannot)\b", "can't"),
            (r"\b(will not)\b", "won't"),
            (r"\b(does not)\b", "doesn't"),
            (r"\b(did not)\b", "didn't"),
            (r"\b(has not)\b", "hasn't"),
            (r"\b(have not)\b", "haven't"),
            (r"\b(had not)\b", "hadn't"),
            (r"\b(would not)\b", "wouldn't"),
            (r"\b(could not)\b", "couldn't"),
            (r"\b(should not)\b", "shouldn't"),
        ]
        for pattern, replacement in contractions:
            text = re.sub(pattern, replacement, text)

        try:
            sentences = sent_tokenize(text)
            if len(sentences) > 2:
                starters = [
                    "Actually,", "Well,", "You know,",
                    "I think", "In my opinion,"
                ]
                for i in range(1, len(sentences), 3):
                    if i < len(sentences) and not sentences[i].startswith(
                            tuple(starters)):
                        s = starters[i % len(starters)]
                        sentences[i] = (
                            f"{s} {sentences[i][0].lower()}"
                            f"{sentences[i][1:]}"
                        )
            return ' '.join(sentences)
        except Exception:
            return text

    # ------------------------------------------------------------------
    # Summarizer
    # ------------------------------------------------------------------
    def summarize_text(self, text, max_length=130, min_length=30):
        """Summarize text using transformer models or fallback."""
        if not text.strip():
            return "No text to summarize"

        try:
            if self.summarizer:
                summary = self.summarizer(
                    text, max_length=max_length,
                    min_length=min_length, do_sample=False)
                return summary[0]['summary_text']
            else:
                return self._extractive_summarization(text, max_sentences=3)
        except Exception as e:
            return f"Error in summarization: {str(e)}"

    def _extractive_summarization(self, text, max_sentences=3):
        """Fallback extractive summarization using NLTK."""
        try:
            sentences = sent_tokenize(text)
            if len(sentences) <= max_sentences:
                return text

            stop_words = set(stopwords.words("english"))
            words = word_tokenize(text.lower())
            freq_table = {}
            for word in words:
                if word in stop_words:
                    continue
                if word.isalnum():
                    freq_table[word] = freq_table.get(word, 0) + 1

            sentence_scores = {}
            for i, sentence in enumerate(sentences):
                for word in word_tokenize(sentence.lower()):
                    if word in freq_table:
                        sentence_scores[i] = (
                            sentence_scores.get(i, 0) + freq_table[word])

            if not sentence_scores:
                return ". ".join(sentences[:max_sentences]) + "."

            sorted_sentences = sorted(
                sentence_scores.items(), key=lambda x: x[1], reverse=True)
            top_indices = sorted(
                [idx for idx, _ in sorted_sentences[:max_sentences]])
            return ". ".join([sentences[i] for i in top_indices]) + "."
        except Exception:
            parts = text.split('.')
            return '.'.join(parts[:max_sentences]) + '.'

    # ------------------------------------------------------------------
    # Paraphraser
    # ------------------------------------------------------------------
    def paraphrase_text(self, text, variations=1):
        """Generate paraphrased versions of text."""
        if not text.strip():
            return ["No text to paraphrase"]

        paraphrases = []

        # Variation 1 – synonym swap
        p1 = text.replace(" important", " crucial")
        p1 = p1.replace(" however", " though")
        p1 = p1.replace(" additionally", " also")
        p1 = p1.replace(" therefore", " thus")
        paraphrases.append(p1)

        # Variation 2 – sentence reorder
        if variations > 1 and ". " in text:
            try:
                sentences = sent_tokenize(text)
                if len(sentences) > 1:
                    p2 = ". ".join(
                        [sentences[1], sentences[0]] + sentences[2:])
                    paraphrases.append(p2)
            except Exception:
                parts = text.split('. ')
                if len(parts) > 1:
                    p2 = ". ".join([parts[1], parts[0]] + parts[2:])
                    paraphrases.append(p2)

        # Additional variations
        if variations > 2:
            for i in range(2, variations):
                if i == 2:
                    p = text.replace(" the ", " a ").replace(" is ", " was ")
                    paraphrases.append(p)
                else:
                    paraphrases.append(f"Paraphrase {i+1}: {text}")

        return paraphrases

    # ------------------------------------------------------------------
    # Grammar Checker
    # ------------------------------------------------------------------
    def check_grammar(self, text):
        """Check and correct grammar in text."""
        if not text.strip():
            return {"original": text, "corrected": text, "changes": []}

        corrected = text
        corrections = [
            (r"\bi\b", "I"),
            (r"\bcan not\b", "cannot"),
            (r"\balot\b", "a lot"),
            (r"\bwould of\b", "would have"),
            (r"\bcould of\b", "could have"),
            (r"\bshould of\b", "should have"),
        ]

        changes = []
        for pattern, replacement in corrections:
            original = corrected
            corrected = re.sub(pattern, replacement, corrected)
            if original != corrected:
                changes.append({
                    'type': 'correction',
                    'message': f'Replaced "{pattern}" with "{replacement}"',
                    'original': pattern,
                    'suggestions': [replacement],
                    'position': 0
                })

        return {
            'original': text,
            'corrected': corrected,
            'changes': changes
        }

    # ------------------------------------------------------------------
    # AI Content Detector
    # ------------------------------------------------------------------
    def detect_ai_content(self, text):
        """Detect if text was likely generated by AI."""
        if not text.strip():
            return {'ai_score': 0, 'is_ai_generated': False, 'analysis': {}}

        ai_patterns = [
            "as an ai", "as a language model",
            "however, it is important to note",
            "additionally, it is worth mentioning",
            "it is essential to", "moreover,"
        ]

        try:
            words = word_tokenize(text.lower())
            unique_words = set(words)
            lexical_diversity = len(unique_words) / len(words) if words else 0

            sentences = sent_tokenize(text)
            if sentences:
                lengths = [len(s.split()) for s in sentences]
                avg_len = sum(lengths) / len(sentences)
                variance = sum(
                    (l - avg_len) ** 2 for l in lengths) / len(sentences)
            else:
                avg_len = 0
                variance = 0
        except Exception:
            words = text.lower().split()
            unique_words = set(words)
            lexical_diversity = len(unique_words) / len(words) if words else 0
            avg_len = 0
            variance = 0

        ai_score = 0
        pattern_matches = sum(
            1 for p in ai_patterns if p in text.lower())
        ai_score += min(0.3, pattern_matches * 0.1)

        if lexical_diversity < 0.5:
            ai_score += 0.2
        elif lexical_diversity < 0.6:
            ai_score += 0.1

        if variance < 5:
            ai_score += 0.2
        elif variance < 10:
            ai_score += 0.1

        if avg_len > 15:
            ai_score += 0.1

        return {
            'ai_score': min(ai_score, 1.0),
            'is_ai_generated': ai_score > 0.5,
            'analysis': {
                'lexical_diversity': round(lexical_diversity, 4),
                'sentence_length_variance': round(variance, 2),
                'avg_sentence_length': round(avg_len, 2),
                'pattern_matches': pattern_matches
            }
        }

    # ------------------------------------------------------------------
    # Plagiarism Checker
    # ------------------------------------------------------------------
    def check_plagiarism(self, text):
        """Check text for plagiarism using internal comparison."""
        if not text.strip():
            return {
                'plagiarism_score': 0,
                'originality_score': 1.0,
                'matches': []
            }

        common_phrases = [
            "the purpose of this", "it is important to", "in conclusion",
            "research has shown", "studies have found", "as a result",
            "on the other hand", "in addition", "for example",
            "it should be noted", "this paper discusses",
            "the results indicate", "based on the findings"
        ]

        matches = []
        text_lower = text.lower()
        for phrase in common_phrases:
            if phrase in text_lower:
                start_idx = text_lower.find(phrase)
                matches.append({
                    'phrase': phrase,
                    'position': start_idx,
                    'length': len(phrase)
                })

        plagiarism_score = min(0.5, len(matches) * 0.05)
        return {
            'plagiarism_score': plagiarism_score,
            'originality_score': 1.0 - plagiarism_score,
            'matches': matches
        }
