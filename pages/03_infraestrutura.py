"""
Página 3 — Infraestrutura
Correlação entre infraestrutura escolar e IDEB 2023 nos municípios de AL.
"""

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from scipy import stats

st.set_page_config(
    page_title="Infraestrutura — Painel Educacional AL",
    page_icon="🏫",
    layout="wide",
)

if "df_ideb" not in st.session_state or "df_infra" not in st.session_state:
    st.warning("Inicie o app pela página principal: `streamlit run app.py`")
    st.stop()

df_ideb = st.session_state["df_ideb"]
df_infra = st.session_state["df_infra"]

# ── Preparação dos dados ──────────────────────────────────────────────────────
ITENS_INFRA = [
    "IN_BIBLIOTECA",
    "IN_BIBLIOTECA_SALA_LEITURA",
    "IN_LABORATORIO_INFORMATICA",
    "IN_LABORATORIO_CIENCIAS",
    "IN_QUADRA_ESPORTES",
    "IN_INTERNET",
]

NOMES = {
    "IN_BIBLIOTECA":             "Biblioteca",
    "IN_BIBLIOTECA_SALA_LEITURA":"Biblioteca/sala leitura",
    "IN_LABORATORIO_INFORMATICA":"Lab. informática",
    "IN_LABORATORIO_CIENCIAS":   "Lab. ciências",
    "IN_QUADRA_ESPORTES":        "Quadra esportiva",
    "IN_INTERNET":               "Internet",
}

ideb_2023 = (
    df_ideb[df_ideb["ano"] == 2023]
    [["CO_MUNICIPIO", "NO_MUNICIPIO", "ideb"]]
    .rename(columns={"ideb": "ideb_2023"})
)

df_merge = df_infra.merge(ideb_2023, on="CO_MUNICIPIO", how="inner")

# Correlações de Spearman
corr_rows = []
for col in ITENS_INFRA:
    sub = df_merge[["ideb_2023", col]].dropna()
    r, p = stats.spearmanr(sub[col], sub["ideb_2023"])
    corr_rows.append({
        "item":         col,
        "label":        NOMES[col],
        "r":            round(r, 3),
        "p":            round(p, 4),
        "significativo": p < 0.05,
    })
df_corr = pd.DataFrame(corr_rows).sort_values("r", ascending=False)

# ── Layout ────────────────────────────────────────────────────────────────────
st.title("Infraestrutura Escolar vs IDEB 2023")
st.caption("Correlação de Spearman · 100 municípios · Rede pública · Censo Escolar 2023")

st.info(
    "**Achado principal:** nenhum item de infraestrutura analisado apresentou "
    "correlação estatisticamente significativa com o IDEB 2023 em Alagoas "
    "(todos os p-valores > 0.05). A presença de infraestrutura física não "
    "explica as diferenças de desempenho entre os municípios."
)

st.divider()

# ── Cobertura média por item ──────────────────────────────────────────────────
st.subheader("Cobertura média de infraestrutura nas escolas públicas de AL")

cobertura = df_infra[ITENS_INFRA].mean().round(1).reset_index()
cobertura.columns = ["item", "pct"]
cobertura["label"] = cobertura["item"].map(NOMES)
cobertura = cobertura.sort_values("pct", ascending=True)

fig_cob = go.Figure(go.Bar(
    x=cobertura["pct"],
    y=cobertura["label"],
    orientation="h",
    marker_color=[
        "#1D9E75" if p >= 50 else "#378ADD" if p >= 20 else "#D85A30"
        for p in cobertura["pct"]
    ],
    text=[f"{p:.1f}%" for p in cobertura["pct"]],
    textposition="outside",
    hovertemplate="<b>%{y}</b><br>Cobertura: %{x:.1f}%<extra></extra>",
))
fig_cob.update_layout(
    height=320,
    xaxis=dict(range=[0, 110], title="% de escolas com o item"),
    margin=dict(l=160, r=60),
    showlegend=False,
)
st.plotly_chart(fig_cob, use_container_width=True)

st.divider()

# ── Tabela de correlações ─────────────────────────────────────────────────────
st.subheader("Correlação de Spearman com IDEB 2023")

df_corr_display = df_corr[["label", "r", "p", "significativo"]].copy()
df_corr_display.columns = ["Item", "r (Spearman)", "p-valor", "Significativo"]
df_corr_display["Significativo"] = df_corr_display["Significativo"].map(
    {True: "✓", False: "✗"}
)

st.dataframe(
    df_corr_display.reset_index(drop=True),
    use_container_width=True,
    hide_index=True,
)

st.divider()

# ── Scatter interativo ────────────────────────────────────────────────────────
st.subheader("Explorar relação entre um item e o IDEB")

item_sel = st.selectbox(
    "Selecione o item de infraestrutura:",
    options=ITENS_INFRA,
    format_func=lambda x: NOMES[x],
)

sub = df_merge[["NO_MUNICIPIO", item_sel, "ideb_2023"]].dropna()
r_val = df_corr[df_corr["item"] == item_sel]["r"].values[0]
p_val = df_corr[df_corr["item"] == item_sel]["p"].values[0]

fig_sc = px.scatter(
    sub,
    x=item_sel,
    y="ideb_2023",
    custom_data=["NO_MUNICIPIO", item_sel, "ideb_2023"],
    color="ideb_2023",
    color_continuous_scale=["#D85A30", "#F1EFE8", "#1D9E75"],
    labels={
        item_sel:    f"% escolas com {NOMES[item_sel]}",
        "ideb_2023": "IDEB 2023",
    },
    title=f"{NOMES[item_sel]} vs IDEB 2023 — r={r_val} | p={p_val}",
    height=420,
)
fig_sc.update_traces(
    marker=dict(size=8),
    hovertemplate=(
        "<b>%{customdata[0]}</b><br>"
        f"{NOMES[item_sel]}: " + "%{customdata[1]:.1f}%<br>"
        "IDEB 2023: %{customdata[2]:.2f}<br>"
        "<extra></extra>"
    ),
)

# Linha de tendência
x = sub[item_sel].values
y = sub["ideb_2023"].values
m, b = np.polyfit(x, y, 1)
x_line = np.linspace(x.min(), x.max(), 100)
fig_sc.add_scatter(
    x=x_line, y=m * x_line + b,
    mode="lines",
    line=dict(color="#888780", width=1.5, dash="dash"),
    hoverinfo="skip",
    showlegend=False,
)

fig_sc.update_coloraxes(showscale=False)
st.plotly_chart(fig_sc, use_container_width=True)