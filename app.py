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
    novo = {}
    for k, v in u["progresso"].items():
        if isinstance(v, bool):
            novo[k] = {"feito": True, "tempo_min": 25, "resumo": "", "data": date.today().isoformat()}
        else:
            novo[k] = v
    u["progresso"] = novo

st.set_page_config(page_title="EvoluiAI", layout="centered")

if not st.session_state.logado:
    st.title("🚀 EvoluiAI")
    t1, t2 = st.tabs(["Entrar", "Cadastrar"])
    with t1:
        u = st.text_input("Usuário")
        s = st.text_input("Senha", type="password")
        if st.button("Entrar"):
            if u in st.session_state.usuarios and st.session_state.usuarios[u]["senha"] == s:
                garantir(u)
                salvar()
                st.session_state.logado = True
                st.session_state.usuario_logado = u
                st.rerun()
            else:
                st.error("Erro")
    with t2:
        nome = st.text_input("Nome")
        user = st.text_input("Usuário novo")
        senha = st.text_input("Senha nova", type="password")
        if st.button("Cadastrar"):
            st.session_state.usuarios[user] = {"nome": nome, "senha": senha, "areas": {"Estudos": {"objetivo": "", "materias": {}}}, "cronograma": [], "progresso": {}, "tempo_total_mes": 0, "chat_duvidas": [], "streak": 0, "foco_materia": None}
            salvar()
            st.success("Cadastrado!")
else:
    garantir(st.session_state.usuario_logado)
    USUARIOS = st.session_state.usuarios
    LOGADO = st.session_state.usuario_logado
    usuario = USUARIOS[LOGADO]

    with st.sidebar:
        st.write(f"**{usuario['nome']}**")
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
        if st.button("Sair"):
            st.session_state.logado = False
            st.rerun()

    if st.session_state.pagina == "Início":
        st.title(f"Olá, {usuario['nome'].split()[0]}!")
        if st.session_state.timer_inicio:
            tempo = datetime.now() - st.session_state.timer_inicio
            with st.container(border=True):
                st.write(f"⏱️ Estudando {st.session_state.materia_em_estudo} - {str(tempo).split('.')[0]}")

        materias_mostrar = usuario["areas"]["Estudos"]["materias"]
        if usuario.get("foco_materia"):
            materias_mostrar = {usuario["foco_materia"]: materias_mostrar.get(usuario["foco_materia"], {})}

        st.subheader("Seus cartões")
        for mat, dados in materias_mostrar.items():
            tarefas = [t for t in usuario["cronograma"] if t.get("materia") == mat]
            feitos = sum(1 for i, t in enumerate(usuario["cronograma"]) if t.get("materia") == mat and f"tarefa_{i}" in usuario["progresso"])
            with st.container(border=True):
                st.write(f"**{mat}** - 📌 Hoje: {dados.get('assunto_dia', dados.get('assunto_atual',''))}")
                st.progress(feitos / len(tarefas) if tarefas else 0, text=f"{feitos}/{len(tarefas)} dias")

    else:
        st.header("🎓 Acadêmico")
        est = usuario["areas"]["Estudos"]
        tab_mat, tab_estudar, tab_chat, tab_resumo = st.tabs(["📚 Disciplinas", "✏️ Estudar", "💬 Dúvidas", "📈 Resumo"])

        with tab_mat:
            st.subheader("Registrar disciplinas")
            if est.get("materias"):
                op = ["Nenhum"] + list(est["materias"].keys())
                f = st.selectbox("Focar em uma só?", op)
                if st.button("Definir foco"):
                    USUARIOS[LOGADO]["foco_materia"] = None if f == "Nenhum" else f
                    salvar()
                    st.rerun()
            st.divider()
            nome_mat = st.text_input("Nome da disciplina")
            c1, c2 = st.columns(2)
            with c1:
                ag = st.text_input("Assunto geral")
            with c2:
                ad = st.text_input("Assunto do dia")
            c3, c4 = st.columns(2)
            with c3:
                dp = st.date_input("Prova", value=date.today()+timedelta(days=7))
            with c4:
                md = st.number_input("Meta dias", 1, 10, 5)
            if st.button("Adicionar", type="primary", use_container_width=True):
                if nome_mat:
                    USUARIOS[LOGADO]["areas"]["Estudos"]["materias"][nome_mat] = {"assunto_atual": ag, "assunto_dia": ad or ag, "dia_prova": dp.isoformat(), "semestre_passado": 6.0, "semestre_atual": 7.0, "meta_nota": 10.0}
                    for i in range(md):
                        USUARIOS[LOGADO]["cronograma"].append({"area":"Estudos","materia":nome_mat,"dia":(date.today()+timedelta(days=i)).strftime('%d/%m'),"texto":f"{nome_mat}: {ad or ag}"})
                    salvar()
                    st.rerun()
            for mat, dados in list(est.get("materias", {}).items()):
                with st.container(border=True):
                    st.write(f"**{mat}** - {dados.get('assunto_dia','')}")
                    b1,b2 = st.columns(2)
                    with b1:
                        if st.button("✏️ Editar", key=f"e_{mat}"):
                            st.session_state[f"ed_{mat}"] = True
                    with b2:
                        if st.button("🗑️ Deletar", key=f"d_{mat}"):
                            del USUARIOS[LOGADO]["areas"]["Estudos"]["materias"][mat]
                            USUARIOS[LOGADO]["cronograma"] = [t for t in USUARIOS[LOGADO]["cronograma"] if t.get("materia")!=mat]
                            salvar()
                            st.rerun()
                    if st.session_state.get(f"ed_{mat}", False):
                        with st.form(f"f_{mat}"):
                            nn = st.text_input("Nome", value=mat)
                            na = st.text_input("Assunto geral", value=dados.get("assunto_atual",""))
                            nd = st.text_input("Assunto dia", value=dados.get("assunto_dia",""))
                            if st.form_submit_button("Salvar"):
                                if nn!= mat:
                                    USUARIOS[LOGADO]["areas"]["Estudos"]["materias"][nn] = USUARIOS[LOGADO]["areas"]["Estudos"]["materias"].pop(mat)
                                    mat = nn
                                USUARIOS[LOGADO]["areas"]["Estudos"]["materias"][mat]["assunto_atual"] = na
                                USUARIOS[LOGADO]["areas"]["Estudos"]["materias"][mat]["assunto_dia"] = nd
                                st.session_state[f"ed_{mat}"] = False
                                salvar()
                                st.rerun()

        with tab_estudar:
            disp = est.get("materias", {})
            if usuario.get("foco_materia"):
                disp = {usuario["foco_materia"]: disp.get(usuario["foco_materia"], {})}
            if not disp:
                st.info("Registre disciplina")
            else:
                if st.session_state.timer_inicio:
                    tempo = datetime.now() - st.session_state.timer_inicio
                    with st.container(border=True):
                        st.subheader(f"⏱️ ESTUDANDO: {st.session_state.materia_em_estudo}")
                        st.title(f"{str(tempo).split('.')[0]}")
                mat_sel = st.selectbox("Qual estudar?", list(disp.keys()))
                ass_d = st.text_input("Assunto do dia", value=disp[mat_sel].get("assunto_dia",""))
                if st.button("Atualizar assunto do dia"):
                    USUARIOS[LOGADO]["areas"]["Estudos"]["materias"][mat_sel]["assunto_dia"] = ass_d
                    salvar()
                    st.success("Ok!")
                if st.session_state.timer_inicio is None:
                    if st.button(f"▶️ Começar {mat_sel}", type="primary", use_container_width=True):
                        st.session_state.timer_inicio = datetime.now()
                        st.session_state.materia_em_estudo = mat_sel
                        st.rerun()
                else:
                    res = st.text_area("O que aprendeu?")
                    if st.button("⏹️ Parar e concluir", type="primary", use_container_width=True):
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
            st.subheader("💬 Chat - explicação clara")
            mat_c = st.selectbox("Matéria", list(est.get("materias", {}).keys()) + ["Geral"])
            for chat in usuario.get("chat_duvidas", []):
                with st.chat_message(chat["role"]):
                    st.markdown(chat["content"])
            duvida = st.chat_input("Ex: Tirei 7 errei delta negativo")
            if duvida:
                USUARIOS[LOGADO]["chat_duvidas"].append({"role": "user", "content": f"[{mat_c}] {duvida}"})
                assunto = est.get("materias", {}).get(mat_c, {}).get("assunto_dia", mat_c)
                dl = duvida.lower()
                if "delta" in dl or "bhaskara" in dl or "errei" in dl or "tirei" in dl:
                    exp = f"""
**Você disse: {duvida}**

**Por que errou {assunto}:**
Delta = b² - 4ac. Se Δ < 0, não tem raiz real. Você tentou calcular raiz de número negativo.

**Exemplo que cai na prova:**
x² + 2x + 5 = 0 → Δ = 4 - 20 = -16 → **Resposta: Sem raízes reais.**

**Como tirar 10:**
Hoje faça 3 exercícios só de Δ negativo.
"""
                else:
                    exp = f"""
**Pergunta: {duvida}**

**Explicação de {assunto}:**
{assunto} é assim: conceito principal em 1 frase. O erro comum é [detalhe]. Pra acertar, faça [dica prática].

Me diz o que ainda ficou confuso?
"""
                q = f"{mat_c} {duvida}".replace(" ", "+")
                exp_final = f"""{exp}

---
**📚 Fontes:**
- Vídeo: https://www.youtube.com/results?search_query={q}
- Exercícios: https://www.google.com/search?q={q}+exercicios
"""
                USUARIOS[LOGADO]["chat_duvidas"].append({"role": "assistant", "content": exp_final})
                salvar()
                st.rerun()

        with tab_resumo:
            st.subheader("📈 Resumo Geral")
            if not est.get("materias"):
                st.info("Sem matérias")
            else:
                mat_r = st.selectbox("Escolha a matéria", list(est["materias"].keys()))
                dados = est["materias"][mat_r]
                tarefas = [t for t in usuario["cronograma"] if t.get("materia")==mat_r]
                feitos = sum(1 for i,t in enumerate(usuario["cronograma"]) if t.get("materia")==mat_r and f"tarefa_{i}" in usuario["progresso"])
                tempo_mat = 0
                for k,v in usuario["progresso"].items():
                    try:
                        idx = int(k.split("_")[1])
                        if usuario["cronograma"][idx].get("materia")==mat_r:
                            tempo_mat += v.get("tempo_min",0) if isinstance(v, dict) else 0
                    except:
                        pass

                with st.container(border=True):
                    st.write(f"### {mat_r}")
                    st.write(f"Hoje: {dados.get('assunto_dia','')}")
                    st.progress(feitos/len(tarefas) if tarefas else 0, text=f"{feitos}/{len(tarefas)} dias")
                    c1,c2 = st.columns(2)
                    with c1:
                        st.metric("Tempo nessa matéria", f"{tempo_mat} min")
                    with c2:
                        st.metric("Total mês", f"{usuario.get('tempo_total_mes',0)} min")

                st.divider()
                c1,c2,c3 = st.columns(3)
                with c1:
                    np = st.number_input("Passado", 0.0, 10.0, float(dados.get("semestre_passado",6.0)), key=f"np_{mat_r}")
                with c2:
                    na = st.number_input("Atual", 0.0, 10.0, float(dados.get("semestre_atual",7.0)), key=f"na_{mat_r}")
                with c3:
                    mn = st.number_input("Meta", 0.0, 10.0, float(dados.get("meta_nota",10.0)), key=f"mn_{mat_r}")

                col1,col2,col3 = st.columns(3)
                with col1:
                    st.metric("Passado", f"{np}")
                with col2:
                    st.metric("Atual", f"{na}", delta=f"{na-np:+.1f}")
                with col3:
                    falta = mn - na
                    st.metric("Meta", f"{mn}", delta="Atingida!" if falta<=0 else f"Falta {falta:.1f}")

                prog = (na/mn*100) if mn>0 else 0
                st.progress(min(prog/100,1.0), text=f"{prog:.0f}% da meta")

                if st.button("Salvar notas", use_container_width=True):
                    USUARIOS[LOGADO]["areas"]["Estudos"]["materias"][mat_r]["semestre_passado"]=np
                    USUARIOS[LOGADO]["areas"]["Estudos"]["materias"][mat_r]["semestre_atual"]=na
                    USUARIOS[LOGADO]["areas"]["Estudos"]["materias"][mat_r]["meta_nota"]=mn
                    salvar()
                    st.success("Salvo!")
