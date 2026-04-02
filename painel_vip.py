import streamlit as st
import pandas as pd
import os
from datetime import date

# Configuração da Página
st.set_page_config(page_title="Painel VIP - Gestão de Apostas", layout="wide")

# --- CONFIGURAÇÕES ---
SENHA_ADMIN = "vip123" 
BANCA_INICIAL = 1000.00 
DB_FILE = "historico_apostas.csv"

# Inicialização do Banco de Dados
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

# --- INTERFACE ---
st.title("🏆 Dashboard de Performance - Grupo VIP")

# --- ÁREA DO ADMIN (PROTEGIDA) ---
st.sidebar.header("🔐 Área do Administrador")
senha_inserida = st.sidebar.text_input("Senha", type="password")

if senha_inserida == SENHA_ADMIN:
    st.sidebar.success("Acesso Autorizado")
    
    # Criamos abas no Admin para não poluir
    aba_add, aba_edit = st.sidebar.tabs(["Adicionar", "Editar/Excluir"])

    with aba_add:
        with st.form("formulario_aposta"):
            data_sel = st.date_input("Data", value=date.today(), format="DD/MM/YYYY")
            equipas = st.text_input("Equipas")
            metodo = st.selectbox("Método", ["Dutching", "Lay Goleada", "Handicap", "Over a frente", "Over limite"])
            resultado = st.selectbox("Resultado", ["Green ✅", "Red ❌", "Reembolsada 🔄"])
            valor = st.number_input("Lucro/Prejuízo (R$)", value=0.0)
            if st.form_submit_button("Registar"):
                nova_aposta = {"Data": data_sel.strftime("%d/%m/%Y"), "Equipas": equipas, "Método": metodo, "Resultado": resultado, "Lucro/Prejuízo": valor}
                df = pd.read_csv(DB_FILE)
                df = pd.concat([df, pd.DataFrame([nova_aposta])], ignore_index=True)
                df.to_csv(DB_FILE, index=False)
                st.rerun()

    with aba_edit:
        df_edit = pd.read_csv(DB_FILE)
        st.write("Edite os valores abaixo:")
        # Editor de dados direto na barra lateral
        novo_df = st.data_editor(df_edit, num_rows="dynamic", hide_index=True)
        if st.button("Salvar Alterações"):
            novo_df.to_csv(DB_FILE, index=False)
            st.success("Dados Atualizados!")
            st.rerun()

# --- VISUALIZAÇÃO PÚBLICA ---
df_atual = carregar_dados()

if not df_atual.empty:
    total_lucro = df_atual["Lucro/Prejuízo"].sum()
    lucro_percentual = (total_lucro / BANCA_INICIAL) * 100
    
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Lucro Total", f"R$ {total_lucro:.2f}")
    m2.metric("Crescimento %", f"{lucro_percentual:.2f}%", delta=f"{lucro_percentual:.2f}%")
    m3.metric("Total de Entradas", len(df_atual))
    m4.metric("Taxa de Acerto", f"{(len(df_atual[df_atual['Resultado'] == 'Green ✅']) / len(df_atual)) * 100:.1f}%")

    st.subheader("📈 Evolução da Banca (R$)")
    df_atual["Evolução"] = df_atual["Lucro/Prejuízo"].cumsum()
    st.line_chart(df_atual.set_index("Data")["Evolução"])

    st.subheader("📜 Histórico de Tips")
    st.dataframe(df_atual[["Data", "Equipas", "Método", "Resultado", "Lucro/Prejuízo"]].iloc[::-1], use_container_width=True, hide_index=True)
    
    # BOTÃO PARA BACKUP (IMPORTANTE)
    csv = df_atual.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Baixar Backup do Histórico (CSV)", csv, "meu_historico.csv", "text/csv")
else:
    st.info("Aguardando registros.")
