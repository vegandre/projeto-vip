import streamlit as st
import pandas as pd
import os
from datetime import date

# Configuração da Página
st.set_page_config(page_title="Painel VIP - Gestão de Apostas", layout="wide")

# --- CONFIGURAÇÕES DO GRUPO ---
SENHA_ADMIN = "vip123" 
BANCA_INICIAL = 1000.00  # Valor base para o cálculo de %

# --- DATABASE SIMULADA ---
DB_FILE = "historico_apostas.csv"

if not os.path.exists(DB_FILE):
    df_init = pd.DataFrame(columns=["Data", "Equipas", "Método", "Resultado", "Lucro/Prejuízo"])
    df_init.to_csv(DB_FILE, index=False)

def carregar_dados():
    try:
        df = pd.read_csv(DB_FILE)
        if not df.empty:
            df['Data_Ord'] = pd.to_datetime(df['Data'], format='%d/%m/%Y')
            df = df.sort_values(by='Data_Ord')
        return df
    except:
        return pd.DataFrame(columns=["Data", "Equipas", "Método", "Resultado", "Lucro/Prejuízo"])

def salvar_dado(nova_linha):
    df = pd.read_csv(DB_FILE)
    df = pd.concat([df, pd.DataFrame([nova_linha])], ignore_index=True)
    df.to_csv(DB_FILE, index=False)

# --- INTERFACE ---
st.title("🏆 Dashboard de Performance - Grupo VIP")

# --- ÁREA DO ADMIN (PROTEGIDA) ---
st.sidebar.header("🔐 Área do Administrador")
senha_inserida = st.sidebar.text_input("Introduza a senha para editar", type="password")

if senha_inserida == SENHA_ADMIN:
    st.sidebar.success("Acesso Autorizado")
    with st.sidebar.form("formulario_aposta"):
        data_sel = st.date_input("Data da Aposta", value=date.today(), format="DD/MM/YYYY")
        equipas = st.text_input("Equipas (Ex: Flamengo vs Palmeiras)")
        metodo = st.selectbox("Método", ["Dutching", "Lay Goleada", "Handicap", "Over a frente", "Over limite"])
        resultado = st.selectbox("Resultado", ["Green ✅", "Red ❌", "Reembolsada 🔄"])
        valor = st.number_input("Lucro/Prejuízo Líquido (R$)", value=0.0, step=1.0)
        
        submetido = st.form_submit_button("Registar Aposta")

    if submetido:
        data_formatada = data_sel.strftime("%d/%m/%Y")
        nova_aposta = {
            "Data": data_formatada,
            "Equipas": equipas,
            "Método": metodo,
            "Resultado": resultado,
            "Lucro/Prejuízo": valor
        }
        salvar_dado(nova_aposta)
        st.sidebar.success(f"Registo de {data_formatada} concluído!")
        st.rerun()

# --- VISUALIZAÇÃO DOS MEMBROS (PÚBLICA) ---
df_atual = carregar_dados()

if not df_atual.empty:
    total_lucro = df_atual["Lucro/Prejuízo"].sum()
    lucro_percentual = (total_lucro / BANCA_INICIAL) * 100
    wins = len(df_atual[df_atual["Resultado"] == "Green ✅"])
    taxa_acerto = (wins / len(df_atual)) * 100

    # Criamos 4 colunas para as métricas
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Lucro Total", f"R$ {total_lucro:.2f}")
    m2.metric("Crescimento %", f"{lucro_percentual:.2f}%", delta=f"{lucro_percentual:.2f}%")
    m3.metric("Total de Entradas", len(df_atual))
    m4.metric("Taxa de Acerto", f"{taxa_acerto:.1f}%")

    st.subheader("📈 Evolução da Banca (R$)")
    df_atual["Evolução"] = df_atual["Lucro/Prejuízo"].cumsum()
    st.line_chart(df_atual.set_index("Data")["Evolução"])

    st.subheader("📜 Histórico de Tips")
    exibir_df = df_atual[["Data", "Equipas", "Método", "Resultado", "Lucro/Prejuízo"]].copy()
    # Inverte para mostrar a mais recente primeiro
    st.dataframe(exibir_df.iloc[::-1], use_container_width=True, hide_index=True)
else:
    st.info("Aguardando o registo das primeiras apostas para calcular o lucro.")
