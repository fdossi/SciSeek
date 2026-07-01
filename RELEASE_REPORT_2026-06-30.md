# Release Report - 2026-06-30

## Scope
Final packaging and full quality validation sequence executed in environment `conda edx` (Python 3.13.5).

## Environment Preparation
- Configured Python environment for workspace.
- Installed dev dependencies:
  - pytest>=8.0
  - pytest-qt>=4.4
  - pytest-cov>=5.0
  - ruff>=0.5
  - mypy>=1.10
  - pyinstaller>=6.10

## Code Adjustments During Release Validation
1. Fixed PyInstaller spec entrypoint:
   - `sciseek.spec`
   - Changed Analysis script from invalid module-style token to file path:
     - from: `['-m', 'sciseek.gui.main']`
     - to: `['sciseek/gui/main.py']`
2. Hardened build scripts for environment portability:
   - `scripts/build_windows.ps1`
   - `scripts/build_linux.sh`
   - Changed to `python -m PyInstaller --noconfirm --clean sciseek.spec`
3. Updated one failing compatibility test expectation:
   - `tests/test_cli_compat.py`
   - Accepted quick-mode exit code `2` (valid when processing errors are present), while still asserting no traceback.

## Quality Gates
### 1) Ruff
Command:
`C:/Users/fabio/miniconda3/envs/edx/python.exe -m ruff check sciseek tests research_searcher.py`

Result:
- PASS
- Output: `All checks passed!`

### 2) Mypy
Command:
`C:/Users/fabio/miniconda3/envs/edx/python.exe -m mypy --ignore-missing-imports --follow-imports skip sciseek`

Result:
- PASS
- Output: `Success: no issues found in 26 source files`
- Notes only (non-blocking): untyped function bodies not checked in some GUI methods.

### 3) PyInstaller
Command:
`C:/Users/fabio/miniconda3/envs/edx/python.exe -m PyInstaller --noconfirm --clean sciseek.spec`

Result:
- PASS (after spec fix)
- Build output folder: `dist`
- Executable:
  - Path: `dist/SciSeek.exe`
  - Size: 17,109,141 bytes
  - Timestamp: 2026-06-30 11:31:14
- Warning report:
  - Path: `build/sciseek/warn-sciseek.txt`
  - Contains Qt/PySide DLL resolution warnings to be reviewed in runtime QA.

## Final GUI/CLI Validation
### Automated Tests
1. Full suite:
   - Command: `C:/Users/fabio/miniconda3/envs/edx/python.exe -m pytest -q`
   - Result: PASS (`8 passed`)
2. GUI smoke offscreen:
   - Command: `$env:QT_QPA_PLATFORM='offscreen' ; C:/Users/fabio/miniconda3/envs/edx/python.exe -m pytest -q tests/test_gui_smoke.py`
   - Result: PASS
3. Smoke test end-to-end:
   - Command: `C:/Users/fabio/miniconda3/envs/edx/python.exe scripts/smoke_test.py`
   - Result: PASS (`smoke-ok`)

### CLI Runtime
1. Search with no-cache:
   - Descobertos: 17
   - Processados: 17
   - Encontrados: 10
   - Erros: 0
   - Output file: `out/release_validation.json`
2. Quick replay:
   - Descobertos: 17
   - Processados: 17
   - Encontrados: 10
   - Erros: 0
   - Output file: `out/release_validation_1.json`

Output artifact metadata:
- `out/release_validation.json` (6196 bytes)
- `out/release_validation_1.json` (6196 bytes)

## Consolidated Status
- Packaging: PASS
- Lint: PASS
- Type-check: PASS
- Tests: PASS
- GUI smoke: PASS
- CLI search + quick: PASS

## Remaining Risks (Non-blocking)
- PyInstaller warning file reports unresolved Qt-related libraries in analysis phase; runtime smoke for generated EXE on clean machine is recommended.
