import sys
import os
import requests
import nltk
import ssl
import urllib.request
import zipfile
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize
import spacy
import re
from difflib import SequenceMatcher
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QTextEdit, QPushButton, QLabel, QTabWidget, QComboBox, 
                             QSpinBox, QGroupBox, QProgressBar, QFileDialog, QMessageBox,
                             QSplitter, QCheckBox)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QFont, QIcon, QPalette, QColor

# Fix SSL certificate issues for NLTK downloads
try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context

# Download all required NLTK data with error handling
def download_nltk_data():
    nltk_data_path = os.path.join(os.path.expanduser('~'), 'nltk_data')
    if not os.path.exists(nltk_data_path):
        os.makedirs(nltk_data_path)
    
    required_data = [
        'punkt', 'stopwords', 'punkt_tab', 'averaged_perceptron_tagger', 'wordnet'
    ]
    
    for data in required_data:
        try:
            print(f"Checking/Downloading {data}...")
            nltk.download(data, quiet=True)
        except Exception as e:
            print(f"Failed to download {data}: {e}")
            # Try alternative download method
            try:
                if data == 'punkt_tab':
                    # Manual download for punkt_tab
                    url = "https://raw.githubusercontent.com/nltk/nltk_data/gh-pages/packages/tokenizers/punkt_tab.zip"
                    download_path = os.path.join(nltk_data_path, 'tokenizers', 'punkt_tab.zip')
                    os.makedirs(os.path.dirname(download_path), exist_ok=True)
                    
                    with urllib.request.urlopen(url) as response:
                        with open(download_path, 'wb') as out_file:
                            out_file.write(response.read())
                    
                    with zipfile.ZipFile(download_path, 'r') as zip_ref:
                        zip_ref.extractall(os.path.join(nltk_data_path, 'tokenizers'))
                    
                    os.remove(download_path)
                    print("Manually downloaded punkt_tab")
            except Exception as manual_error:
                print(f"Manual download also failed: {manual_error}")

# Download NLTK data on import
download_nltk_data()

class TextProcessor:
    def __init__(self):
        self.nlp = None
        self.summarizer = None
        self._initialize_models()
    
    def _initialize_models(self):
        """Initialize models in a way that won't crash the application if some fail"""
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except:
            print("spaCy model not found, some features may be limited")
        
        # Try to load summarization model but don't crash if it fails
        try:
            from transformers import pipeline
            self.summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
        except ImportError:
            print("Transformers not available, using fallback summarization")
        except Exception as e:
            print(f"Summarization model could not be loaded: {e}")
    
    def ai_to_human_converter(self, text):
        """Convert AI-generated text to more human-like text"""
        if not text.strip():
            return text
            
        # Simple transformations
        text = re.sub(r"\b(is not)\b", "isn't", text)
        text = re.sub(r"\b(are not)\b", "aren't", text)
        text = re.sub(r"\b(cannot)\b", "can't", text)
        text = re.sub(r"\b(will not)\b", "won't", text)
        text = re.sub(r"\b(does not)\b", "doesn't", text)
        text = re.sub(r"\b(did not)\b", "didn't", text)
        text = re.sub(r"\b(has not)\b", "hasn't", text)
        text = re.sub(r"\b(have not)\b", "haven't", text)
        text = re.sub(r"\b(had not)\b", "hadn't", text)
        text = re.sub(r"\b(would not)\b", "wouldn't", text)
        text = re.sub(r"\b(could not)\b", "couldn't", text)
        text = re.sub(r"\b(should not)\b", "shouldn't", text)
        
        # Add sentence variety
        try:
            sentences = sent_tokenize(text)
            if len(sentences) > 2:
                conversational_starters = ["Actually,", "Well,", "You know,", "I think", "In my opinion,"]
                for i in range(1, len(sentences), 3):
                    if i < len(sentences) and not sentences[i].startswith(tuple(conversational_starters)):
                        starter = conversational_starters[i % len(conversational_starters)]
                        sentences[i] = f"{starter} {sentences[i][0].lower() + sentences[i][1:]}"
            
            return ' '.join(sentences)
        except:
            return text  # Fallback if tokenization fails
    
    def summarize_text(self, text, max_length=130, min_length=30):
        """Summarize text using transformer models or fallback"""
        if not text.strip():
            return "No text to summarize"
            
        try:
            if self.summarizer:
                summary = self.summarizer(text, max_length=max_length, min_length=min_length, do_sample=False)
                return summary[0]['summary_text']
            else:
                # Fallback extractive summarization
                return self._extractive_summarization(text, max_sentences=3)
        except Exception as e:
            return f"Error in summarization: {str(e)}"
    
    def _extractive_summarization(self, text, max_sentences=3):
        """Fallback extractive summarization using NLTK"""
        try:
            sentences = sent_tokenize(text)
            if len(sentences) <= max_sentences:
                return text
                
            # Calculate word frequencies (excluding stopwords)
            stop_words = set(stopwords.words("english"))
            words = word_tokenize(text.lower())
            freq_table = {}
            
            for word in words:
                if word in stop_words:
                    continue
                if word.isalnum():
                    freq_table[word] = freq_table.get(word, 0) + 1
            
            # Score sentences based on word frequencies
            sentence_scores = {}
            for i, sentence in enumerate(sentences):
                for word in word_tokenize(sentence.lower()):
                    if word in freq_table:
                        sentence_scores[i] = sentence_scores.get(i, 0) + freq_table[word]
            
            # Get top sentences
            if not sentence_scores:
                return ". ".join(sentences[:max_sentences]) + "."
                
            sorted_sentences = sorted(sentence_scores.items(), key=lambda x: x[1], reverse=True)
            top_sentence_indices = [idx for idx, score in sorted_sentences[:max_sentences]]
            top_sentence_indices.sort()
            
            return ". ".join([sentences[i] for i in top_sentence_indices]) + "."
        except:
            # Ultimate fallback - return first few sentences
            sentences = text.split('.')
            return '.'.join(sentences[:max_sentences]) + '.'
    
    def paraphrase_text(self, text, variations=1):
        """Generate paraphrased versions of text"""
        if not text.strip():
            return ["No text to paraphrase"]
            
        # Simple rule-based paraphrasing
        paraphrases = []
        
        # Variation 1: Replace words with synonyms (simplified)
        paraphrase1 = text.replace(" important", " crucial")
        paraphrase1 = paraphrase1.replace(" however", " though")
        paraphrase1 = paraphrase1.replace(" additionally", " also")
        paraphrase1 = paraphrase1.replace(" therefore", " thus")
        paraphrases.append(paraphrase1)
        
        # Variation 2: Change sentence structure
        if variations > 1 and ". " in text:
            try:
                sentences = sent_tokenize(text)
                if len(sentences) > 1:
                    paraphrase2 = ". ".join([sentences[1], sentences[0]] + sentences[2:])
                    paraphrases.append(paraphrase2)
            except:
                # If tokenization fails, use simple method
                parts = text.split('. ')
                if len(parts) > 1:
                    paraphrase2 = ". ".join([parts[1], parts[0]] + parts[2:])
                    paraphrases.append(paraphrase2)
        
        # Add more variations if requested
        if variations > 2:
            for i in range(2, variations):
                if i == 2:
                    # Simple word substitution
                    paraphrase = text.replace(" the ", " a ").replace(" is ", " was ")
                    paraphrases.append(paraphrase)
                else:
                    paraphrases.append(f"Paraphrase {i+1}: {text}")
        
        return paraphrases
    
    def check_grammar(self, text):
        """Check and correct grammar in text (simplified version)"""
        if not text.strip():
            return {"original": text, "corrected": text, "changes": []}
            
        # Simple grammar correction rules
        corrected = text
        
        # Common errors
        corrections = [
            (r"\bi\b", "I"),  # lowercase i to I
            (r"your\b", "you're"),  # your to you're in some contexts
            (r"their\b", "they're"),  # their to they're in some contexts
            (r"its\b", "it's"),  # its to it's in some contexts
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
                    'position': 0  # Simplified position
                })
        
        return {
            'original': text,
            'corrected': corrected,
            'changes': changes
        }
    
    def detect_ai_content(self, text):
        """Detect if text was likely generated by AI"""
        if not text.strip():
            return {'ai_score': 0, 'is_ai_generated': False, 'analysis': {}}
        
        # Heuristic-based detection
        ai_patterns = [
            "as an AI", "as a language model", "however, it is important to note",
            "additionally, it is worth mentioning", "it is essential to", "moreover,"
        ]
        
        try:
            words = word_tokenize(text.lower())
            unique_words = set(words)
            lexical_diversity = len(unique_words) / len(words) if words else 0
            
            sentences = sent_tokenize(text)
            if sentences:
                sentence_lengths = [len(sent.split()) for sent in sentences]
                avg_sentence_length = sum(sentence_lengths) / len(sentences)
                sentence_length_variance = sum((length - avg_sentence_length) ** 2 for length in sentence_lengths) / len(sentences)
            else:
                avg_sentence_length = 0
                sentence_length_variance = 0
        except:
            # Fallback if tokenization fails
            words = text.lower().split()
            unique_words = set(words)
            lexical_diversity = len(unique_words) / len(words) if words else 0
            avg_sentence_length = 0
            sentence_length_variance = 0
        
        # Score calculation
        ai_score = 0
        
        # Pattern matching
        pattern_matches = sum(1 for pattern in ai_patterns if pattern in text.lower())
        ai_score += min(0.3, pattern_matches * 0.1)
        
        # Lexical diversity (AI text often has lower diversity)
        if lexical_diversity < 0.5:
            ai_score += 0.2
        elif lexical_diversity < 0.6:
            ai_score += 0.1
        
        # Sentence length consistency (AI text often has very consistent sentence lengths)
        if sentence_length_variance < 5:
            ai_score += 0.2
        elif sentence_length_variance < 10:
            ai_score += 0.1
        
        # Average sentence length (AI text often has medium to long sentences)
        if avg_sentence_length > 15:
            ai_score += 0.1
        
        return {
            'ai_score': min(ai_score, 1.0),
            'is_ai_generated': ai_score > 0.5,
            'analysis': {
                'lexical_diversity': lexical_diversity,
                'sentence_length_variance': sentence_length_variance,
                'avg_sentence_length': avg_sentence_length,
                'pattern_matches': pattern_matches
            }
        }
    
    def check_plagiarism(self, text):
        """Check text for plagiarism using simple internal comparison"""
        if not text.strip():
            return {'plagiarism_score': 0, 'originality_score': 1.0, 'matches': []}
        
        # This is a simplified version - real plagiarism check would use external sources
        common_phrases = [
            "the purpose of this", "it is important to", "in conclusion", 
            "research has shown", "studies have found", "as a result",
            "on the other hand", "in addition", "for example", "it should be noted",
            "this paper discusses", "the results indicate", "based on the findings"
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


class ProcessingThread(QThread):
    """Thread for processing text to avoid UI freezing"""
    finished = pyqtSignal(object)
    progress = pyqtSignal(int)
    
    def __init__(self, processor, function, *args):
        super().__init__()
        self.processor = processor
        self.function = function
        self.args = args
    
    def run(self):
        try:
            self.progress.emit(25)
            result = self.function(*self.args)
            self.progress.emit(100)
            self.finished.emit(result)
        except Exception as e:
            self.finished.emit({"error": str(e)})


class TextProcessingApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.processor = TextProcessor()
        self.current_file = None
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle("Jasper - AI Writing Excellence.")
        self.setGeometry(100, 100, 1200, 800)
        
        # Central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # Create tab widget
        self.tabs = QTabWidget()
        main_layout.addWidget(self.tabs)
        
        # Create tabs
        self.create_text_input_tab()
        self.create_ai_to_human_tab()
        self.create_summarizer_tab()
        self.create_paraphraser_tab()
        self.create_grammar_tab()
        self.create_ai_detector_tab()
        self.create_plagiarism_tab()
        
        # Status bar
        self.statusBar().showMessage("Ready")
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        main_layout.addWidget(self.progress_bar)
    
    def create_text_input_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Input section
        input_group = QGroupBox("Input Text")
        input_layout = QVBoxLayout(input_group)
        
        self.input_text = QTextEdit()
        self.input_text.setPlaceholderText("Paste your text here or load from a file...")
        input_layout.addWidget(self.input_text)
        
        # Button layout
        button_layout = QHBoxLayout()
        self.load_btn = QPushButton("Load from File")
        self.load_btn.clicked.connect(self.load_file)
        button_layout.addWidget(self.load_btn)
        
        self.clear_btn = QPushButton("Clear Text")
        self.clear_btn.clicked.connect(self.clear_text)
        button_layout.addWidget(self.clear_btn)
        
        input_layout.addLayout(button_layout)
        layout.addWidget(input_group)
        
        # Output section (for quick results)
        output_group = QGroupBox("Quick Actions")
        output_layout = QVBoxLayout(output_group)
        
        quick_btn_layout = QHBoxLayout()
        self.quick_summarize_btn = QPushButton("Quick Summarize")
        self.quick_summarize_btn.clicked.connect(lambda: self.quick_process("summarize"))
        quick_btn_layout.addWidget(self.quick_summarize_btn)
        
        self.quick_grammar_btn = QPushButton("Quick Grammar Check")
        self.quick_grammar_btn.clicked.connect(lambda: self.quick_process("grammar"))
        quick_btn_layout.addWidget(self.quick_grammar_btn)
        
        output_layout.addLayout(quick_btn_layout)
        
        self.quick_output = QTextEdit()
        self.quick_output.setReadOnly(True)
        output_layout.addWidget(self.quick_output)
        
        layout.addWidget(output_group)
        self.tabs.addTab(tab, "Text Input")
    
    def create_ai_to_human_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        description = QLabel("Convert AI-generated text to more human-like text:")
        layout.addWidget(description)
        
        # Button
        self.humanize_btn = QPushButton("Humanize Text")
        self.humanize_btn.clicked.connect(self.humanize_text)
        layout.addWidget(self.humanize_btn)
        
        # Output
        self.humanize_output = QTextEdit()
        self.humanize_output.setReadOnly(True)
        layout.addWidget(self.humanize_output)
        
        self.tabs.addTab(tab, "AI to Human")
    
    def create_summarizer_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Options
        options_layout = QHBoxLayout()
        options_layout.addWidget(QLabel("Summary Length:"))
        
        self.summary_length = QComboBox()
        self.summary_length.addItems(["Short", "Medium", "Long"])
        self.summary_length.setCurrentIndex(1)
        options_layout.addWidget(self.summary_length)
        
        options_layout.addStretch()
        layout.addLayout(options_layout)
        
        # Button
        self.summarize_btn = QPushButton("Summarize Text")
        self.summarize_btn.clicked.connect(self.summarize_text)
        layout.addWidget(self.summarize_btn)
        
        # Output
        self.summary_output = QTextEdit()
        self.summary_output.setReadOnly(True)
        layout.addWidget(self.summary_output)
        
        self.tabs.addTab(tab, "Summarizer")
    
    def create_paraphraser_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Options
        options_layout = QHBoxLayout()
        options_layout.addWidget(QLabel("Number of variations:"))
        
        self.variation_count = QSpinBox()
        self.variation_count.setMinimum(1)
        self.variation_count.setMaximum(5)
        self.variation_count.setValue(2)
        options_layout.addWidget(self.variation_count)
        
        options_layout.addStretch()
        layout.addLayout(options_layout)
        
        # Button
        self.paraphrase_btn = QPushButton("Paraphrase Text")
        self.paraphrase_btn.clicked.connect(self.paraphrase_text)
        layout.addWidget(self.paraphrase_btn)
        
        # Output
        self.paraphrase_output = QTextEdit()
        self.paraphrase_output.setReadOnly(True)
        layout.addWidget(self.paraphrase_output)
        
        self.tabs.addTab(tab, "Paraphraser")
    
    def create_grammar_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        splitter = QSplitter(Qt.Horizontal)
        
        # Original text
        original_group = QGroupBox("Original Text")
        original_layout = QVBoxLayout(original_group)
        self.grammar_original = QTextEdit()
        self.grammar_original.setReadOnly(True)
        original_layout.addWidget(self.grammar_original)
        splitter.addWidget(original_group)
        
        # Corrected text
        corrected_group = QGroupBox("Corrected Text")
        corrected_layout = QVBoxLayout(corrected_group)
        self.grammar_corrected = QTextEdit()
        self.grammar_corrected.setReadOnly(True)
        corrected_layout.addWidget(self.grammar_corrected)
        splitter.addWidget(corrected_group)
        
        splitter.setSizes([400, 400])
        layout.addWidget(splitter)
        
        # Button
        self.grammar_btn = QPushButton("Check Grammar")
        self.grammar_btn.clicked.connect(self.check_grammar)
        layout.addWidget(self.grammar_btn)
        
        # Errors list
        self.grammar_errors = QTextEdit()
        self.grammar_errors.setReadOnly(True)
        self.grammar_errors.setMaximumHeight(150)
        layout.addWidget(self.grammar_errors)
        
        self.tabs.addTab(tab, "Grammar Checker")
    
    def create_ai_detector_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Button
        self.ai_detect_btn = QPushButton("Detect AI Content")
        self.ai_detect_btn.clicked.connect(self.detect_ai_content)
        layout.addWidget(self.ai_detect_btn)
        
        # Result
        self.ai_result = QLabel("AI detection result will appear here")
        self.ai_result.setAlignment(Qt.AlignCenter)
        self.ai_result.setStyleSheet("font-size: 16px; padding: 20px;")
        layout.addWidget(self.ai_result)
        
        # Details
        self.ai_details = QTextEdit()
        self.ai_details.setReadOnly(True)
        self.ai_details.setMaximumHeight(200)
        layout.addWidget(self.ai_details)
        
        self.tabs.addTab(tab, "AI Detector")
    
    def create_plagiarism_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Button
        self.plagiarism_btn = QPushButton("Check for Plagiarism")
        self.plagiarism_btn.clicked.connect(self.check_plagiarism)
        layout.addWidget(self.plagiarism_btn)
        
        # Result
        self.plagiarism_result = QLabel("Plagiarism check result will appear here")
        self.plagiarism_result.setAlignment(Qt.AlignCenter)
        self.plagiarism_result.setStyleSheet("font-size: 16px; padding: 20px;")
        layout.addWidget(self.plagiarism_result)
        
        # Details
        self.plagiarism_details = QTextEdit()
        self.plagiarism_details.setReadOnly(True)
        self.plagiarism_details.setMaximumHeight(200)
        layout.addWidget(self.plagiarism_details)
        
        self.tabs.addTab(tab, "Plagiarism Checker")
    
    def load_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open Text File", "", "Text Files (*.txt);;All Files (*)"
        )
        
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    content = file.read()
                    self.input_text.setPlainText(content)
                    self.current_file = file_path
                    self.statusBar().showMessage(f"Loaded: {file_path}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Could not load file: {str(e)}")
    
    def clear_text(self):
        self.input_text.clear()
        self.current_file = None
        self.statusBar().showMessage("Text cleared")
    
    def get_input_text(self):
        return self.input_text.toPlainText().strip()
    
    def quick_process(self, action):
        text = self.get_input_text()
        if not text:
            QMessageBox.warning(self, "Warning", "Please enter some text first")
            return
        
        if action == "summarize":
            result = self.processor.summarize_text(text)
            self.quick_output.setPlainText(result)
            self.statusBar().showMessage("Text summarized")
        elif action == "grammar":
            result = self.processor.check_grammar(text)
            self.quick_output.setPlainText(result['corrected'])
            self.statusBar().showMessage("Grammar checked")
    
    def humanize_text(self):
        text = self.get_input_text()
        if not text:
            QMessageBox.warning(self, "Warning", "Please enter some text first")
            return
        
        self.start_processing(
            self.processor.ai_to_human_converter, 
            [text],
            self.humanize_output,
            "Text humanized"
        )
    
    def summarize_text(self):
        text = self.get_input_text()
        if not text:
            QMessageBox.warning(self, "Warning", "Please enter some text first")
            return
        
        # Determine max_length based on selection
        length_option = self.summary_length.currentText()
        if length_option == "Short":
            max_length = 80
        elif length_option == "Medium":
            max_length = 130
        else:  # Long
            max_length = 200
        
        self.start_processing(
            self.processor.summarize_text, 
            [text, max_length],
            self.summary_output,
            "Text summarized"
        )
    
    def paraphrase_text(self):
        text = self.get_input_text()
        if not text:
            QMessageBox.warning(self, "Warning", "Please enter some text first")
            return
        
        variations = self.variation_count.value()
        
        self.start_processing(
            self.processor.paraphrase_text, 
            [text, variations],
            self.paraphrase_output,
            "Text paraphrased",
            lambda result: "\n\n--- Variation ---\n\n".join(result) if isinstance(result, list) else str(result)
        )
    
    def check_grammar(self):
        text = self.get_input_text()
        if not text:
            QMessageBox.warning(self, "Warning", "Please enter some text first")
            return
        
        self.start_processing(
            self.processor.check_grammar, 
            [text],
            None,
            "Grammar checked",
            self.handle_grammar_result
        )
    
    def handle_grammar_result(self, result):
        self.grammar_original.setPlainText(result['original'])
        self.grammar_corrected.setPlainText(result['corrected'])
        
        errors_text = ""
        for error in result['changes']:
            errors_text += f"Position {error['position']}: {error['message']}\n"
            errors_text += f"Suggested: {', '.join(error['suggestions'][:3])}\n\n"
        
        self.grammar_errors.setPlainText(errors_text if errors_text else "No grammar errors found!")
    
    def detect_ai_content(self):
        text = self.get_input_text()
        if not text:
            QMessageBox.warning(self, "Warning", "Please enter some text first")
            return
        
        self.start_processing(
            self.processor.detect_ai_content, 
            [text],
            None,
            "AI detection completed",
            self.handle_ai_result
        )
    
    def handle_ai_result(self, result):
        if 'error' in result:
            self.ai_result.setText(f"Error: {result['error']}")
            self.ai_details.setPlainText("")
            return
        
        score = result['ai_score']
        is_ai = result['is_ai_generated']
        analysis = result['analysis']
        
        # Set result text
        if is_ai:
            self.ai_result.setText(f"AI-Generated Content Detected ({score*100:.1f}% confidence)")
            self.ai_result.setStyleSheet("color: red; font-size: 16px; padding: 20px;")
        else:
            self.ai_result.setText(f"Human-Like Content Detected ({(1-score)*100:.1f}% confidence)")
            self.ai_result.setStyleSheet("color: green; font-size: 16px; padding: 20px;")
        
        # Set details
        details = f"Analysis Details:\n"
        details += f"Lexical Diversity: {analysis['lexical_diversity']:.3f}\n"
        details += f"Sentence Length Variance: {analysis['sentence_length_variance']:.2f}\n"
        details += f"Average Sentence Length: {analysis['avg_sentence_length']:.2f}\n"
        details += f"AI Pattern Matches: {analysis['pattern_matches']}\n"
        
        self.ai_details.setPlainText(details)
    
    def check_plagiarism(self):
        text = self.get_input_text()
        if not text:
            QMessageBox.warning(self, "Warning", "Please enter some text first")
            return
        
        self.start_processing(
            self.processor.check_plagiarism, 
            [text],
            None,
            "Plagiarism check completed",
            self.handle_plagiarism_result
        )
    
    def handle_plagiarism_result(self, result):
        if 'error' in result:
            self.plagiarism_result.setText(f"Error: {result['error']}")
            self.plagiarism_details.setPlainText("")
            return
        
        score = result['plagiarism_score']
        originality = result['originality_score']
        matches = result['matches']
        
        # Set result text
        if score > 0.7:
            color = "red"
            text = "High Plagiarism Detected"
        elif score > 0.3:
            color = "orange"
            text = "Moderate Plagiarism Detected"
        else:
            color = "green"
            text = "Original Content"
        
        self.plagiarism_result.setText(f"{text} ({originality*100:.1f}% original)")
        self.plagiarism_result.setStyleSheet(f"color: {color}; font-size: 16px; padding: 20px;")
        
        # Set details
        details = f"Plagiarism Score: {score:.3f}\n"
        details += f"Originality Score: {originality:.3f}\n\n"
        
        if matches:
            details += f"Found {len(matches)} potential plagiarism matches:\n"
            for match in matches:
                details += f"- '{match['phrase']}' at position {match['position']}\n"
        else:
            details += "No significant plagiarism detected."
        
        self.plagiarism_details.setPlainText(details)
    
    def start_processing(self, func, args, output_widget, success_message, result_handler=None):
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.statusBar().showMessage("Processing...")
        
        # Disable buttons during processing
        for btn in self.findChildren(QPushButton):
            btn.setEnabled(False)
        
        self.thread = ProcessingThread(self.processor, func, *args)
        self.thread.finished.connect(
            lambda result: self.processing_finished(result, output_widget, success_message, result_handler)
        )
        self.thread.progress.connect(self.progress_bar.setValue)
        self.thread.start()
    
    def processing_finished(self, result, output_widget, success_message, result_handler):
        self.progress_bar.setVisible(False)
        
        # Re-enable buttons
        for btn in self.findChildren(QPushButton):
            btn.setEnabled(True)
        
        if 'error' in result:
            self.statusBar().showMessage(f"Error: {result['error']}")
            QMessageBox.critical(self, "Error", f"An error occurred: {result['error']}")
            return
        
        if result_handler:
            result_handler(result)
        elif output_widget:
            output_widget.setPlainText(str(result))
        
        self.statusBar().showMessage(success_message)


def main():
    app = QApplication(sys.argv)
    
    # Set application style
    app.setStyle('Fusion')
    
    # Create and show the main window
    window = TextProcessingApp()
    window.show()
    
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()