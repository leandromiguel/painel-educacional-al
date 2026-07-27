"""
Página 1 — Visão Geral
Evolução do IDEB de Alagoas vs Brasil (2005–2023) com metric cards.
"""

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(
    page_title="Visão Geral — Painel Educacional AL",
    page_icon="📈",
    layout="wide",
)

# ── Dados ─────────────────────────────────────────────────────────────────────
IDEB_BRASIL = {
    2005: 3.8, 2007: 4.2, 2009: 4.6,
    2011: 4.9, 2013: 5.2, 2015: 5.3,
    2017: 5.5, 2019: 5.7, 2021: 5.8, 2023: 6.0,
}
META = 6.0

if "df_ideb" not in st.session_state:
    st.warning("Inicie o app pela página principal: `streamlit run app.py`")
    st.stop()

df = st.session_state["df_ideb"]

# ── Cálculos ──────────────────────────────────────────────────────────────────
al_ano = (
    df.groupby("ano")["ideb"]
    .mean()
    .reset_index()
    .rename(columns={"ideb": "ideb_al"})
)
al_ano["ideb_brasil"] = al_ano["ano"].map(IDEB_BRASIL)
al_ano["gap"] = (al_ano["ideb_brasil"] - al_ano["ideb_al"]).round(2)

ideb_2023   = al_ano[al_ano["ano"] == 2023]["ideb_al"].values[0]
ideb_2005   = al_ano[al_ano["ano"] == 2005]["ideb_al"].values[0]
gap_2023    = al_ano[al_ano["ano"] == 2023]["gap"].values[0]
gap_2005    = al_ano[al_ano["ano"] == 2005]["gap"].values[0]
variacao    = round(ideb_2023 - ideb_2005, 2)
muns_meta   = df[df["ano"] == 2023]
n_meta      = int((muns_meta["ideb"] >= META).sum())
total_muns  = muns_meta["CO_MUNICIPIO"].nunique()

# ── Layout ────────────────────────────────────────────────────────────────────
st.title("Visão Geral — IDEB Alagoas vs Brasil")
st.caption("Ensino Fundamental Anos Iniciais · Rede Pública · 2005–2023")

# Metric cards
c1, c2, c3, c4 = st.columns(4)
c1.metric(
    "IDEB médio AL (2023)",
    f"{ideb_2023:.2f}",
    f"+{variacao} desde 2005",
)
c2.metric(
    "Gap AL vs Brasil (2023)",
    f"{gap_2023:.2f}",
    f"{round(gap_2023 - gap_2005, 2):.2f} desde 2005",
    delta_color="inverse",
)
c3.metric(
    "Municípios acima da meta 6.0",
    f"{n_meta} de {total_muns}",
    f"{round(n_meta/total_muns*100, 1)}% do total",
)
c4.metric(
    "Meta nacional (EF AI)",
    f"{META}",
    f"AL atingiu em 0 edições",
    delta_color="off",
)

st.divider()

# ── Gráfico de linha ──────────────────────────────────────────────────────────
st.subheader("Evolução do IDEB — Alagoas vs Brasil")

anos_destaque = {
    2005: "Gap: 1.37",
    2013: "Gap máx: 1.61",
    2019: "Gap: 0.43",
    2023: "Gap: 0.09",
}

fig = go.Figure()

# Área do gap
fig.add_trace(go.Scatter(
    x=pd.concat([al_ano["ano"], al_ano["ano"][::-1]]),
    y=pd.concat([al_ano["ideb_brasil"], al_ano["ideb_al"][::-1]]),
    fill="toself",
    fillcolor="rgba(55,138,221,0.08)",
    line=dict(color="rgba(0,0,0,0)"),
    name="Gap AL vs Brasil",
    hoverinfo="skip",
))

# Brasil
fig.add_trace(go.Scatter(
    x=al_ano["ano"], y=al_ano["ideb_brasil"],
    name="Brasil", mode="lines+markers",
    line=dict(color="#378ADD", width=2),
    marker=dict(size=6),
    hovertemplate="Brasil %{x}: %{y:.2f}<extra></extra>",
))

# Alagoas
fig.add_trace(go.Scatter(
    x=al_ano["ano"], y=al_ano["ideb_al"],
    name="Alagoas", mode="lines+markers",
    line=dict(color="#D85A30", width=2, dash="dash"),
    marker=dict(size=6),
    hovertemplate="Alagoas %{x}: %{y:.2f}<extra></extra>",
))

# Meta
fig.add_hline(
    y=META, line_dash="dot", line_color="#888780",
    annotation_text="Meta 6.0",
    annotation_position="right",
)

# Anotações do gap
for ano, texto in anos_destaque.items():
    linha = al_ano[al_ano["ano"] == ano].iloc[0]
    y_meio = (linha["ideb_brasil"] + linha["ideb_al"]) / 2
    fig.add_annotation(
        x=ano, y=y_meio, text=texto,
        showarrow=False,
        font=dict(size=9, color="#185FA5"),
        bgcolor="rgba(255,255,255,0.75)",
        bordercolor="#378ADD",
        borderwidth=0.5,
        borderpad=3,
    )

fig.update_layout(
    height=450,
    xaxis=dict(tickmode="array", tickvals=al_ano["ano"].tolist()),
    yaxis=dict(range=[2.0, 7.0], title="IDEB"),
    xaxis_title="Ano",
    legend=dict(orientation="h", yanchor="bottom", y=1.02),
    margin=dict(r=80),
)

st.plotly_chart(fig, use_container_width=True)

# ── Tabela de dados ───────────────────────────────────────────────────────────
with st.expander("Ver dados completos"):
    st.dataframe(
        al_ano.rename(columns={
            "ano": "Ano",
            "ideb_al": "IDEB AL",
            "ideb_brasil": "IDEB Brasil",
            "gap": "Gap",
        }).set_index("Ano"),
        use_container_width=True,
    )