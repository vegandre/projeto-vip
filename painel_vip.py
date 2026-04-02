import streamlit as st
import pandas as pd
import os
from datetime import date

# Configuração da Página
st.set_page_config(page_title="Painel VIP - Gestão de Apostas", layout="wide")

# --- DEFINIÇÃO DA SENHA ---
SENHA_ADMIN = "vip123" 

# --- DATABASE SIMULADA ---
DB_FILE = "historico_apostas.csv"

if not os.path.exists(DB_FILE):
    df_init = pd.DataFrame(columns=["Data", "Equipas", "Método", "Resultado", "Lucro/Prejuízo"])
    df_init.to_csv(DB_FILE, index=False)

def carregar_dados():
    df = pd.read_csv(DB_FILE)
    # Converter a coluna Data de texto para formato de data real para o gráfico funcionar
    if not df.empty:
        df['Data_Ord'] = pd.to_datetime(df['Data'], format='%d/%m/%Y')
        df = df.sort_values(by='Data_Ord')
    return df

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
        data_sel = st.date_input("Data", date.today())
        equipas = st.text_input("Equipas (Ex: Flamengo vs Palmeiras)")
        metodo = st.selectbox("Método", ["Dutching", "Lay Goleada", "Handicap", "Over a frente", "Over limite"])
        resultado = st.selectbox("Resultado", ["Green ✅", "Red ❌", "Reembolsada 🔄"])
        valor = st.number_input("Lucro/Prejuízo Líquido (R$)", value=0.0, step=1.0)
        
        submetido = st.form_submit_button("Registar Aposta")

    if submetido:
        # AQUI É ONDE FORMATAMOS PARA O PADRÃO BRASILEIRO
        data_formatada = data_sel.strftime("%d/%m/%Y")
        
        nova_aposta = {
            "Data": data_formatada,
            "Equipas": equipas,
            "Método": metodo,
            "Resultado": resultado,
            "Lucro/Prejuízo": valor
        }
        salvar_dado(nova_aposta)
        st.sidebar.success(f"Aposta de {data_formatada} guardada!")
        st.rerun()

# --- VISUALIZAÇÃO DOS MEMBROS (PÚBLICA) ---
df_atual = carregar_dados()

if not df_atual.empty:
    total_lucro = df_atual["Lucro/Prejuízo"].sum()
    wins = len(df_atual[df_atual["Resultado"] == "Green ✅"])
    taxa_acerto = (wins / len(df_atual)) * 100

    m1, m2, m3 = st.columns(3)
    m1.metric("Lucro Total", f"R$ {total_lucro:.2f}")
    m2.metric("Total de Entradas", len(df_atual))
    m3.metric("Taxa de Acerto", f"{taxa_acerto:.1f}%")

    st.subheader("📈 Gráfico de Evolução da Banca")
    df_atual["Evolução"] = df_atual["Lucro/Prejuízo"].cumsum()
    
    # Usamos a data formatada no eixo X do gráfico
    st.line_chart(df_atual.set_index("Data")["Evolução"])

    st.subheader("📜 Histórico de Tips")
    # Mostramos a tabela (sem a coluna auxiliar de ordenação)
    st.dataframe(df_atual[["Data", "Equipas", "Método", "Resultado", "Lucro/Prejuízo"]].iloc[::-1], use_container_width=True)
else:
    st.info("Aguardando o registo das primeiras apostas.")
