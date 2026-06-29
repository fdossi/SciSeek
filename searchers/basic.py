"""
Searchers básico e avançado para buscar termos em textos extraídos.
"""

import re
from typing import List, Dict, Any, Tuple, Set
from dataclasses import dataclass, field
from enum import Enum


class SearchMode(Enum):
    """Modos de busca disponíveis."""
    SIMPLE = "simple"        # Busca por strings simples
    REGEX = "regex"          # Busca por expressões regulares
    PROXIMITY = "proximity"  # Busca por proximidade de termos
    BOOLEAN = "boolean"      # Busca com operadores booleanos


@dataclass
class SearchResult:
    """Resultado de uma busca em um documento."""
    document_path: str
    document_name: str
    search_terms: List[str]
    search_mode: SearchMode
    matches_found: bool
    match_count: int = 0
    matched_terms: List[str] = field(default_factory=list)
    context_snippets: List[str] = field(default_factory=list)
    search_time_ms: float = 0.0


class BasicSearcher:
    """Searcher básico com busca simples por strings."""

    def __init__(self, case_sensitive: bool = False):
        """
        Inicializa o searcher.
        
        Args:
            case_sensitive: Se deve diferenciar maiúsculas/minúsculas
        """
        self.case_sensitive = case_sensitive

    def search(self, text: str, terms: List[str]) -> SearchResult:
        """
        Busca termos simples em um texto.
        
        Args:
            text: Texto onde buscar
            terms: Lista de termos a buscar
            
        Returns:
            SearchResult com os resultados
        """
        matched_terms = []
        match_count = 0

        # Normalizar texto se necessário
        search_text = text if self.case_sensitive else text.lower()

        for term in terms:
            search_term = term if self.case_sensitive else term.lower()
            
            if search_term in search_text:
                matched_terms.append(term)
                # Contar ocorrências
                count = search_text.count(search_term)
                match_count += count

        matches_found = len(matched_terms) > 0

        return SearchResult(
            document_path="",
            document_name="",
            search_terms=terms,
            search_mode=SearchMode.SIMPLE,
            matches_found=matches_found,
            match_count=match_count,
            matched_terms=matched_terms
        )

    def search_in_document(self, text: str, terms: List[str], 
                          doc_path: str, doc_name: str) -> SearchResult:
        """
        Busca termos em um documento específico.
        
        Args:
            text: Conteúdo do documento
            terms: Termos a buscar
            doc_path: Caminho do documento
            doc_name: Nome do documento
            
        Returns:
            SearchResult com informações do documento
        """
        result = self.search(text, terms)
        result.document_path = str(doc_path)
        result.document_name = doc_name
        return result


class AdvancedSearcher:
    """Searcher avançado com regex, proximidade e operadores booleanos."""

    def __init__(self, case_sensitive: bool = False, 
                 fuzzy_threshold: float = 0.8,
                 proximity_words: int = 10):
        """
        Inicializa o searcher avançado.
        
        Args:
            case_sensitive: Diferenciar maiúsculas
            fuzzy_threshold: Limiar para fuzzy matching (0-1)
            proximity_words: Número de palavras para busca de proximidade
        """
        self.case_sensitive = case_sensitive
        self.fuzzy_threshold = fuzzy_threshold
        self.proximity_words = proximity_words

    def search_regex(self, text: str, patterns: List[str]) -> SearchResult:
        """
        Busca usando expressões regulares.
        
        Args:
            text: Texto onde buscar
            patterns: Lista de padrões regex
            
        Returns:
            SearchResult com correspondências
        """
        matched_terms = []
        match_count = 0
        flags = 0 if self.case_sensitive else re.IGNORECASE

        for pattern in patterns:
            try:
                regex = re.compile(pattern, flags)
                matches = regex.findall(text)
                
                if matches:
                    matched_terms.append(pattern)
                    match_count += len(matches)
            except re.error:
                # Ignorar padrões regex inválidos
                continue

        matches_found = len(matched_terms) > 0

        return SearchResult(
            document_path="",
            document_name="",
            search_terms=patterns,
            search_mode=SearchMode.REGEX,
            matches_found=matches_found,
            match_count=match_count,
            matched_terms=matched_terms
        )

    def search_proximity(self, text: str, term1: str, term2: str,
                        max_distance: int = None) -> bool:
        """
        Busca dois termos próximos um do outro.
        
        Args:
            text: Texto onde buscar
            term1: Primeiro termo
            term2: Segundo termo
            max_distance: Distância máxima em palavras
            
        Returns:
            True se termos encontrados próximos
        """
        if max_distance is None:
            max_distance = self.proximity_words

        search_text = text if self.case_sensitive else text.lower()
        search_term1 = term1 if self.case_sensitive else term1.lower()
        search_term2 = term2 if self.case_sensitive else term2.lower()

        # Encontrar posições dos termos
        pattern1 = re.compile(rf'\b{re.escape(search_term1)}\b', 
                             re.IGNORECASE if not self.case_sensitive else 0)
        pattern2 = re.compile(rf'\b{re.escape(search_term2)}\b',
                             re.IGNORECASE if not self.case_sensitive else 0)

        matches1 = [m.start() for m in pattern1.finditer(search_text)]
        matches2 = [m.start() for m in pattern2.finditer(search_text)]

        # Verificar proximidade
        for pos1 in matches1:
            for pos2 in matches2:
                # Calcular distância em palavras
                text_between = search_text[min(pos1, pos2):max(pos1, pos2)]
                word_distance = len(text_between.split())
                
                if word_distance <= max_distance:
                    return True

        return False

    def search_boolean(self, text: str, boolean_query: str) -> bool:
        """
        Busca com operadores booleanos (AND, OR, NOT).
        
        Sintaxe:
        - "termo1 AND termo2" - ambos devem estar presentes
        - "termo1 OR termo2" - pelo menos um deve estar presente
        - "NOT termo1" - termo não deve estar presente
        
        Args:
            text: Texto onde buscar
            boolean_query: Query com operadores booleanos
            
        Returns:
            True se a query é satisfeita
        """
        search_text = text if self.case_sensitive else text.lower()

        # Processar operadores
        # Simplificado: suporta AND, OR, NOT básicos
        
        # Remover parênteses por enquanto
        query = boolean_query.strip()
        
        # Processar NOT
        not_pattern = r'NOT\s+(\w+)'
        not_matches = re.findall(not_pattern, query, re.IGNORECASE)
        for term in not_matches:
            search_term = term if self.case_sensitive else term.lower()
            if search_term in search_text:
                return False
            query = re.sub(rf'NOT\s+{term}', '', query, flags=re.IGNORECASE)

        # Processar AND (todos devem estar presentes)
        if " AND " in query.upper():
            parts = re.split(r'\s+AND\s+', query, flags=re.IGNORECASE)
            for part in parts:
                search_term = part.strip() if self.case_sensitive else part.strip().lower()
                if search_term and search_term not in search_text:
                    return False
            return True

        # Processar OR (pelo menos um deve estar presente)
        if " OR " in query.upper():
            parts = re.split(r'\s+OR\s+', query, flags=re.IGNORECASE)
            for part in parts:
                search_term = part.strip() if self.case_sensitive else part.strip().lower()
                if search_term and search_term in search_text:
                    return True
            return False

        # Query simples (sem operadores)
        search_query = query if self.case_sensitive else query.lower()
        return search_query in search_text

    def extract_context(self, text: str, term: str, 
                       context_words: int = 20) -> str:
        """
        Extrai trecho de contexto ao redor de um termo.
        
        Args:
            text: Texto completo
            term: Termo para extrair contexto
            context_words: Número de palavras antes e depois
            
        Returns:
            Trecho com o termo em contexto
        """
        search_text = text if self.case_sensitive else text.lower()
        search_term = term if self.case_sensitive else term.lower()

        # Encontrar primeira ocorrência
        pos = search_text.find(search_term)
        if pos == -1:
            return ""

        # Extrair contexto
        words_before = text[:pos].split()[-context_words:]
        words_after = text[pos + len(search_term):].split()[:context_words]

        context = " ".join(words_before) + " " + term + " " + " ".join(words_after)
        return context.strip()
