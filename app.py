# ==============================
# 🔗 MERGE POR CONTRATO
# ==============================

df = df_2faltas.copy()

# Garantir que coluna Contrato exista
if "Contrato" not in df.columns:
    st.error("Coluna 'Contrato' não encontrada na aba 2 Faltas")
    st.stop()

# Merge com M1 (Responsabilidade)
if "Contrato" in df_m1.columns and "Responsabilidade" in df_m1.columns:
    df = df.merge(
        df_m1[["Contrato", "Responsabilidade"]],
        on="Contrato",
        how="left"
    )

# Criar coluna Status manualmente
df["Status"] = "Em Risco"

# Marcar desistentes
if "Contrato" in df_desistentes.columns:
    contratos_desistentes = df_desistentes["Contrato"].unique()
    df.loc[df["Contrato"].isin(contratos_desistentes), "Status"] = "Desistente"

# Marcar recuperados
if "Contrato" in df_recuperacao.columns:
    contratos_recuperados = df_recuperacao["Contrato"].unique()
    df.loc[df["Contrato"].isin(contratos_recuperados), "Status"] = "Recuperado"
