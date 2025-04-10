import streamlit as st
import json
import pandas as pd
from pathlib import Path
from hashlib import sha256

CONFIG_PATH = Path("config")
DATA_PATH = Path("data")

# 🔐 Funções de autenticação
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

# 📁 Funções de ficheiros
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

# 🔐 Login
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

# 🚀 Menu
st.sidebar.success(f"Olá, {st.session_state.username} ({st.session_state.role})")
menu_items = ["Equipamentos"]
if st.session_state.role == "Administrador":
    menu_items += ["Usuários", "Configuração"]
menu = st.sidebar.radio("Menu", menu_items)

# 📦 Equipamentos
if menu == "Equipamentos":
    st.title("Equipamentos")
    df = load_csv_data()
    st.dataframe(df)

    st.subheader("Novo Equipamento")
    with st.form("add_equipamento"):
        categorias = load_json("categorias.json")
        cat_options = sorted(set(c["codigo"] for c in categorias))
        numero_manual = st.text_input("Número (deixe vazio para gerar)")
        descricao = st.text_input("Descrição")
        categoria = st.selectbox("Categoria", cat_options)
        if st.form_submit_button("Guardar"):
            if not descricao or not categoria:
                st.error("Descrição e categoria são obrigatórios.")
                st.stop()

            if numero_manual:
                if numero_manual in df["Numero"].astype(str).values:
                    st.error("Já existe um equipamento com esse número.")
                    st.stop()
                numero = numero_manual
            else:
                base = load_json("dados_base.json")
                intervs = load_json("intervalos.json")
                linha = next((b for b in base if b["categoria"] == categoria), None)
                if not linha:
                    st.error("Configuração da categoria não encontrada.")
                    st.stop()
                cod = linha["intervalo_interno"]
                intv = next((i for i in intervs if i["codigo"] == cod), None)
                if not intv:
                    st.error("Intervalo interno não encontrado.")
                    st.stop()
                numero = str(intv["proximo"]).zfill(8)
                intv["proximo"] += 1
                save_json("intervalos.json", intervs)

            df.loc[len(df)] = [numero, descricao, categoria] + [""]*6
            save_csv_data(df)
            st.success(f"Equipamento {numero} guardado.")
            st.rerun()

# ⚙️ Configuração
elif menu == "Configuração":
    st.title("🛠️ Configuração do Sistema")
    config_tab = st.selectbox("Escolher tabela para configurar:", ["Categorias", "Dados Base", "Intervalos"])

    if config_tab == "Categorias":
        st.subheader("Categorias de Equipamento")
        categorias = load_json("categorias.json")
        df = pd.DataFrame(categorias)
        st.dataframe(df)

        with st.form("add_cat"):
            st.markdown("### Adicionar nova categoria")
            codigo = st.text_input("Código da Categoria")
            descricao = st.text_input("Descrição")
            idioma = st.selectbox("Idioma", ["PT", "EN", "ES", "FR"])
            if st.form_submit_button("Adicionar"):
                categorias.append({"codigo": codigo, "descricao": descricao, "idioma": idioma})
                save_json("categorias.json", categorias)
                st.success("Categoria adicionada.")
                st.rerun()

    elif config_tab == "Dados Base":
        st.subheader("Dados Base das Categorias")
        dados = load_json("dados_base.json")
        df = pd.DataFrame(dados)
        st.dataframe(df)

        with st.form("add_dbase"):
            st.markdown("### Adicionar ligação de categoria")
            categoria = st.text_input("Categoria")
            grupo = st.text_input("Grupo de Campos")
            intervalo_i = st.text_input("Intervalo Interno")
            intervalo_e = st.text_input("Intervalo Externo (opcional)")
            if st.form_submit_button("Adicionar"):
                entrada = {
                    "categoria": categoria,
                    "grupo": grupo,
                    "intervalo_interno": intervalo_i
                }
                if intervalo_e:
                    entrada["intervalo_externo"] = intervalo_e
                dados.append(entrada)
                save_json("dados_base.json", dados)
                st.success("Ligação adicionada.")
                st.rerun()

    elif config_tab == "Intervalos":
        st.subheader("Intervalos de Numeração")
        intervalos = load_json("intervalos.json")
        df = pd.DataFrame(intervalos)
        st.dataframe(df)

        with st.form("add_intv"):
            st.markdown("### Adicionar novo intervalo")
            codigo = st.text_input("Código")
            externo = st.checkbox("É externo?")
            inicio = st.number_input("Início", min_value=1)
            fim = st.number_input("Fim", min_value=inicio)
            proximo = st.number_input("Próximo número", min_value=inicio, value=inicio)
            if st.form_submit_button("Adicionar"):
                intervalos.append({
                    "codigo": codigo,
                    "externo": externo,
                    "inicio": int(inicio),
                    "fim": int(fim),
                    "proximo": int(proximo)
                })
                save_json("intervalos.json", intervalos)
                st.success("Intervalo adicionado.")
                st.rerun()

# 👥 Gestão de Utilizadores (placeholder)
elif menu == "Usuários":
    st.title("Gestão de Utilizadores")
    st.info("Este módulo será implementado em breve.")
