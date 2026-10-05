import streamlit as st
import json, os, random
from datetime import date, datetime, timedelta

ARQUIVO = "banco_usuarios.json"
FRASES = ["🚀 Hoje é um ótimo dia para evoluir 1%!", "💪 Consistência vence talento!", "📚 Foco no assunto do dia!"]

def explicacao_real(materia, assunto, duvida):
    d = duvida.lower()
    if "multiplic" in d:
        return f"### O que é multiplicação?\n\n**3 x 4 = 4+4+4 = 12**\n\nEx: 3 caixas com 4 lápis = 12"
    if "delta" in d:
        return f"### Delta negativo\n\nΔ = b² - 4ac. Se deu -16, **sem raiz real**."
    return f"### {assunto}\n\nPergunta: {duvida}\n\nExplicação simples de {assunto}."

def carregar():
    if os.path.exists(ARQUIVO):
        try:
            with open(ARQUIVO, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return {}
    return {}

def salvar():
    with open(ARQUIVO, "w", encoding="utf-8") as f:
        json.dump(st.session_state.usuarios, f, indent=4, ensure_ascii=False)

if "usuarios" not in st.session_state:
    st.session_state.usuarios = carregar()
if "logado" not in st.session_state:
    st.session_state.logado = False
    st.session_state.usuario_logado = ""
    st.session_state.pagina = "Início"
    st.session_state.timer_inicio = None
    st.session_state.materia_em_estudo = None

def garantir(uid):
    try:
        u = st.session_state.usuarios[uid]
        if not isinstance(u.get("areas"), dict):
            u["areas"] = {"Estudos": {"objetivo": "", "materias": {}}}
        if "Estudos" not in u["areas"] or not isinstance(u["areas"]["Estudos"], dict):
            u["areas"]["Estudos"] = {"objetivo": "", "materias": {}}
        est = u["areas"]["Estudos"]
        if not isinstance(est.get("materias"), dict):
            est["materias"] = {}
        est.setdefault("objetivo", "")
        u.setdefault("cronograma", [])
        u.setdefault("progresso", {})
        u.setdefault("tempo_total_mes", 0)
        u.setdefault("chat_duvidas", [])
        u.setdefault("streak", 0)
        u.setdefault("frase_dia", random.choice(FRASES))
        # conserta materias antigas sem dias_estudo
        for m in est["materias"].values():
            if isinstance(m, dict):
                m.setdefault("dias_estudo", ["Segunda", "Quinta"])
                m.setdefault("horas_dia", 2)
                m.setdefault("objetivo", "")
                m.setdefault("area", "Estudos")
    except Exception:
        st.session_state.usuarios[uid] = {
            "nome": uid, "senha": "123",
            "areas": {"Estudos": {"objetivo": "", "materias": {}}},
            "cronograma": [], "progresso": {}, "tempo_total_mes": 0,
            "chat_duvidas": [], "streak": 0, "frase_dia": random.choice(FRASES)
        }

for uid in list(st.session_state.usuarios.keys()):
    garantir(uid)

st.set_page_config(page_title="EvoluiAI", layout="centered")

def safe_progress(feitos, total):
    """Evita o erro da sua foto: divisão por zero e valor >1"""
    if total <= 0:
        total = 1
    val = feitos / total
    return max(0.0, min(1.0, val))

if not st.session_state.logado:
    st.title("🚀 EvoluiAI")
    t1, t2 = st.tabs(["Entrar", "Cadastrar"])
    with t1:
        u = st.text_input("Usuário", key="login_user")
        s = st.text_input("Senha", type="password", key="login_pass")
        if st.button("Entrar"):
            if u in st.session_state.usuarios and st.session_state.usuarios[u]["senha"] == s:
                garantir(u)
                st.session_state.logado = True
                st.session_state.usuario_logado = u
                st.rerun()
    with t2:
        nome = st.text_input("Nome", key="cad_nome")
        user = st.text_input("Usuário novo", key="cad_user")
        senha = st.text_input("Senha nova", type="password", key="cad_senha")
        if st.button("Cadastrar"):
            st.session_state.usuarios[user] = {"nome": nome or user, "senha": senha or "123", "areas": {"Estudos": {"objetivo": "", "materias": {}}}, "cronograma": [], "progresso": {}, "tempo_total_mes": 0, "chat_duvidas": [], "streak": 0, "frase_dia": random.choice(FRASES)}
            salvar()
            st.success("Cadastrado!")
else:
    garantir(st.session_state.usuario_logado)
    USUARIOS = st.session_state.usuarios
    LOGADO = st.session_state.usuario_logado
    usuario = USUARIOS[LOGADO]

    with st.sidebar:
        st.write(f"**{usuario['nome']}**")
        if st.button("🏠 Início", use_container_width=True, key="btn_inicio"):
            st.session_state.pagina = "Início"
            st.rerun()
        if st.button("🎓 Acadêmico", use_container_width=True, key="btn_acad"):
            st.session_state.pagina = "Acadêmico"
            st.rerun()
        if st.button("⚙️ Config", use_container_width=True, key="btn_config"):
            st.session_state.pagina = "Config"
            st.rerun()
        if st.button("Sair", key="btn_sair"):
            st.session_state.logado = False
            st.rerun()

    if st.session_state.pagina == "Início":
        st.title(f"Olá, {usuario['nome'].split()[0]}! 👋")
        st.caption(f"*{usuario.get('frase_dia')}*")
        st.subheader("Seus cartões - Estudo")
        for mat, dados in usuario["areas"]["Estudos"]["materias"].items():
            with st.container(border=True):
                st.write(f"**{mat}** - {dados.get('assunto_dia','')}")
                st.caption(f"{dados.get('objetivo','')} | {', '.join(dados.get('dias_estudo',[]))} | {dados.get('horas_dia',2)}h")

    elif st.session_state.pagina == "Config":
        st.header("⚙️ Configuração")
        obj = st.text_input("Objetivo geral Estudos", value=usuario["areas"]["Estudos"].get("objetivo",""), key="obj_geral")
        if st.button("Salvar", key="save_config"):
            USUARIOS[LOGADO]["areas"]["Estudos"]["objetivo"] = obj
            salvar()
            st.success("Salvo!")

    else:
        st.header("🎓 Acadêmico")
        tab_estudo, tab_estudar, tab_chat, tab_resumo, tab_futuro = st.tabs(["📚 Estudo", "✏️ Estudar", "💬 Dúvidas", "📈 Resumo", "➕ Outras Áreas"])

        with tab_estudo:
            st.subheader("📚 Área: Estudo")

            with st.container(border=True):
                st.write("**Cadastrar nova matéria (com dias e horas)**")
                nome_mat = st.text_input("Nome da disciplina *", key="nome_mat_add")
                objetivo_mat = st.text_input("Objetivo dessa matéria", key="obj_mat_add")
                c1, c2 = st.columns(2)
                with c1:
                    ass_geral = st.text_input("Assunto geral", key="ass_geral_add")
                with c2:
                    ass_dia = st.text_input("Assunto do dia", key="ass_dia_add")
                dias_op = ["Segunda", "Terça", "Quarta", "Quinta", "Sexta", "Sábado", "Domingo"]
                dias_sel = st.multiselect("Quantos dias na semana? Escolha os dias", dias_op, default=["Segunda", "Quinta"], key="dias_mat_add")
                horas_sel = st.number_input("Quantas horas por dia?", 1, 8, 2, key="horas_mat_add")
                dp = st.date_input("Dia da prova", value=date.today()+timedelta(days=7), key="prova_add")
                if st.button("Adicionar em Estudo", type="primary", use_container_width=True, key="btn_add_mat"):
                    if not nome_mat:
                        st.warning("Digite o nome")
                    elif not dias_sel:
                        st.warning("Escolha os dias - é obrigatório pra não dar erro 1/6")
                    else:
                        USUARIOS[LOGADO]["areas"]["Estudos"]["materias"][nome_mat] = {
                            "assunto_atual": ass_geral, "assunto_dia": ass_dia or ass_geral,
                            "objetivo": objetivo_mat or f"Tirar 10 em {nome_mat}",
                            "area": "Estudos", "dias_estudo": dias_sel, "horas_dia": horas_sel,
                            "dia_prova": dp.isoformat(), "semestre_passado": 6.0, "semestre_atual": 7.0, "meta_nota": 10.0,
                        }
                        for i in range(len(dias_sel)):
                            USUARIOS[LOGADO]["cronograma"].append({"area": "Estudos", "materia": nome_mat, "dia": (date.today()+timedelta(days=i)).strftime('%d/%m'), "texto": f"{nome_mat}: {ass_dia or ass_geral}"})
                        salvar()
                        st.success(f"{nome_mat} salva! {len(dias_sel)} dias, {horas_sel}h/dia")
                        st.rerun()

            st.divider()
            st.subheader("Seus cartões - Área Estudo")
            hoje = date.today()
            inicio_semana = hoje - timedelta(days=hoje.weekday())
            dia_nome_hoje = ["Segunda", "Terça", "Quarta", "Quinta", "Sexta", "Sábado", "Domingo"][hoje.weekday()]

            for mat, dados in list(usuario["areas"]["Estudos"]["materias"].items()):
                dias_mat = dados.get("dias_estudo", ["Segunda", "Quinta"])
                horas_mat = dados.get("horas_dia", 2)
                feitos_semana = 0
                for k, v in usuario["progresso"].items():
                    try:
                        idx = int(k.split("_")[1])
                        if usuario["cronograma"][idx].get("materia") == mat:
                            d = date.fromisoformat(v.get("data", ""))
                            if d >= inicio_semana:
                                feitos_semana += 1
                    except:
                        pass
                total_semana = len(dias_mat)

                with st.container(border=True):
                    st.write(f"### 📚 {mat}")
                    st.write(f"**🎯 Objetivo:** {dados.get('objetivo','')}")
                    st.write(f"**📂 Área:** {dados.get('area','')}")
                    st.write(f"**📅 Dias:** {', '.join(dias_mat)} ({total_semana} dias)")
                    st.write(f"**⏰ Horas/dia:** {horas_mat}h")
                    st.write(f"**📌 Assunto:** {dados.get('assunto_dia','')}")
                    st.divider()
                    # FIX DO ERRO DA SUA FOTO AQUI
                    prog_val = safe_progress(feitos_semana, total_semana)
                    st.progress(prog_val, text=f"{feitos_semana}/{total_semana} - Hoje {dia_nome_hoje}")
                    if dia_nome_hoje in dias_mat:
                        st.success(f"Hoje tem {mat}! Dia {feitos_semana+1}/{total_semana} - ex: 1/6 se estuda 6 dias e hoje é segunda")
                    if st.button("🗑️ Deletar", key=f"del_card_{mat}"):
                        del USUARIOS[LOGADO]["areas"]["Estudos"]["materias"][mat]
                        USUARIOS[LOGADO]["cronograma"] = [t for t in USUARIOS[LOGADO]["cronograma"] if t.get("materia")!=mat]
                        salvar()
                        st.rerun()

        with tab_estudar:
            disp = usuario["areas"]["Estudos"]["materias"]
            if not disp:
                st.info("Cadastre em 📚 Estudo")
            else:
                if st.session_state.timer_inicio:
                    tempo = datetime.now() - st.session_state.timer_inicio
                    with st.container(border=True):
                        st.subheader(f"⏱️ {st.session_state.materia_em_estudo}")
                        st.title(f"{str(tempo).split('.')[0]}")
                mat_sel = st.selectbox("Qual matéria?", list(disp.keys()), key="mat_estudar")
                st.caption(f"{disp[mat_sel].get('objetivo','')} | {disp[mat_sel].get('horas_dia',2)}h | {', '.join(disp[mat_sel].get('dias_estudo',[]))}")
                if st.session_state.timer_inicio is None:
                    if st.button(f"▶️ Começar {mat_sel}", type="primary", use_container_width=True, key=f"btn_comecar_{mat_sel}"):
                        st.session_state.timer_inicio = datetime.now()
                        st.session_state.materia_em_estudo = mat_sel
                        st.rerun()
                else:
                    res = st.text_area("O que aprendeu?", key=f"res_{mat_sel}")
                    if st.button("⏹️ Parar", type="primary", use_container_width=True, key="btn_parar"):
                        if res.strip():
                            tempo = datetime.now() - st.session_state.timer_inicio
                            tm = int(tempo.total_seconds()/60) if tempo.total_seconds()>60 else 1
                            for i,t in enumerate(USUARIOS[LOGADO]["cronograma"]):
                                if t.get("materia")==mat_sel and f"tarefa_{i}" not in USUARIOS[LOGADO]["progresso"]:
                                    USUARIOS[LOGADO]["progresso"][f"tarefa_{i}"] = {"feito": True, "tempo_min": tm, "resumo": res, "data": date.today().isoformat()}
                                    USUARIOS[LOGADO]["tempo_total_mes"] += tm
                                    break
                            st.session_state.timer_inicio = None
                            st.session_state.materia_em_estudo = None
                            salvar()
                            st.balloons()
                            st.rerun()

        with tab_chat:
            st.subheader("💬 Dúvidas - Estudo")
            disp = usuario["areas"]["Estudos"]["materias"]
            mat_c = st.selectbox("Matéria", list(disp.keys()) + ["Geral"], key="mat_chat")
            for chat in usuario.get("chat_duvidas", []):
                with st.chat_message(chat["role"]):
                    st.markdown(chat["content"])
            duvida = st.chat_input("Ex: o que é multiplicação")
            if duvida:
                USUARIOS[LOGADO]["chat_duvidas"].append({"role": "user", "content": f"[{mat_c}] {duvida}"})
                assunto = disp.get(mat_c, {}).get("assunto_dia", mat_c) if mat_c!= "Geral" else mat_c
                exp = explicacao_real(mat_c, assunto, duvida)
                q = f"{mat_c} {duvida}".replace(" ", "+")
                exp_final = f"{exp}\n\n---\n📚 Vídeo: https://www.youtube.com/results?search_query={q}"
                USUARIOS[LOGADO]["chat_duvidas"].append({"role": "assistant", "content": exp_final})
                salvar()
                st.rerun()

        with tab_resumo:
            st.subheader("📈 Resumo - Estudo")
            disp = usuario["areas"]["Estudos"]["materias"]
            if disp:
                mat_r = st.selectbox("Matéria", list(disp.keys()), key="mat_resumo")
                dados = disp[mat_r]
                with st.container(border=True):
                    st.write(f"### {mat_r}")
                    st.write(f"Objetivo: {dados.get('objetivo','')}")
                    st.write(f"Área: {dados.get('area','')} | {', '.join(dados.get('dias_estudo',[]))} | {dados.get('horas_dia',2)}h/dia")

        with tab_futuro:
            st.info("Aqui depois você cria Trabalho, Saúde etc")
