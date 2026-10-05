import streamlit as st
from datetime import datetime
import json
import os

ARQUIVO_BANCO = "banco_usuarios.json"

# FUNÇÕES PARA NUNCA MAIS PERDER CADASTRO
def carregar_usuarios():
    if os.path.exists(ARQUIVO_BANCO):
        try:
            with open(ARQUIVO_BANCO, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return {}
    return {}

def salvar_usuarios():
    with open(ARQUIVO_BANCO, "w", encoding="utf-8") as f:
        json.dump(st.session_state.usuarios, f, indent=4, ensure_ascii=False)

# Carrega do arquivo se for a primeira vez
if "usuarios" not in st.session_state:
    st.session_state.usuarios = carregar_usuarios()

if "logado" not in st.session_state:
    st.session_state.logado = False
    st.session_state.usuario_logado = ""

def gerar_meta_pela_ia(area, objetivo, tempo, dias):
    qtd_dias = len(dias) if dias else 3
    horas_semana = tempo * qtd_dias
    meta = f"Meta IA: Conquistar '{objetivo}' em {area} com {horas_semana}h/semana ({tempo}h em {qtd_dias} dias)."
    frase = f"Bem-vindo à sua jornada de {area.lower()}! Com {horas_semana}h por semana, você vai alcançar '{objetivo}'."
    return meta, frase

st.title("🚀 EvoluiAI")

if not st.session_state.logado:
    aba1, aba2, aba3 = st.tabs(["Entrar com Usuário", "Cadastrar", "Trocar Senha"])
    
    with aba1:
        u_login = st.text_input("Seu NOME DE USUÁRIO", key="user_login_001", placeholder="ex: matheus10")
        s_login = st.text_input("Sua Senha", type="password", key="pass_login_001")
        if st.button("Entrar"):
            if u_login in st.session_state.usuarios and st.session_state.usuarios[u_login]["senha"] == s_login:
                st.session_state.logado = True
                st.session_state.usuario_logado = u_login
                st.rerun()
            else:
                st.error("Usuário ou senha incorreta. Se é a primeira vez, cadastra na aba Cadastrar.")

    with aba2:
        st.subheader("Crie sua conta")
        nome = st.text_input("Seu nome completo", key="nome_cad_002")
        
        col1, col2 = st.columns(2)
        with col1:
            genero = st.selectbox("Gênero", ["Masculino", "Feminino", "Outro", "Prefiro não dizer"], key="gen_002")
        with col2:
            idade = st.number_input("Idade", min_value=10, max_value=100, value=20, key="idade_002")
        
        email = st.text_input("Seu e-mail", key="email_cad_002")
        usuario_escolhido = st.text_input("Escolha seu NOME DE USUÁRIO (será seu login)", key="user_cad_002", placeholder="ex: matheus10, sem espaço")
        senha = st.text_input("Crie uma senha", type="password", key="senha_cad_002")
        
        if st.button("Cadastrar agora"):
            if not nome or not email or not usuario_escolhido or not senha:
                st.warning("Preenche tudo!")
            elif usuario_escolhido in st.session_state.usuarios:
                st.warning(f"O usuário '{usuario_escolhido}' já existe. Tenta outro, tipo {usuario_escolhido}123")
            elif " " in usuario_escolhido:
                st.warning("Nome de usuário não pode ter espaço. Usa _ ou junta tudo.")
            else:
                st.session_state.usuarios[usuario_escolhido] = {
                    "nome": nome,
                    "genero": genero,
                    "idade": idade,
                    "email": email,
                    "senha": senha,
                    "perfil": None,
                    "cronograma": []
                }
                salvar_usuarios() # SALVA NO ARQUIVO DE VERDADE
                st.success(f"Pronto, {nome}! Seu usuário é '{usuario_escolhido}'. Agora entra na aba Entrar.")

    with aba3:
        u_rec = st.text_input("Seu nome de usuário", key="user_rec_003")
        if u_rec in st.session_state.usuarios:
            nova = st.text_input("Nova senha", type="password", key="nova_003")
            if st.button("Salvar nova senha"):
                st.session_state.usuarios[u_rec]["senha"] = nova
                salvar_usuarios()
                st.success("Senha trocada! Pode entrar agora.")
        else:
            if u_rec != "": st.error("Usuário não encontrado.")

else:
    usuario = st.session_state.usuarios[st.session_state.usuario_logado]
    
    if usuario["perfil"] is None:
        st.header(f"Olá, {usuario['nome']}! Vamos te conhecer")
        st.write(f"Vi aqui que você tem {usuario['idade']} anos. Agora me conta seus objetivos.")
        
        area = st.selectbox("ÁREA da sua vida?", ["Saúde", "Financeira", "Espiritual", "Estudos", "Carreira", "Relacionamento", "Outra"], key="area_10")
        objetivo = st.text_area(f"O que você quer em {area}?", placeholder="Ex: Quero ter mais foco", key="obj_11")
        st.subheader("Sua disponibilidade")
        c1, c2 = st.columns(2)
        with c1: tempo = st.slider("Horas por dia?", 1, 5, 2, key="t_12")
        with c2: horario = st.selectbox("Melhor horário?", ["Manhã", "Tarde", "Noite", "Flexível"], key="h_13")
        dias = st.multiselect("Quais dias?", ["Segunda", "Terça", "Quarta", "Quinta", "Sexta", "Sábado", "Domingo"], default=["Segunda","Quarta","Sexta"], key="d_14")

        if st.button("✨ Criar meu plano com IA"):
            if not objetivo: st.warning("Escreve seu objetivo!")
            else:
                meta_ia, frase_ia = gerar_meta_pela_ia(area, objetivo, tempo, dias)
                st.session_state.usuarios[st.session_state.usuario_logado]["perfil"] = {
                    "area": area, "objetivo_aberto": objetivo, "tempo": tempo, "horario": horario, "dias": dias,
                    "meta_criada_pela_ia": meta_ia, "frase_boas_vindas": frase_ia
                }
                salvar_usuarios()
                st.rerun()
    else:
        p = usuario["perfil"]
        st.success(f"💬 {p['frase_boas_vindas']}")
        st.header(f"Painel de {p['area']} - {usuario['nome']} ({usuario['genero']}, {usuario['idade']} anos)")
        st.info(f"🎯 {p['meta_criada_pela_ia']}")
        st.divider()
        st.subheader("📚 Cronograma")
        if not usuario["cronograma"]:
            if st.button("Gerar cronograma"):
                cron = [f"Dia: {d} - {p['area']} ({p['horario']})" for d in p['dias']]
                st.session_state.usuarios[st.session_state.usuario_logado]["cronograma"] = cron
                salvar_usuarios()
                st.rerun()
        else:
            for i, aula in enumerate(usuario["cronograma"], 1):
                st.checkbox(aula, key=f"chk_{i}")

    if st.button("Sair", key="sair_fim"):
        st.session_state.logado = False
        st.rerun()
