"""
Build local corpus for offline plagiarism detection.
This version uses pre-existing local text files instead of downloading from internet.
"""

import sys
import os
from pathlib import Path
import json

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.detection.corpus_manager import CorpusManager

print("=" * 60)
print("Jasper — Offline Corpus Builder")
print("Building local index for plagiarism detection")
print("=" * 60)

# Initialize corpus manager
corpus_mgr = CorpusManager()

# Sample corpus directory
corpus_source_dir = Path(__file__).parent.parent / "data" / "corpus_source"
corpus_source_dir.mkdir(parents=True, exist_ok=True)

# Check if sample documents exist
sample_files = list(corpus_source_dir.glob("*.txt"))

if len(sample_files) == 0:
    print("\nℹ️  No sample documents found in data/corpus_source/")
    print("\nCreating sample corpus from built-in texts...")
    
    # Create sample documents programmatically
    sample_docs = [
        {
            "title": "Artificial Intelligence Overview",
            "content": """Artificial intelligence (AI) is intelligence demonstrated by machines, as opposed to natural intelligence displayed by animals including humans. AI research has been defined as the field of study of intelligent agents, which refers to any system that perceives its environment and takes actions that maximize its chance of achieving its goals. The term artificial intelligence had previously been used to describe machines that mimic and display human cognitive skills that are associated with the human mind, such as learning and problem-solving. This definition has since been rejected by major AI researchers who now describe AI in terms of rationality and acting rationally, which does not limit how intelligence can be articulated.""",
            "source": "Built-in Sample",
            "url": ""
        },
        {
            "title": "Machine Learning Fundamentals",
            "content": """Machine learning is a method of data analysis that automates analytical model building. It is a branch of artificial intelligence based on the idea that systems can learn from data, identify patterns and make decisions with minimal human intervention. Machine learning algorithms are trained on data sets that contain many examples that include the desired inputs and outputs. The algorithm then tries to identify patterns in the data that map the inputs to the outputs.""",
            "source": "Built-in Sample",
            "url": ""
        },
        {
            "title": "Data Science Introduction",
            "content": """Data science is an interdisciplinary field that uses scientific methods, processes, algorithms and systems to extract knowledge and insights from structured and unstructured data. Data science is related to data mining, machine learning and big data. Data science is a concept to unify statistics, data analysis, informatics, and their related methods in order to understand and analyze actual phenomena with data.""",
            "source": "Built-in Sample",
            "url": ""
        },
        {
            "title": "Natural Language Processing",
            "content": """Natural language processing (NLP) is a subfield of linguistics, computer science, and artificial intelligence concerned with the interactions between computers and human language, in particular how to program computers to process and analyze large amounts of natural language data. The goal is a computer capable of understanding the contents of documents, including the contextual nuances of the language within them.""",
            "source": "Built-in Sample",
            "url": ""
        },
        {
            "title": "Deep Learning Networks",
            "content": """Deep learning is part of a broader family of machine learning methods based on artificial neural networks with representation learning. Learning can be supervised, semi-supervised or unsupervised. Deep-learning architectures such as deep neural networks, deep belief networks, deep reinforcement learning, recurrent neural networks and convolutional neural networks have been applied to fields including computer vision, speech recognition, natural language processing, machine translation, bioinformatics, drug design, medical image analysis, material inspection and board game programs.""",
            "source": "Built-in Sample",
            "url": ""
        },
    ]
    
    # Add more sample documents to reach 50+
    additional_topics = [
        "Computer Vision", "Reinforcement Learning", "Neural Architecture Search",
        "Transfer Learning", "Generative Adversarial Networks", "Transformer Models",
        "BERT and Language Models", "Computer Graphics", "Quantum Computing",
        "Blockchain Technology", "Cloud Computing", "Edge Computing",
        "Internet of Things", "Cybersecurity", "Software Engineering",
        "Database Systems", "Distributed Systems", "Operating Systems",
        "Computer Networks", "Web Development", "Mobile Development",
        "DevOps Practices", "Agile Methodology", "Software Testing",
        "Version Control Systems", "Continuous Integration"
    ]
    
    for i, topic in enumerate(additional_topics, start=6):
        sample_docs.append({
            "title": topic,
            "content": f"""{topic} is an important area of study in computer science and technology. It encompasses various methodologies, techniques, and best practices that are essential for modern software development and technological advancement. Understanding {topic} requires both theoretical knowledge and practical experience. Researchers and practitioners continue to develop new approaches and improvements in this field.""",
            "source": "Built-in Sample",
            "url": ""
        })
    
    # Index sample documents
    print(f"\nIndexing {len(sample_docs)} sample documents...")
    for i, doc in enumerate(sample_docs):
        doc_id = f"sample_{i+1:03d}"
        corpus_mgr.add_document(
            doc_id=doc_id,
            title=doc['title'],
            text=doc['content'],
            source=doc['source'],
            url=doc['url']
        )
        print(f"  [{i+1}/{len(sample_docs)}] {doc['title']}")

else:
    print(f"\nFound {len(sample_files)} text files in corpus_source/")
    print("\nIndexing local documents...")
    
    for i, txt_file in enumerate(sample_files):
        with open(txt_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        doc_id = txt_file.stem
        title = txt_file.stem.replace('_', ' ').title()
        
        corpus_mgr.add_document(
            doc_id=doc_id,
            title=title,
            text=content,
            source="Local File",
            url=""
        )
        print(f"  [{i+1}/{len(sample_files)}] {title}")

# Save index
print("\nSaving FAISS index and metadata...")
corpus_mgr.save()

# Get statistics
stats = corpus_mgr.get_stats()
print("\n" + "=" * 60)
print("Corpus built successfully!")
print(f"Total documents: {stats['total_documents']}")
print(f"Total vectors: {stats['total_vectors']}")
print(f"Index size: {stats['index_size_mb']:.2f} MB")
print(f"Storage: {corpus_mgr.corpus_dir}")
print("\nNOTE: This corpus runs 100% offline.")
print("Add more .txt files to data/corpus_source/ and re-run this script to expand the corpus.")
print("=" * 60)
