import streamlit as st
import pandas as pd
from auth import load_users, authenticate, update_password, add_user, delete_user, save_users

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
    path = "data/dados_mestre.csv"
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
