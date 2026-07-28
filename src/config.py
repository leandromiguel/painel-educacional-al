"""
Configuração central do projeto.
Todos os caminhos, constantes e parâmetros ficam aqui.
Este módulo é importado nos outros scripts em vez de hardcodar strings.
"""

from pathlib import Path

# ── Raiz do projeto ───────────────────────────────────────────────────────────
ROOT = Path(__file__).resolve().parents[1]

# ── Diretórios de dados ───────────────────────────────────────────────────────
DATA_RAW      = ROOT / "data" / "raw"
DATA_INEP     = DATA_RAW / "inep"
DATA_IBGE     = DATA_RAW / "ibge"
DATA_FNDE     = DATA_RAW / "fnde"
DATA_EXTERNAL = ROOT / "data" / "external"
DATA_PROC     = ROOT / "data" / "processed"

# ── Arquivos processados (gerados pelo ETL, consumidos pelo dashboard) ────────
MUNICIPIOS_PARQUET  = DATA_PROC / "municipios_al.parquet"
INFRA_PARQUET = DATA_PROC / "infra_municipios_al.parquet"
SHAPEFILE_AL        = DATA_PROC / "municipios_al.gpkg"
IDEB_SERIES_PARQUET = DATA_PROC / "ideb_series_al.parquet"

# ── Escopo geográfico ─────────────────────────────────────────────────────────
UF_CODIGO    = 27
UF_SIGLA     = "AL"
N_MUNICIPIOS = 102

# ── Escopo temporal ───────────────────────────────────────────────────────────
ANOS_IDEB              = [2005, 2007, 2009, 2011, 2013, 2015, 2017, 2019, 2021, 2023]
ANO_CENSO_MAIS_RECENTE = 2023

# ── Indicadores disponíveis no dashboard ─────────────────────────────────────
INDICADORES = {
    "ideb_ai":     "IDEB — EF Anos Iniciais",
    "ideb_af":     "IDEB — EF Anos Finais",
    "ideb_em":     "IDEB — Ensino Médio",
    "abandono":    "Taxa de abandono (%)",
    "distorcao":   "Distorção idade-série (%)",
    "gasto_aluno": "Gasto por aluno — FUNDEB (R$)",
}

# Metas nacionais IDEB por etapa
METAS_IDEB = {
    "ideb_ai": 6.0,
    "ideb_af": 5.5,
    "ideb_em": 5.2,
}
