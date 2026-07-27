# Painel de Indicadores Educacionais — Alagoas

Dashboard interativo de análise de dados educacionais dos municípios
alagoanos. Desenvolvido como projeto final do curso de Data Analytics e Visualização de Dados.

## Escopo do projeto

**Etapa analisada:** Ensino Fundamental Anos Iniciais (1º ao 5º ano)

Esta etapa foi escolhida por três motivos:

- Cobertura completa: 102 municípios com dados disponíveis
- Série histórica mais longa: 2005 a 2023 (10 edições)
- Comparabilidade direta com a média nacional

## Perguntas analíticas

1. Alagoas está convergindo ou divergindo da média nacional no IDEB desde 2005?
2. Quais municípios mais melhoraram e mais pioraram entre 2005 e 2023?
3. Qual item de infraestrutura escolar tem maior correlação com o IDEB?
4. Qual é o perfil dos municípios que já atingiram a meta do IDEB de 6.0?

## Fontes de dados

| Fonte | Dataset | Período | Uso no projeto |
|-------|---------|---------|----------------|
| INEP | IDEB municipal — EF Anos Iniciais | 2005–2023 | Indicador principal de desempenho |
| INEP | Censo Escolar — infraestrutura escolar | 2023 | Variáveis explicativas (infraestrutura) |
| IBGE | Shapefile municípios de Alagoas | 2022 | Mapa coroplético |

## Estrutura de pastas

    painel_educacional_al/
    │
    ├── data/
    │   ├── raw/
    │   │   ├── inep/          # IDEB + Censo Escolar (não versionado)
    │   │   └── ibge/          # shapefile municípios AL (não versionado)
    │   ├── processed/         # datasets limpos e integrados (não versionado)
    │   └── external/          # dados auxiliares
    │
    ├── notebooks/
    │   ├── 01_limpeza.ipynb           # ETL — leitura, filtro, tidy, salva parquet
    │   ├── 02_eda.ipynb               # Perguntas 1 e 2 — convergência e variação
    │   ├── 03_infraestrutura.ipynb    # Pergunta 3 — infraestrutura vs IDEB
    │   └── 04_meta_ideb.ipynb         # Pergunta 4 — municípios que atingiram meta 6.0
    │
    ├── pages/
    │   ├── 01_visao_geral.py
    │   ├── 02_municipios.py
    │   ├── 03_infraestrutura.py
    │   ├── 04_meta.py
    │   └── 05_mapa.py
    │
    ├── src/
    │   └── config.py                  # caminhos e constantes centralizados
    │
    ├── app.py                         # dashboard Streamlit
    ├── environment.yml                # ambiente conda reproduzível
    └── README.md

## Como reproduzir

**1. Clonar o repositório**

    git clone https://github.com/leandromiguel/painel-educacional-al.git
    cd painel_educacional_al

**2. Criar o ambiente conda**

    mamba env create -f environment.yml
    conda activate painel-al

**3. Baixar os dados manualmente**

- IDEB: https://www.gov.br/inep/pt-br/areas-de-atuacao/pesquisas-estatisticas-e-indicadores/ideb/resultados
- Censo Escolar: https://www.gov.br/inep/pt-br/acesso-a-informacao/dados-abertos/microdados/censo-escolar
- Salvar em data/raw/inep/

**4. Executar os notebooks em ordem**

- notebooks/01_limpeza.ipynb
- notebooks/02_eda.ipynb
- notebooks/03_infraestrutura.ipynb
- notebooks/04_fundeb.ipynb

**5. Rodar o dashboard**

    streamlit run app.py

## Tecnologias

Python 3.12 · pandas · GeoPandas · Plotly · Streamlit · SciPy

## Autor

Leandro Miguel dos Santos — curso de Data Analytics e Visualização de Dados — 2026