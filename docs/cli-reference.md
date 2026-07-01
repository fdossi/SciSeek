# CLI Reference

## Entrypoints
- `python -m sciseek`
- `sciseek`
- compatibilidade: `python research_searcher.py`

## Comandos
### `sciseek`
Executa wizard interativo.

### `sciseek gui`
Abre interface grafica.

### `sciseek search`
Opcoes principais:
- `--root`
- `--formats`
- `--terms`
- `--groups`
- `--mode`
- `--boolean-query`
- `--proximity`
- `--context-words`
- `--case-sensitive`
- `--no-recursive`
- `--include-hidden`
- `--no-cache`
- `--output`
- `--output-dir`
- `--output-name`
- `--max-pages`
- `--config-file`
- `--quiet`

### `sciseek cache`
- `stats`
- `clear`

### `sciseek history`
- `--limit`
- `--json`

### `sciseek config`
- `show`
- `set --key KEY --value VALUE`

### `sciseek --quick`
Mostra a ultima execucao registrada e orienta reaproveitamento.
