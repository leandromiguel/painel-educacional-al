"""
Página 5 — Mapa Coroplético
Distribuição geográfica do IDEB nos municípios de Alagoas.
"""

import json
import sys
from pathlib import Path

import geopandas as gpd
import pandas as pd
import plotly.express as px
import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.config import IDEB_SERIES_PARQUET, SHAPEFILE_AL

st.set_page_config(
    page_title="Mapa — Painel Educacional AL",
    page_icon="🗺️",
    layout="wide",
)

# ── Carregar dados ────────────────────────────────────────────────────────────
@st.cache_data
def carregar_geodados():
    gdf = gpd.read_file(SHAPEFILE_AL)
    gdf["CD_MUN"] = gdf["CD_MUN"].astype(str)
    return gdf[["CD_MUN", "NM_MUN", "AREA_KM2", "geometry"]].copy()

@st.cache_data
def carregar_ideb_completo():
    df = pd.read_parquet(IDEB_SERIES_PARQUET)
    return df[df["etapa"] == "EF Anos Iniciais"].copy()

gdf = carregar_geodados()
df  = carregar_ideb_completo()

# ── Layout ────────────────────────────────────────────────────────────────────
st.title("Mapa de Indicadores Educacionais — Alagoas")
st.caption("Ensino Fundamental Anos Iniciais · Rede Pública · Municípios de AL")

# Controles
col_ctrl1, col_ctrl2, _ = st.columns([1, 1, 2])

with col_ctrl1:
    anos_disp = sorted(df["ano"].unique(), reverse=True)
    ano_sel = st.selectbox("Edição do IDEB:", anos_disp)

with col_ctrl2:
    escala = st.selectbox(
        "Escala de cores:",
        ["Blues", "RdYlGn", "Viridis"],
        index=1,
    )

# Definir col_ideb ANTES de usá-lo
col_ideb = f"ideb_{ano_sel}"

# Preparar dados do ano selecionado
ideb_ano = (
    df[df["ano"] == ano_sel]
    [["CO_MUNICIPIO", "NO_MUNICIPIO", "ideb"]]
    .rename(columns={"ideb": col_ideb})
)

gdf_plot = gdf.merge(
    ideb_ano,
    left_on="CD_MUN",
    right_on="CO_MUNICIPIO",
    how="left",
)

# Converter para GeoJSON
geojson = json.loads(gdf_plot.to_json())

# Metric cards
dados_validos = gdf_plot[col_ideb].dropna()
c1, c2, c3, c4 = st.columns(4)
c1.metric("IDEB médio AL", f"{dados_validos.mean():.2f}")
c2.metric(
    "Maior IDEB", f"{dados_validos.max():.1f}",
    gdf_plot.loc[gdf_plot[col_ideb].idxmax(), "NM_MUN"],
)
c3.metric(
    "Menor IDEB", f"{dados_validos.min():.1f}",
    gdf_plot.loc[gdf_plot[col_ideb].idxmin(), "NM_MUN"],
)
c4.metric(
    "Acima da meta 6.0",
    f"{(dados_validos >= 6.0).sum()} municípios",
)

st.divider()

# ── Mapa coroplético ──────────────────────────────────────────────────────────
fig = px.choropleth(
    gdf_plot,
    geojson=geojson,
    locations=gdf_plot.index,
    color=col_ideb,
    hover_name="NM_MUN",
    hover_data={
        col_ideb:       ":.2f",
        "AREA_KM2":     ":.0f",
        "CO_MUNICIPIO": False,
    },
    color_continuous_scale=escala,
    range_color=[
        dados_validos.min() - 0.5,
        dados_validos.max() + 0.5,
    ],
    labels={col_ideb: f"IDEB {ano_sel}"},
    title=f"IDEB {ano_sel} — EF Anos Iniciais · Alagoas",
)

fig.update_geos(fitbounds="locations", visible=False)
fig.update_layout(
    height=580,
    margin=dict(l=0, r=0, t=40, b=0),
    coloraxis_colorbar=dict(
        title=f"IDEB {ano_sel}",
        thickness=14,
        len=0.6,
    ),
)

st.plotly_chart(fig, use_container_width=True)

st.caption(
    "Municípios sem cor: sem IDEB disponível nesta edição "
    "(escolas com menos de 10 alunos avaliados ficam fora do cálculo do IDEB)."
)

st.divider()

# ── Tabela ────────────────────────────────────────────────────────────────────
with st.expander(f"Ver dados completos — IDEB {ano_sel}"):
    tabela = (
        gdf_plot[["NM_MUN", col_ideb]]
        .rename(columns={
            "NM_MUN": "Município",
            col_ideb: f"IDEB {ano_sel}",
        })
        .sort_values(f"IDEB {ano_sel}", ascending=False)
        .reset_index(drop=True)
    )
    st.dataframe(tabela, use_container_width=True, hide_index=True, height=300)