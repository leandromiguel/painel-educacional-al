"""
Página 2 — Municípios
Variação do IDEB entre 2005 e 2023 + scatter ponto de partida vs variação.
"""

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(
    page_title="Municípios — Painel Educacional AL",
    page_icon="🏙️",
    layout="wide",
)

if "df_ideb" not in st.session_state:
    st.warning("Inicie o app pela página principal: `streamlit run app.py`")
    st.stop()

df = st.session_state["df_ideb"]
ai = df.copy()

# ── Cálculo da variação ───────────────────────────────────────────────────────
ideb_2005 = (
    ai[ai["ano"] == 2005]
    .set_index("CO_MUNICIPIO")["ideb"]
    .rename("ideb_2005")
)
ideb_2023 = (
    ai[ai["ano"] == 2023]
    .set_index("CO_MUNICIPIO")["ideb"]
    .rename("ideb_2023")
)
nomes = (
    ai[["CO_MUNICIPIO", "NO_MUNICIPIO"]]
    .drop_duplicates()
    .set_index("CO_MUNICIPIO")
)

variacao = (
    pd.concat([nomes, ideb_2005, ideb_2023], axis=1)
    .dropna(subset=["ideb_2005", "ideb_2023"])
    .assign(variacao=lambda x: (x["ideb_2023"] - x["ideb_2005"]).round(2))
    .sort_values("variacao", ascending=False)
    .reset_index()
)

# ── Layout ────────────────────────────────────────────────────────────────────
st.title("Municípios — Variação do IDEB (2005→2023)")
st.caption("Ensino Fundamental Anos Iniciais · Rede Pública · 96 municípios com dados nos dois anos")

# Metric cards
c1, c2, c3, c4 = st.columns(4)
c1.metric("Municípios analisados", len(variacao))
c2.metric(
    "Maior variação",
    f"+{variacao['variacao'].max():.1f}",
    variacao.iloc[0]["NO_MUNICIPIO"],
)
c3.metric(
    "Menor variação",
    f"+{variacao['variacao'].min():.1f}",
    variacao.iloc[-1]["NO_MUNICIPIO"],
)
c4.metric(
    "Variação média",
    f"+{variacao['variacao'].mean():.2f}",
    "nenhum município piorou",
)

st.divider()

# ── Controle: quantos municípios mostrar ─────────────────────────────────────
col_ctrl, _ = st.columns([1, 3])
with col_ctrl:
    top_n = st.slider("Municípios por extremo", min_value=5, max_value=20, value=10)

st.subheader(f"Top {top_n} que mais melhoraram e menos melhoraram")

top_melhores = variacao.head(top_n)
top_piores   = variacao.tail(top_n).sort_values("variacao")

fig_bar = go.Figure()
fig_bar.add_trace(go.Bar(
    y=top_melhores["NO_MUNICIPIO"],
    x=top_melhores["variacao"],
    orientation="h",
    name="Mais melhoraram",
    marker_color="#1D9E75",
    hovertemplate="<b>%{y}</b><br>Variação: +%{x:.2f}<extra></extra>",
))
fig_bar.add_trace(go.Bar(
    y=top_piores["NO_MUNICIPIO"],
    x=top_piores["variacao"],
    orientation="h",
    name="Menos melhoraram",
    marker_color="#D85A30",
    hovertemplate="<b>%{y}</b><br>Variação: +%{x:.2f}<extra></extra>",
))
fig_bar.update_layout(
    height=max(400, top_n * 40),
    xaxis_title="Variação do IDEB (2005→2023)",
    barmode="overlay",
    legend=dict(orientation="h", yanchor="bottom", y=1.02),
    margin=dict(l=160),
)
st.plotly_chart(fig_bar, use_container_width=True)

st.divider()

# ── Scatter: ponto de partida vs variação ────────────────────────────────────
st.subheader("Ponto de partida (2005) vs Variação até 2023")
st.caption(
    "Cada ponto é um município. "
    "Linha vertical = média de AL em 2005. "
    "Todos os municípios tiveram variação positiva."
)

media_2005 = variacao["ideb_2005"].mean()

fig_sc = px.scatter(
    variacao,
    x="ideb_2005",
    y="variacao",
    color="variacao",
    color_continuous_scale=["#D85A30", "#F1EFE8", "#1D9E75"],
    custom_data=["NO_MUNICIPIO", "ideb_2005", "ideb_2023", "variacao"],
    labels={
        "ideb_2005": "IDEB em 2005",
        "variacao":  "Variação 2005→2023",
    },
    height=480,
)
fig_sc.update_traces(
    marker=dict(size=8),
    hovertemplate=(
        "<b>%{customdata[0]}</b><br>"
        "IDEB 2005: %{customdata[1]:.2f}<br>"
        "IDEB 2023: %{customdata[2]:.2f}<br>"
        "Variação: +%{customdata[3]:.2f}<br>"
        "<extra></extra>"
    ),
)
fig_sc.add_vline(
    x=media_2005, line_dash="dash", line_color="#888780",
    annotation_text="Média AL 2005",
    annotation_position="top",
)
fig_sc.add_hline(
    y=0, line_dash="dash", line_color="#888780",
    annotation_text="Sem variação",
    annotation_position="right",
)
fig_sc.update_coloraxes(showscale=False)
fig_sc.update_layout(showlegend=False)
st.plotly_chart(fig_sc, use_container_width=True)

# ── Tabela completa ───────────────────────────────────────────────────────────
with st.expander("Ver tabela completa de municípios"):
    st.dataframe(
        variacao[["NO_MUNICIPIO", "ideb_2005", "ideb_2023", "variacao"]]
        .rename(columns={
            "NO_MUNICIPIO": "Município",
            "ideb_2005":    "IDEB 2005",
            "ideb_2023":    "IDEB 2023",
            "variacao":     "Variação",
        })
        .reset_index(drop=True),
        use_container_width=True,
        height=300,
    )