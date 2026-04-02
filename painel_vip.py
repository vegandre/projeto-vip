import streamlit as st
import pandas as pd
import os
from datetime import date

# 1. CONFIGURAÇÃO DA PÁGINA
st.set_page_config(page_title="Painel VIP - Gestão de Apostas", layout="wide", page_icon="🏆")

# --- CONFIGURAÇÕES DO ADMINISTRADOR ---
SENHA_ADMIN = "vip123" 
BANCA_INICIAL = 1000.00 
DB_FILE = "historico_apostas.csv"

# 2. FUNÇÕES DE DADOS
def inicializar_db():
    if not os.path.exists(DB_FILE):
        df_init = pd.DataFrame(columns=["Data", "Equipas", "Método", "Resultado", "Lucro/Prejuízo"])
        df_init.to_csv(DB_FILE, index=False, sep=";", encoding="utf-8-sig")

def carregar_dados():
    try:
        df = pd.read_csv(DB_FILE, sep=";", encoding="utf-8-sig")
        if not df.empty:
            df['Data_Ord'] = pd.to_datetime(df['Data'], format='%d/%m/%Y', errors='coerce')
            df = df.sort_values(by='Data_Ord')
        return df
    except:
        return pd.DataFrame(columns=["Data", "Equipas", "Método", "Resultado", "Lucro/Prejuízo"])

def salvar_dados_completos(df_novo):
    df_novo.to_csv(DB_FILE, index=False, sep=";", encoding="utf-8-sig")

inicializar_db()

# 3. INTERFACE PRINCIPAL
st.title("🏆 Dashboard de Performance - Grupo VIP")
st.markdown("---")

# --- ÁREA DO ADMIN (BARRA LATERAL) ---
st.sidebar.header("🔐 Área do Administrador")
senha_inserida = st.sidebar.text_input("Introduza a senha para gerir", type="password")

if senha_inserida == SENHA_ADMIN:
    st.sidebar.success("Acesso Autorizado")
    aba_add, aba_edit = st.sidebar.tabs(["➕ Adicionar", "✏️ Editar/Excluir"])

    with aba_add:
        with st.form("form_nova_aposta", clear_on_submit=True):
            data_sel = st.date_input("Data da Aposta", value=date.today(), format="DD/MM/YYYY")
            equipas = st.text_input("Equipas (Ex: Flamengo x Vasco)")
            metodo = st.selectbox("Método", ["Dutching", "Lay Goleada", "Handicap", "Over a frente", "Over limite"])
            resultado = st.selectbox("Resultado", ["Green ✅", "Red ❌", "Reembolsada 🔄"])
            valor = st.number_input("Lucro/Prejuízo (R$)", value=0.0, step=0.01) # Permitir centavos
            
            if st.form_submit_button("Registar Aposta"):
                if equipas:
                    nova_linha = {
                        "Data": data_sel.strftime("%d/%m/%Y"),
                        "Equipas": equipas,
                        "Método": metodo,
                        "Resultado": resultado,
                        "Lucro/Prejuízo": valor
                    }
                    df_atual = pd.read_csv(DB_FILE, sep=";", encoding="utf-8-sig")
                    df_novo = pd.concat([df_atual, pd.DataFrame([nova_linha])], ignore_index=True)
                    salvar_dados_completos(df_novo)
                    st.sidebar.success("Aposta registrada!")
                    st.rerun()

    with aba_edit:
        st.write("Modifique as células ou apague linhas:")
        df_para_editar = pd.read_csv(DB_FILE, sep=";", encoding="utf-8-sig")
        df_editado = st.data_editor(df_para_editar, num_rows="dynamic", hide_index=True)
        if st.button("Confirmar Alterações"):
            salvar_dados_completos(df_editado)
            st.success("Dados atualizados!")
            st.rerun()

# 4. VISUALIZAÇÃO PÚBLICA
df_dados = carregar_dados()

if not df_dados.empty:
    total_lucro = df_dados["Lucro/Prejuízo"].sum()
    lucro_percentual = (total_lucro / BANCA_INICIAL) * 100
    wins = len(df_dados[df_dados["Resultado"] == "Green ✅"])
    taxa_acerto = (wins / len(df_dados)) * 100

    # FORMATANDO PARA MOSTRAR AO CLIENTE
    m1, m2, m3, m4 = st.columns(4)
    # Formato brasileiro: R$ 1.234,56
    m1.metric("Lucro Total", f"R$ {total_lucro:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'))
    m2.metric("Crescimento %", f"{lucro_percentual:.2f}%", delta=f"{lucro_percentual:.2f}%")
    m3.metric("Total de Entradas", len(df_dados))
    m4.metric("Taxa de Acerto", f"{taxa_acerto:.1f}%")

    st.subheader("📈 Evolução da Banca (R$)")
    df_dados["Evolução"] = df_dados["Lucro/Prejuízo"].cumsum()
    st.line_chart(df_dados.set_index("Data")["Evolução"])

    st.subheader("📜 Histórico de Tips")
    
    # Criamos uma cópia para formatar a exibição sem estragar o cálculo
    df_exibicao = df_dados[["Data", "Equipas", "Método", "Resultado", "Lucro/Prejuízo"]].iloc[::-1].copy()
    
    # FORMATANDO A COLUNA DE DINHEIRO NA TABELA
    # Isso coloca o R$ e ajusta vírgulas e pontos
    df_exibicao["Lucro/Prejuízo"] = df_exibicao["Lucro/Prejuízo"].map("R$ {:,.2f}".format).str.replace(",", "X").str.replace(".", ",").str.replace("X", ".")

    st.dataframe(df_exibicao, use_container_width=True, hide_index=True)

    st.markdown("---")
    csv_excel = df_dados[["Data", "Equipas", "Método", "Resultado", "Lucro/Prejuízo"]].to_csv(index=False, sep=";", encoding="utf-8-sig").encode('utf-8-sig')
    st.download_button(
        label="📥 Baixar Backup para Excel (.csv)",
        data=csv_excel,
        file_name=f"historico_vip_{date.today().strftime('%d_%m_%Y')}.csv",
        mime="text/csv",
    )
else:
    st.info("📊 O histórico está vazio.")
