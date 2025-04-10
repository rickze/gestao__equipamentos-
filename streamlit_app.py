import streamlit as st
import json
import pandas as pd
from pathlib import Path
from hashlib import sha256

CONFIG_PATH = Path("config")
DATA_PATH = Path("data")

def hash_pw(pw): return sha256(pw.encode()).hexdigest()

def load_users():
    with open("users.json", "r", encoding="utf-8") as f:
        return json.load(f)

def save_users(users):
    with open("users.json", "w", encoding="utf-8") as f:
        json.dump(users, f, indent=4)

def authenticate(username, password, users):
    user = users.get(username)
    if user and user["password"] == hash_pw(password):
        return user["role"], user.get("first_login", False)
    return None, None

def update_password(username, new_password, users):
    if username in users:
        users[username]["password"] = hash_pw(new_password)
        users[username]["first_login"] = False
        save_users(users)
        return True
    return False

def load_json(file):
    with open(CONFIG_PATH / file, "r", encoding="utf-8") as f:
        return json.load(f)

def save_json(file, data):
    with open(CONFIG_PATH / file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def load_csv_data():
    file_path = DATA_PATH / "equipamentos.csv"
    if file_path.exists():
        return pd.read_csv(file_path)
    return pd.DataFrame(columns=["Numero", "Descricao", "Categoria", "Organizacao", "Dimensoes", "Tecnologia", "Gestao", "Documentos", "Financeira"])

def save_csv_data(df):
    df.to_csv(DATA_PATH / "equipamentos.csv", index=False)

users = load_users()
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.session_state.role = ""
    st.session_state.first_login = False

if not st.session_state.logged_in:
    st.title("Login")
    u = st.text_input("Utilizador")
    p = st.text_input("Palavra-passe", type="password")
    if st.button("Entrar"):
        role, first = authenticate(u, p, users)
        if role:
            st.session_state.update({
                "logged_in": True, "username": u, "role": role, "first_login": first
            })
            st.rerun()
        else:
            st.error("Credenciais inválidas.")
    st.stop()

if st.session_state.first_login:
    st.warning("Altere a palavra-passe no primeiro acesso.")
    with st.form("pwchange"):
        np = st.text_input("Nova palavra-passe", type="password")
        cp = st.text_input("Confirmar", type="password")
        if st.form_submit_button("Alterar"):
            if np == cp and len(np) >= 4:
                update_password(st.session_state.username, np, users)
                st.success("Palavra-passe atualizada.")
                st.session_state.first_login = False
                st.rerun()
            else:
                st.error("Erro na confirmação ou tamanho.")
    st.stop()

st.sidebar.success(f"Olá, {st.session_state.username} ({st.session_state.role})")
menu_items = ["Equipamentos"]
if st.session_state.role == "Administrador":
    menu_items += ["Usuários", "Configuração"]
menu = st.sidebar.radio("Menu", menu_items)
