import streamlit as st
from datetime import datetime

if "usuarios" not in st.session_state:
    st.session_state.usuarios = {}
if "logado" not in st.session_state:
    st.session_state.logado = False
    st.session_state.usuario_logado = ""

st.title("🚀 EvoluiAI")

if not st.session_state.logado:
    aba1, aba2, aba3 = st.tabs(["Entrar", "Cadastrar", "Trocar Senha"])
    with aba1:
        email_login = st.text_input("Seu E-MAIL", key="entrar_email_001")
        senha_login = st.text_input("Sua Senha", type="password", key="entrar_senha_001")
        if st.button("Entrar"):
            if email_login in st.session_state.usuarios and st.session_state.usuarios[email_login]["senha"] == senha_login:
                st.session_state.logado = True
                st.session_state.usuario_logado = email_login
                st.rerun()
            else:
                st.error("E-mail ou senha incorreta.")
    with aba2:
        nome = st.text_input("Seu nome", key="cad_nome_002")
        email_cad = st.text_input("Seu e-mail", key="cad_email_002")
        senha_cad = st.text_input("Crie uma senha", type="password", key="cad_senha_002")
        if st.button("Cadastrar agora"):
            if not nome or not email_cad or not senha_cad:
                st.warning("Preenche tudo!")
            elif email_cad in st.session_state.usuarios:
                st.warning("E-mail já existe.")
            else:
                st.session_state.usuarios[email_cad] = {"nome": nome, "senha": senha_cad, "perfil": None, "cronograma": []}
                st.success(f"Pronto, {nome}! Faz login agora.")
    with aba3:
        email_rec = st.text_input("Seu e-mail", key="rec_email_003")
        if email_rec in st.session_state.usuarios:
            nova_senha = st.text_input("Nova senha", type="password", key="rec_nova_senha_003")
            if st.button("Salvar nova senha"):
                st.session_state.usuarios[email_rec]["senha"] = nova_senha
                st.success("Senha trocada!")
        else:
            if email_rec != "": st.error("E-mail não encontrado")
else:
    usuario = st.session_state.usuarios[st.session_state.usuario_logado]
    st.success(f"Bem-vindo, {usuario['nome']}!")
    if usuario["perfil"] is None:
        st.header("🎯 Vamos te conhecer")
        objetivo = st.selectbox("OBJETIVO principal?", ["Estudar para concurso", "Estudar programação", "Emagrecer", "Ganhar massa", "Aprender inglês", "Outro"], key="obj_1")
        meta_especifica = st.text_input("META específica? Ex: Passar no INSS", key="meta_1")
        tempo = st.slider("Tempo por dia?", 1, 6, 2, key="tempo_1")
        frase = st.text_area("Sua FRASE de motivação:", key="frase_1")
        if st.button("Salvar meus objetivos"):
            if not meta_especifica or not frase:
                st.warning("Preenche meta e frase!")
            else:
                st.session_state.usuarios[st.session_state.usuario_logado]["perfil"] = {"objetivo": objetivo, "meta": meta_especifica, "tempo": tempo, "frase": frase, "data": datetime.now().strftime("%d/%m/%Y")}
                st.rerun()
    else:
        perfil = usuario["perfil"]
        st.info(f"💬 Sua frase: \"{perfil['frase']}\"")
        col1, col2 = st.columns(2)
        col1.metric("Objetivo", perfil['objetivo'])
        col2.metric("Tempo/dia", f"{perfil['tempo']}h")
        st.write(f"**Meta:** {perfil['meta']}")
        st.divider()
        st.subheader("📚 Seu Cronograma Inteligente")
        if not usuario["cronograma"]:
            if st.button("✨ Gerar meu cronograma"):
                cronograma = [f"Dia 1: Teoria - {perfil['meta']} ({perfil['tempo']}h)", "Dia 2: Exercícios práticos", "Dia 3: Revisão", "Dia 4: Simulado", "Dia 5: Revisão da semana"]
                st.session_state.usuarios[st.session_state.usuario_logado]["cronograma"] = cronograma
                st.rerun()
        else:
            for i, aula in enumerate(usuario["cronograma"], 1):
                st.checkbox(aula, key=f"aula_check_{i}")
            if st.button("Gerar novo"):
                st.session_state.usuarios[st.session_state.usuario_logado]["cronograma"] = []
                st.rerun()
    if st.button("Sair da conta", key="sair_geral"):
        st.session_state.logado = False
        st.rerun()
