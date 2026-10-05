import streamlit as st
import json, os
from datetime import date, timedelta
import random

ARQUIVO_BANCO = "banco_usuarios.json"
def carregar():
    if os.path.exists(ARQUIVO_BANCO):
        try:
            with open(ARQUIVO_BANCO, "r", encoding="utf-8") as f: return json.load(f)
        except: return {}
    return {}
def salvar():
    with open(ARQUIVO_BANCO, "w", encoding="utf-8") as f:
        json.dump(st.session_state.usuarios, f, indent=4, ensure_ascii=False)

if "usuarios" not in st.session_state: st.session_state.usuarios = carregar()
if "logado" not in st.session_state:
    st.session_state.logado = False
    st.session_state.usuario_logado = ""

FRASES = ["Continue! 🚀", "Mais um passo! 🔥", "Você é imparável! 💪", "Seu futuro agradece! ✨", "QUASE LÁ! 🏆", "VOCÊ CONSEGUIU! 🎉"]

st.title("🚀 EvoluiAI")

if not st.session_state.logado:
    a1, a2 = st.tabs(["Entrar", "Cadastrar"])
    with a1:
        u = st.text_input("Usuário", key="l1")
        s = st.text_input("Senha", type="password", key="l2")
        if st.button("Entrar"):
            if u in st.session_state.usuarios and st.session_state.usuarios[u]["senha"] == s:
                st.session_state.logado = True
                st.session_state.usuario_logado = u
                st.rerun()
            else: st.error("Usuário ou senha errada.")
    with a2:
        nome = st.text_input("Nome", key="c1")
        c1, c2 = st.columns(2)
        with c1: genero = st.selectbox("Gênero", ["Masculino","Feminino","Outro"], key="c2")
        with c2: idade = st.number_input("Idade", 10, 100, 20, key="c3")
        email = st.text_input("E-mail", key="c4")
        user = st.text_input("Usuário", key="c5", placeholder="sem espaço")
        senha = st.text_input("Senha", type="password", key="c6")
        if st.button("Cadastrar"):
            if not nome or not user or not senha: st.warning("Preenche tudo")
            elif user in st.session_state.usuarios: st.warning("Usuário já existe")
            else:
                st.session_state.usuarios[user] = {"nome": nome, "genero": genero, "idade": idade, "email": email, "senha": senha, "perfil": None, "cronograma": [], "progresso": {}, "streak": 0}
                salvar()
                st.success(f"Cadastrado {user}!")
else:
    usuario = st.session_state.usuarios[st.session_state.usuario_logado]
    # CORREÇÃO PARA CONTAS ANTIGAS
    if "progresso" not in usuario: st.session_state.usuarios[st.session_state.usuario_logado]["progresso"] = {}
    if "streak" not in usuario: st.session_state.usuarios[st.session_state.usuario_logado]["streak"] = 0
    if "cronograma" not in usuario: st.session_state.usuarios[st.session_state.usuario_logado]["cronograma"] = []

    if usuario["perfil"] is None:
        st.header(f"Olá {usuario['nome']}!")
        area = st.selectbox("Área?", ["Estudos","Saúde","Financeira","Espiritual","Carreira"], key="area")
        if area == "Estudos":
            nivel = st.selectbox("Nível?", ["Ensino Fundamental","Ensino Médio","Ensino Superior","Concurso/ENEM","Autodidata"], key="niv")
            curso = st.text_input("Qual curso?", key="cur") if nivel == "Ensino Superior" else ""
            materia = st.text_input("Matéria atual?", key="mat")
            quer = st.multiselect("Quer o que?", ["Cronograma","Vídeos","Livros","Simulados","Revisão"], default=["Cronograma"], key="quer")
            tempo = st.slider("Horas/dia?", 1, 6, 2, key="tmp")
            dias = st.multiselect("Dias?", ["Segunda","Terça","Quarta","Quinta","Sexta","Sábado","Domingo"], default=["Segunda","Quarta","Sexta"], key="ds")
            if st.button("✨ Criar meu plano"):
                if not materia: st.warning("Qual matéria?")
                else:
                    hoje = date.today()
                    cron = [f"{dias[i]} ({(hoje + timedelta(days=i)).strftime('%d/%m')}) - {materia}: {quer[i % len(quer)] if quer else 'Estudar'}" for i in range(len(dias))]
                    st.session_state.usuarios[st.session_state.usuario_logado]["perfil"] = {"area": area, "nivel": nivel, "curso": curso, "materia": materia, "quer": quer, "tempo": tempo, "dias": dias, "meta_ia": f"Dominar {materia} com {tempo}h/dia", "frase_boas_vindas": f"Bora evoluir em {materia}! Plano de {nivel} começando hoje!", "data_inicio": date.today().isoformat()}
                    st.session_state.usuarios[st.session_state.usuario_logado]["cronograma"] = cron
                    st.session_state.usuarios[st.session_state.usuario_logado]["progresso"] = {}
                    salvar()
                    st.rerun()
        else:
            obj = st.text_area("Objetivo?", key="ob")
            tempo = st.slider("Horas/dia?", 1, 5, 2, key="to")
            dias = st.multiselect("Dias?", ["Segunda","Terça","Quarta","Quinta","Sexta","Sábado","Domingo"], default=["Segunda","Quarta","Sexta"], key="do")
            if st.button("Criar"):
                st.session_state.usuarios[st.session_state.usuario_logado]["perfil"] = {"area": area, "objetivo": obj, "tempo": tempo, "dias": dias, "meta_ia": f"Meta {area}: {obj}", "frase_boas_vindas": f"Bora evoluir em {area}!", "data_inicio": date.today().isoformat(), "materia": obj}
                st.session_state.usuarios[st.session_state.usuario_logado]["cronograma"] = [f"{d} - {obj}" for d in dias]
                st.session_state.usuarios[st.session_state.usuario_logado]["progresso"] = {}
                salvar()
                st.rerun()
    else:
        p = usuario["perfil"]
        # CORREÇÃO AQUI - USA.get PRA NÃO QUEBRAR
        progresso_dict = usuario.get("progresso", {})

        st.success(f"💬 {p.get('frase_boas_vindas','Bem-vindo!')}")
        col1, col2, col3 = st.columns(3)
        with col1: st.metric("Área", p.get('area',''))
        with col2: st.metric("🔥 Sequência", f"{usuario.get('streak',0)} dias")
        with col3: st.metric("Início", p.get('data_inicio','hoje'))

        total = len(usuario.get("cronograma", []))
        feitos = len(progresso_dict)
        pct = feitos / total if total > 0 else 0

        st.subheader(f"Progresso: {feitos}/{total}")
        st.progress(pct)

        if pct == 0: st.info("💡 Marque sua primeira tarefa!")
        elif pct < 1: st.warning(f"💬 {random.choice(FRASES)} - {int(pct*100)}% completo!")
        else:
            st.balloons()
            st.success("🎉 VOCÊ CONSEGUIU! Tudo feito hoje!")

        st.divider()
        st.subheader(f"📅 Hoje é {date.today().strftime('%d/%m/%Y')}")

        for i, tarefa in enumerate(usuario.get("cronograma", [])):
            chave = f"tarefa_{i}"
            ja_feito = progresso_dict.get(chave, False) # LINHA 150 CORRIGIDA
            marcado = st.checkbox(tarefa, value=ja_feito, key=chave)

            if marcado and not ja_feito:
                st.session_state.usuarios[st.session_state.usuario_logado]["progresso"][chave] = True
                st.session_state.usuarios[st.session_state.usuario_logado]["streak"] = usuario.get("streak",0) + 1
                salvar()
                st.toast(f"✅ {random.choice(FRASES)}")
                st.rerun()
            elif not marcado and ja_feito:
                del st.session_state.usuarios[st.session_state.usuario_logado]["progresso"][chave]
                salvar()
                st.rerun()

        st.divider()
        c1, c2 = st.columns(2)
        with c1:
            st.write("✅ FEITOS")
            for k in progresso_dict:
                idx = int(k.split("_")[1])
                if idx < len(usuario.get("cronograma", [])): st.write(f"- {usuario['cronograma'][idx]}")
        with c2:
            st.write("⏳ FALTA")
            for i, t in enumerate(usuario.get("cronograma", [])):
                if f"tarefa_{i}" not in progresso_dict: st.write(f"- {t}")

        if st.button("🔄 Refazer plano"):
            st.session_state.usuarios[st.session_state.usuario_logado]["perfil"] = None
            st.session_state.usuarios[st.session_state.usuario_logado]["cronograma"] = []
            st.session_state.usuarios[st.session_state.usuario_logado]["progresso"] = {}
            salvar()
            st.rerun()

    if st.button("Sair"):
        st.session_state.logado = False
        st.rerun()
