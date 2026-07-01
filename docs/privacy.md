# Privacy

SciSeek processa documentos localmente.

## O que nao faz
- Nao envia arquivos para internet.
- Nao usa telemetria.
- Nao integra servicos externos para leitura de conteudo.

## O que armazena localmente
- Configuracoes do usuario.
- Cache de texto extraido (se habilitado).
- Historico de execucoes (metadados, sem conteudo integral).
- Logs tecnicos locais.

## Controle do usuario
- Limpar cache via CLI (`sciseek cache clear`).
- Limpar historico via API/rotina de manutencao.
- Desativar cache na execucao (`--no-cache`).
