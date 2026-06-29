#!/usr/bin/env python3
"""
Testes rápidos do Research Document Searcher
"""

import sys
from pathlib import Path

# Adicionar diretório ao path
sys.path.insert(0, str(Path(__file__).parent))

from extractors.factory import ExtractorFactory
from searchers.basic import BasicSearcher, AdvancedSearcher, SearchMode
from database.cache import SearchCache
from utils.path_resolver import PathResolver
from utils.validators import ConfigValidator


def test_extractor_factory():
    """Testa factory de extractores."""
    print("Testando ExtractorFactory...")
    factory = ExtractorFactory()
    
    # Verificar formatos suportados
    formats = factory.get_supported_formats()
    assert "pdf" in formats, "PDF não suportado"
    assert "docx" in formats, "DOCX não suportado"
    assert "md" in formats, "Markdown não suportado"
    assert "txt" in formats, "TXT não suportado"
    
    print(f"  ✓ Formatos suportados: {', '.join(formats)}")


def test_basic_searcher():
    """Testa busca básica."""
    print("Testando BasicSearcher...")
    searcher = BasicSearcher()
    
    text = "Este é um texto com microscopia e histologia"
    terms = ["microscopia", "histologia", "não_existe"]
    
    result = searcher.search(text, terms)
    
    assert result.matches_found, "Deveria encontrar correspondências"
    assert len(result.matched_terms) == 2, "Deveria encontrar 2 termos"
    assert "não_existe" not in result.matched_terms, "Não deveria encontrar termo ausente"
    
    print(f"  ✓ Encontrados: {', '.join(result.matched_terms)}")


def test_advanced_searcher():
    """Testa busca avançada."""
    print("Testando AdvancedSearcher...")
    searcher = AdvancedSearcher()
    
    text = "A microscopia eletrônica revela estruturas colágenas no tendão"
    
    # Teste de proximidade
    proximity_result = searcher.search_proximity(text, "microscopia", "tendão")
    assert proximity_result, "Deveria encontrar termos próximos"
    
    print(f"  ✓ Proximidade testada com sucesso")
    
    # Teste booleano
    boolean_result = searcher.search_boolean(text, "microscopia AND tendão")
    assert boolean_result, "Deveria satisfazer query AND"
    
    print(f"  ✓ Busca booleana testada com sucesso")


def test_path_resolver():
    """Testa resolução de caminhos."""
    print("Testando PathResolver...")
    
    # Resolver caminho relativo
    root = PathResolver.resolve_root(".")
    assert root.exists(), "Diretório deve existir"
    
    print(f"  ✓ Caminho resolvido: {root}")


def test_validators():
    """Testa validadores."""
    print("Testando Validators...")
    
    # Validar formatos
    valid, msg = ConfigValidator.validate_file_formats(["pdf", "md"])
    assert valid, f"Deveria validar formatos: {msg}"
    
    invalid, msg = ConfigValidator.validate_file_formats(["xyz", "invalid"])
    assert not invalid, "Deveria rejeitar formatos inválidos"
    
    print(f"  ✓ Validadores funcionando")


def test_cache():
    """Testa cache."""
    print("Testando SearchCache...")
    
    cache = SearchCache()
    stats = cache.get_cache_stats()
    
    print(f"  ✓ Cache stats: {stats}")
    print(f"    - Documentos em cache: {stats.get('cached_documents', 0)}")
    print(f"    - Histórico de buscas: {stats.get('search_history_entries', 0)}")


def run_all_tests():
    """Executa todos os testes."""
    print("\n" + "=" * 60)
    print("Testes do Research Document Searcher")
    print("=" * 60 + "\n")
    
    tests = [
        test_extractor_factory,
        test_basic_searcher,
        test_advanced_searcher,
        test_path_resolver,
        test_validators,
        test_cache,
    ]
    
    for test in tests:
        try:
            test()
        except AssertionError as e:
            print(f"  ✗ Falha: {e}")
            return 1
        except Exception as e:
            print(f"  ✗ Erro: {e}")
            return 1
    
    print("\n" + "=" * 60)
    print("✓ Todos os testes passaram!")
    print("=" * 60 + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(run_all_tests())
