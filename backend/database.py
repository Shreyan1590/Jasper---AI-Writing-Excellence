"""
SQLite Database Manager for Local Storage
Handles document indexing and detection history (offline mode).
"""

import sqlite3
import json
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime


class LocalDatabase:
    def __init__(self, db_path: str = "data/jasper.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.init_db()
    
    def init_db(self):
        """Initialize database schema."""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        # Documents table for corpus
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS documents (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                source TEXT,
                url TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Detection history table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS detection_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                input_text TEXT NOT NULL,
                detection_type TEXT NOT NULL,
                result TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # User settings table (future use)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def add_document(self, doc_id: str, title: str, content: str, source: str = "", url: str = ""):
        """Add a document to the corpus."""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO documents (id, title, content, source, url)
            VALUES (?, ?, ?, ?, ?)
        ''', (doc_id, title, content, source, url))
        
        conn.commit()
        conn.close()
    
    def get_all_documents(self) -> List[Dict]:
        """Retrieve all documents."""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute('SELECT id, title, content, source, url FROM documents')
        rows = cursor.fetchall()
        conn.close()
        
        return [
            {
                'id': row[0],
                'title': row[1],
                'content': row[2],
                'source': row[3],
                'url': row[4]
            }
            for row in rows
        ]
    
    def get_document_count(self) -> int:
        """Get total number of documents."""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*) FROM documents')
        count = cursor.fetchone()[0]
        conn.close()
        
        return count
    
    def save_detection_result(self, input_text: str, detection_type: str, result: Dict):
        """Save detection result to history."""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO detection_history (input_text, detection_type, result)
            VALUES (?, ?, ?)
        ''', (input_text[:1000], detection_type, json.dumps(result)))  # Limit input text size
        
        conn.commit()
        conn.close()
    
    def get_detection_history(self, limit: int = 50) -> List[Dict]:
        """Retrieve recent detection history."""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, input_text, detection_type, result, created_at
            FROM detection_history
            ORDER BY created_at DESC
            LIMIT ?
        ''', (limit,))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [
            {
                'id': row[0],
                'input_text': row[1],
                'detection_type': row[2],
                'result': json.loads(row[3]),
                'created_at': row[4]
            }
            for row in rows
        ]
    
    def clear_history(self):
        """Clear all detection history."""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM detection_history')
        conn.commit()
        conn.close()
    
    def get_setting(self, key: str) -> Optional[str]:
        """Get a setting value."""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute('SELECT value FROM settings WHERE key = ?', (key,))
        row = cursor.fetchone()
        conn.close()
        
        return row[0] if row else None
    
    def set_setting(self, key: str, value: str):
        """Set a setting value."""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO settings (key, value, updated_at)
            VALUES (?, ?, ?)
        ''', (key, value, datetime.now().isoformat()))
        
        conn.commit()
        conn.close()
