# Troubleshooting

## `ModuleNotFoundError`
Instale dependencias:
```bash
pip install -r requirements.txt
pip install -e .
```

## GUI nao abre
- Verifique instalacao do PySide6.
- Teste: `python -m sciseek gui`.

## Nenhum resultado encontrado
- Revise termos e modo de busca.
- Para boolean, valide sintaxe em docs/search-syntax.md.

## Performance
- Ative cache.
- Limite extensoes com `--formats`.
- Ajuste `--max-pages` para PDFs.

## Limpar cache
```bash
python -m sciseek cache clear
```
