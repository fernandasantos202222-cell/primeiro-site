import streamlit as st
import json, os
from datetime import date, datetime, timedelta
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

FRASES_MOTIVACIONAIS = [
    "Você está no caminho certo! Continue! 🚀",
    "Incrível! Mais um passo para sua meta! 🔥",
    "Olha sua evolução! Você é imparável! 💪",
    "Metade feita! Seu futuro agradece! ✨",
    "QUASE LÁ! Finaliza com tudo! 🏆",
    "VOCÊ CONSEGUIU! Hoje foi seu dia! 🎉"
]

def gerar_meta_estudos(dados):
    meta = f"Dominar {dados['materia']} ({dados['nivel']}) com {dados['tempo']}h/dia."
    frase = f"Bora, {dados['materia']} não vai se vencer sozinha! Seu plano de {dados['nivel']} começou hoje!"
    return meta, frase

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
            else: st.error("Errado")
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
                st.session_state.usuarios[user] = {
                    "nome": nome, "genero": genero, "idade": idade, "email": email, "senha": senha,
                    "perfil": None, "cronograma": [], "progresso": {}, "streak": 0, "ultimo_acesso": None
                }
                salvar()
                st.success(f"Cadastrado {user}!")
else:
    usuario = st.session_state.usuarios[st.session_state.usuario_logado]

    if usuario["perfil"] is None:
        st.header(f"Olá {usuario['nome']}!")
        area = st.selectbox("Área?", ["Estudos","Saúde","Financeira","Espiritual","Carreira"], key="area")
        if area == "Estudos":
            nivel = st.selectbox("Nível?", ["Ensino Fundamental","Ensino Médio","Ensino Superior","Concurso/ENEM","Autodidata"], key="niv")
            curso = ""
            if nivel == "Ensino Superior": curso = st.text_input("Qual curso?", key="cur")
            materia = st.text_input("Matéria atual?", key="mat", placeholder="Ex: Constitucional")
            quer = st.multiselect("Quer o que?", ["Cronograma","Vídeos","Livros","Simulados","Revisão"], default=["Cronograma"], key="quer")
            tempo = st.slider("Horas/dia?", 1, 6, 2, key="tmp")
            dias = st.multiselect("Dias?", ["Segunda","Terça","Quarta","Quinta","Sexta","Sábado","Domingo"], default=["Segunda","Quarta","Sexta"], key="ds")
            if st.button("✨ Criar meu plano"):
                if not materia: st.warning("Qual matéria?")
                else:
                    dados = {"nivel": nivel, "curso_superior": curso, "materia": materia, "quer": quer, "tempo": tempo, "dias": dias, "area": area}
                    meta, frase = gerar_meta_estudos(dados)
                    st.session_state.usuarios[st.session_state.usuario_logado]["perfil"] = {
                        "area": area, "nivel": nivel, "curso": curso, "materia": materia, "quer": quer,
                        "tempo": tempo, "dias": dias, "meta_ia": meta, "frase_boas_vindas": frase,
                        "data_inicio": date.today().isoformat()
                    }
                    # CRIA CRONOGRAMA COM DATA COMEÇANDO HOJE
                    hoje = date.today()
                    cron = []
                    for i in range(len(dias)):
                        data_tarefa = hoje + timedelta(days=i)
                        tarefa = f"{dias[i]} ({data_tarefa.strftime('%d/%m')}) - {materia}: {quer[i % len(quer)] if quer else 'Estudar'}"
                        cron.append(tarefa)

                    st.session_state.usuarios[st.session_state.usuario_logado]["cronograma"] = cron
                    st.session_state.usuarios[st.session_state.usuario_logado]["progresso"] = {}
                    salvar()
                    st.rerun()
        else:
            obj = st.text_area("Objetivo?", key="ob")
            tempo = st.slider("Horas/dia?", 1, 5, 2, key="to")
            dias = st.multiselect("Dias?", ["Segunda","Terça","Quarta","Quinta","Sexta","Sábado","Domingo"], default=["Segunda","Quarta","Sexta"], key="do")
            if st.button("Criar"):
                st.session_state.usuarios[st.session_state.usuario_logado]["perfil"] = {
                    "area": area, "objetivo": obj, "tempo": tempo, "dias": dias,
                    "meta_ia": f"Meta {area}: {obj}", "frase_boas_vindas": f"Bora evoluir em {area}!", "data_inicio": date.today().isoformat()
                }
                st.session_state.usuarios[st.session_state.usuario_logado]["cronograma"] = [f"{d} - {obj}" for d in dias]
                salvar()
                st.rerun()
    else:
        p = usuario["perfil"]
        # ===== CABEÇALHO COM STREAK E FRASE =====
        st.success(f"💬 {p['frase_boas_vindas']}")

        col1, col2, col3 = st.columns(3)
        with col1: st.metric("Área", p['area'])
        with col2: st.metric("🔥 Sequência", f"{usuario.get('streak',0)} dias")
        with col3: st.metric("Início", p.get('data_inicio','hoje'))

        # ===== PROGRESSO =====
        total = len(usuario["cronograma"])
        feitos = len(usuario.get("progresso", {}))
        progresso_pct = feitos / total if total > 0 else 0

        st.subheader(f"Seu Progresso: {feitos}/{total}")
        st.progress(progresso_pct)

        # FRASE MOTIVACIONAL QUE MUDA COM PROGRESSO
        if progresso_pct == 0: st.info("💡 Comece marcando sua primeira tarefa como feita!")
        elif progresso_pct < 0.5: st.info(f"💬 {FRASES_MOTIVACIONAIS[0]} - {int(progresso_pct*100)}% já foi!")
        elif progresso_pct < 1: st.warning(f"💬 {FRASES_MOTIVACIONAIS[2]} - {int(progresso_pct*100)}% completo!")
        else:
            st.balloons()
            st.success(f"💬 {FRASES_MOTIVACIONAIS[5]} Você terminou tudo hoje!")

        st.divider()

        # ===== CALENDÁRIO + TAREFAS =====
        st.subheader(f"📅 Calendário - Hoje é {date.today().strftime('%d/%m/%Y')}")
        st.write(f"Matéria: **{p.get('materia', p.get('objetivo',''))}**")

        # Mostra tarefas com checkbox que aumenta progresso
        for i, tarefa in enumerate(usuario["cronograma"]):
            chave = f"tarefa_{i}"
            ja_feito = usuario["progresso"].get(chave, False)

            # Se marcar como feito
            marcado = st.checkbox(tarefa, value=ja_feito, key=chave)

            if marcado and not ja_feito:
                # Acabou de fazer
                st.session_state.usuarios[st.session_state.usuario_logado]["progresso"][chave] = True
                st.session_state.usuarios[st.session_state.usuario_logado]["streak"] = usuario.get("streak",0) + 1
                salvar()
                st.toast(f"✅ Feito! {random.choice(FRASES_MOTIVACIONAIS)}")
                st.rerun()
            elif not marcado and ja_feito:
                # Desmarcou
                del st.session_state.usuarios[st.session_state.usuario_logado]["progresso"][chave]
                salvar()
                st.rerun()

        # ===== RESUMO DE FEITO E NÃO FEITO =====
        st.divider()
        col_feito, col_falta = st.columns(2)
        with col_feito:
            st.write("✅ **FEITOS**")
            if feitos == 0: st.write("Nenhum ainda")
            for k in usuario["progresso"]:
                idx = int(k.split("_")[1])
                if idx < len(usuario["cronograma"]):
                    st.write(f"- {usuario['cronograma'][idx]}")
        with col_falta:
            st.write("⏳ **FALTA FAZER**")
            faltam = 0
            for i, t in enumerate(usuario["cronograma"]):
                if f"tarefa_{i}" not in usuario["progresso"]:
                    st.write(f"- {t}")
                    faltam += 1
            if faltam == 0: st.write("Tudo feito! 🎉")

        if st.button("🔄 Refazer plano (zera progresso)"):
            st.session_state.usuarios[st.session_state.usuario_logado]["perfil"] = None
            st.session_state.usuarios[st.session_state.usuario_logado]["cronograma"] = []
            st.session_state.usuarios[st.session_state.usuario_logado]["progresso"] = {}
            st.session_state.usuarios[st.session_state.usuario_logado]["streak"] = 0
            salvar()
            st.rerun()

    if st.button("Sair"):
        st.session_state.logado = False
        st.rerun()
