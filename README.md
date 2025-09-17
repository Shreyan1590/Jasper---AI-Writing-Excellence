
# Jasper - AI Writing Excellence

A comprehensive, all-in-one desktop application for advanced text processing tasks, built with Python and PyQt5. This application combines multiple AI-powered text processing capabilities into a single, user-friendly interface.

![Version](https://img.shields.io/badge/Version-2.0.0-blue.svg) ![Python](https://img.shields.io/badge/Python-3.8%252B-green.svg) ![License](https://img.shields.io/badge/License-MIT-yellow.svg) ![Platform](https://img.shields.io/badge/Platform-Windows%2520%257C%2520macOS%2520%257C%2520Linux-lightgrey.svg)

## 🌟 Features

### 🔄 AI to Human Text Converter
Transform AI-generated content into natural, human-like text with improved readability and conversational flow.

### 📝 Text Summarizer
- **Advanced Transformer Models**: Utilizes Facebook's BART model for abstractive summarization  
- **Extractive Fallback**: NLTK-based extractive summarization when transformers are unavailable  
- **Customizable Length**: Short, medium, and long summary options  

### 🔄 Paraphrasing Tool
- Generate multiple variations of your text while preserving the original meaning  
- Word substitution with contextual synonyms  
- Sentence structure reorganization  
- Multiple output variations  

### ✍️ Grammar Checker
- Real-time grammar and spelling correction  
- Detailed error explanations and suggestions  
- Side-by-side comparison of original and corrected text  

### 🤖 AI Content Detector
- Advanced heuristics to identify AI-generated content  
- Lexical diversity analysis  
- Sentence structure patterns  
- Common AI text pattern recognition  
- Confidence scoring system  

### 🔍 Plagiarism Checker
- Internal phrase matching algorithm  
- Common academic phrase detection  
- Originality scoring system  
- Detailed match reporting  

## 🚀 Installation

### Prerequisites
- Python 3.8 or higher  
- 4GB RAM minimum (8GB recommended)  
- 2GB free disk space  

### Automated Installation
```bash
git clone https://github.com/Shreyan1590/Jasper---AI-Writing-Excellence.git
cd Jasper---AI-Writing-Excellence.git
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

### Manual Installation
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install PyQt5==5.15.9 nltk==3.8.1 spacy==3.8.7
pip install transformers==4.36.2 torch==2.8.0
pip install requests==2.31.0 numpy==2.2.6
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords'); nltk.download('punkt_tab')"
python -m spacy download en_core_web_sm
```

### 📦 Building the Executable

#### Using PyInstaller
```bash
python build.py
# Executable at build/dist/Jasper.exe
```

#### Advanced Build Options
```bash
python build.py --icon=assets/icon.ico
python build.py --windowed
python build.py --onefile --distpath=dist
```

## 🎯 Usage

### Basic Operation
1. Launch the application  
2. Paste text into input area or load from file  
3. Select processing tab  
4. Click process  
5. Review output  

### File Operations
- Load Text: `File → Open` or Load button  
- Save Results: Right-click output → Save As  
- Export Options: Copy or save as text files  

### Advanced Features
- Batch Processing  
- Custom Settings  
- History (up to 10 sessions)  

## 🏗️ Architecture

```
Jasper/
├── main.py
├── processor.py
├── gui.py
├── utils.py
├── build.py
├── requirements.txt
└── assets/
    ├── icons/
    ├── styles/
    └── models/
```

### Technology Stack
- Frontend: PyQt5 with QSS styling  
- NLP Core: spaCy, NLTK, Transformers  
- AI Models: BART, heuristic algorithms  
- Threading: QThread for non-blocking ops  
- Packaging: PyInstaller  

## ⚙️ Configuration

### config.ini Example
```ini
[UI]
language = en
theme = dark
font_size = 12
max_history = 10

[Processing]
max_text_length = 10000
default_summary_length = medium
auto_save_results = true

[Models]
use_gpu = false
model_cache_size = 1024
download_missing_models = true
```

### Environment Variables
```bash
export TEXT_SUITE_CACHE_DIR="/path/to/cache"
export TEXT_SUITE_LOG_LEVEL="DEBUG"
export TEXT_SUITE_GPU_ENABLED="true"
```

## 🔧 Advanced Customization

### Adding New Processors
- Implement `process_text(text, **kwargs)` in `processor.py`  
- Register in main app  
- Add UI elements in `gui.py`

### Custom Model Integration
```python
from transformers import AutoModel, AutoTokenizer

class CustomProcessor:
    def __init__(self):
        self.model = AutoModel.from_pretrained("your-model")
        self.tokenizer = AutoTokenizer.from_pretrained("your-model")

    def process(self, text):
        return processed_text
```

### Theme Customization
```css
/* assets/styles/custom_dark.qss */
QMainWindow {
    background-color: #2b2b2b;
    color: #ffffff;
}

QTextEdit {
    background-color: #3c3f41;
    color: #a9b7c6;
    border: 1px solid #555555;
}
```

## 📊 Performance

| Operation            | Avg Time (1000 words) |
|----------------------|-----------------------|
| AI to Human          | 0.5-1.5 sec           |
| Summarization        | 2-5 sec               |
| Paraphrasing         | 1-3 sec               |
| Grammar Check        | 0.3-1 sec             |
| AI Detection         | 0.2-0.8 sec           |
| Plagiarism Check     | 0.1-0.5 sec           |

## 🐛 Troubleshooting

### NLTK Data Missing
```bash
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords'); nltk.download('punkt_tab'); nltk.download('averaged_perceptron_tagger')"
```

### spaCy Model Issues
```bash
python -m spacy download en_core_web_sm --force
```

### GPU Acceleration
```bash
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

### Debug Mode
```bash
python main.py --debug
```
Logs:  
- Windows: `%APPDATA%/Jasper/logs/`  
- macOS: `~/Library/Logs/Jasper/`  
- Linux: `~/.local/share/Jasper/logs/`  

## 🤝 Contributing

Development Setup
```bash
git clone https://github.com/Shreyan1590/Jasper---AI-Writing-Excellence.git
pip install -r requirements-dev.txt
pre-commit install
pytest tests/
```

### Code Style
- Black (formatting)  
- Flake8 (linting)  
- MyPy (type checking)  
- Pre-commit hooks  

## 📄 License

MIT License – see LICENSE file

## 🙏 Acknowledgments
- Facebook Research for BART  
- Explosion AI for spaCy  
- NLTK Team  
- Hugging Face for Transformers  
- PyQt5 Developers  

## 📞 Support

📧 Email: shreyanofficial25@gmail.com
🐛 Issue Tracker  
💬 Discord Community  
📖 Documentation  

## 🔗 Related Projects
- Advanced Text Analytics Toolkit  
- AI Content Detection API  
- Multilingual Text Processor  

Made by [Shreyan S](https://shreyan-portfolio.vercel.app/) with ❤️ by Shreyan S

