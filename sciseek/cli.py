"""SciSeek command line interface."""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict
from pathlib import Path
from typing import List

# Allow direct execution via `python sciseek\cli.py ...`.
if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sciseek.app import build_service
from sciseek.core.exceptions import ValidationError
from sciseek.core.models import SearchConfig, SearchMode, sanitize_terms

LAST_SEARCH_FILE = "last_search.json"


def _split_csv(value: str | None) -> List[str]:
    if not value:
        return []
    return [p.strip() for p in value.split(",") if p.strip()]


def _load_group_terms(config_file: Path, groups: List[str]) -> List[str]:
    if not groups:
        return []
    try:
        import yaml
    except ImportError:
        return []
    if not config_file.exists():
        return []
    payload = yaml.safe_load(config_file.read_text(encoding="utf-8")) or {}
    group_map = payload.get("search_groups", {})
    out: List[str] = []
    for g in groups:
        item = group_map.get(g)
        if item and isinstance(item, dict):
            out.extend(item.get("patterns", []))
    return out


def build_config_from_args(args: argparse.Namespace) -> SearchConfig:
    root = Path(args.root or ".").resolve()
    formats = _split_csv(args.formats) or ["pdf", "docx", "md", "txt"]
    terms = _split_csv(args.terms)
    groups = _split_csv(args.groups)
    terms.extend(_load_group_terms(Path(args.config_file), groups))
    terms = sanitize_terms(terms)
    mode = SearchMode(args.mode)

    boolean_query = args.boolean_query or ""
    if mode == SearchMode.BOOLEAN and not boolean_query:
        boolean_query = " ".join(terms)

    return SearchConfig(
        root=root,
        file_formats=formats,
        mode=mode,
        terms=terms,
        boolean_query=boolean_query,
        groups=groups,
        recursive=not args.no_recursive,
        ignore_hidden=not args.include_hidden,
        case_sensitive=args.case_sensitive,
        use_cache=not args.no_cache,
        output_format=args.output,
        output_dir=Path(args.output_dir).resolve() if args.output_dir else None,
        output_name=args.output_name,
        max_pdf_pages=args.max_pages,
        proximity_words=args.proximity,
        context_words=args.context_words,
    )


def _search_args_dict(args: argparse.Namespace) -> dict[str, object]:
    return {
        "root": args.root,
        "formats": args.formats,
        "terms": args.terms,
        "groups": args.groups,
        "mode": args.mode,
        "boolean_query": args.boolean_query,
        "proximity": args.proximity,
        "context_words": args.context_words,
        "case_sensitive": args.case_sensitive,
        "no_recursive": args.no_recursive,
        "include_hidden": args.include_hidden,
        "no_cache": args.no_cache,
        "output": args.output,
        "output_dir": args.output_dir,
        "output_name": args.output_name,
        "max_pages": args.max_pages,
        "config_file": args.config_file,
        "quiet": args.quiet,
    }


def _run_search(args: argparse.Namespace) -> int:
    service = build_service()
    cfg = build_config_from_args(args)

    def on_progress(evt):
        if args.quiet:
            return
        fp = f" - {evt.file_path.name}" if evt.file_path else ""
        print(f"[{evt.stage}] {evt.current}/{evt.total} {evt.message}{fp}")

    try:
        result = service.run(cfg, progress=on_progress if not args.quiet else None)
    except ValidationError as exc:
        print(f"Erro de validacao: {exc}")
        return 2

    last_file = service.paths.config_dir / LAST_SEARCH_FILE
    last_file.write_text(json.dumps(_search_args_dict(args), ensure_ascii=False, indent=2), encoding="utf-8")

    if not args.quiet:
        print("\nResumo:")
        print(f"  Descobertos: {result.summary.total_discovered}")
        print(f"  Processados: {result.summary.total_processed}")
        print(f"  Encontrados: {result.summary.total_matched}")
        print(f"  Erros: {result.summary.total_errors}")
        print(f"  Saida: {result.summary.output_file}")
    return 0 if result.summary.total_errors == 0 else 2


def _run_history(args: argparse.Namespace) -> int:
    service = build_service()
    entries = service.history(limit=args.limit)
    if args.json:
        print(json.dumps([asdict(e) for e in entries], ensure_ascii=False, indent=2))
        return 0
    if not entries:
        print("Historico vazio.")
        return 0
    for i, e in enumerate(entries, start=1):
        print(f"{i}. {e.run_at} | {e.mode} | {e.total_matched}/{e.total_processed} | {e.output_file}")
    return 0


def _run_cache(args: argparse.Namespace) -> int:
    service = build_service()
    if args.action == "stats":
        print(service.cache_stats())
        return 0
    if args.action == "clear":
        removed = service.clear_cache()
        print(f"Entradas removidas: {removed}")
        return 0
    return 1


def _run_config(args: argparse.Namespace) -> int:
    service = build_service()
    if args.action == "show":
        print(service.get_settings())
        return 0
    if args.action == "set":
        key = args.key
        value = args.value
        if value in {"true", "false"}:
            parsed = value == "true"
        else:
            try:
                parsed = int(value)
            except ValueError:
                parsed = value
        service.update_settings(**{key: parsed})
        print("Configuracao atualizada.")
        return 0
    return 1


def _run_gui(_: argparse.Namespace) -> int:
    try:
        from sciseek.gui.main import run_gui
    except Exception as exc:
        print(f"GUI indisponivel: {exc}")
        return 1
    return run_gui()


def _run_wizard() -> int:
    print("SciSeek Wizard")
    root = input("Diretorio raiz [.]: ").strip() or "."
    mode = input("Modo [simple|regex|proximity|boolean] (simple): ").strip() or "simple"
    terms = input("Termos separados por virgula: ").strip()
    output = input("Formato de saida [markdown|csv|json|html|bibtex] (markdown): ").strip() or "markdown"
    args = argparse.Namespace(
        root=root,
        formats="pdf,docx,md,txt",
        terms=terms,
        groups="",
        mode=mode,
        boolean_query="",
        no_recursive=False,
        include_hidden=False,
        case_sensitive=False,
        no_cache=False,
        output=output,
        output_dir="",
        output_name="",
        max_pages=30,
        proximity=10,
        context_words=20,
        config_file="config/default.yml",
        quiet=False,
    )
    return _run_search(args)


def _run_quick() -> int:
    service = build_service()
    last_file = service.paths.config_dir / LAST_SEARCH_FILE
    if not last_file.exists():
        print("Sem historico para executar --quick.")
        return 1
    data = json.loads(last_file.read_text(encoding="utf-8"))
    args = argparse.Namespace(**data)
    return _run_search(args)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="sciseek", description="SciSeek CLI")
    sub = parser.add_subparsers(dest="cmd")

    sub.add_parser("gui", help="Abrir interface grafica")

    s = sub.add_parser("search", help="Executar busca")
    s.add_argument("--root", type=str, default=".")
    s.add_argument("--formats", type=str, default="pdf,docx,md,txt")
    s.add_argument("--terms", type=str, default="")
    s.add_argument("--groups", type=str, default="")
    s.add_argument("--mode", choices=[m.value for m in SearchMode], default="simple")
    s.add_argument("--boolean-query", type=str, default="")
    s.add_argument("--proximity", type=int, default=10)
    s.add_argument("--context-words", type=int, default=20)
    s.add_argument("--case-sensitive", action="store_true")
    s.add_argument("--no-recursive", action="store_true")
    s.add_argument("--include-hidden", action="store_true")
    s.add_argument("--no-cache", action="store_true")
    s.add_argument("--output", choices=["markdown", "csv", "json", "html", "bibtex"], default="markdown")
    s.add_argument("--output-dir", type=str, default="")
    s.add_argument("--output-name", type=str, default="")
    s.add_argument("--max-pages", type=int, default=30)
    s.add_argument("--config-file", type=str, default="config/default.yml")
    s.add_argument("--quiet", action="store_true")

    c = sub.add_parser("cache", help="Operacoes de cache")
    c.add_argument("action", choices=["stats", "clear"])

    h = sub.add_parser("history", help="Historico")
    h.add_argument("--limit", type=int, default=25)
    h.add_argument("--json", action="store_true")

    cfg = sub.add_parser("config", help="Configuracoes")
    cfg.add_argument("action", choices=["show", "set"])
    cfg.add_argument("--key", type=str, default="")
    cfg.add_argument("--value", type=str, default="")

    parser.add_argument("--quick", action="store_true", help="Repetir ultima busca")
    return parser


def main(argv: List[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.quick:
        return _run_quick()

    if args.cmd is None:
        return _run_wizard()
    if args.cmd == "gui":
        return _run_gui(args)
    if args.cmd == "search":
        return _run_search(args)
    if args.cmd == "cache":
        return _run_cache(args)
    if args.cmd == "history":
        return _run_history(args)
    if args.cmd == "config":
        return _run_config(args)
    return 1
