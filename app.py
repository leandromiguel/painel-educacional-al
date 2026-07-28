"""
app.py — Ponto de entrada do dashboard.

Carrega os dados uma única vez e os armazena em st.session_state
para que todas as páginas possam acessar sem recarregar.

Uso:
    streamlit run app.py
"""

import sys
from pathlib import Path
import pandas as pd
import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parent))
from src.config import IDEB_SERIES_PARQUET, DATA_INEP

# ── Configuração da página ────────────────────────────────────────────────────
st.set_page_config(
    page_title="Painel Educacional — Alagoas",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Carregamento de dados (apenas uma vez por sessão) ─────────────────────────
@st.cache_data
def carregar_ideb():
    df = pd.read_parquet(IDEB_SERIES_PARQUET)
    return df[df["etapa"] == "EF Anos Iniciais"].copy()

@st.cache_data
def carregar_censo():
    from src.config import INFRA_PARQUET
    return pd.read_parquet(INFRA_PARQUET)

    COLUNAS = [
        "CO_UF", "CO_MUNICIPIO", "NO_MUNICIPIO",
        "TP_DEPENDENCIA", "TP_SITUACAO_FUNCIONAMENTO",
        "IN_BIBLIOTECA", "IN_BIBLIOTECA_SALA_LEITURA",
        "IN_LABORATORIO_INFORMATICA", "IN_LABORATORIO_CIENCIAS",
        "IN_QUADRA_ESPORTES", "IN_INTERNET",
    ]

    ITENS = [
        "IN_BIBLIOTECA", "IN_BIBLIOTECA_SALA_LEITURA",
        "IN_LABORATORIO_INFORMATICA", "IN_LABORATORIO_CIENCIAS",
        "IN_QUADRA_ESPORTES", "IN_INTERNET",
    ]

    chunks = []
    for chunk in pd.read_csv(
        censo_path, sep=";", encoding="latin-1",
        usecols=COLUNAS, chunksize=10_000,
    ):
        f = chunk[
            (chunk["CO_UF"] == 27) &
            (chunk["TP_SITUACAO_FUNCIONAMENTO"] == 1) &
            (chunk["TP_DEPENDENCIA"].isin([2, 3]))
        ]
        if not f.empty:
            chunks.append(f)

    df_censo = pd.concat(chunks, ignore_index=True)

    df_infra = (
        df_censo.groupby("CO_MUNICIPIO")[ITENS]
        .mean().multiply(100).round(1).reset_index()
    )
    df_infra["CO_MUNICIPIO"] = df_infra["CO_MUNICIPIO"].astype(str)
    return df_infra

# Carregar e armazenar em session_state
if "df_ideb" not in st.session_state:
    st.session_state["df_ideb"] = carregar_ideb()

if "df_infra" not in st.session_state:
    with st.spinner("Carregando dados do Censo Escolar..."):
        st.session_state["df_infra"] = carregar_censo()

# ── Página inicial ────────────────────────────────────────────────────────────
st.title("Painel de Indicadores Educacionais — Alagoas")
st.markdown("""
Análise do desempenho educacional dos **102 municípios alagoanos**
no Ensino Fundamental Anos Iniciais, com dados do INEP (2005–2023).

Navegue pelas páginas no menu lateral para explorar as análises:

- **Visão geral** — evolução do IDEB de AL vs Brasil
- **Municípios** — quem mais melhorou e mais piorou
- **Infraestrutura** — relação entre estrutura escolar e IDEB
- **Meta 6.0** — municípios que já atingiram a média nacional
- **Mapa** - mapa coroplético
""")

st.info(
    "💡 Os dados são carregados uma única vez e ficam em cache durante a sessão. "
    "A primeira execução pode levar alguns segundos para processar o Censo Escolar."
)