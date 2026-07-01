# Problemas Conhecidos (Auditoria Inicial)

## Confirmados
1. `--quick` nao implementado na CLI legada.
2. `--no-cache` sem efeito real (cache usado sempre).
3. Exportadores HTML e BibTeX expostos em opcoes, nao implementados.
4. Busca booleana simplificada sem parser completo de parenteses.
5. CSV montado por concatenacao manual sem `csv`.
6. Contagem de "Arquivos examinados" inconsistente em relatorio Markdown.
7. Nucleo atual acoplado a `print/input` e sem separacao completa de interface.

## Riscos detectados
1. Possivel regex custosa sem limite de seguranca.
2. Pouca cobertura de testes de integracao e GUI.
3. Estado de erros pode persistir entre execucoes no mesmo objeto.

## Estrategia de correcao
- Refatorar para `SearchService` desacoplado.
- Implementar parser booleano dedicado.
- Implementar exportadores robustos.
- Criar testes unitarios e de integracao cobrindo os defeitos.
