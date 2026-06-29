# SciSeek

SciSeek is a universal scientific document search tool that scans files like PDF, DOCX, Markdown, and TXT for keywords and custom terms.

## Features

- Multi-format extraction: PDF, DOCX, MD, TXT
- Advanced search modes: simple, regex, proximity, boolean
- Configurable search groups + custom terms
- SQLite cache for faster reruns
- Export results to Markdown, CSV, or JSON

## Installation

```bash
pip install -r requirements.txt
```

## Quick Start

```bash
python research_searcher.py
```

Run the interactive wizard and choose:
1. Root folder
2. File formats
3. Search groups or custom terms
4. Search mode
5. Output format

## CLI Example

```bash
python research_searcher.py --root . --formats pdf,md --terms "microscopy,histology" --mode simple --output markdown
```

## Project Structure

- `research_searcher.py`: main entry point
- `extractors/`: format-specific text extractors
- `searchers/`: search engines and modes
- `database/`: SQLite cache layer
- `config/default.yml`: default settings

## License

MIT
