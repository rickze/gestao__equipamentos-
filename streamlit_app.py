import streamlit as st
import pandas as pd
from auth import load_users, authenticate, update_password, add_user, delete_user, save_users
from pathlib import Path

import streamlit as st
import pandas as pd
from auth import load_users, authenticate, update_password
from utils import load_data, save_data

st.set_page_config(page_title="Gestão de Equipamentos", layout="wide")
users = load_users()

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = ''
    st.session_state.role = ''
    st.session_state.first_login = False

def login():
    st.title("Login")
    username = st.text_input("Utilizador")
    password = st.text_input("Palavra-passe", type="password")
    if st.button("Entrar"):
        role, first_login = authenticate(username, password, users)
        if role:
            st.session_state.logged_in = True
            st.session_state.username = username
            st.session_state.role = role
            st.session_state.first_login = first_login
            st.rerun()
        else:
            st.error("Credenciais inválidas")

if not st.session_state.logged_in:
    login()
    st.stop()

if st.session_state.first_login:
    st.warning("É necessário alterar a palavra-passe no primeiro acesso.")
    with st.form("update_pw_form"):
        new_pw = st.text_input("Nova palavra-passe", type="password")
        confirm_pw = st.text_input("Confirmar nova palavra-passe", type="password")
        if st.form_submit_button("Alterar"):
            if new_pw != confirm_pw:
                st.error("As palavras-passe não coincidem.")
            elif len(new_pw) < 4:
                st.error("A palavra-passe deve ter pelo menos 4 caracteres.")
            else:
                update_password(st.session_state.username, new_pw, users)
                st.success("Palavra-passe alterada com sucesso.")
                st.session_state.first_login = False
                st.rerun()
    st.stop()

# Interface principal
st.sidebar.success(f"Utilizador: {st.session_state.username} ({st.session_state.role})")
menu = st.sidebar.selectbox("Menu", ["Dados Mestre", "Administração de Utilizadores"] if st.session_state.role == "Administrador" else ["Dados Mestre"])

if menu == "Dados Mestre":
    st.title("Gestão de Equipamentos - Dados Mestre")
    columns = ["Número", "Nome", "Categoria", "Tipo", "Classe", "Matrícula", "Descrição Detalhada"]
    path = "data/dados_gerais.csv"
    df = pd.read_csv(path) if Path(path).exists() else pd.DataFrame(columns=columns)
    st.dataframe(df)
    if st.session_state.role != "Visualizador":
        with st.form("add_equipment"):
            values = [st.text_input(col) for col in columns]
            if st.form_submit_button("Adicionar"):
                df.loc[len(df)] = values
                df.to_csv(path, index=False)
                st.success("Equipamento adicionado com sucesso.")
                st.rerun()

elif menu == "Administração de Utilizadores":
    st.title("Administração de Utilizadores")
    st.subheader("Utilizadores existentes")
    st.table(pd.DataFrame([{ "Utilizador": u, "Perfil": d['role'], "Primeiro Login": d.get("first_login", False) } for u, d in users.items()]))
    
    st.subheader("Criar novo utilizador")
    with st.form("create_user"):
        new_user = st.text_input("Novo utilizador")
        new_pw = st.text_input("Palavra-passe", type="password")
        role = st.selectbox("Perfil", ["Administrador", "Utilizador", "Visualizador"])
        if st.form_submit_button("Criar"):
            if new_user in users:
                st.error("Utilizador já existe.")
            elif len(new_pw) < 4:
                st.error("Palavra-passe demasiado curta.")
            else:
                add_user(new_user, new_pw, role, users)
                st.success("Utilizador criado com sucesso.")
                st.rerun()

    st.subheader("Remover utilizador")
    user_to_delete = st.selectbox("Selecionar utilizador", [u for u in users if u != "admin"])
    if st.button("Eliminar"):
        delete_user(user_to_delete, users)
        st.success(f"Utilizador '{user_to_delete}' removido.")
        st.rerun()

    st.warning("Altere a palavra-passe no primeiro login.")
    with st.form("pw_update"):
        new_pw = st.text_input("Nova palavra-passe", type="password")
        confirm_pw = st.text_input("Confirmar palavra-passe", type="password")
        if st.form_submit_button("Alterar"):
            if new_pw == confirm_pw and len(new_pw) >= 4:
                update_password(st.session_state.username, new_pw, users)
                st.success("Palavra-passe alterada.")
                st.session_state.first_login = False
                st.rerun()
            else:
                st.error("Erro na confirmação ou tamanho da palavra-passe.")
    st.stop()

st.sidebar.success(f"Utilizador: {st.session_state.username} ({st.session_state.role})")
tabs = st.tabs(['Dados Gerais', 'Organização', 'Dimensões', 'Tecnologia', 'Gestão', 'Documentos', 'Financeira'])


with tabs[0]:
    st.subheader("Dados Gerais")
    df = load_data("data/dados_gerais.csv", ['Número', 'Nome', 'Categoria', 'Tipo', 'Classe', 'Matrícula', 'Descrição Detalhada'])
    st.dataframe(df)
    if st.session_state.role != "Visualizador":
        with st.form("form_dados_gerais"):
            inputs = [st.text_input(col) for col in ['Número', 'Nome', 'Categoria', 'Tipo', 'Classe', 'Matrícula', 'Descrição Detalhada']]
            if st.form_submit_button("Guardar"):
                df.loc[len(df)] = inputs
                save_data("data/dados_gerais.csv", df)
                st.success("Registo adicionado com sucesso.")
                st.rerun()


with tabs[1]:
    st.subheader("Organização")
    df = load_data("data/organização.csv", ['Número', 'Empresa', 'Localização', 'Departamento', 'Centro de Custo'])
    st.dataframe(df)
    if st.session_state.role != "Visualizador":
        with st.form("form_organização"):
            inputs = [st.text_input(col) for col in ['Número', 'Empresa', 'Localização', 'Departamento', 'Centro de Custo']]
            if st.form_submit_button("Guardar"):
                df.loc[len(df)] = inputs
                save_data("data/organização.csv", df)
                st.success("Registo adicionado com sucesso.")
                st.rerun()


with tabs[2]:
    st.subheader("Dimensões")
    df = load_data("data/dimensões.csv", ['Número', 'Peso', 'Altura', 'Largura', 'Comprimento'])
    st.dataframe(df)
    if st.session_state.role != "Visualizador":
        with st.form("form_dimensões"):
            inputs = [st.text_input(col) for col in ['Número', 'Peso', 'Altura', 'Largura', 'Comprimento']]
            if st.form_submit_button("Guardar"):
                df.loc[len(df)] = inputs
                save_data("data/dimensões.csv", df)
                st.success("Registo adicionado com sucesso.")
                st.rerun()


with tabs[3]:
    st.subheader("Tecnologia")
    df = load_data("data/tecnologia.csv", ['Número', 'Fabricante', 'Modelo', 'Número de Série', 'VIN', 'Ano Fabrico', 'Tipo Combustível'])
    st.dataframe(df)
    if st.session_state.role != "Visualizador":
        with st.form("form_tecnologia"):
            inputs = [st.text_input(col) for col in ['Número', 'Fabricante', 'Modelo', 'Número de Série', 'VIN', 'Ano Fabrico', 'Tipo Combustível']]
            if st.form_submit_button("Guardar"):
                df.loc[len(df)] = inputs
                save_data("data/tecnologia.csv", df)
                st.success("Registo adicionado com sucesso.")
                st.rerun()


with tabs[4]:
    st.subheader("Gestão")
    df = load_data("data/gestão.csv", ['Número', 'Data Início', 'Estado', 'Responsável', 'Data Desativação'])
    st.dataframe(df)
    if st.session_state.role != "Visualizador":
        with st.form("form_gestão"):
            inputs = [st.text_input(col) for col in ['Número', 'Data Início', 'Estado', 'Responsável', 'Data Desativação']]
            if st.form_submit_button("Guardar"):
                df.loc[len(df)] = inputs
                save_data("data/gestão.csv", df)
                st.success("Registo adicionado com sucesso.")
                st.rerun()


with tabs[5]:
    st.subheader("Documentos")
    df = load_data("data/documentos.csv", ['Número', 'Tipo Documento', 'Descrição Documento', 'Ficheiro'])
    st.dataframe(df)
    if st.session_state.role != "Visualizador":
        with st.form("form_documentos"):
            inputs = [st.text_input(col) for col in ['Número', 'Tipo Documento', 'Descrição Documento', 'Ficheiro']]
            if st.form_submit_button("Guardar"):
                df.loc[len(df)] = inputs
                save_data("data/documentos.csv", df)
                st.success("Registo adicionado com sucesso.")
                st.rerun()


with tabs[6]:
    st.subheader("Financeira")
    df = load_data("data/financeira.csv", ['Número', 'Data Aquisição', 'Valor', 'Moeda', 'Ativo Fixo', 'Fim Garantia', 'Fornecedor'])
    st.dataframe(df)
    if st.session_state.role != "Visualizador":
        with st.form("form_financeira"):
            inputs = [st.text_input(col) for col in ['Número', 'Data Aquisição', 'Valor', 'Moeda', 'Ativo Fixo', 'Fim Garantia', 'Fornecedor']]
            if st.form_submit_button("Guardar"):
                df.loc[len(df)] = inputs
                save_data("data/financeira.csv", df)
                st.success("Registo adicionado com sucesso.")
                st.rerun()
