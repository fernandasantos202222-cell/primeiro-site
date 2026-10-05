import streamlit as st
import json, os, random
from datetime import date, datetime, timedelta

ARQUIVO = "banco_usuarios.json"

AVATARES_ANIME = {
    "Naruto 🍥": "🍥", "Goku 🐉": "🐉", "Luffy 👒": "👒",
    "Pikachu ⚡": "⚡", "Sasuke 🔥": "🔥", "Tanjiro 🌊": "🌊",
    "Nezuko 🎀": "🎀", "Gon 🎣": "🎣", "Hinata 🏐": "🏐", "Sailor Moon 🌙": "🌙"
}

FRASES = ["🚀 Hoje é 1% melhor!", "💪 Foco total!", "📚 Bora estudar!"]

def resumo_ia(materia, assunto):
    """Gera resumo automático da IA - sem precisar de API"""
    if not assunto:
        return "Cadastre um assunto para gerar resumo"
    return f"""
**📘 RESUMO IA - {materia}: {assunto}**

**O que é {assunto}?**
{assunto} é um conceito importante em {materia}. Serve para resolver problemas do dia a dia e da prova.

**Pontos principais:**
1. **Definição:** {assunto} é a base para entender o próximo conteúdo
2. **Como usar:** Aplica a fórmula/regra principal em 3 passos
3. **Exemplo prático:** Se cair na prova, vai pedir para calcular {assunto} com números

**Como estudar hoje (30 min):**
- 10 min: lê esse resumo
- 10 min: vê vídeo abaixo
- 10 min: faz 2 exercícios

**Dica de ouro:** Explica pra alguém o que aprendeu. Se conseguir explicar, aprendeu!
"""

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
    u = st.session_state.usuarios[uid]
    u.setdefault("nome", uid)
    u.setdefault("avatar", "🍥")
    u.setdefault("areas", {"Estudos": {"objetivo": "", "materias": {}}})
    if not isinstance(u["areas"], dict):
        u["areas"] = {"Estudos": {"objetivo": "", "materias": {}}}
    if "Estudos" not in u["areas"] or not isinstance(u["areas"]["Estudos"], dict):
        u["areas"]["Estudos"] = {"objetivo": "", "materias": {}}
    est = u["areas"]["Estudos"]
    if not isinstance(est.get("materias"), dict):
        est["materias"] = {}
    # GERAL - por fora
    u.setdefault("dias_estudo_geral", ["Segunda", "Quarta", "Sexta"])
    u.setdefault("horas_dia_geral", 2)
    u.setdefault("cronograma", [])
    u.setdefault("progresso", {})
    u.setdefault("tempo_total_mes", 0)
    u.setdefault("frase_dia", random.choice(FRASES))
    u.setdefault("notas_historico", {}) # {materia: [{mes, nota, data}]}
    u.setdefault("estudo_atual", {"materia": None, "assunto": ""})
    # conserta materias antigas
    for mat, dados in est["materias"].items():
        if isinstance(dados, dict):
            dados.setdefault("data_prova", date.today().isoformat())
            dados.setdefault("nota_prova", 0.0)
            dados.setdefault("assunto_dia", "")

for uid in list(st.session_state.usuarios.keys()):
    garantir(uid)

st.set_page_config(page_title="EvoluiAI", layout="centered")

def safe_progress(feitos, total):
    if total <= 0:
        total = 1
    return max(0.0, min(1.0, feitos/total))

if not st.session_state.logado:
    st.title("🚀 EvoluiAI")
    t1, t2, t3 = st.tabs(["Entrar", "Cadastrar", "🔑 Esqueci senha"])

    with t1:
        u = st.text_input("Usuário", key="login_user")
        s = st.text_input("Senha", type="password", key="login_pass")
        if st.button("Entrar", use_container_width=True):
            if u in st.session_state.usuarios and st.session_state.usuarios[u]["senha"] == s:
                garantir(u)
                salvar()
                st.session_state.logado = True
                st.session_state.usuario_logado = u
                st.rerun()
            else:
                st.error("Usuário ou senha errado")

    with t2:
        nome = st.text_input("Seu nome", key="cad_nome")
        user = st.text_input("Usuário novo", key="cad_user")
        senha = st.text_input("Senha nova", type="password", key="cad_senha")
        avatar = st.selectbox("Escolha seu avatar anime", list(AVATARES_ANIME.keys()), key="cad_avatar")
        if st.button("Cadastrar", use_container_width=True):
            if not user:
                st.warning("Digite usuário")
            elif user in st.session_state.usuarios:
                st.warning("Usuário já existe")
            else:
                st.session_state.usuarios[user] = {
                    "nome": nome or user, "senha": senha or "123", "avatar": AVATARES_ANIME[avatar],
                    "areas": {"Estudos": {"objetivo": "", "materias": {}}},
                    "dias_estudo_geral": ["Segunda", "Quarta", "Sexta"], "horas_dia_geral": 2,
                    "cronograma": [], "progresso": {}, "tempo_total_mes": 0,
                    "frase_dia": random.choice(FRASES), "notas_historico": {},
                    "estudo_atual": {"materia": None, "assunto": ""}
                }
                salvar()
                st.success("Cadastrado! Vá em Entrar")

    with t3:
        st.write("**Trocar senha**")
        user_r = st.text_input("Seu usuário", key="rec_user")
        nova_senha = st.text_input("Nova senha", type="password", key="rec_senha")
        if st.button("Trocar senha", use_container_width=True):
            if user_r in st.session_state.usuarios:
                st.session_state.usuarios[user_r]["senha"] = nova_senha
                salvar()
                st.success("Senha trocada! Vá em Entrar")
            else:
                st.error("Usuário não encontrado")

else:
    USUARIOS = st.session_state.usuarios
    LOGADO = st.session_state.usuario_logado
    usuario = USUARIOS[LOGADO]
    garantir(LOGADO)

    with st.sidebar:
        st.write(f"# {usuario.get('avatar','🍥')}")
        st.write(f"**{usuario['nome']}**")
        st.caption(f"*{usuario.get('frase_dia')}*")
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
        st.title(f"{usuario.get('avatar','🍥')} Olá, {usuario['nome'].split()[0]}!")

        # TEMPO MÉDIO MÊS
        dias_no_mes = date.today().day
        media = usuario.get("tempo_total_mes", 0) / dias_no_mes if dias_no_mes else 0

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Tempo total mês", f"{usuario.get('tempo_total_mes',0)} min")
        with col2:
            st.metric("Média por dia", f"{media:.0f} min")
        with col3:
            st.metric("Matérias", len(usuario["areas"]["Estudos"]["materias"]))

        # GERAL
        with st.container(border=True):
            st.write(f"**📅 Seu plano geral:** {', '.join(usuario.get('dias_estudo_geral',[]))} | {usuario.get('horas_dia_geral',2)}h por dia")

        st.subheader("Seus cartões")
        hoje = date.today()
        inicio_semana = hoje - timedelta(days=hoje.weekday())
        dia_nome = ["Segunda", "Terça", "Quarta", "Quinta", "Sexta", "Sábado", "Domingo"][hoje.weekday()]

        feitos_semana = sum(1 for v in usuario["progresso"].values() if "data" in v and date.fromisoformat(v["data"]) >= inicio_semana)
        total_semana = len(usuario.get("dias_estudo_geral", []))
        prog = safe_progress(feitos_semana, total_semana)
        st.progress(prog, text=f"Semana: {feitos_semana}/{total_semana} - Hoje {dia_nome} é {feitos_semana+1}/{total_semana}")

        for mat, dados in usuario["areas"]["Estudos"]["materias"].items():
            with st.container(border=True):
                st.write(f"### {dados.get('avatar','📚')} {mat}")
                st.write(f"**Prova:** {dados.get('data_prova','')} | **Nota:** {dados.get('nota_prova',0)}")
                st.write(f"**Assunto atual:** {dados.get('assunto_dia','')}")

    elif st.session_state.pagina == "Config":
        st.header("⚙️ Configuração")

        st.subheader("👤 Foto de perfil - Avatar anime")
        avatar_sel = st.selectbox("Escolha personagem", list(AVATARES_ANIME.keys()), key="config_avatar")
        if st.button("Salvar avatar"):
            USUARIOS[LOGADO]["avatar"] = AVATARES_ANIME[avatar_sel]
            salvar()
            st.success(f"Avatar trocado para {avatar_sel}!")

        st.divider()
        st.subheader("📅 Configuração GERAL - Dias e horas (por fora)")
        st.caption("Isso vale para todas as matérias")
        dias_op = ["Segunda", "Terça", "Quarta", "Quinta", "Sexta", "Sábado", "Domingo"]
        dias_geral = st.multiselect("Quantos dias na semana você estuda?", dias_op, default=usuario.get("dias_estudo_geral", ["Segunda", "Quarta", "Sexta"]), key="dias_geral")
        horas_geral = st.number_input("Quantas horas por dia (geral)?", 1, 8, usuario.get("horas_dia_geral", 2), key="horas_geral")

        if st.button("Salvar config geral", use_container_width=True):
            USUARIOS[LOGADO]["dias_estudo_geral"] = dias_geral
            USUARIOS[LOGADO]["horas_dia_geral"] = horas_geral
            salvar()
            st.success(f"Salvo! {len(dias_geral)} dias: {', '.join(dias_geral)}, {horas_geral}h/dia")

    else:
        st.header("🎓 Acadêmico")
        tab_materias, tab_estudo, tab_materiais, tab_resumo = st.tabs(["📚 Minhas Matérias", "✏️ Estudo", "📖 Materiais IA", "📈 Resumo & Evolução"])

        with tab_materias:
            st.subheader("📚 Cadastrar matérias da escola/faculdade/curso")
            with st.container(border=True):
                nome_mat = st.text_input("Nome da matéria *", placeholder="Ex: Matemática, Português", key="nome_mat_add")
                c1, c2 = st.columns(2)
                with c1:
                    data_prova = st.date_input("Data da prova", value=date.today()+timedelta(days=7), key="data_prova_add")
                with c2:
                    nota_prova = st.number_input("Nota da prova", 0.0, 10.0, 0.0, key="nota_prova_add")

                if st.button("Adicionar matéria", type="primary", use_container_width=True, key="btn_add_mat"):
                    if not nome_mat:
                        st.warning("Digite o nome da matéria")
                    else:
                        USUARIOS[LOGADO]["areas"]["Estudos"]["materias"][nome_mat] = {
                            "data_prova": data_prova.isoformat(),
                            "nota_prova": nota_prova,
                            "assunto_dia": "",
                            "semestre_passado": 6.0,
                            "semestre_atual": nota_prova,
                            "meta_nota": 10.0
                        }
                        # guarda no histórico
                        if nome_mat not in USUARIOS[LOGADO]["notas_historico"]:
                            USUARIOS[LOGADO]["notas_historico"][nome_mat] = []
                        USUARIOS[LOGADO]["notas_historico"][nome_mat].append({
                            "mes": date.today().strftime("%m/%Y"),
                            "nota": nota_prova,
                            "data": date.today().isoformat()
                        })
                        salvar()
                        st.success(f"{nome_mat} adicionada!")
                        st.rerun()

            st.divider()
            st.subheader("Matérias cadastradas")
            for mat, dados in list(usuario["areas"]["Estudos"]["materias"].items()):
                with st.container(border=True):
                    st.write(f"**{mat}**")
                    st.write(f"📅 Prova: {dados.get('data_prova','')} | 🎯 Nota: {dados.get('nota_prova',0)}")
                    if st.button("🗑️ Deletar", key=f"del_{mat}"):
                        del USUARIOS[LOGADO]["areas"]["Estudos"]["materias"][mat]
                        salvar()
                        st.rerun()

        with tab_estudo:
            st.subheader("✏️ O que estou estudando agora?")
            materias = list(usuario["areas"]["Estudos"]["materias"].keys())
            if not materias:
                st.info("Cadastre matérias em 📚 Minhas Matérias primeiro")
            else:
                # SELECIONAR DISCIPLINA CADASTRADA
                mat_sel = st.selectbox("Selecione a disciplina que você cadastrou", materias, key="estudo_mat_sel")
                assunto = st.text_input("Qual assunto/disciplina está vendo agora?", placeholder="Ex: Bhaskara - Delta negativo", value=usuario["estudo_atual"].get("assunto",""), key="estudo_assunto")

                if st.button("Salvar estudo atual", use_container_width=True):
                    USUARIOS[LOGADO]["estudo_atual"] = {"materia": mat_sel, "assunto": assunto}
                    USUARIOS[LOGADO]["areas"]["Estudos"]["materias"][mat_sel]["assunto_dia"] = assunto
                    salvar()
                    st.success(f"Estudando {mat_sel}: {assunto}")

                st.divider()
                if st.session_state.timer_inicio:
                    tempo = datetime.now() - st.session_state.timer_inicio
                    with st.container(border=True):
                        st.subheader(f"⏱️ ESTUDANDO: {st.session_state.materia_em_estudo}")
                        st.title(f"{str(tempo).split('.')[0]}")

                if st.session_state.timer_inicio is None:
                    if st.button(f"▶️ Começar a estudar {mat_sel}", type="primary", use_container_width=True, key=f"comecar_{mat_sel}"):
                        st.session_state.timer_inicio = datetime.now()
                        st.session_state.materia_em_estudo = mat_sel
                        st.rerun()
                else:
                    res = st.text_area("O que aprendeu hoje?", key="resumo_estudo")
                    if st.button("⏹️ Parar e salvar", type="primary", use_container_width=True):
                        if res.strip():
                            tempo = datetime.now() - st.session_state.timer_inicio
                            tm = int(tempo.total_seconds()/60) if tempo.total_seconds()>60 else 1
                            USUARIOS[LOGADO]["progresso"][f"tarefa_{len(usuario['progresso'])}"] = {
                                "feito": True, "tempo_min": tm, "resumo": res, "data": date.today().isoformat(), "materia": mat_sel
                            }
                            USUARIOS[LOGADO]["tempo_total_mes"] += tm
                            st.session_state.timer_inicio = None
                            st.session_state.materia_em_estudo = None
                            salvar()
                            st.balloons()
                            st.success(f"Salvo! +{tm} min")
                            st.rerun()

        with tab_materiais:
            st.subheader("📖 Materiais que a IA disponibiliza")
            materias = list(usuario["areas"]["Estudos"]["materias"].keys())
            if not materias:
                st.info("Cadastre matérias primeiro")
            else:
                mat_m = st.selectbox("Selecione a disciplina", materias, key="mat_materiais")
                dados_m = usuario["areas"]["Estudos"]["materias"][mat_m]
                assunto_m = dados_m.get("assunto_dia", "") or USUARIOS[LOGADO]["estudo_atual"].get("assunto","")

                if not assunto_m:
                    st.warning(f"Vá em ✏️ Estudo e coloque o assunto de {mat_m}")
                else:
                    st.write(f"**Matéria:** {mat_m} | **Assunto:** {assunto_m}")

                    # RESUMO IA
                    with st.container(border=True):
                        st.write(resumo_ia(mat_m, assunto_m))

                    # YOUTUBE E EBOOK GRÁTIS
                    q = f"{mat_m} {assunto_m}".replace(" ", "+")
                    with st.container(border=True):
                        st.write("**🎥 Vídeos YouTube:**")
                        st.link_button(f"Ver vídeos de {assunto_m}", f"https://www.youtube.com/results?search_query={q}", use_container_width=True)

                    with st.container(border=True):
                        st.write("**📚 Ebook grátis:**")
                        st.link_button(f"Buscar ebook grátis de {assunto_m}", f"https://www.google.com/search?q={q}+ebook+gratis+pdf", use_container_width=True)

                    with st.container(border=True):
                        st.write("**📝 Exercícios:**")
                        st.link_button(f"Exercícios de {assunto_m}", f"https://www.google.com/search?q={q}+exercicios+com+resposta", use_container_width=True)

        with tab_resumo:
            st.subheader("📈 Resumo & Evolução")

            # TEMPO MÉDIO
            with st.container(border=True):
                st.write("**⏱️ Tempo de estudo**")
                total = usuario.get("tempo_total_mes", 0)
                media = total / date.today().day if date.today().day else 0
                c1, c2 = st.columns(2)
                with c1:
                    st.metric("Total no mês", f"{total} min")
                    st.metric("Média por dia", f"{media:.1f} min")
                with c2:
                    st.metric("Horas totais", f"{total/60:.1f} h")
                    st.write(f"Meta: {usuario.get('horas_dia_geral',2)*60} min/dia")

            st.divider()
            st.write("**📊 Evolução de notas por matéria**")
            materias = list(usuario["areas"]["Estudos"]["materias"].keys())
            if not materias:
                st.info("Cadastre matérias")
            else:
                mat_evo = st.selectbox("Selecione disciplina para ver evolução", materias, key="mat_evolucao")

                # Adicionar nota mensal
                with st.container(border=True):
                    st.write(f"Adicionar nota de {mat_evo}")
                    nova_nota = st.number_input("Nota", 0.0, 10.0, 7.0, key="nova_nota_evo")
                    mes_nota = st.text_input("Mês/Ano", value=date.today().strftime("%m/%Y"), key="mes_nota")
                    if st.button("Salvar nota", key="btn_salvar_nota"):
                        if mat_evo not in USUARIOS[LOGADO]["notas_historico"]:
                            USUARIOS[LOGADO]["notas_historico"][mat_evo] = []
                        USUARIOS[LOGADO]["notas_historico"][mat_evo].append({
                            "mes": mes_nota, "nota": nova_nota, "data": date.today().isoformat()
                        })
                        USUARIOS[LOGADO]["areas"]["Estudos"]["materias"][mat_evo]["nota_prova"] = nova_nota
                        salvar()
                        st.success("Nota salva!")
                        st.rerun()

                # MOSTRAR EVOLUÇÃO
                historico = usuario.get("notas_historico", {}).get(mat_evo, [])
                if historico:
                    st.write(f"**Evolução de {mat_evo}:**")
                    for h in historico[-6:]: # últimos 6
                        st.write(f"📅 {h['mes']}: **{h['nota']}**")

                    # Gráfico simples com barras de texto
                    st.write("**Gráfico de evolução:**")
                    for h in historico:
                        barras = "█" * int(h['nota'])
                        st.write(f"{h['mes']}: {barras} {h['nota']}")

                    # Evolução por mês
                    if len(historico) >= 2:
                        diff = historico[-1]['nota'] - historico[0]['nota']
                        st.metric("Evolução total", f"{historico[-1]['nota']}", delta=f"{diff:+.1f}")
                else:
                    st.info("Nenhuma nota ainda. Adicione acima")
