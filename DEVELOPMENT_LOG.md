# DEVELOPMENT LOG - SciSeek

## 2026-06-29 - Rodada de desenvolvimento autonomo

### Auditoria inicial
Comandos executados:
- `python test_research_searcher.py`
- `python research_searcher.py --quick`
- `python research_searcher.py --root . --formats md --terms SciSeek --mode simple --output csv --no-cache`

Problemas confirmados:
- `--quick` nao implementado.
- `--no-cache` sem efeito real.
- Saidas html/bibtex nao implementadas no fluxo legado.
- Sem parser booleano com parenteses.

### Refatoracao do nucleo
Implementado novo pacote `sciseek` com:
- `SearchService` compartilhado entre CLI e GUI.
- modelos tipados em `sciseek/core/models.py`.
- parser booleano em `sciseek/searchers/boolean_parser.py`.
- exportadores dedicados em `sciseek/exporters/writers.py`.
- datastore sqlite para cache e historico em `sciseek/database/store.py`.

### CLI e compatibilidade
- CLI nova com subcomandos (`search/gui/cache/history/config`).
- `--quick` funcional via persistencia de ultima busca.
- Wrapper legado `research_searcher.py` apontando para a nova CLI.

### GUI
- GUI inicial em PySide6 com:
  - configuracao de busca,
  - worker em thread,
  - cancelamento,
  - progresso,
  - tabela de resultados baseada em `QAbstractTableModel`.

### Qualidade e validacao
Comandos executados:
- `python -m pytest -q` -> passou
- `python scripts/smoke_test.py` -> smoke-ok
- `python -m ruff check sciseek tests research_searcher.py` -> passou
- `python -m mypy --ignore-missing-imports --follow-imports skip sciseek` -> sem erros criticos
- `python -m sciseek search ...` -> passou
- `python -m sciseek --quick` -> passou

### Limites atuais documentados
- UX da GUI ainda inicial (sem todos os refinamentos de painel/filtro/historico visual).
- Validacao de build confirmada apenas no ambiente Windows da sessao.
