# Packaging

## Instalacao editavel
```bash
pip install -e .
```

## Binarios CLI/GUI
Entrypoints:
- `sciseek`
- `sciseek-gui`

## Build com PyInstaller
Windows:
```powershell
scripts/build_windows.ps1
```

Linux:
```bash
bash scripts/build_linux.sh
```

Arquivo spec:
- `sciseek.spec`

## Observacao
A validacao de build foi executada apenas no ambiente Windows desta sessao.
