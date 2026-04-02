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

# 2. FUNÇÕES DE DADOS (BANCO DE DADOS EM CSV)
def inicializar_db():
    if not os.path.exists(DB_FILE):
        df_init = pd.DataFrame(columns=["Data", "Equipas", "Método", "Resultado", "Lucro/Prejuízo"])
        df_init.to_csv(DB_FILE, index=False, sep=";", encoding="utf-8-sig")

def carregar_dados():
    try:
        # Lemos com sep=";" para compatibilidade total com Excel
        df = pd.read_csv(DB_FILE, sep=";", encoding="utf-8-sig")
        if not df.empty:
            # Criamos uma coluna temporária para ordenar por data real
            df['Data_Ord'] = pd.to_datetime(df['Data'], format='%d/%m/%Y', errors='coerce')
            df = df.sort_values(by='Data_Ord')
        return df
    except:
        return pd.DataFrame(columns=["Data", "Equipas", "Método", "Resultado", "Lucro/Prejuízo"])

def salvar_dados_completos(df_novo):
    # Salva o DataFrame inteiro (usado na edição/exclusão)
    df_novo.to_csv(DB_FILE, index=False, sep=";", encoding="utf-8-sig")

# Inicializa o ficheiro se não existir
inicializar_db()

# 3. INTERFACE PRINCIPAL
st.title("🏆 Dashboard de Performance - Grupo VIP")
st.markdown("---")

# --- ÁREA DO ADMIN (BARRA LATERAL) ---
st.sidebar.header("🔐 Área do Administrador")
senha_inserida = st.sidebar.text_input("Introduza a senha para gerir", type="password")

if senha_inserida == SENHA_ADMIN:
    st.sidebar.success("Acesso Autorizado")
    
    # Abas dentro da lateral para organizar as funções de admin
    aba_add, aba_edit = st.sidebar.tabs(["➕ Adicionar", "✏️ Editar/Excluir"])

    with aba_add:
        with st.form("form_nova_aposta", clear_on_submit=True):
            data_sel = st.date_input("Data da Aposta", value=date.today(), format="DD/MM/YYYY")
            equipas = st.text_input("Equipas (Ex: Real Madrid x City)")
            metodo = st.selectbox("Método", ["Dutching", "Lay Goleada", "Handicap", "Over a frente", "Over limite"])
            resultado = st.selectbox("Resultado", ["Green ✅", "Red ❌", "Reembolsada 🔄"])
            valor = st.number_input("Lucro/Prejuízo Líquido (R$)", value=0.0, step=1.0)
            
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
                    st.sidebar.success("Aposta registada!")
                    st.rerun()
                else:
                    st.error("Preencha o nome das equipas!")

    with aba_edit:
        st.write("Modifique as células ou apague linhas:")
        df_para_editar = pd.read_csv(DB_FILE, sep=";", encoding="utf-8-sig")
        # O data_editor permite editar como uma planilha
        df_editado = st.data_editor(df_para_editar, num_rows="dynamic", hide_index=True)
        
        if st.button("Confirmar Alterações"):
            salvar_dados_completos(df_editado)
            st.success("Dados atualizados com sucesso!")
            st.rerun()

elif senha_inserida != "":
    st.sidebar.error("Senha Incorreta")

# 4. VISUALIZAÇÃO PÚBLICA (O QUE O CLIENTE VÊ)
df_dados = carregar_dados()

if not df_dados.empty:
    # Cálculos de Métricas
    total_lucro = df_dados["Lucro/Prejuízo"].sum()
    lucro_percentual = (total_lucro / BANCA_INICIAL) * 100
    wins = len(df_dados[df_dados["Resultado"] == "Green ✅"])
    taxa_acerto = (wins / len(df_dados)) * 100

    # Exibição de Métricas em Colunas
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Lucro Total", f"R$ {total_lucro:.2f}")
    m2.metric("Crescimento %", f"{lucro_percentual:.2f}%", delta=f"{lucro_percentual:.2f}%")
    m3.metric("Total de Entradas", len(df_dados))
    m4.metric("Taxa de Acerto", f"{taxa_acerto:.1f}%")

    # Gráfico de Evolução
    st.subheader("📈 Evolução da Banca (R$)")
    df_dados["Evolução"] = df_dados["Lucro/Prejuízo"].cumsum()
    st.line_chart(df_dados.set_index("Data")["Evolução"])

    # Tabela de Histórico
    st.subheader("📜 Histórico de Tips")
    # Invertemos a ordem para mostrar a mais recente primeiro na tabela
    colunas_exibir = ["Data", "Equipas", "Método", "Resultado", "Lucro/Prejuízo"]
    st.dataframe(df_dados[colunas_exibir].iloc[::-1], use_container_width=True, hide_index=True)

    # BOTÃO DE BACKUP PROFISSIONAL (CORRIGIDO PARA EXCEL)
    st.markdown("---")
    csv_excel = df_dados[colunas_exibir].to_csv(index=False, sep=";", encoding="utf-8-sig").encode('utf-8-sig')
    st.download_button(
        label="📥 Baixar Backup para Excel (.csv)",
        data=csv_excel,
        file_name=f"historico_vip_{date.today().strftime('%d_%m_%Y')}.csv",
        mime="text/csv",
    )
else:
    st.info("📊 O histórico está vazio. O administrador precisa de registar as primeiras apostas.")
