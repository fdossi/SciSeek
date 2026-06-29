# Quick Start - Research Document Searcher

## Instalação Rápida (2 minutos)

```bash
# 1. Navegar para o diretório
cd research-searcher

# 2. Instalar dependências
pip install -r requirements.txt

# 3. Testar
python test_research_searcher.py
```

Se todos os testes passarem ✓, você está pronto!

## Primeiro Uso (5 minutos)

### Opção A: Wizard Interativo (Recomendado)

```bash
python research_searcher.py
```

Responda às perguntas:
1. Diretório para busca (Enter = atual)
2. Formatos (Enter = todos)
3. Grupos de busca (números separados por vírgula)
4. Modo de busca (1=simples, 2=regex, 3=proximidade, 4=booleano)
5. Formato de saída (1=markdown, 2=csv, etc)

Resultados aparecerão em `outputs/search_results_YYYYMMDD-HHMMSS.md`

### Opção B: Linha de Comando (Rápido)

```bash
# Buscar termos em PDFs
python research_searcher.py --root . --formats pdf --terms "microscopia,histologia"

# Busca avançada com regex
python research_searcher.py --root . --formats pdf,md --terms "microscop.*" --mode regex

# Busca booleana
python research_searcher.py --root . --terms "(microscopia OR histologia) AND tendão" --mode boolean

# Exportar em CSV
python research_searcher.py --root . --output csv
```

## Exemplos Práticos

### Exemplo 1: Buscar papers sobre microscopia de tendão

```bash
python research_searcher.py \
  --root . \
  --formats pdf \
  --groups microscopy \
  --output markdown
```

Saída: Tabela com todos os PDFs que mencionam termos de microscopia.

### Exemplo 2: Busca de metodologia molecular

```bash
python research_searcher.py \
  --root . \
  --groups molecular_biology \
  --terms "RNA-Seq, qPCR, transcriptoma" \
  --mode simple
```

### Exemplo 3: Busca de interação entre termos

```bash
python research_searcher.py \
  --root . \
  --terms "microplástico,colágeno" \
  --mode proximity
```

Encontra documentos onde "microplástico" e "colágeno" aparecem próximos (< 10 palavras).

## Entender os Resultados

### Arquivo de Saída (Markdown)

```markdown
# Resultado de Busca em Documentos

## Resumo
- **Diretório analisado**: D:\...
- **Arquivos examinados**: 150
- **Resultados encontrados**: 45
- **Modo de busca**: simple
- **Formatos processados**: pdf, md, txt
- **Data/Hora**: 2026-06-26 10:30:00

## Documentos com Correspondência

| Arquivo | Termos Encontrados | Ocorrências | Formato |
|---------|-------------------|-------------|---------|
| paper1.pdf | microscopia, SEM, TEM | 12 | pdf |
| paper2.pdf | histologia, microscop | 8 | pdf |
```

**Interpretar**:
- Arquivo: Nome do documento encontrado
- Termos Encontrados: Quais termos foram encontrados
- Ocorrências: Quantas vezes aparecem
- Formato: Tipo de arquivo (pdf, docx, etc)

## Modos de Busca Explicados

### Simple (Padrão)
```bash
python research_searcher.py --terms "microscopia" --mode simple
```
Busca a string exata "microscopia" (case-insensitive).

### Regex (Avançado)
```bash
python research_searcher.py --terms "microscop(ia|y)" --mode regex
```
Encontra "microscopia" OU "microscopy".

Padrões úteis:
- `.` = qualquer caractere
- `*` = zero ou mais
- `+` = um ou mais
- `|` = OU
- `[abc]` = um dos caracteres

### Proximity (Contextual)
```bash
python research_searcher.py --terms "colágeno,microplástico" --mode proximity
```
Encontra onde os termos aparecem próximos (padrão: 10 palavras).

### Boolean (Lógico)
```bash
python research_searcher.py --terms "(microscopia OR histologia) AND tendão" --mode boolean
```

Operadores:
- `AND`: Ambos devem estar presentes
- `OR`: Pelo menos um deve estar presente
- `NOT`: Não deve estar presente

## Cache

O programa automaticamente cacheia PDFs processados:
- Primeira execução: Lenta (extrai todos)
- Execuções posteriores: Rápidas (usa cache)

Para limpar cache:
```bash
rm -r .cache
```

## Formatos de Saída

### Markdown (Padrão)
Melhor para: Visualização no editor, GitHub
```bash
python research_searcher.py --output markdown
```

### CSV
Melhor para: Excel, análise em Sheets
```bash
python research_searcher.py --output csv
```

### JSON
Melhor para: Processamento automático
```bash
python research_searcher.py --output json
```

Acessar dados em Python:
```python
import json
with open("search_results_*.json") as f:
    data = json.load(f)
    for result in data["results"]:
        print(result["file_name"])
```

## Solução de Problemas

### Erro: "Module not found: docx"
```bash
pip install python-docx
```

### Erro: "ModuleNotFoundError: pyyaml"
```bash
pip install pyyaml
```

### Busca muito lenta?
- Use `--formats pdf` (apenas PDFs)
- Use `--root pasta_pequena` (reduzir escopo)
- Aumente `max_pages` em config/default.yml

### Nenhum resultado encontrado?
- Verifique se os termos estão corretos
- Tente `--mode regex` para flexibilidade
- Verifique se a extensão do arquivo é suportada

## Próximos Passos

1. **Criar arquivo de config customizado**:
   Crie `config/my_config.yml` baseado em `config/default.yml`

2. **Adicionar novos grupos de busca**:
   Edite `config/default.yml`, seção `search_groups`

3. **Automatizar buscas**:
   ```bash
   # Cria script que roda a mesma busca
   python research_searcher.py --root . --groups microscopy > busca_automatica.log
   ```

4. **Estender com novos formatos**:
   Consulte [EXTENSION_GUIDE.md](EXTENSION_GUIDE.md)

## Dicas Avançadas

### Busca recursiva em subpastas
```bash
python research_searcher.py --root . --formats pdf
```
Procura em todas as subpastas (padrão).

### Excluir pastas (editar config)
Edite `config/default.yml`:
```yaml
paths:
  ignore_hidden_files: true  # Ignora .pasta
  recursive_search: true     # Busca em subpastas
```

### Combinar múltiplos grupos
```bash
# No wizard, selecione: 1,2,3
# Ou via CLI: combinar termos manualmente
python research_searcher.py --terms "termo_grupo1,termo_grupo2,termo_custom"
```

### Filtrar por data de modificação
Atualmente não suportado, mas você pode ordenar manualmente depois.

## Recursos Adicionais

- [README.md](README.md) - Documentação completa
- [EXTENSION_GUIDE.md](EXTENSION_GUIDE.md) - Como estender
- [config/default.yml](config/default.yml) - Todas as opções de configuração

## Obter Ajuda

```bash
python research_searcher.py --help
```

Exibe todas as opções disponíveis.

---

**Pronto para começar?**
```bash
python research_searcher.py
```

Boa sorte! 🚀
