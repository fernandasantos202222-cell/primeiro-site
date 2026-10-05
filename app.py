import streamlit as st

if "usuarios" not in st.session_state:
    st.session_state.usuarios = {}

if "logado" not in st.session_state:
    st.session_state.logado = False
    st.session_state.usuario_logado = ""

st.title("🚀 EvoluiAI - Parte 1.2")

if not st.session_state.logado:
    aba1, aba2, aba3 = st.tabs(["Entrar", "Cadastrar", "Esqueci senha"])

    with aba1:
        st.subheader("Entrar")
        email_login = st.text_input("Seu E-MAIL", key="login_email")
        senha_login = st.text_input("Sua Senha", type="password", key="login_senha")
        if st.button("Entrar"):
            if email_login in st.session_state.usuarios and st.session_state.usuarios[email_login]["senha"] == senha_login:
                st.session_state.logado = True
                st.session_state.usuario_logado = email_login
                st.rerun()
            else:
                st.error("E-mail ou senha incorreta.")

    with aba2:
        st.subheader("Criar sua conta")
        nome = st.text_input("Seu nome completo", key="cad_nome")
        email_cad = st.text_input("Seu e-mail (vai ser seu login)", key="cad_email")
        senha_cad = st.text_input("Crie uma senha", type="password", key="cad_senha")
        
        if st.button("Cadastrar agora"):
            if not nome or not email_cad or not senha_cad:
                st.warning("Preenche tudo!")
            elif email_cad in st.session_state.usuarios:
                st.warning("Esse e-mail já existe. Realize o seu login.")
            else:
                st.session_state.usuarios[email_cad] = {"nome": nome, "senha": senha_cad}
                st.success(f"Pronto, {nome}! Agora faz login na aba Entrar.")

    with aba3:
        st.subheader("Trocar sua senha")
        email_rec = st.text_input("Qual seu e-mail?", key="rec_email")
        if email_rec in st.session_state.usuarios:
            st.write(f"Olá, {st.session_state.usuarios[email_rec]['nome']}!")
            nova_senha = st.text_input("Digite sua NOVA senha", type="password", key="nova_senha")
            if st.button("Salvar nova senha"):
                if nova_senha:
                    st.session_state.usuarios[email_rec]["senha"] = nova_senha
                    st.success("Senha trocada com sucesso! Agora é só entrar.")
                else:
                    st.warning("Digite a nova senha")
        else:
            if email_rec != "":
                st.error("E-mail não encontrado")

else:
    dados = st.session_state.usuarios[st.session_state.usuario_logado]
    st.success(f"Bem-vindo, {dados['nome']}!")
    st.write(f"Seu e-mail: {st.session_state.usuario_logado}")
    st.balloons()
    
    if st.button("Sair da conta"):
        st.session_state.logado = False
        st.rerun()
