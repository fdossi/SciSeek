#!/usr/bin/env python3
"""
Research Document Searcher - Ferramenta profissional para busca em documentos científicos.

Implementa 3 fases:
1. Extração multi-formato (PDF, DOCX, MD, TXT) com cache
2. Interface com wizard interativo e histórico
3. Busca avançada (regex, proximidade, booleana) com cache persistente

Uso:
    python research_searcher.py              # Primeira vez (wizard interativo)
    python research_searcher.py --quick      # Usar última configuração
    python research_searcher.py --config config.yml
"""

import sys
import time
import argparse
import json
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
import unicodedata

# Importações internas
sys.path.insert(0, str(Path(__file__).parent))

from extractors.factory import ExtractorFactory
from extractors.base import ExtractionResult
from searchers.basic import BasicSearcher, AdvancedSearcher, SearchMode
from database.cache import SearchCache
from utils.path_resolver import PathResolver
from utils.validators import ConfigValidator
from utils.logger import log

try:
    import yaml
except ImportError:
    yaml = None
    log.warning("PyYAML não instalado. Usando configuração padrão.")

try:
    from tqdm import tqdm
except ImportError:
    tqdm = None


@dataclass
class SearchConfig:
    """Configuração de uma busca."""
    root: Path
    file_formats: List[str]
    search_terms: List[str]
    search_groups: List[str]
    search_mode: SearchMode = SearchMode.SIMPLE
    case_sensitive: bool = False
    use_cache: bool = True
    output_format: str = "markdown"


@dataclass
class DocumentMatch:
    """Resultado de um documento buscado."""
    file_path: Path
    file_name: str
    format_type: str
    matched_terms: List[str]
    match_count: int
    search_mode: SearchMode


class ResearchSearcher:
    """Orquestrador principal de busca em documentos."""

    def __init__(self, config_path: Path = None):
        """
        Inicializa o searcher.
        
        Args:
            config_path: Caminho para arquivo de configuração YAML
        """
        self.config_path = config_path
        self.config = self._load_config()
        self.factory = ExtractorFactory(self.config.get("extraction", {}))
        self.cache = SearchCache(Path(self.config.get("database", {}).get("cache_directory", ".cache")))
        self.results: List[DocumentMatch] = []
        self.errors: List[Tuple[str, str]] = []

    def _load_config(self) -> Dict[str, Any]:
        """Carrega configuração do arquivo YAML ou padrão."""
        default_config_path = Path(__file__).parent / "config" / "default.yml"
        
        # Tentar carregar config customizada
        if self.config_path and self.config_path.exists() and yaml:
            try:
                with open(self.config_path) as f:
                    return yaml.safe_load(f) or {}
            except Exception as e:
                log.error(f"Erro ao carregar config: {e}")

        # Fallback para padrão
        if default_config_path.exists() and yaml:
            try:
                with open(default_config_path) as f:
                    return yaml.safe_load(f) or {}
            except Exception:
                pass

        return self._default_config()

    @staticmethod
    def _default_config() -> Dict[str, Any]:
        """Retorna configuração padrão hardcoded."""
        return {
            "file_formats": {"enabled": ["pdf", "docx", "md", "txt"]},
            "extraction": {"pdf": {"max_pages": 30}},
            "search": {"case_sensitive": False, "proximity_words": 10},
            "output": {"format": "markdown"},
            "database": {"cache_enabled": True, "cache_directory": ".cache"}
        }

    def interactive_wizard(self) -> SearchConfig:
        """
        Wizard interativo para primeira execução.
        
        Returns:
            SearchConfig configurada
        """
        print("\n" + "=" * 60)
        print("Research Document Searcher - Wizard de Configuração")
        print("=" * 60)

        # 1. Selecionar diretório raiz
        print("\n[1/5] Diretório raiz para busca")
        print(f"Padrão: {Path.cwd()}")
        root_input = input("Caminho (Enter para padrão): ").strip()
        root = PathResolver.resolve_root(root_input or None)
        print(f"✓ Usando: {root}")

        # 2. Selecionar formatos
        print("\n[2/5] Formatos de arquivo")
        enabled_formats = self.config.get("file_formats", {}).get("enabled", ["pdf", "docx", "md", "txt"])
        print(f"Disponíveis: {', '.join(enabled_formats)}")
        formats_input = input("Formatos (Enter para todos, ou ex: pdf,md): ").strip()
        
        if formats_input:
            file_formats = [f.strip().lower() for f in formats_input.split(",")]
        else:
            file_formats = enabled_formats
        
        print(f"✓ Formatos: {', '.join(file_formats)}")

        # 3. Selecionar grupos de busca
        print("\n[3/5] Grupos de busca predefinidos")
        groups_config = self.config.get("search_groups", {})
        available_groups = list(groups_config.keys())
        
        print("Grupos disponíveis:")
        for i, group in enumerate(available_groups, 1):
            desc = groups_config[group].get("name", group)
            print(f"  {i}. {group} - {desc}")
        print(f"  {len(available_groups) + 1}. Customizado (inserir termos manualmente)")

        groups_input = input("Selecione grupos (números separados por vírgula): ").strip()
        selected_groups = []
        custom_terms = []

        if groups_input:
            for choice in groups_input.split(","):
                choice = choice.strip()
                if choice.isdigit():
                    idx = int(choice) - 1
                    if 0 <= idx < len(available_groups):
                        selected_groups.append(available_groups[idx])
                    elif idx == len(available_groups):
                        # Custom
                        terms = input("Digite os termos customizados (separados por vírgula): ").strip()
                        custom_terms = [t.strip() for t in terms.split(",") if t.strip()]

        print(f"✓ Grupos: {', '.join(selected_groups)}")
        if custom_terms:
            print(f"✓ Termos customizados: {', '.join(custom_terms)}")

        # 4. Modo de busca
        print("\n[4/5] Modo de busca")
        print("  1. Simples (strings exatas)")
        print("  2. Regex (expressões regulares)")
        print("  3. Proximidade (termos próximos)")
        print("  4. Booleano (AND, OR, NOT)")
        mode_input = input("Modo (padrão: 1): ").strip() or "1"
        
        modes_map = {"1": SearchMode.SIMPLE, "2": SearchMode.REGEX, 
                     "3": SearchMode.PROXIMITY, "4": SearchMode.BOOLEAN}
        search_mode = modes_map.get(mode_input, SearchMode.SIMPLE)
        print(f"✓ Modo: {search_mode.value}")

        # 5. Formato de saída
        print("\n[5/5] Formato de saída")
        print("  1. Markdown (padrão)")
        print("  2. CSV")
        print("  3. JSON")
        print("  4. HTML")
        print("  5. BibTeX")
        output_input = input("Formato (padrão: 1): ").strip() or "1"
        
        output_map = {"1": "markdown", "2": "csv", "3": "json", "4": "html", "5": "bibtex"}
        output_format = output_map.get(output_input, "markdown")
        print(f"✓ Formato: {output_format}")

        # Compilar termos de busca
        search_terms = custom_terms
        for group in selected_groups:
            if group in groups_config:
                patterns = groups_config[group].get("patterns", [])
                search_terms.extend(patterns)

        print("\n" + "=" * 60)
        print(f"Configuração pronta: {len(search_terms)} termos a buscar")
        print("=" * 60 + "\n")

        return SearchConfig(
            root=root,
            file_formats=file_formats,
            search_terms=search_terms,
            search_groups=selected_groups,
            search_mode=search_mode,
            case_sensitive=self.config.get("search", {}).get("case_sensitive", False),
            use_cache=self.config.get("database", {}).get("cache_enabled", True),
            output_format=output_format
        )

    def discover_files(self, search_config: SearchConfig) -> List[Path]:
        """
        Descobre arquivos no diretório raiz.
        
        Args:
            search_config: Configuração da busca
            
        Returns:
            Lista de caminhos de arquivo
        """
        files = PathResolver.find_files(
            search_config.root,
            extensions=[f".{fmt}" for fmt in search_config.file_formats],
            recursive=self.config.get("paths", {}).get("recursive_search", True),
            ignore_hidden=self.config.get("paths", {}).get("ignore_hidden_files", True)
        )
        return files

    def extract_documents(self, files: List[Path]) -> Dict[Path, ExtractionResult]:
        """
        Extrai texto de todos os arquivos.
        
        Args:
            files: Lista de caminhos
            
        Returns:
            Dicionário com resultados de extração
        """
        results = {}
        iterator = tqdm(files, desc="Extraindo documentos") if tqdm else files
        
        if not tqdm:
            print(f"Extraindo {len(files)} documentos...")

        for i, file_path in enumerate(iterator):
            if not tqdm:
                print(f"  [{i+1}/{len(files)}] {file_path.name}...", end="", flush=True)

            try:
                # Tentar usar cache
                if True:  # search_config.use_cache:
                    cached = self.cache.get_cached_document(file_path)
                    if cached:
                        if not tqdm:
                            print(" [cache]")
                        results[file_path] = self._cached_to_extraction_result(file_path, cached)
                        continue

                # Extrair documento
                extractor = self.factory.get_extractor(file_path)
                if extractor:
                    result = extractor.extract(file_path)
                    results[file_path] = result

                    # Cachear
                    if result.success:
                        self.cache.cache_document(
                            file_path,
                            result.text_content,
                            result.format_type,
                            result.metadata,
                            result.extraction_time_ms
                        )

                    if not tqdm:
                        print(f" [{result.extraction_time_ms:.0f}ms]")
                else:
                    if not tqdm:
                        print(" [formato não suportado]")

            except Exception as e:
                self.errors.append((file_path.name, str(e)))
                if not tqdm:
                    print(f" [erro: {str(e)[:30]}...]")

        return results

    def search_documents(self, documents: Dict[Path, ExtractionResult],
                        search_config: SearchConfig) -> List[DocumentMatch]:
        """
        Busca termos nos documentos extraídos.
        
        Args:
            documents: Dicionário de documentos
            search_config: Configuração da busca
            
        Returns:
            Lista de correspondências
        """
        matches = []
        
        # Escolher searcher
        if search_config.search_mode == SearchMode.SIMPLE:
            searcher = BasicSearcher(case_sensitive=search_config.case_sensitive)
        else:
            searcher = AdvancedSearcher(
                case_sensitive=search_config.case_sensitive,
                proximity_words=self.config.get("search", {}).get("proximity_words", 10)
            )

        iterator = tqdm(documents.items(), desc="Buscando termos") if tqdm else documents.items()
        
        if not tqdm:
            print(f"\nBuscando em {len(documents)} documentos...")

        for i, (file_path, extraction_result) in enumerate(iterator):
            if not tqdm:
                print(f"  [{i+1}/{len(documents)}] {file_path.name}...", end="", flush=True)

            if not extraction_result.success:
                if not tqdm:
                    print(" [erro na extração]")
                continue

            try:
                # Buscar dependendo do modo
                if search_config.search_mode == SearchMode.SIMPLE:
                    result = searcher.search(extraction_result.text_content, search_config.search_terms)

                elif search_config.search_mode == SearchMode.REGEX:
                    result = searcher.search_regex(extraction_result.text_content, search_config.search_terms)

                elif search_config.search_mode == SearchMode.PROXIMITY:
                    # Para proximidade, verificar cada par de termos
                    matched_terms = []
                    if len(search_config.search_terms) >= 2:
                        for i in range(len(search_config.search_terms) - 1):
                            if searcher.search_proximity(
                                extraction_result.text_content,
                                search_config.search_terms[i],
                                search_config.search_terms[i + 1]
                            ):
                                matched_terms.extend([search_config.search_terms[i], search_config.search_terms[i+1]])
                    result_found = len(matched_terms) > 0

                elif search_config.search_mode == SearchMode.BOOLEAN:
                    # Para booleano, usar query
                    query = " AND ".join(search_config.search_terms)
                    result_found = searcher.search_boolean(extraction_result.text_content, query)
                    matched_terms = search_config.search_terms if result_found else []

                if search_config.search_mode in [SearchMode.PROXIMITY, SearchMode.BOOLEAN]:
                    if result_found:
                        match = DocumentMatch(
                            file_path=file_path,
                            file_name=file_path.name,
                            format_type=extraction_result.format_type,
                            matched_terms=list(set(matched_terms)),
                            match_count=len(matched_terms),
                            search_mode=search_config.search_mode
                        )
                        matches.append(match)
                        if not tqdm:
                            print(f" [{len(matched_terms)} termos]")
                    else:
                        if not tqdm:
                            print(" [sem correspondência]")
                else:
                    if result.matches_found:
                        match = DocumentMatch(
                            file_path=file_path,
                            file_name=file_path.name,
                            format_type=extraction_result.format_type,
                            matched_terms=result.matched_terms,
                            match_count=result.match_count,
                            search_mode=search_config.search_mode
                        )
                        matches.append(match)
                        if not tqdm:
                            print(f" [{result.match_count} ocorrências]")
                    else:
                        if not tqdm:
                            print(" [sem correspondência]")

            except Exception as e:
                self.errors.append((file_path.name, f"Erro na busca: {str(e)}"))
                if not tqdm:
                    print(f" [erro: {str(e)[:30]}...]")

        return matches

    def generate_output(self, matches: List[DocumentMatch],
                       search_config: SearchConfig,
                       output_dir: Path = None) -> Path:
        """
        Gera saída nos formatos configurados.
        
        Args:
            matches: Correspondências encontradas
            search_config: Configuração da busca
            output_dir: Diretório para saída (padrão: mesmo da busca)
            
        Returns:
            Caminho do arquivo de saída
        """
        if output_dir is None:
            output_dir = search_config.root / "outputs"
        
        output_dir.mkdir(exist_ok=True, parents=True)

        # Timestamp para nome único
        timestamp = time.strftime("%Y%m%d-%H%M%S")
        base_name = f"search_results_{timestamp}"

        # Gerar arquivo de resultado
        if search_config.output_format == "markdown":
            return self._output_markdown(matches, search_config, output_dir, base_name)
        elif search_config.output_format == "csv":
            return self._output_csv(matches, output_dir, base_name)
        elif search_config.output_format == "json":
            return self._output_json(matches, search_config, output_dir, base_name)
        else:
            return self._output_markdown(matches, search_config, output_dir, base_name)

    def _output_markdown(self, matches: List[DocumentMatch],
                        search_config: SearchConfig,
                        output_dir: Path, base_name: str) -> Path:
        """Gera saída em Markdown."""
        output_path = output_dir / f"{base_name}.md"

        with output_path.open("w", encoding="utf-8") as f:
            f.write("# Resultado de Busca em Documentos\n\n")
            
            f.write("## Resumo\n\n")
            f.write(f"- **Diretório analisado**: {search_config.root}\n")
            f.write(f"- **Arquivos examinados**: {len(self.results) + len(self.errors)}\n")
            f.write(f"- **Resultados encontrados**: {len(matches)}\n")
            f.write(f"- **Modo de busca**: {search_config.search_mode.value}\n")
            f.write(f"- **Formatos processados**: {', '.join(search_config.file_formats)}\n")
            f.write(f"- **Data/Hora**: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")

            f.write("## Documentos com Correspondência\n\n")
            
            if matches:
                f.write("| Arquivo | Termos Encontrados | Ocorrências | Formato |\n")
                f.write("|---------|-------------------|-------------|----------|\n")
                
                for match in sorted(matches, key=lambda m: m.file_name):
                    terms_str = ", ".join(match.matched_terms[:3])
                    if len(match.matched_terms) > 3:
                        terms_str += f", +{len(match.matched_terms) - 3}"
                    
                    f.write(f"| {match.file_name} | {terms_str} | {match.match_count} | {match.format_type} |\n")
            else:
                f.write("Nenhum documento encontrado com os termos especificados.\n\n")

            if self.errors:
                f.write(f"\n## Erros de Processamento ({len(self.errors)})\n\n")
                for file_name, error in self.errors:
                    f.write(f"- **{file_name}**: {error}\n")

        print(f"\n✓ Resultado salvo em: {output_path}")
        return output_path

    def _output_csv(self, matches: List[DocumentMatch],
                    output_dir: Path, base_name: str) -> Path:
        """Gera saída em CSV."""
        output_path = output_dir / f"{base_name}.csv"

        with output_path.open("w", encoding="utf-8") as f:
            f.write("Arquivo,Termos,Ocorrências,Formato\n")
            for match in matches:
                f.write(f'"{match.file_name}","{"; ".join(match.matched_terms)}",{match.match_count},{match.format_type}\n')

        print(f"\n✓ Resultado salvo em: {output_path}")
        return output_path

    def _output_json(self, matches: List[DocumentMatch],
                     search_config: SearchConfig,
                     output_dir: Path, base_name: str) -> Path:
        """Gera saída em JSON."""
        output_path = output_dir / f"{base_name}.json"

        data = {
            "metadata": {
                "root": str(search_config.root),
                "search_mode": search_config.search_mode.value,
                "results_count": len(matches),
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
            },
            "results": [
                {
                    "file_name": match.file_name,
                    "format": match.format_type,
                    "matched_terms": match.matched_terms,
                    "match_count": match.match_count
                }
                for match in matches
            ]
        }

        with output_path.open("w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        print(f"\n✓ Resultado salvo em: {output_path}")
        return output_path

    @staticmethod
    def _cached_to_extraction_result(file_path: Path, cached: Dict[str, Any]) -> ExtractionResult:
        """Converte entrada do cache para ExtractionResult."""
        from extractors.base import ExtractionResult
        
        return ExtractionResult(
            file_path=file_path,
            file_name=cached["file_name"],
            format_type=cached["format_type"],
            text_content=cached["text_content"],
            metadata=cached["metadata"],
            extraction_time_ms=cached["extraction_time_ms"],
            success=True
        )

    def run(self, search_config: SearchConfig = None) -> int:
        """
        Executa a busca completa.
        
        Args:
            search_config: Configuração (None = usar wizard)
            
        Returns:
            Exit code
        """
        try:
            start_time = time.time()

            # Usar wizard se não houver config
            if search_config is None:
                search_config = self.interactive_wizard()

            # Descobrir arquivos
            print("\n[Fase 1] Descobrindo arquivos...")
            files = self.discover_files(search_config)
            print(f"✓ {len(files)} arquivos encontrados")

            # Extrair documentos
            print("\n[Fase 2] Extraindo conteúdo dos documentos...")
            documents = self.extract_documents(files)
            print(f"✓ {len(documents)} documentos processados")

            # Buscar termos
            print(f"\n[Fase 3] Buscando {len(search_config.search_terms)} termos...")
            matches = self.search_documents(documents, search_config)
            self.results = matches
            print(f"✓ {len(matches)} documentos com correspondência")

            # Gerar saída
            print("\n[Fase 4] Gerando saída...")
            output_file = self.generate_output(matches, search_config)

            # Estatísticas finais
            total_time = time.time() - start_time
            print(f"\n{'='*60}")
            print(f"Busca concluída em {total_time:.2f}s")
            print(f"  - Documentos analisados: {len(documents)}")
            print(f"  - Correspondências: {len(matches)}")
            print(f"  - Erros: {len(self.errors)}")
            print(f"  - Saída: {output_file}")
            print(f"{'='*60}\n")

            return 0

        except KeyboardInterrupt:
            print("\n\nBusca cancelada pelo usuário.")
            return 1
        except Exception as e:
            log.error(f"Erro na execução: {e}")
            print(f"\nErro: {e}")
            return 1


def main():
    """Função principal."""
    parser = argparse.ArgumentParser(
        description="Research Document Searcher - Busca profissional em documentos",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos:
  %(prog)s                    # Wizard interativo
  %(prog)s --quick            # Usar última configuração
  %(prog)s --config conf.yml  # Usar arquivo de configuração
  %(prog)s --root . --formats pdf,md --terms "termo1,termo2"
        """
    )

    parser.add_argument("--config", type=Path, help="Arquivo de configuração YAML")
    parser.add_argument("--root", type=str, help="Diretório raiz para busca")
    parser.add_argument("--formats", type=str, help="Formatos (pdf,docx,md,txt)")
    parser.add_argument("--terms", type=str, help="Termos de busca (separados por vírgula)")
    parser.add_argument("--groups", type=str, help="Grupos predefinidos")
    parser.add_argument("--mode", choices=["simple", "regex", "proximity", "boolean"],
                       default="simple", help="Modo de busca")
    parser.add_argument("--output", choices=["markdown", "csv", "json", "html", "bibtex"],
                       default="markdown", help="Formato de saída")
    parser.add_argument("--quick", action="store_true", help="Usar última configuração")
    parser.add_argument("--no-cache", action="store_true", help="Não usar cache")
    parser.add_argument("--debug", action="store_true", help="Modo debug")

    args = parser.parse_args()

    # Criar searcher
    searcher = ResearchSearcher(config_path=args.config)

    # Modo quick (última configuração)
    if args.quick:
        # TODO: Implementar recuperação da última configuração
        print("Modo quick ainda não implementado.")
        return 1

    # Modo com argumentos CLI
    if args.root or args.formats or args.terms:
        try:
            root = PathResolver.resolve_root(args.root)
            file_formats = args.formats.split(",") if args.formats else ["pdf"]
            search_terms = args.terms.split(",") if args.terms else []
            search_groups = args.groups.split(",") if args.groups else []

            search_config = SearchConfig(
                root=root,
                file_formats=file_formats,
                search_terms=search_terms,
                search_groups=search_groups,
                search_mode=SearchMode[args.mode.upper()],
                output_format=args.output,
                use_cache=not args.no_cache
            )

            return searcher.run(search_config)
        except Exception as e:
            print(f"Erro nos argumentos: {e}")
            return 1

    # Modo wizard (padrão)
    return searcher.run()


if __name__ == "__main__":
    sys.exit(main())
