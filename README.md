# SciSeek

SciSeek is a local-first desktop and CLI application to find terms, patterns and expressions in scientific documents.

## Overview

SciSeek scans local files and runs search modes:
- simple literal terms
- regex patterns
- proximity terms
- boolean expressions with parentheses

Supported formats today:
- PDF
- DOCX
- Markdown
- TXT

## Privacy

SciSeek is local-only:
- no telemetry
- no cloud upload
- no external API calls for document content

## Requirements

- Python 3.11+
- Dependencies from requirements.txt

## Installation

```bash
python -m venv .venv
. .venv/Scripts/activate
pip install -r requirements.txt
pip install -e .
```

## Run GUI

```bash
python -m sciseek gui
```

Or:

```bash
sciseek gui
```

## Run CLI

Wizard mode:

```bash
python -m sciseek
```

Search mode:

```bash
python -m sciseek search --root . --formats pdf,md --terms "microscopy,histology" --mode simple --output markdown
```

Windows (PowerShell) direct script mode:

```powershell
python sciseek\cli.py search --root . --formats md,txt --terms SciSeek --mode simple --output json --output-dir out --output-name manual_direct
```

Boolean mode:

```bash
python -m sciseek search --root . --mode boolean --boolean-query "(microplastic OR nanoplastic) AND tendon AND NOT review"
```

Regex mode (valid):

```bash
python -m sciseek search --root . --formats md,txt --terms "microplast(ic|ics)" --mode regex --output json --output-dir out --output-name manual_regex
```

Regex mode (invalid pattern, expected friendly validation error):

```bash
python -m sciseek search --root . --formats md,txt --terms "(" --mode regex --output json --output-dir out --output-name manual_regex_invalid
```

## Legacy compatibility

Existing commands remain available:

```bash
python research_searcher.py --root . --formats md --terms SciSeek --mode simple --output markdown
python research_searcher.py --quick
```

## Search modes

- simple: literal terms independently
- regex: each term interpreted as regular expression
- proximity: consecutive term pairs must appear within a configurable word distance
- boolean: explicit parser for AND, OR, NOT and parentheses

More details in docs/search-syntax.md.

## Groups and config

You can pass pre-defined groups from config/default.yml using:

```bash
python -m sciseek search --groups microscopy,plastics --config-file config/default.yml
```

## Cache and history

Cache commands:

```bash
python -m sciseek cache stats
python -m sciseek cache clear
```

History command:

```bash
python -m sciseek history --limit 10
python -m sciseek history --limit 10 --json
```

## Exports

Formats:
- Markdown
- CSV (stdlib csv)
- JSON
- HTML
- BibTeX partial mode

## Testing

```bash
pytest -q
python scripts/smoke_test.py
```

Recommended full validation (edx environment on Windows):

```powershell
C:/Users/fabio/miniconda3/envs/edx/python.exe -m ruff check .
C:/Users/fabio/miniconda3/envs/edx/python.exe -m mypy sciseek
C:/Users/fabio/miniconda3/envs/edx/python.exe -m pytest -q
```

## Packaging

```bash
# Windows
scripts/build_windows.ps1

# Linux
bash scripts/build_linux.sh
```

See docs/packaging.md.

## Development checks

```bash
ruff check .
mypy sciseek
pytest --cov=sciseek
```

## Project structure

- sciseek/core: shared service, models, settings
- sciseek/cli.py: command line interface
- sciseek/gui: PySide6 desktop interface
- sciseek/exporters: output writers
- sciseek/database: cache and history storage
- research_searcher.py: compatibility wrapper

## Troubleshooting

See docs/troubleshooting.md.

## License

MIT
