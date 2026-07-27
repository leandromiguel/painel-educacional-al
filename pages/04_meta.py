"""
Página 4 — Meta 6.0
Municípios que atingiram a meta nacional do IDEB de 6.0.
"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(
    page_title="Meta 6.0 — Painel Educacional AL",
    page_icon="🎯",
    layout="wide",
)

if "df_ideb" not in st.session_state:
    st.warning("Inicie o app pela página principal: `streamlit run app.py`")
    st.stop()

df = st.session_state["df_ideb"]
META = 6.0

# ── Preparação dos dados ──────────────────────────────────────────────────────
ideb_2023 = (
    df[df["ano"] == 2023]
    [["CO_MUNICIPIO", "NO_MUNICIPIO", "ideb"]]
    .rename(columns={"ideb": "ideb_2023"})
    .sort_values("ideb_2023", ascending=False)
    .reset_index(drop=True)
)

acima = ideb_2023[ideb_2023["ideb_2023"] >= META].copy()
abaixo = ideb_2023[ideb_2023["ideb_2023"] < META].copy()

# Primeiro ano que cada município cruzou a meta
primeiro_ano = []
for cod in acima["CO_MUNICIPIO"]:
    serie = df[df["CO_MUNICIPIO"] == cod].sort_values("ano")
    cruzou = serie[serie["ideb"] >= META]
    if not cruzou.empty:
        primeiro_ano.append({
            "CO_MUNICIPIO":       cod,
            "NO_MUNICIPIO":       serie["NO_MUNICIPIO"].iloc[0],
            "ideb_2023":          acima[acima["CO_MUNICIPIO"] == cod]["ideb_2023"].values[0],
            "primeiro_ano_meta":  int(cruzou["ano"].min()),
        })

df_meta = pd.DataFrame(primeiro_ano).sort_values("primeiro_ano_meta")

# ── Layout ────────────────────────────────────────────────────────────────────
st.title("Municípios que Atingiram a Meta IDEB 6.0")
st.caption("Ensino Fundamental Anos Iniciais · Rede Pública · 2023")

# Metric cards
c1, c2, c3, c4 = st.columns(4)
c1.metric(
    "Atingiram a meta",
    f"{len(acima)} municípios",
    f"{round(len(acima)/len(ideb_2023)*100, 1)}% do total",
)
c2.metric(
    "Ainda abaixo da meta",
    f"{len(abaixo)} municípios",
    f"IDEB médio: {abaixo['ideb_2023'].mean():.2f}",
    delta_color="inverse",
)
c3.metric(
    "Primeiro a atingir",
    "2015",
    "Coruripe, Jequiá da Praia, Campo Alegre",
)
c4.metric(
    "Cruzaram a meta em 2023",
    f"{len(df_meta[df_meta['primeiro_ano_meta'] == 2023])} municípios",
    "maior salto em uma edição",
)

st.divider()

# ── Evolução temporal dos municípios acima da meta ────────────────────────────
st.subheader("Evolução do IDEB — municípios que atingiram a meta")

fig_linha = go.Figure()

cores = [
    "#1D9E75", "#378ADD", "#D85A30", "#BA7517",
    "#534AB7", "#0C447C", "#7F77DD", "#5DCAA5",
]

for i, cod in enumerate(acima["CO_MUNICIPIO"]):
    serie = df[df["CO_MUNICIPIO"] == cod].sort_values("ano")
    nome = serie["NO_MUNICIPIO"].iloc[0]
    cor = cores[i % len(cores)]
    fig_linha.add_trace(go.Scatter(
        x=serie["ano"],
        y=serie["ideb"],
        mode="lines+markers",
        name=nome,
        line=dict(width=1.5, color=cor),
        marker=dict(size=4),
        hovertemplate=f"<b>{nome}</b><br>Ano: %{{x}}<br>IDEB: %{{y:.1f}}<extra></extra>",
    ))

fig_linha.add_hline(
    y=META,
    line_dash="dash",
    line_color="#D85A30",
    annotation_text="Meta 6.0",
    annotation_position="right",
)
fig_linha.update_layout(
    height=480,
    xaxis=dict(
        tickmode="array",
        tickvals=sorted(df["ano"].unique()),
        title="Ano",
    ),
    yaxis=dict(title="IDEB", range=[1.5, 10.5]),
    legend=dict(
        orientation="v",
        x=1.02, y=1,
        font=dict(size=8),
    ),
    margin=dict(r=160),
)
st.plotly_chart(fig_linha, use_container_width=True)

st.divider()

# ── Progressão por ano ────────────────────────────────────────────────────────
st.subheader("Em que ano cada município cruzou a meta pela primeira vez")

anos_unicos = sorted(df_meta["primeiro_ano_meta"].unique())
cols = st.columns(len(anos_unicos))

for col, ano in zip(cols, anos_unicos):
    grupo = df_meta[df_meta["primeiro_ano_meta"] == ano]
    with col:
        st.markdown(f"**{ano}**")
        st.caption(f"{len(grupo)} município{'s' if len(grupo) > 1 else ''}")
        for _, row in grupo.iterrows():
            st.markdown(
                f"🟢 {row['NO_MUNICIPIO']} "
                f"<span style='color:gray;font-size:11px'>({row['ideb_2023']:.1f})</span>",
                unsafe_allow_html=True,
            )

st.divider()

# ── Tabela comparativa: acima vs abaixo ──────────────────────────────────────
st.subheader("Comparativo — acima vs abaixo da meta em 2023")

col_a, col_b = st.columns(2)

with col_a:
    st.markdown(f"**✅ Acima da meta (≥ {META}) — {len(acima)} municípios**")
    st.dataframe(
        acima[["NO_MUNICIPIO", "ideb_2023"]]
        .rename(columns={
            "NO_MUNICIPIO": "Município",
            "ideb_2023":    "IDEB 2023",
        })
        .reset_index(drop=True),
        use_container_width=True,
        height=350,
        hide_index=True,
    )

with col_b:
    st.markdown(f"**⚠️ Abaixo da meta (< {META}) — {len(abaixo)} municípios**")
    st.dataframe(
        abaixo[["NO_MUNICIPIO", "ideb_2023"]]
        .rename(columns={
            "NO_MUNICIPIO": "Município",
            "ideb_2023":    "IDEB 2023",
        })
        .sort_values("IDEB 2023", ascending=False)
        .reset_index(drop=True),
        use_container_width=True,
        height=350,
        hide_index=True,
    )