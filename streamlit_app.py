
import streamlit as st
import json
import pandas as pd
from pathlib import Path

CONFIG_PATH = Path("config")

def load_json(file):
    with open(CONFIG_PATH / file, "r", encoding="utf-8") as f:
        return json.load(f)

def save_json(file, data):
    with open(CONFIG_PATH / file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

st.set_page_config("Gestão de Equipamentos", layout="wide")
st.sidebar.title("Menu")
menu = st.sidebar.radio("Ir para", ["Equipamentos", "Usuários", "Configuração"])

if menu == "Configuração":
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

else:
    st.title("🛠️ Área ainda em desenvolvimento")
    st.info("Apenas o menu de Configuração está funcional nesta versão.")
