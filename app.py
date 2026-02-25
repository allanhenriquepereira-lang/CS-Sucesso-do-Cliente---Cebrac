import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="CS Dashboard", layout="wide")

st.title("📊 Dashboard CS | Evasão & Engajamento")

# ==============================
# LINKS CSV
# ==============================

url_2faltas = "https://docs.google.com/spreadsheets/d/1i1IRwad7fpzOmBuY5Ntx1u0887U5T4DmgSj_HM7_AhM/export?format=csv&gid=55844215"
url_m1 = "https://docs.google.com/spreadsheets/d/1i1IRwad7fpzOmBuY5Ntx1u0887U5T4DmgSj_HM7_AhM/export?format=csv&gid=1769040659"
url_desistentes = "https://docs.google.com/spreadsheets/d/1i1IRwad7fpzOmBuY5Ntx1u0887U5T4DmgSj_HM7_AhM/export?format=csv&gid=146646633"
url_recuperacao = "https://docs.google.com/spreadsheets/d/1i1IRwad7fpzOmBuY5Ntx1u0887U5T4DmgSj_HM7_AhM/export?format=csv&gid=930693728"

# ==============================
# CARREGAR DADOS
# ==============================

@st.cache_data(ttl=60)
def load_data():
    df1 = pd.read_csv(url_2faltas, sep=None, engine="python")
    df2 = pd.read_csv(url_m1, sep=None, engine="python")
    df3 = pd.read_csv(url_desistentes, sep=None, engine="python")
    df4 = pd.read_csv(url_recuperacao, sep=None, engine="python")
    return df1, df2, df3, df4

df_2faltas, df_m1, df_desistentes, df_recuperacao = load_data()

# ==============================
# BASE PRINCIPAL
# ==============================

df = df_2faltas.copy()

# Garantir que coluna Contrato exista
if "Contrato" not in df.columns:
    st.error("Coluna 'Contrato' não encontrada na aba 2 Faltas.")
    st.stop()

# Adicionar Responsabilidade
if "Contrato" in df_m1.columns and "Responsabilidade" in df_m1.columns:
    df = df.merge(
        df_m1[["Contrato", "Responsabilidade"]],
        on="Contrato",
        how="left"
    )

# Criar coluna Status padrão
df["Status"] = "Em Risco"

# Marcar Desistentes
if "Contrato" in df_desistentes.columns:
    df.loc[df["Contrato"].isin(df_desistentes["Contrato"]), "Status"] = "Desistente"

# Marcar Recuperados
if "Contrato" in df_recuperacao.columns:
    df.loc[df["Contrato"].isin(df_recuperacao["Contrato"]), "Status"] = "Recuperado"

# ==============================
# FILTROS
# ==============================

st.sidebar.header("Filtros")

if "Resposta" in df.columns:
    filtro_resp = st.sidebar.selectbox(
        "Resposta",
        ["Todos"] + list(df["Resposta"].dropna().unique())
    )
    if filtro_resp != "Todos":
        df = df[df["Resposta"] == filtro_resp]

# ==============================
# KPIs
# ==============================

total = len(df)

if "Resposta" in df.columns:
    responderam = df[df["Resposta"].astype(str).str.lower() == "sim"].shape[0]
    taxa = (responderam / total * 100) if total > 0 else 0
else:
    responderam = 0
    taxa = 0

recuperados = df[df["Status"] == "Recuperado"].shape[0]

col1, col2, col3 = st.columns(3)

col1.metric("Total Alunos", total)
col2.metric("Taxa Resposta (%)", f"{taxa:.1f}%")
col3.metric("Recuperados", recuperados)

# ==============================
# GRÁFICO RESPONSABILIDADE
# ==============================

if "Responsabilidade" in df.columns and "Resposta" in df.columns:
    perf = (
        df.groupby("Responsabilidade")["Resposta"]
        .apply(lambda x: (x.astype(str).str.lower() == "sim").mean() * 100)
        .reset_index()
    )

    fig = px.bar(
        perf,
        x="Responsabilidade",
        y="Resposta",
        title="Taxa de Resposta por Responsável (%)",
        text_auto=".1f"
    )

    st.plotly_chart(fig, use_container_width=True)

# ==============================
# TABELA
# ==============================

st.subheader("Base Completa")
st.dataframe(df, use_container_width=True)
