# Arquitetura - SciSeek

## Objetivo
Unificar CLI e GUI sobre um unico nucleo de aplicacao local, sem subprocess entre interfaces.

## Decisoes tecnicas
1. Nucleo unico em `sciseek/core/service.py` com API `SearchService`.
2. Contratos tipados com `dataclasses` em `sciseek/core/models.py`.
3. Cancelamento cooperativo por `threading.Event`.
4. Progresso via callbacks e eventos tipados.
5. Persistencia local via SQLite e diretorios do usuario com `platformdirs`.
6. CLI (`sciseek/cli.py`) e GUI (`sciseek/gui/main_window.py`) apenas orquestram o nucleo.
7. Compatibilidade preservada por wrapper em `research_searcher.py`.

## Fluxo de execucao
Discover -> Extract -> Search -> Export -> History

## Semantica de busca
- simple: termos literais independentes
- regex: padroes independentes com validacao
- proximity: distancia maxima em palavras
- boolean: parser com `AND`, `OR`, `NOT` e parenteses

## Seguranca local
- Sem envio de dados para rede.
- Validacao de caminhos de entrada e saida.
- Escrita de exportacao dentro de pasta autorizada.
- Logs sem dump integral do conteudo dos documentos.
