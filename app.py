import streamlit as st
import pandas as pd
import os
from datetime import datetime

# Configuração da página
st.set_page_config(page_title="Gestão de Pacientes - Clínica", layout="wide")

# Diretórios para salvar uploads
UPLOADS_DIR = "uploads"
OS_DIR_DOCS = os.path.join(UPLOADS_DIR, "documentos")
OS_DIR_FOTOS = os.path.join(UPLOADS_DIR, "fotos")

os.makedirs(OS_DIR_DOCS, exist_ok=True)
os.makedirs(OS_DIR_FOTOS, exist_ok=True)

# Banco de dados simulado (CSV)
DATA_FILE = "pacientes.csv"

if os.path.exists(DATA_FILE):
    df_pacientes = pd.read_csv(DATA_FILE)
else:
    df_pacientes = pd.DataFrame(columns=[
        "ID", "Data Cadastro", "Nome", "CPF", "Data Nasc.", "Gênero", 
        "Telefone", "Endereço", "Diagnóstico", "Histórico / Observações",
        "Caminho Foto", "Caminho Documento"
    ])

st.title("🏥 Sistema de Registro de Pacientes")

# Criação das Abas
aba1, aba2, aba3 = st.tabs(["📝 Novo Cadastro", "📋 Pacientes & Documentos", "📊 Relatórios & Levantamentos"])

# ---------------------------------------------------------
# ABA 1: NOVO CADASTRO
# ---------------------------------------------------------
with aba1:
    st.subheader("Cadastro de Paciente")
    
    with st.form("form_paciente", clear_on_submit=True):
        col1, col2 = st.columns(2)
        
        with col1:
            nome = st.text_input("Nome Completo*")
            cpf = st.text_input("CPF*")
            data_nasc = st.date_input("Data de Nascimento")
            genero = st.selectbox("Gênero", ["Masculino", "Feminino", "Outro", "Não informar"])
            telefone = st.text_input("Telefone/WhatsApp")
            
        with col2:
            endereco = st.text_input("Endereço Completo")
            diagnostico = st.text_area("Diagnóstico Principal / Queixa")
            historico = st.text_area("Histórico Médico / Observações")
            
        st.markdown("---")
        st.subheader("Anexo de Arquivos")
        col_f, col_d = st.columns(2)
        
        with col_f:
            foto = st.file_uploader("Foto do Paciente (PNG, JPG)", type=["png", "jpg", "jpeg"])
        with col_d:
            documento = st.file_uploader("Documento / Laudo (PDF, PNG, JPG)", type=["pdf", "png", "jpg", "jpeg"])
            
        submitted = st.form_submit_button("Salvar Paciente")
        
        if submitted:
            if not nome or not cpf:
                st.error("Por favor, preencha os campos obrigatórios (Nome e CPF).")
            else:
                # Salvar arquivos
                foto_path = ""
                doc_path = ""
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                
                if foto:
                    foto_path = os.path.join(OS_DIR_FOTOS, f"{cpf}_{timestamp}_{foto.name}")
                    with open(foto_path, "wb") as f:
                        f.write(foto.getbuffer())
                        
                if documento:
                    doc_path = os.path.join(OS_DIR_DOCS, f"{cpf}_{timestamp}_{documento.name}")
                    with open(doc_path, "wb") as f:
                        f.write(documento.getbuffer())
                
                # Novo registro
                novo_id = len(df_pacientes) + 1
                novo_registro = {
                    "ID": novo_id,
                    "Data Cadastro": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "Nome": nome,
                    "CPF": cpf,
                    "Data Nasc.": str(data_nasc),
                    "Gênero": genero,
                    "Telefone": telefone,
                    "Endereço": endereco,
                    "Diagnóstico": diagnostico,
                    "Histórico / Observações": historico,
                    "Caminho Foto": foto_path,
                    "Caminho Documento": doc_path
                }
                
                df_pacientes = pd.concat([df_pacientes, pd.DataFrame([novo_registro])], ignore_index=True)
                df_pacientes.to_csv(DATA_FILE, index=False)
                st.success(f"Paciente **{nome}** cadastrado com sucesso!")

# ---------------------------------------------------------
# ABA 2: CONSULTA DE PACIENTES E ANEXOS
# ---------------------------------------------------------
with aba2:
    st.subheader("Consulta de Pacientes Registrados")
    
    if df_pacientes.empty:
        st.info("Nenhum paciente cadastrado até o momento.")
    else:
        busca = st.text_input("Buscar por Nome ou CPF")
        
        df_filtrado = df_pacientes
        if busca:
            df_filtrado = df_pacientes[
                df_pacientes["Nome"].str.contains(busca, case=False, na=False) |
                df_pacientes["CPF"].str.contains(busca, case=False, na=False)
            ]
            
        st.dataframe(df_filtrado[["ID", "Data Cadastro", "Nome", "CPF", "Telefone", "Diagnóstico"]], use_container_width=True)
        
        st.markdown("---")
        st.subheader("Detalhes e Arquivos")
        
        paciente_selecionado = st.selectbox("Selecione o paciente para ver detalhes:", df_filtrado["Nome"].tolist() if not df_filtrado.empty else [])
        
        if paciente_selecionado:
            pac_data = df_filtrado[df_filtrado["Nome"] == paciente_selecionado].iloc[0]
            
            c1, c2 = st.columns([1, 2])
            with c1:
                if pd.notna(pac_data["Caminho Foto"]) and os.path.exists(pac_data["Caminho Foto"]):
                    st.image(pac_data["Caminho Foto"], caption=f"Foto: {pac_data['Nome']}", width=200)
                else:
                    st.info("Sem foto cadastrada.")
                    
            with c2:
                st.write(f"**CPF:** {pac_data['CPF']}")
                st.write(f"**Data Nasc.:** {pac_data['Data Nasc.']}")
                st.write(f"**Telefone:** {pac_data['Telefone']}")
                st.write(f"**Endereço:** {pac_data['Endereço']}")
                st.write(f"**Diagnóstico:** {pac_data['Diagnóstico']}")
                st.write(f"**Histórico:** {pac_data['Histórico / Observações']}")
                
                if pd.notna(pac_data["Caminho Documento"]) and os.path.exists(pac_data["Caminho Documento"]):
                    with open(pac_data["Caminho Documento"], "rb") as file:
                        st.download_button(
                            label="📥 Baixar Documento/Laudo",
                            data=file,
                            file_name=os.path.basename(pac_data["Caminho Documento"])
                        )

# ---------------------------------------------------------
# ABA 3: RELATÓRIOS E LEVANTAMENTOS
# ---------------------------------------------------------
with aba3:
    st.subheader("Levantamento Estatístico da Clínica")
    
    if df_pacientes.empty:
        st.warning("Cadastre pacientes para gerar relatórios.")
    else:
        m1, m2, m3 = st.columns(3)
        m1.metric("Total de Pacientes", len(df_pacientes))
        
        # Gráficos simples
        st.markdown("### Distribuição por Gênero")
        st.bar_chart(df_pacientes["Gênero"].value_counts())
        
        st.markdown("### Diagnósticos Frequentes")
        st.dataframe(df_pacientes["Diagnóstico"].value_counts().reset_index().rename(columns={"index": "Diagnóstico", "Diagnóstico": "Quantidade"}))
