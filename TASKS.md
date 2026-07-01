# TASKS - SciSeek

## Fase 0 - Preservacao e Inventario
- [x] Inventariar estrutura do repositorio
- [x] Executar testes existentes
- [x] Executar CLI atual
- [x] Registrar falhas iniciais
- [x] Criar arquivos de controle

## Fase 1 - Auditoria Tecnica
- [x] Auditar descoberta de arquivos e formatos
- [x] Auditar semantica de busca (simple/regex/proximity/boolean)
- [x] Auditar cache e quick mode
- [x] Auditar exportacao
- [x] Registrar problemas em docs/known_issues.md

## Fase 2 - Nucleo Compartilhado
- [x] Criar pacote sciseek com modelos tipados
- [x] Criar SearchService com progresso e cancelamento
- [x] Integrar extractors legados via adaptador
- [x] Implementar parser booleano com parenteses
- [x] Implementar validacao de regex

## Fase 3 - CLI Completa
- [x] Implementar comandos `sciseek search/gui/cache/history/config`
- [x] Preservar compatibilidade de `research_searcher.py`
- [x] Implementar `--quick`
- [x] Implementar `--no-cache` efetivo

## Fase 4 - GUI Desktop
- [x] Janela principal funcional em PySide6
- [x] Worker em thread com cancelamento cooperativo
- [x] Progresso em tempo real
- [x] Resultados em QAbstractTableModel
- [x] Recursos avançados de UX (filtro, agrupamento, historico visual, detalhes, acoes de abrir/copiar)

## Fase 5 - Exportadores
- [x] Markdown com escaping basico
- [x] CSV com biblioteca csv
- [x] JSON estruturado
- [x] HTML funcional
- [x] BibTeX parcial documentado

## Fase 6 - Configuracao e dados locais
- [x] Estrutura por platformdirs com fallback local
- [x] Separacao de cache/historico/config
- [x] Invalidação de cache por tamanho+mtime+versao+parametros
- [ ] Migracao de esquema avançada

## Fase 7 - Testes
- [x] Unitarios (parser, engine)
- [x] Integracao (discover/extract/search/export)
- [x] Smoke test
- [x] GUI smoke com skip seguro

## Fase 8 - Qualidade
- [x] pyproject com ruff/mypy/pytest
- [x] ruff check passando
- [x] mypy do pacote sciseek sem erros criticos
- [x] pytest passando

## Fase 9 - Documentacao
- [x] README atualizado
- [x] docs/user-guide.md
- [x] docs/cli-reference.md
- [x] docs/search-syntax.md
- [x] docs/architecture.md
- [x] docs/packaging.md
- [x] docs/troubleshooting.md
- [x] docs/privacy.md

## Fase 10 - Empacotamento
- [x] pyproject com entrypoints
- [x] sciseek.spec
- [x] scripts build/run/smoke
- [ ] Validacao cross-platform fora do ambiente Windows

## Fase 11 - CI
- [x] Workflow GitHub Actions (lint, mypy, pytest, smoke)
