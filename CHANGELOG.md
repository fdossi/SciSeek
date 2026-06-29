# Changelog - Research Document Searcher

## v1.0.0 (2026-06-26) - Release Inicial

### ✨ Fase 1: Extração Multi-Formato

- ✅ Factory Pattern para extractores
- ✅ Suporte a PDF (pypdf)
  - Extração de texto de múltiplas páginas
  - Configuração de limite de páginas
  - Extração de metadados (título, autor, data)
  - Tratamento de erros robusto
  
- ✅ Suporte a DOCX (python-docx)
  - Extração de parágrafos
  - Suporte a tabelas
  - Extração de metadados
  
- ✅ Suporte a Markdown
  - Parser de frontmatter YAML
  - Opção de remover blocos de código
  - Normalização de texto
  
- ✅ Suporte a TXT
  - Detecção automática de encoding
  - Fallback para múltiplas encodings (utf-8, latin-1, cp1252)

- ✅ Cache SQLite
  - Armazenamento de documentos extraídos
  - Histórico de buscas
  - Limpeza automática de entradas antigas
  - Estatísticas de cache

### 🔍 Fase 2: Interface Interativa

- ✅ Wizard interativo
  - Seleção de diretório raiz
  - Escolha de formatos de arquivo
  - Seleção de grupos de busca predefinidos
  - Modo de busca
  - Formato de saída
  
- ✅ Menu em linha de comando
  - Argumentos para execução rápida
  - Help automático (--help)
  
- ✅ Histórico de buscas
  - Persistência em SQLite
  - Recuperação de última configuração (preparado)
  
- ✅ Grupos de busca predefinidos
  - Microscopia e histologia (22 termos)
  - Biologia molecular (20 termos)
  - Microplásticos e nanoplásticos (12 termos)
  - Opção para termos customizados

### 🚀 Fase 3: Busca Avançada

- ✅ Busca Simples
  - Strings exatas
  - Case-sensitive opcional
  - Contagem de ocorrências
  
- ✅ Busca com Regex
  - Expressões regulares complexas
  - Flags de case-insensitive
  - Tratamento de padrões inválidos
  
- ✅ Busca por Proximidade
  - Detecção de termos próximos
  - Configuração de distância máxima
  - Extração de contexto
  
- ✅ Busca Booleana
  - Operador AND (ambos presentes)
  - Operador OR (pelo menos um presente)
  - Operador NOT (ausência)
  
- ✅ Extrair contexto
  - Trecho de texto ao redor do termo
  - Configuração de palavras antes/depois

### 📊 Formatos de Saída

- ✅ Markdown
  - Tabelas formatadas
  - Seções estruturadas
  - Metadados legíveis
  
- ✅ CSV
  - Compatível com Excel/Sheets
  - Fácil importação
  
- ✅ JSON
  - Estrutura de dados legível por máquina
  - Metadados completos
  
- ✅ HTML (Framework)
- ✅ BibTeX (Framework)

### ⚙️ Configuração

- ✅ Arquivo YAML (default.yml)
  - Grupos de busca customizáveis
  - Configuração de extração por formato
  - Parâmetros de busca
  - Opções de cache
  - Configuração de logging
  
- ✅ Argparse para CLI
- ✅ Validadores de entrada
- ✅ Logger centralizado

### 🧪 Qualidade

- ✅ Testes unitários
  - ExtractorFactory
  - BasicSearcher
  - AdvancedSearcher
  - PathResolver
  - Validators
  - SearchCache

- ✅ Validação de sintaxe
  - Py_compile para todos os módulos
  - Sem erros de compilação

### 📚 Documentação

- ✅ README.md (completo)
- ✅ QUICKSTART.md (guia rápido)
- ✅ EXTENSION_GUIDE.md (para desenvolvedores)
- ✅ requirements.txt (dependências)
- ✅ Docstrings em todas as funções
- ✅ Comentários inline em código complexo

### 🏗️ Arquitetura

```
research-searcher/
├── research_searcher.py          # Main (500+ linhas, bem documentado)
├── extractors/                   # Módulo plugável
│   ├── base.py                  # Interface abstrata
│   ├── factory.py               # Factory pattern
│   ├── pdf.py                   # PDFExtractor
│   ├── docx.py                  # DocxExtractor
│   ├── markdown_text.py         # MarkdownExtractor + TextExtractor
│   └── __init__.py              # Exports
├── searchers/                   # Lógica de busca
│   ├── basic.py                 # BasicSearcher + AdvancedSearcher
│   └── __init__.py
├── database/                    # Cache e persistência
│   ├── cache.py                 # SQLite manager
│   └── __init__.py
├── utils/                       # Utilitários
│   ├── logger.py               # Logging centralizado
│   ├── path_resolver.py        # Resolução de caminhos
│   ├── validators.py           # Validadores de entrada
│   └── __init__.py
├── config/                      # Configuração
│   ├── default.yml             # Config padrão completa
│   └── __init__.py
├── outputs/                     # Diretório de resultados
├── test_research_searcher.py    # Testes
├── requirements.txt             # Dependências
├── README.md                    # Documentação
├── QUICKSTART.md               # Guia rápido
├── EXTENSION_GUIDE.md          # Para desenvolvedores
└── CHANGELOG.md                # Este arquivo
```

### ✅ Dependências

**Essenciais:**
- pypdf >= 4.0.0 (extração PDF)
- python-docx >= 0.8.11 (suporte DOCX)
- pyyaml >= 6.0 (configuração)

**Opcionais (recomendados):**
- tqdm >= 4.65.0 (barras de progresso)

**Desenvolvimento:**
- pytest >= 7.0 (testes)
- black >= 23.0 (formatação)

## Próximas Versões (Roadmap)

### v1.1.0 (Planejado)
- Suporte a XML
- Suporte a XLSX
- Busca fuzzy (com fuzzywuzzy)
- Modo "quick" para última configuração
- Interface web (Flask)

### v1.2.0 (Planejado)
- Suporte a PPTX
- Busca com stemming
- Análise de similaridade
- Geração de relatório em Word

### v2.0.0 (Planejado)
- API REST
- Banco de dados PostgreSQL
- Processamento em background
- Interface web moderna
- Integração com Zotero

## Notas de Desenvolvimento

### Decisões Arquiteturais

1. **Factory Pattern** para extractores
   - Facilita adicionar novos formatos
   - Interface consistente
   - Fácil de testar

2. **Searcher separado** para cada modo
   - Lógica isolada
   - Fácil de estender
   - Evita classe monolítica

3. **SQLite para cache**
   - Sem dependências externas
   - Persistência automática
   - Fácil de backupear

4. **YAML para configuração**
   - Legível para humanos
   - Mais flexível que JSON
   - Padrão em Python

5. **Logger centralizado**
   - Consistência em toda aplicação
   - Fácil de mudar nivel de detalhe
   - Rastreamento de erros

### Padrões Utilizados

- Factory Pattern (ExtractorFactory)
- Strategy Pattern (SearchMode)
- Singleton Pattern (Logger)
- Template Method (BaseExtractor)
- Dataclass (SearchConfig, DocumentMatch)

### Performance

- Cache SQLite reduz processamento
- Limite de páginas em PDFs (padrão: 30)
- Processamento streaming em buscas
- Progress bars com tqdm

## Agradecimentos

Desenvolvido como ferramenta profissional para análise de documentos científicos.

## Licença

MIT - Veja LICENSE para detalhes.

---

**Versão Atual**: 1.0.0  
**Data**: 2026-06-26  
**Status**: ✅ Estável
