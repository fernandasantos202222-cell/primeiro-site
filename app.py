import streamlit as st
data = st.date_input("Selecione  a data")
st.write("Dia", data.day)
st.write("Mês", data.month)
st.write("Ano", data.year)
data_str = data.strftime("%d/%m/%Y")
st.write(data_str)
datas = st.date_input("Periodo",)
st.write(datas)
import streamlit as st
if "usuarios" not in st.session_state:
    st.session_state.usuarios = {}
if "logado" not in st.session_state:
    st.session_state.logado = False
st.title("EvoluiAI - Parte 1: Login")

if not st.session_state.logado:
    aba1,aba2 = st.tabs(["Entrar","Cadastrar"])

    with aba1:
        user = st.text_input("Usuário")
        senha = st.text_input("Senha", type="password")
        if st.button("Entrar"):
            if user in st.session_state.usuarios and st.session_state.usuarios[user] == senha:
                st.session_state.logado = True
                st.success("Login realizado com sucesso!")
            else:
                st.error("Usuário ou senha incorretos.")
    with aba2:
        novo_user = st.text_input("Novo usuário")
        nova_senha = st.text_input("Nova senha", type="password")
        if st.button("Cadastrar"):
            if novo_user and nova_senha:
                st.session_state.usuarios[novo_user] = nova_senha
                st.success("Usuário cadastrado com sucesso!")
            else:
                st.error("Preencha todos os campos para cadastrar.")
else:
    st.write("Bem-vindo! Você está logado.")
    if st.button("Sair"):
        st.session_state.logado = False
        st.experimental_rerun()

