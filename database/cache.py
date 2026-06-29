"""
Cache SQLite para persistência de resultados e histórico de buscas.
"""

import sqlite3
import json
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import hashlib


class SearchCache:
    """
    Gerencia cache de resultados e histórico de buscas em SQLite.
    """

    def __init__(self, cache_dir: Path = None):
        """
        Inicializa o cache.
        
        Args:
            cache_dir: Diretório para armazenar banco de dados
        """
        if cache_dir is None:
            cache_dir = Path.cwd() / ".cache"
        
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True, parents=True)
        
        self.db_path = self.cache_dir / "research_cache.db"
        self._init_database()

    def _init_database(self) -> None:
        """Inicializa as tabelas do banco de dados."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # Tabela de documentos em cache
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS cached_documents (
                    id INTEGER PRIMARY KEY,
                    file_hash TEXT UNIQUE NOT NULL,
                    file_path TEXT NOT NULL,
                    file_name TEXT NOT NULL,
                    format_type TEXT NOT NULL,
                    text_content TEXT,
                    metadata TEXT,
                    extraction_time_ms REAL,
                    cached_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_modified TIMESTAMP
                )
            """)

            # Tabela de histórico de buscas
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS search_history (
                    id INTEGER PRIMARY KEY,
                    search_query TEXT NOT NULL,
                    search_terms TEXT NOT NULL,
                    search_groups TEXT,
                    results_count INTEGER,
                    search_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    execution_time_ms REAL
                )
            """)

            # Tabela de resultados de buscas
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS search_results (
                    id INTEGER PRIMARY KEY,
                    history_id INTEGER,
                    file_path TEXT NOT NULL,
                    file_name TEXT NOT NULL,
                    matched_terms TEXT,
                    match_count INTEGER,
                    FOREIGN KEY(history_id) REFERENCES search_history(id)
                )
            """)

            conn.commit()

    def get_file_hash(self, file_path: Path) -> str:
        """Gera hash MD5 do arquivo para identificação única."""
        with open(file_path, 'rb') as f:
            return hashlib.md5(f.read()).hexdigest()

    def is_cached(self, file_path: Path) -> bool:
        """Verifica se arquivo já está em cache."""
        try:
            file_hash = self.get_file_hash(file_path)
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT 1 FROM cached_documents WHERE file_hash = ?",
                    (file_hash,)
                )
                return cursor.fetchone() is not None
        except Exception:
            return False

    def get_cached_document(self, file_path: Path) -> Optional[Dict[str, Any]]:
        """Recupera documento do cache."""
        try:
            file_hash = self.get_file_hash(file_path)
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT * FROM cached_documents WHERE file_hash = ?",
                    (file_hash,)
                )
                row = cursor.fetchone()
                
                if row:
                    return {
                        'file_path': row['file_path'],
                        'file_name': row['file_name'],
                        'format_type': row['format_type'],
                        'text_content': row['text_content'],
                        'metadata': json.loads(row['metadata']) if row['metadata'] else {},
                        'extraction_time_ms': row['extraction_time_ms']
                    }
        except Exception:
            pass
        
        return None

    def cache_document(self, file_path: Path, text_content: str,
                      format_type: str, metadata: Dict[str, Any] = None,
                      extraction_time_ms: float = 0.0) -> None:
        """
        Armazena documento em cache.
        
        Args:
            file_path: Caminho do arquivo
            text_content: Conteúdo extraído
            format_type: Tipo de formato (pdf, docx, etc)
            metadata: Metadados do documento
            extraction_time_ms: Tempo de extração em ms
        """
        try:
            file_hash = self.get_file_hash(file_path)
            last_modified = datetime.fromtimestamp(file_path.stat().st_mtime)
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT OR REPLACE INTO cached_documents
                    (file_hash, file_path, file_name, format_type, text_content, 
                     metadata, extraction_time_ms, last_modified)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    file_hash,
                    str(file_path),
                    file_path.name,
                    format_type,
                    text_content,
                    json.dumps(metadata or {}),
                    extraction_time_ms,
                    last_modified
                ))
                conn.commit()
        except Exception as e:
            print(f"Erro ao cachear documento: {e}")

    def add_search_to_history(self, search_query: str, search_terms: List[str],
                             search_groups: List[str] = None,
                             results_count: int = 0,
                             execution_time_ms: float = 0.0) -> int:
        """
        Adiciona busca ao histórico.
        
        Args:
            search_query: Query de busca
            search_terms: Termos utilizados
            search_groups: Grupos de busca utilizados
            results_count: Número de resultados
            execution_time_ms: Tempo de execução
            
        Returns:
            ID da entrada no histórico
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO search_history
                    (search_query, search_terms, search_groups, results_count, execution_time_ms)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    search_query,
                    json.dumps(search_terms),
                    json.dumps(search_groups or []),
                    results_count,
                    execution_time_ms
                ))
                conn.commit()
                return cursor.lastrowid
        except Exception as e:
            print(f"Erro ao adicionar ao histórico: {e}")
            return -1

    def get_search_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Recupera histórico de buscas."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT * FROM search_history 
                    ORDER BY search_date DESC 
                    LIMIT ?
                """, (limit,))
                
                return [dict(row) for row in cursor.fetchall()]
        except Exception:
            return []

    def clear_old_cache(self, days: int = 30) -> int:
        """
        Remove entradas do cache mais antigas que o número de dias especificado.
        
        Args:
            days: Número de dias a manter no cache
            
        Returns:
            Número de registros deletados
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    DELETE FROM cached_documents 
                    WHERE cached_at < datetime('now', '-' || ? || ' days')
                """, (days,))
                conn.commit()
                return cursor.rowcount
        except Exception:
            return 0

    def get_cache_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas do cache."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("SELECT COUNT(*) FROM cached_documents")
                doc_count = cursor.fetchone()[0]
                
                cursor.execute("SELECT COUNT(*) FROM search_history")
                search_count = cursor.fetchone()[0]
                
                cursor.execute("SELECT SUM(extraction_time_ms) FROM cached_documents")
                total_time = cursor.fetchone()[0] or 0
                
                return {
                    'cached_documents': doc_count,
                    'search_history_entries': search_count,
                    'total_extraction_time_ms': total_time,
                    'cache_size_mb': self.db_path.stat().st_size / (1024 * 1024)
                }
        except Exception:
            return {}
