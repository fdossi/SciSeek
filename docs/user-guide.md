# User Guide

## O que e o SciSeek
SciSeek e um buscador local de termos e expressoes para documentos cientificos.

## Fluxo recomendado
1. Abra a GUI com `python -m sciseek gui`.
2. Escolha a pasta de documentos.
3. Selecione formatos.
4. Defina termos ou expressao booleana.
5. Inicie a busca e acompanhe progresso.
6. Revise resultados na tabela e exporte.

## Modos de busca
- Simple: termos literais.
- Regex: expressoes regulares.
- Proximity: termos proximos em numero de palavras.
- Boolean: AND, OR, NOT, parenteses.

## Historico e cache
- Historico registra metadados da execucao (sem conteudo integral dos arquivos).
- Cache acelera leituras repetidas e pode ser limpo a qualquer momento.

## Exportacao
Use Markdown, CSV, JSON, HTML ou BibTeX parcial.
