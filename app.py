import streamlit as st
import json, os, random
from datetime import date, datetime, timedelta

ARQUIVO = "banco_usuarios.json"
FRASES = ["🚀 Hoje é um ótimo dia para evoluir 1%!", "💪 Consistência vence talento!", "📚 Foco no assunto do dia!"]

def explicacao_real(materia, assunto, duvida):
    d = duvida.lower()
    if "multiplic" in d:
        return f"### O que é multiplicação?\n\nÉ soma repetida.\n\n**3 x 4 = 4+4+4 = 12**\n\n**Exemplo real:** 3 caixas com 4 lápis = 12 lápis\n\n**Erro comum:** Confundir com 3+4=7. Na multiplicação 3x4=12\n\n**Como praticar:** Tabuada do 3, 10 min hoje."
    if "delta" in d:
        return f"### Delta negativo\n\nΔ = b² - 4ac. Se deu -16, **sem raiz real**.\n\nEx: x²+2x+5=0 → Δ=-16 → Resposta: sem raiz real.\n\nNão tenta fazer √-16."
    return f"### {assunto}\n\n**Pergunta: {duvida}**\n\nExplicação simples de {assunto}:\n1. Conceito base\n2. Exemplo prático\n3. Como cai na prova\n\nMe fala o que ficou confuso!"

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
    u.setdefault("nome", "")
    u.setdefault("areas", {"Estudos": {"objetivo": "", "materias": {}}})
    u["areas"]["Estudos"].setdefault("materias", {})
    u.setdefault("cronograma", [])
    u.setdefault("progresso", {})
    u.setdefault("tempo_total_mes", 0)
    u.setdefault("chat_duvidas", [])
    u.setdefault("streak", 0)
    u.setdefault("frase_dia", random.choice(FRASES))

if "usuarios" in st.session_state:
    for uid in st.session_state.usuarios:
        garantir(uid)

st.set_page_config(page_title="EvoluiAI", layout="centered")

if not st.session_state.logado:
    st.title("🚀 EvoluiAI")
    t1, t2 = st.tabs(["Entrar", "Cadastrar"])
    with t1:
        u = st.text_input("Usuário", key="login_user")
        s = st.text_input("Senha", type="password", key="login_pass")
        if st.button("Entrar"):
            if u in st.session_state.usuarios and st.session_state.usuarios[u]["senha"] == s:
                st.session_state.logado = True
                st.session_state.usuario_logado = u
                st.rerun()
    with t2:
        nome = st.text_input("Nome", key="cad_nome")
        user = st.text_input("Usuário novo", key="cad_user")
        senha = st.text_input("Senha nova", type="password", key="cad_senha")
        if st.button("Cadastrar"):
            st.session_state.usuarios[user] = {"nome": nome, "senha": senha, "areas": {"Estudos": {"objetivo": "", "materias": {}}}, "cronograma": [], "progresso": {}, "tempo_total_mes": 0, "chat_duvidas": [], "streak": 0, "frase_dia": random.choice(FRASES)}
            salvar()
            st.success("Cadastrado!")
else:
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
        if st.session_state.timer_inicio:
            tempo = datetime.now() - st.session_state.timer_inicio
            with st.container(border=True):
                st.write(f"⏱️ {st.session_state.materia_em_estudo} - {str(tempo).split('.')[0]}")

        # RESUMO RÁPIDO DOS CARTÕES DE ESTUDO
        st.subheader("Seus cartões - Estudo")
        for mat, dados in usuario["areas"]["Estudos"]["materias"].items():
            with st.container(border=True):
                st.write(f"**{mat}** - {dados.get('assunto_dia','')}")
                st.caption(f"{dados.get('objetivo','')} | {len(dados.get('dias_estudo',[]))} dias/semana")

    elif st.session_state.pagina == "Config":
        st.header("⚙️ Configuração")
        obj = st.text_input("Objetivo geral Estudos", value=usuario["areas"]["Estudos"].get("objetivo",""), key="obj_geral")
        if st.button("Salvar", key="save_config"):
            USUARIOS[LOGADO]["areas"]["Estudos"]["objetivo"] = obj
            salvar()
            st.success("Salvo!")

    else:
        st.header("🎓 Acadêmico")
        # AQUI SEPARA POR ÁREA - TUDO DE ESTUDO FICA NA ABA ESTUDO
        tab_estudo, tab_estudar, tab_chat, tab_resumo, tab_futuro = st.tabs(["📚 Estudo", "✏️ Estudar", "💬 Dúvidas", "📈 Resumo", "➕ Outras Áreas"])

        with tab_estudo:
            st.subheader("📚 Área: Estudo")
            st.caption("Tudo de estudo fica aqui. Depois você cria Trabalho, Pessoal etc na aba Outras Áreas")

            # --- CADASTRO DENTRO DA ABA ESTUDO ---
            with st.container(border=True):
                st.write("**Cadastrar nova matéria**")
                nome_mat = st.text_input("Nome da disciplina *", placeholder="Ex: Matemática", key="nome_mat_add")
                objetivo_mat = st.text_input("Objetivo dessa matéria", placeholder="Ex: Tirar 10 na prova final", key="obj_mat_add")
                area_mat = st.text_input("Área", value="Estudos", disabled=True, key="area_mat_add")

                c1, c2 = st.columns(2)
                with c1:
                    ass_geral = st.text_input("Assunto geral", key="ass_geral_add")
                with c2:
                    ass_dia = st.text_input("Assunto do dia", key="ass_dia_add")

                st.write("**📅 Quantos dias na semana vai estudar essa matéria?**")
                dias_op = ["Segunda", "Terça", "Quarta", "Quinta", "Sexta", "Sábado", "Domingo"]
                dias_sel = st.multiselect("Escolha os dias", dias_op, default=["Segunda", "Quinta"], key="dias_mat_add")
                horas_sel = st.number_input("Quantas horas por dia nessa matéria?", 1, 8, 2, key="horas_mat_add")

                dp = st.date_input("Dia da prova", value=date.today()+timedelta(days=7), key="prova_add")

                if st.button("Adicionar em Estudo", type="primary", use_container_width=True, key="btn_add_mat"):
                    if not nome_mat:
                        st.warning("Digite o nome")
                    elif not dias_sel:
                        st.warning("Escolha os dias")
                    else:
                        USUARIOS[LOGADO]["areas"]["Estudos"]["materias"][nome_mat] = {
                            "assunto_atual": ass_geral,
                            "assunto_dia": ass_dia or ass_geral,
                            "objetivo": objetivo_mat or f"Tirar 10 em {nome_mat}",
                            "area": "Estudos",
                            "dias_estudo": dias_sel,
                            "horas_dia": horas_sel,
                            "dia_prova": dp.isoformat(),
                            "semestre_passado": 6.0,
                            "semestre_atual": 7.0,
                            "meta_nota": 10.0,
                        }
                        for i in range(len(dias_sel)):
                            USUARIOS[LOGADO]["cronograma"].append({"area": "Estudos", "materia": nome_mat, "dia": (date.today()+timedelta(days=i)).strftime('%d/%m'), "texto": f"{nome_mat}: {ass_dia or ass_geral}"})
                        salvar()
                        st.success(f"{nome_mat} salva em Estudo! {len(dias_sel)} dias, {horas_sel}h/dia")
                        st.rerun()

            st.divider()
            st.subheader("Seus cartões - Área Estudo")

            hoje = date.today()
            inicio_semana = hoje - timedelta(days=hoje.weekday())
            dia_nome_hoje = ["Segunda", "Terça", "Quarta", "Quinta", "Sexta", "Sábado", "Domingo"][hoje.weekday()]

            if not usuario["areas"]["Estudos"]["materias"]:
                st.info("Nenhuma matéria em Estudo ainda")

            for mat, dados in list(usuario["areas"]["Estudos"]["materias"].items()):
                dias_mat = dados.get("dias_estudo", [])
                horas_mat = dados.get("horas_dia", 2)
                objetivo_mat = dados.get("objetivo", "")
                area_mat = dados.get("area", "Estudos")

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
                    st.write(f"**🎯 Objetivo:** {objetivo_mat}")
                    st.write(f"**📂 Área:** {area_mat}")
                    st.write(f"**📅 Dias de estudo:** {', '.join(dias_mat)} ({total_semana} dias na semana)")
                    st.write(f"**⏰ Horas por dia:** {horas_mat}h")
                    st.write(f"**📌 Assunto do dia:** {dados.get('assunto_dia','')}")
                    st.write(f"**📆 Prova:** {dados.get('dia_prova','')}")

                    # PROGRESSO 1/6 QUE VOCÊ PEDIU
                    st.divider()
                    st.write(f"**Progresso dessa semana:**")
                    st.progress(feitos_semana / total_semana if total_semana else 0, text=f"{feitos_semana}/{total_semana} - Hoje é {dia_nome_hoje}")

                    # Explica o 1/6
                    if dia_nome_hoje in dias_mat:
                        st.info(f"Hoje é dia de {mat}! Dia {feitos_semana+1}/{total_semana} da semana. Exemplo: se hoje é segunda e você estuda Seg e Qui, hoje é 1/2")
                    else:
                        st.caption(f"Hoje não tem {mat}. Próximos dias: {', '.join(dias_mat)}")

                    if st.button("🗑️ Deletar", key=f"del_card_{mat}"):
                        del USUARIOS[LOGADO]["areas"]["Estudos"]["materias"][mat]
                        USUARIOS[LOGADO]["cronograma"] = [t for t in USUARIOS[LOGADO]["cronograma"] if t.get("materia")!=mat]
                        salvar()
                        st.rerun()

        with tab_estudar:
            disp = usuario["areas"]["Estudos"]["materias"]
            if not disp:
                st.info("Cadastre em 📚 Estudo primeiro")
            else:
                if st.session_state.timer_inicio:
                    tempo = datetime.now() - st.session_state.timer_inicio
                    with st.container(border=True):
                        st.subheader(f"⏱️ ESTUDANDO: {st.session_state.materia_em_estudo}")
                        st.title(f"{str(tempo).split('.')[0]}")
                mat_sel = st.selectbox("Qual matéria de Estudo?", list(disp.keys()), key="mat_estudar")
                st.caption(f"Objetivo: {disp[mat_sel].get('objetivo','')} | {disp[mat_sel].get('horas_dia',2)}h/dia | Dias: {', '.join(disp[mat_sel].get('dias_estudo',[]))}")
                ass_d = st.text_input("Assunto do dia", value=disp[mat_sel].get("assunto_dia",""), key=f"ass_dia_estudar_{mat_sel}")
                if st.button("Atualizar assunto", key="btn_att_ass"):
                    USUARIOS[LOGADO]["areas"]["Estudos"]["materias"][mat_sel]["assunto_dia"] = ass_d
                    salvar()
                    st.success("Ok!")
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
            if not disp:
                st.info("Sem matérias")
            else:
                mat_r = st.selectbox("Escolha a matéria de Estudo", list(disp.keys()), key="mat_resumo")
                dados = disp[mat_r]
                with st.container(border=True):
                    st.write(f"### {mat_r}")
                    st.write(f"Objetivo: {dados.get('objetivo','')}")
                    st.write(f"Área: {dados.get('area','')} | {', '.join(dados.get('dias_estudo',[]))} | {dados.get('horas_dia',2)}h/dia")

        with tab_futuro:
            st.subheader("➕ Outras Áreas (futuro)")
            st.info("Aqui depois você cria outras áreas como Trabalho, Saúde, etc. Por enquanto tudo de estudo fica em 📚 Estudo")
            st.write("Exemplo futuro: Área Trabalho com cartões de tarefas de trabalho, cada uma com seus dias e horas também")
