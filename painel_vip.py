import streamlit as st
import pandas as pd
import os
from datetime import date

# Configuração da Página
st.set_page_config(page_title="Painel VIP - Gestão de Apostas", layout="wide")

# --- DEFINIÇÃO DA SENHA ---
SENHA_ADMIN = "vip123"  # Altera para a senha que desejares

# --- DATABASE SIMULADA ---
DB_FILE = "historico_apostas.csv"

if not os.path.exists(DB_FILE):
    df_init = pd.DataFrame(columns=["Data", "Equipas", "Método", "Resultado", "Lucro/Prejuízo"])
    df_init.to_csv(DB_FILE, index=False)

def carregar_dados():
    return pd.read_csv(DB_FILE)

def salvar_dado(nova_linha):
    df = carregar_dados()
    df = pd.concat([df, pd.DataFrame([nova_linha])], ignore_index=True)
    df.to_csv(DB_FILE, index=False)

# --- INTERFACE ---
st.title("🏆 Dashboard de Performance - Grupo VIP")
st.markdown("Bem-vindo ao painel oficial de transparência do grupo.")

# --- ÁREA DO ADMIN (PROTEGIDA) ---
st.sidebar.header("🔐 Área do Administrador")
senha_inserida = st.sidebar.text_input("Introduza a senha para editar", type="password")

if senha_inserida == SENHA_ADMIN:
    st.sidebar.success("Acesso Autorizado")
    with st.sidebar.form("formulario_aposta"):
        data_aposta = st.date_input("Data", date.today())
        equipas = st.text_input("Equipas (Ex: Real Madrid vs Milan)")
        metodo = st.selectbox("Método", ["Dutching", "Lay Goleada", "Handicap", "Over a frente", "Over limite"])
        resultado = st.selectbox("Resultado", ["Green ✅", "Red ❌", "Reembolsada 🔄"])
        valor = st.number_input("Lucro/Prejuízo Líquido (€)", value=0.0, step=1.0)
        
        submetido = st.form_submit_button("Registar Aposta")

    if submetido:
        nova_aposta = {
            "Data": data_aposta.strftime("%d/%m/%Y"), # Formata a data para ficar bonita
            "Equipas": equipas,
            "Método": metodo,
            "Resultado": resultado,
            "Lucro/Prejuízo": valor
        }
        salvar_dado(nova_aposta)
        st.sidebar.success("Aposta guardada!")
        st.rerun() # Atualiza a página para mostrar os novos dados imediatamente
else:
    if senha_inserida != "":
        st.sidebar.error("Senha Incorreta")

# --- VISUALIZAÇÃO DOS MEMBROS (PÚBLICA) ---
df_atual = carregar_dados()

if not df_atual.empty:
    # Métricas principais
    total_lucro = df_atual["Lucro/Prejuízo"].sum()
    wins = len(df_atual[df_atual["Resultado"] == "Green ✅"])
    taxa_acerto = (wins / len(df_atual)) * 100

    m1, m2, m3 = st.columns(3)
    m1.metric("Lucro Total", f"{total_lucro:.2f}€", delta=f"{total_lucro:.2f}€")
    m2.metric("Total de Entradas", len(df_atual))
    m3.metric("Taxa de Acerto", f"{taxa_acerto:.1f}%")

    # Gráfico de Evolução
    st.subheader("📈 Gráfico de Evolução da Banca")
    df_atual["Evolução"] = df_atual["Lucro/Prejuízo"].cumsum()
    st.line_chart(df_atual["Evolução"])

    # Tabela de Histórico
    st.subheader("📜 Histórico de Tips")
    st.dataframe(df_atual.sort_values(by="Data", ascending=False), use_container_width=True)
else:
    st.info("Aguardando o registo das primeiras apostas pelo administrador.")
