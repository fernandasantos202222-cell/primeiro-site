import streamlit as st
if "usuarios" not in st.session_state:
    st.session_state.usuarios = {}
if "logado" not in st.session_state:
    st.session_state.logado = False
st.title("EvoluiAI - Parte 1: Login")

if not st.session_state.logado:
    aba1,aba2,aba3 = st.tabs(["Entrar","Cadastrar,","Esqueci minha senha"])

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
        st.subheader("Cadastro de Usuário")
        st.write("Preencha os campos abaixo para criar uma nova conta.")
        nome = st.text_input("Nome")
        email = st.text_input("Email")
        senha = st.text_input("Senha", type="password")
        if st.button("Cadastrar"):
            if not email or not senha or not nome:
                st.warning("Por favor, preencha nome, email e senha.")
            elif email in st.session_state.usuarios:
                st.warning("Este email já está cadastrado. Por favor, escolha outro.")
            else:
                st.session_state.usuarios[email] = {"nome": nome, "senha": senha}
                st.success("Cadastro realizado com sucesso! Agora você pode fazer login.")
    with aba3:
        st.subheader("Recuperação de Senha")
        st.write("Digite seu email para recuperar sua senha.")
        email_recuperacao = st.text_input("Email de recuperação")
        if st.button("Recuperar Senha"):
            if email_recuperacao in st.session_state.usuarios:
                st.success(f"Senha recuperada com sucesso! Sua senha é: {st.session_state.usuarios[email_recuperacao]['senha']}")
            else:
                st.error("Email não encontrado. Por favor, verifique o email digitado.")

else:
    st.write("Bem-vindo! Você está logado.")
    st.success(f"Logado como: {user} ({st.session_state.usuarios[user]['nome']})")
    if st.button("Sair"):
        st.session_state.logado = False
        st.rerun()
