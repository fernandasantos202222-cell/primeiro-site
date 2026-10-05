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
import streamlit as st
from datetime import datetime

if "usuarios" not in st.session_state:
    st.session_state.usuarios = {}

if "logado" not in st.session_state:
    st.session_state.logado = False
    st.session_state.usuario_logado = ""

st.title("🚀 EvoluiAI")

if not st.session_state.logado:
    # ===== PARTE 1 - LOGIN (igual) =====
    aba1, aba2, aba3 = st.tabs(["Entrar", "Cadastrar", "Trocar Senha"])
    with aba1:
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
        nome = st.text_input("Seu nome completo", key="cad_nome")
        email_cad = st.text_input("Seu e-mail", key="cad_email")
        senha_cad = st.text_input("Crie uma senha", type="password", key="cad_senha")
        if st.button("Cadastrar agora"):
            if not nome or not email_cad or not senha_cad:
                st.warning("Preenche tudo!")
            elif email_cad in st.session_state.usuarios:
                st.warning("E-mail já existe.")
            else:
                # AGORA SALVAMOS MAIS COISAS
                st.session_state.usuarios[email_cad] = {
                    "nome": nome, 
                    "senha": senha_cad,
                    "perfil": None, # Ainda não tem objetivo
                    "cronograma": []
                }
                st.success(f"Pronto, {nome}! Faz login agora.")
    with aba3:
        email_rec = st.text_input("Seu e-mail", key="rec_email")
        if email_rec in st.session_state.usuarios:
            nova_senha = st.text_input("Nova senha", type="password", key="nova_senha")
            if st.button("Salvar nova senha"):
                st.session_state.usuarios[email_rec]["senha"] = nova_senha
                st.success("Senha trocada!")
        else:
            if email_rec != "": st.error("E-mail não encontrado")

else:
    # ===== PARTE 2 - CONHECENDO O ALUNO =====
    usuario = st.session_state.usuarios[st.session_state.usuario_logado]
    st.success(f"Bem-vindo, {usuario['nome']}!")
    
    # Se ainda NÃO tem perfil, mostra o questionário
    if usuario["perfil"] is None:
        st.header("🎯 Primeiro, vamos te conhecer")
        st.write("Antes de criar seu cronograma, me conta seus objetivos.")

        objetivo = st.selectbox("Qual seu OBJETIVO principal agora?", 
                                ["Estudar para concurso", "Estudar programação", "Emagrecer", "Ganhar massa", "Aprender inglês", "Outro"])
        
        meta_especifica = st.text_input("Qual sua META específica? Ex: Passar no concurso do INSS, Aprender Python em 3 meses")
        
        tempo = st.slider("Quanto tempo você tem por dia para isso?", 1, 6, 2)

        frase = st.text_area("Escreve uma frase de MOTIVAÇÃO que te move. (Ex: Vou mudar minha vida esse ano)")
        
        if st.button("Salvar meus objetivos e continuar"):
            if not meta_especifica or not frase:
                st.warning("Preenche sua meta e sua frase de motivação!")
            else:
                # GUARDANDO as informações dele
                st.session_state.usuarios[st.session_state.usuario_logado]["perfil"] = {
                    "objetivo": objetivo,
                    "meta": meta_especifica,
                    "tempo": tempo,
                    "frase": frase,
                    "data_cadastro": datetime.now().strftime("%d/%m/%Y")
                }
                st.success("Objetivos salvos! Gerando seu painel...")
                st.rerun()
    else:
        # Se JÁ tem perfil, mostra o painel
        perfil = usuario["perfil"]
        st.header("Seu Painel EvoluiAI")
        
        # FRASE DE MOTIVAÇÃO EM DESTAQUE
        st.info(f"💬 Sua frase: \"{perfil['frase']}\"")
        
        col1, col2 = st.columns(2)
        col1.metric("Objetivo", perfil['objetivo'])
        col2.metric("Tempo por dia", f"{perfil['tempo']}h")

        st.write(f"**Sua meta:** {perfil['meta']}")

        st.divider()
        
        # AQUI VAI ENTRAR A IA
        st.subheader("📚 Seu Cronograma Inteligente")
        if not usuario["cronograma"]:
            if st.button("✨ Gerar meu cronograma com IA agora"):
                # SIMULAÇÃO da IA por enquanto
                if "Estudar" in perfil['objetivo']:
                    cronograma = [
                        f"Dia 1: Foco total em {perfil['meta']} - Teoria ( {perfil['tempo']}h )",
                        f"Dia 2: Revisão + Exercícios práticos",
                        f"Dia 3: Aula nova + Resumo",
                        f"Dia 4: Simulado rápido",
                        f"Dia 5: Revisão da semana"
                    ]
                else:
                    cronograma = [
                        f"Dia 1: Treino / Estudo focado - {perfil['meta']}",
                        f"Dia 2: Descanso ativo + Revisão",
                        f"Dia 3: Aprofundamento"
                    ]
                st.session_state.usuarios[st.session_state.usuario_logado]["cronograma"] = cronograma
                st.rerun()
        else:
            for i, aula in enumerate(usuario["cronograma"], 1):
                st.checkbox(aula, key=f"aula_{i}")
            if st.button("Gerar novo cronograma"):
                st.session_state.usuarios[st.session_state.usuario_logado]["cronograma"] = []
                st.rerun()

    st.divider()
    if st.button("Sair"):
        st.session_state.logado = False
        st.rerun()        
        
