import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="CS - Dashboard Sucesso do Cliente", layout="wide")

st.title("📊 Dashboard CS | Evasão, Engajamento & Proatividade")

# ==============================
# 🔗 LINKS DAS PLANILHAS (CSV)
# ==============================

url_2faltas = "https://docs.google.com/spreadsheets/d/1i1IRwad7fpzOmBuY5Ntx1u0887U5T4DmgSj_HM7_AhM/edit?usp=sharing"
url_m1 = "https://docs.google.com/spreadsheets/d/1i1IRwad7fpzOmBuY5Ntx1u0887U5T4DmgSj_HM7_AhM/edit?usp=sharing"
url_desistentes = "https://docs.google.com/spreadsheets/d/1i1IRwad7fpzOmBuY5Ntx1u0887U5T4DmgSj_HM7_AhM/edit?usp=sharing"
url_recuperacao = "https://docs.google.com/spreadsheets/d/1i1IRwad7fpzOmBuY5Ntx1u0887U5T4DmgSj_HM7_AhM/edit?usp=sharing"

# ==============================
# 🔄 CARREGAMENTO DOS DADOS
# ==============================

@st.cache_data(ttl=60)
def load_data():
    df_2faltas = pd.read_csv(url_2faltas)
    df_m1 = pd.read_csv(url_m1)
    df_desistentes = pd.read_csv(url_desistentes)
    df_recuperacao = pd.read_csv(url_recuperacao)
    return df_2faltas, df_m1, df_desistentes, df_recuperacao

df_2faltas, df_m1, df_desistentes, df_recuperacao = load_data()

# ==============================
# 🔗 MERGE DAS BASES (Contrato)
# ==============================

df = df_2faltas.copy()

# Junta Responsabilidade
if "Contrato" in df.columns and "Contrato" in df_m1.columns:
    df = df.merge(
        df_m1[["Contrato", "Responsabilidade"]],
        on="Contrato",
        how="left"
    )

# Criar status de evasão / recuperação
df_desistentes["Status"] = "Desistente"
df_recuperacao["Status"] = "Recuperado"

df_status = pd.concat([
    df_desistentes[["Contrato", "Grupo", "Status"]],
    df_recuperacao[["Contrato", "Grupo", "Status"]]
])

df = df.merge(df_status, on="Contrato", how="left")

df["Status"] = df["Status"].fillna("Em Risco")

# ==============================
# 🎛 FILTROS LATERAIS
# ==============================

st.sidebar.header("Filtros")

# Filtro Mês
if "Mes" in df.columns:
    mes = st.sidebar.selectbox("Filtrar por Mês", ["Todos"] + list(df["Mes"].dropna().unique()))
    if mes != "Todos":
        df = df[df["Mes"] == mes]

# Filtro Histórico
if "Historico" in df.columns:
    hist = st.sidebar.selectbox("Histórico", ["Todos"] + list(df["Historico"].dropna().unique()))
    if hist != "Todos":
        df = df[df["Historico"] == hist]

# Filtro Resposta
if "Resposta" in df.columns:
    resp = st.sidebar.selectbox("Resposta", ["Todos"] + list(df["Resposta"].dropna().unique()))
    if resp != "Todos":
        df = df[df["Resposta"] == resp]

# ==============================
# 📊 KPIs PRINCIPAIS
# ==============================

total_alunos = len(df)

if "Resposta" in df.columns:
    responderam = df[df["Resposta"].str.lower() == "sim"].shape[0]
    taxa_resposta = (responderam / total_alunos * 100) if total_alunos > 0 else 0
else:
    responderam = 0
    taxa_resposta = 0

total_desistentes = df[df["Status"] == "Desistente"].shape[0]
total_recuperados = df[df["Status"] == "Recuperado"].shape[0]

col1, col2, col3, col4 = st.columns(4)

col1.metric("Total Alunos", total_alunos)
col2.metric("Responderam", responderam)
col3.metric("Taxa Resposta", f"{taxa_resposta:.1f}%")
col4.metric("Recuperados", total_recuperados)

# ==============================
# 📈 GRÁFICO PERFORMANCE RESPONSÁVEL
# ==============================

if "Responsabilidade" in df.columns and "Resposta" in df.columns:
    perf = (
        df.groupby("Responsabilidade")["Resposta"]
        .apply(lambda x: (x.str.lower() == "sim").mean() * 100)
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
# 🥧 GRÁFICO ENGAJAMENTO
# ==============================

if "Grupo" in df.columns:
    fig2 = px.pie(
        df,
        names="Grupo",
        title="Distribuição de Engajamento"
    )

    st.plotly_chart(fig2, use_container_width=True)

# ==============================
# 📋 TABELA DETALHADA
# ==============================

st.subheader("📄 Base Detalhada")
st.dataframe(df, use_container_width=True)
