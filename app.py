import streamlit as st
import json, os
from datetime import date, datetime, timedelta

ARQUIVO = "banco_usuarios.json"

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
    if "Estudos" not in u["areas"]:
        u["areas"]["Estudos"] = {"objetivo": "", "materias": {}}
    u["areas"]["Estudos"].setdefault("materias", {})
    u.setdefault("cronograma", [])
    u.setdefault("progresso", {})
    u.setdefault("tempo_total_mes", 0)
    u.setdefault("chat_duvidas", [])
    u.setdefault("streak", 0)
    u.setdefault("foco_materia", None)
    # corrige conta antiga que era True
    novo = {}
    for k, v in u["progresso"].items():
        if isinstance(v, bool):
            novo[k] = {"feito": True, "tempo_min": 25, "resumo": "", "data": date.today().isoformat()}
        else:
            novo[k] = v
    u["progresso"] = novo

def explicacao_ia(materia, assunto_dia, duvida):
    d = duvida.lower()
    if "delta" in d or "bhaskara" in d:
        return f"""
**Você disse:** {duvida}

**Explicação de {materia} - {assunto_dia}:**
Delta = b² - 4ac. Se Δ < 0, não tem raiz real. Você errou porque tentou tirar raiz de número negativo.

Ex: x²+2x+5=0 → Δ = 4-20 = -16 → **Sem raiz real.**

Como acertar: Se Δ < 0, já responde "sem raízes reais".
"""
    return f"""
**Você disse:** {duvida}

**Explicação de {materia} - {assunto_dia}:**
{assunto_dia} funciona assim: conceito base é [explicado simples]. Erro comum é confundir o detalhe. Pra acertar, faça 3 exercícios hoje focado nisso.
"""

st.set_page_config(page_title="EvoluiAI", layout="centered")

# LOGIN
if not st.session_state.logado:
    st.title("🚀 EvoluiAI")
    t1, t2 = st.tabs(["Entrar", "Cadastrar"])
    with t1:
        u = st.text_input("Usuário", key="l1")
        s = st.text_input("Senha", type="password", key="l2")
        if st.button("Entrar"):
            if u in st.session_state.usuarios and st.session_state.usuarios[u]["senha"] == s:
                garantir(u)
                salvar()
                st.session_state.logado = True
                st.session_state.usuario_logado = u
                st.rerun()
            else:
                st.error("Usuário ou senha errado")
    with t2:
        nome = st.text_input("Seu nome", key="c1")
        user = st.text_input("Usuário novo", key="c5")
        senha = st.text_input("Senha nova", type="password", key="c6")
        if st.button("Cadastrar"):
            if not nome or not user or not senha:
                st.warning("Preencha tudo")
            else:
                st.session_state.usuarios[user] = {"nome": nome, "senha": senha, "areas": {"Estudos": {"objetivo": "", "materias": {}}}, "cronograma": [], "progresso": {}, "tempo_total_mes": 0, "chat_duvidas": [], "streak": 0, "foco_materia": None}
                salvar()
                st.success("Cadastrado! Faça login na aba Entrar")
else:
    garantir(st.session_state.usuario_logado)
    USUARIOS = st.session_state.usuarios
    LOGADO = st.session_state.usuario_logado
    usuario = USUARIOS[LOGADO]

    with st.sidebar:
        st.write(f"**{usuario['nome']}** 🔥 {usuario['streak']} dias")
        if usuario.get("foco_materia"):
            st.info(f"🎯 Foco: {usuario['foco_materia']}")
            if st.button("Sair do foco"):
                USUARIOS[LOGADO]["foco_materia"] = None
                salvar()
                st.rerun()
        if st.button("🏠 Início", use_container_width=True):
            st.session_state.pagina = "Início"
            st.rerun()
        if st.button("🎓 Acadêmico", use_container_width=True):
            st.session_state.pagina = "Acadêmico"
            st.rerun()
        if st.button("⚙️ Perfil", use_container_width=True):
            st.session_state.pagina = "Config"
            st.rerun()
        if st.button("Sair"):
            st.session_state.logado = False
            st.rerun()

    if st.session_state.pagina == "Início":
        st.title(f"Olá, {usuario['nome'].split()[0]}!")
        # Lembrete prova
        for mat, dados in usuario["areas"]["Estudos"]["materias"].items():
            try:
                dp = date.fromisoformat(dados.get("dia_prova", ""))
                dias = (dp - date.today()).days
                if 0 <= dias <= 7:
                    st.warning(f"⚠️ Prova de {mat} em {dias} dias ({dp.strftime('%d/%m')}) - {dados.get('assunto_dia','')}")
            except:
                pass
        if st.session_state.timer_inicio:
            tempo = datetime.now() - st.session_state.timer_inicio
            with st.container(border=True):
                st.write(f"⏱️ Estudando {st.session_state.materia_em_estudo} - {str(tempo).split('.')[0]}")

        st.subheader("Seus cartões")
        materias_mostrar = usuario["areas"]["Estudos"]["materias"]
        if usuario.get("foco_materia"):
            materias_mostrar = {usuario["foco_materia"]: materias_mostrar.get(usuario["foco_materia"], {})}

        for mat, dados in materias_mostrar.items():
            tarefas = [t for t in usuario["cronograma"] if t.get("materia") == mat]
            feitos = sum(1 for i, t in enumerate(usuario["cronograma"]) if t.get("materia") == mat and f"tarefa_{i}" in usuario["progresso"])
            with st.container(border=True):
                st.write(f"**{mat}** - 📌 Hoje: {dados.get('assunto_dia', dados.get('assunto_atual',''))}")
                st.progress(feitos / len(tarefas) if tarefas else 0, text=f"{feitos}/{len(tarefas)} dias")
                c1, c2 = st.columns(2)
                with c1:
                    if st.button(f"✏️ Editar {mat}", key=f"edit_ini_{mat}"):
                        st.session_state.pagina = "Acadêmico"
                        st.rerun()
                with c2:
                    if st.button(f"🗑️ Deletar {mat}", key=f"del_ini_{mat}"):
                        del USUARIOS[LOGADO]["areas"]["Estudos"]["materias"][mat]
                        USUARIOS[LOGADO]["cronograma"] = [t for t in USUARIOS[LOGADO]["cronograma"] if t.get("materia")!= mat]
                        salvar()
                        st.rerun()

    elif st.session_state.pagina == "Config":
        st.header("⚙️ Perfil")
        obj = st.text_input("Objetivo geral", value=usuario["areas"]["Estudos"].get("objetivo", ""))
        if st.button("Salvar"):
            USUARIOS[LOGADO]["areas"]["Estudos"]["objetivo"] = obj
            salvar()
            st.success("Salvo!")

    else:
        st.header("🎓 Acadêmico")
        est = usuario["areas"]["Estudos"]
        tab_mat, tab_estudar, tab_chat, tab_resumo = st.tabs(["📚 Disciplinas", "✏️ Estudar", "💬 Dúvidas", "📈 Resumo Geral"])

        with tab_mat:
            st.subheader("Registrar disciplinas")
            if est.get("materias"):
                opcoes = ["Nenhum - ver todas"] + list(est["materias"].keys())
                foco_sel = st.selectbox("Focar em uma só?", opcoes)
                if st.button("Definir foco"):
                    USUARIOS[LOGADO]["foco_materia"] = None if foco_sel == "Nenhum - ver todas" else foco_sel
                    salvar()
                    st.rerun()

            st.divider()
            nome_mat = st.text_input("Nome da disciplina", placeholder="Ex: Matemática")
            c1, c2 = st.columns(2)
            with c1:
                ass_geral = st.text_input("Assunto geral", placeholder="Ex: Bhaskara")
            with c2:
                ass_dia = st.text_input("Assunto do dia", placeholder="Ex: Delta negativo")
            c3, c4 = st.columns(2)
            with c3:
                dia_prova = st.date_input("Dia da prova", value=date.today() + timedelta(days=7))
            with c4:
                meta_dias = st.number_input("Meta dias", 1, 10, 5)

            if st.button("Adicionar disciplina", type="primary", use_container_width=True):
                if not nome_mat:
                    st.warning("Digite o nome")
                else:
                    USUARIOS[LOGADO]["areas"]["Estudos"]["materias"][nome_mat] = {
                        "assunto_atual": ass_geral,
                        "assunto_dia": ass_dia or ass_geral,
                        "dia_prova": dia_prova.isoformat(),
                        "semestre_passado": 6.0,
                        "semestre_atual": 7.0,
                        "meta_nota": 10.0,
                    }
                    for i in range(meta_dias):
                        USUARIOS[LOGADO]["cronograma"].append({"area": "Estudos", "materia": nome_mat, "dia": (date.today() + timedelta(days=i)).strftime('%d/%m'), "texto": f"{nome_mat}: {ass_dia or ass_geral}"})
                    salvar()
                    st.success(f"{nome_mat} adicionada!")
                    st.rerun()

            st.divider()
            st.write(f"Suas disciplinas ({len(est.get('materias',{}))})")
            for mat, dados in list(est.get("materias", {}).items()):
                with st.container(border=True):
                    st.write(f"**{mat}** | Hoje: {dados.get('assunto_dia','')} | Prova: {dados.get('dia_prova','')}")
                    cc1, cc2, cc3 = st.columns(3)
                    with cc1:
                        if st.button("🎯 Focar", key=f"f_{mat}"):
                            USUARIOS[LOGADO]["foco_materia"] = mat
                            salvar()
                            st.rerun()
                    with cc2:
                        if st.button("✏️ Editar", key=f"ed_{mat}"):
                            st.session_state[f"edit_{mat}"] = True
                    with cc3:
                        if st.button("🗑️ Deletar", key=f"de_{mat}"):
                            del USUARIOS[LOGADO]["areas"]["Estudos"]["materias"][mat]
                            USUARIOS[LOGADO]["cronograma"] = [t for t in USUARIOS[LOGADO]["cronograma"] if t.get("materia")!= mat]
                            salvar()
                            st.rerun()
                    if st.session_state.get(f"edit_{mat}", False):
                        with st.form(f"form_{mat}"):
                            novo_nome = st.text_input("Nome", value=mat)
                            novo_ass = st.text_input("Assunto geral", value=dados.get("assunto_atual",""))
                            novo_dia = st.text_input("Assunto do dia", value=dados.get("assunto_dia",""))
                            nova_data = st.date_input("Data prova", value=date.fromisoformat(dados.get("dia_prova", date.today().isoformat())))
                            if st.form_submit_button("Salvar"):
                                if novo_nome!= mat:
                                    USUARIOS[LOGADO]["areas"]["Estudos"]["materias"][novo_nome] = USUARIOS[LOGADO]["areas"]["Estudos"]["materias"].pop(mat)
                                    mat = novo_nome
                                USUARIOS[LOGADO]["areas"]["Estudos"]["materias"][mat]["assunto_atual"] = novo_ass
                                USUARIOS[LOGADO]["areas"]["Estudos"]["materias"][mat]["assunto_dia"] = novo_dia
                                USUARIOS[LOGADO]["areas"]["Estudos"]["materias"][mat]["dia_prova"] = nova_data.isoformat()
                                st.session_state[f"edit_{mat}"] = False
                                salvar()
                                st.rerun()

        with tab_estudar:
            materias_disp = est.get("materias", {})
            if usuario.get("foco_materia"):
                materias_disp = {usuario["foco_materia"]: materias_disp.get(usuario["foco_materia"], {})}

            if not materias_disp:
                st.info("Registre uma disciplina primeiro")
            else:
                # TIMER EM CIMA
                if st.session_state.timer_inicio:
                    tempo = datetime.now() - st.session_state.timer_inicio
                    with st.container(border=True):
                        st.subheader(f"⏱️ ESTUDANDO: {st.session_state.materia_em_estudo}")
                        st.title(f"{str(tempo).split('.')[0]}")

                mat_sel = st.selectbox("Qual disciplina estudar?", list(materias_disp.keys()))
                ass_atual = st.text_input(f"Assunto do dia para {mat_sel}", value=materias_disp[mat_sel].get("assunto_dia",""))

                if st.button("Atualizar assunto do dia"):
                    USUARIOS[LOGADO]["areas"]["Estudos"]["materias"][mat_sel]["assunto_dia"] = ass_atual
                    salvar()
                    st.success("Atualizado!")

                if st.session_state.timer_inicio is None:
                    if st.button(f"▶️ Começar {mat_sel}", type="primary", use_container_width=True):
                        st.session_state.timer_inicio = datetime.now()
                        st.session_state.materia_em_estudo = mat_sel
                        st.rerun()
                else:
                    resumo = st.text_area("O que aprendeu?", key=f"res_{mat_sel}")
                    if st.button("⏹️ Parar e concluir", type="primary", use_container_width=True):
                        if not resumo.strip():
                            st.warning("Escreve o que aprendeu")
                        else:
                            tempo = datetime.now() - st.session_state.timer_inicio
                            tempo_min = int(tempo.total_seconds() / 60) if tempo.total_seconds() > 60 else 1
                            for i, t in enumerate(USUARIOS[LOGADO]["cronograma"]):
                                if t.get("materia") == mat_sel and f"tarefa_{i}" not in USUARIOS[LOGADO]["progresso"]:
                                    USUARIOS[LOGADO]["progresso"][f"tarefa_{i}"] = {"feito": True, "tempo_min": tempo_min, "resumo": resumo, "data": date.today().isoformat()}
                                    USUARIOS[LOGADO]["tempo_total_mes"] += tempo_min
                                    USUARIOS[LOGADO]["streak"] += 1
                                    break
                            st.session_state.timer_inicio = None
                            st.session_state.materia_em_estudo = None
                            salvar()
                            st.balloons()
                            st.success(f"✅ {tempo_min} min salvos! {mat_sel} atualizado")
                            st.rerun()

                st.divider()
                st.info(f"📚 IA preparou para {mat_sel}: {ass_atual}")
                st.link_button("🎥 Ver vídeos", f"https://www.youtube.com/results?search_query={mat_sel}+{ass_atual}")
                st.link_button("📄 Buscar PDF grátis", f"https://www.google.com/search?q={mat_sel}+{ass_atual}+pdf+gratis")

        with tab_chat:
            st.subheader("💬 Chat dúvidas - com explicação")
            mat_chat = st.selectbox("Matéria da dúvida", list(est.get("materias", {}).keys()) + ["Geral"])

            for chat in usuario.get("chat_duvidas", []):
                with st.chat_message(chat["role"]):
                    st.markdown(chat["content"])

            duvida = st.chat_input(f"Dúvida de {mat_chat}... Ex: Tirei 7 errei delta")

            if duvida:
                USUARIOS[LOGADO]["chat_duvidas"].append({"role": "user", "content": f"[{mat_chat}] {duvida}"})
                assunto = est.get("materias", {}).get(mat_chat, {}).get("assunto_dia", mat_chat)
                exp = explicacao_ia(mat_chat, assunto, duvida)
                q = f"{mat_chat}+{duvida}".replace(" ", "+")
                link_g = f"https://www.google.com/search?q={q}"
                link_y = f"https://www.youtube.com/results?search_query={q}"
                resposta = f"""{exp}

---
### 🔗 Fontes pesquisadas:

1. **Google - explicação + exercícios**
{link_g}

2. **YouTube - vídeo aula**
{link_y}

3. **Wikipedia - {mat_chat}**
https://pt.wikipedia.org/wiki/{mat_chat}
"""
                USUARIOS[LOGADO]["chat_duvidas"].append({"role": "assistant", "content": resposta})
                salvar()
                st.rerun()

            if st.button("Limpar chat"):
                USUARIOS[LOGADO]["chat_duvidas"] = []
                salvar()
                st.rerun()

        with tab_resumo:
            st.subheader("📈 Resumo Geral")

            if not est.get("materias"):
                st.info("Registre disciplina")
            else:
                # ESCOLHE POR MATÉRIA - NÃO FICA MUITA ABA
                mat_res = st.selectbox("Selecione a disciplina", list(est["materias"].keys()))

                dados = est["materias"][mat_res]
                tarefas = [t for t in usuario["cronograma"] if t.get("materia") == mat_res]
                feitos = sum(1 for i, t in enumerate(usuario["cronograma"]) if t.get("materia") == mat_res and f"tarefa_{i}" in usuario["progresso"])

                with st.container(border=True):
                    st.write(f"**{mat_res}** - Hoje: {dados.get('assunto_dia','')}")
                    st.progress(feitos / len(tarefas) if tarefas else 0, text=f"{feitos}/{len(tarefas)} dias concluídos")

                    # CORREÇÃO DO ERRO DA SUA FOTO - linha 312
                    tempo_mat = 0
                    for k, v in usuario["progresso"].items():
                        try:
                            idx = int(k.split("_")[1])
                            if usuario["cronograma"][idx].get("materia") == mat_res:
                                if isinstance(v, dict):
                                    tempo_mat += v.get("tempo_min", 0)
                        except:
                            pass
                    st.metric("Tempo nessa matéria (mês)", f"{tempo_mat} min")

                st.divider()
                c1, c2, c3 = st.columns(3)
                with c1:
                    np = st.number_input("Sem passado", 0.0, 10.0, float(dados.get("semestre_passado", 6.0)), key=f"np_{mat_res}")
                with c2:
                    na = st.number_input("Sem atual", 0.0, 10.0, float(dados.get("semestre_atual", 7.0)), key=f"na_{mat_res}")
                with c3:
                    mn = st.number_input("Meta", 0.0, 10.0, float(dados.get("meta_nota", 10.0)), key=f"mn_{mat_res}")

                if na >= mn:
                    st.success(f"🏆 Meta atingida em {mat_res}!")
                else:
                    falta = mn - na
                    plano = f"Revise {dados.get('assunto_dia','')} 30min/dia" if falta <= 1 else f"Estude 1h extra + exercícios" if falta <= 3 else f"Foco total 2h/dia"
                    st.warning(f"Evolução: {np} → {na} ({na-np:+.1f}) | {plano}")

                if st.button("Salvar notas", use_container_width=True):
                    USUARIOS[LOGADO]["areas"]["Estudos"]["materias"][mat_res]["semestre_passado"] = np
                    USUARIOS[LOGADO]["areas"]["Estudos"]["materias"][mat_res]["semestre_atual"] = na
                    USUARIOS[LOGADO]["areas"]["Estudos"]["materias"][mat_res]["meta_nota"] = mn
                    salvar()
                    st.success("Salvo!")

                st.divider()
                # GRÁFICOS VOLTARAM
                st.subheader("📊 Tempo por matéria (mês)")
                tempo_por_mat = {}
                for m in est["materias"].keys():
                    tot = 0
                    for k, v in usuario["progresso"].items():
                        try:
                            idx = int(k.split("_")[1])
                            if usuario["cronograma"][idx].get("materia") == m:
                                tot += v.get("tempo_min", 0) if isinstance(v, dict) else 0
                        except:
                            pass
                    tempo_por_mat[m] = tot

                if tempo_por_mat:
                    st.bar_chart(tempo_por_mat)

                st.subheader("📈 Notas: passado vs atual")
                notas = {}
                for m, d in est["materias"].items():
                    notas[m] = {"Passado": d.get("semestre_passado",0), "Atual": d.get("semestre_atual",0), "Meta": d.get("meta_nota",0)}

                if notas:
                    st.bar_chart(notas)

                st.subheader("⏱️ Evolução tempo total")
                st.line_chart({"Mês passado": [0, 60, 120], "Este mês": [0, usuario.get("tempo_total_mes",0)//2, usuario.get("tempo_total_mes",0)]})
