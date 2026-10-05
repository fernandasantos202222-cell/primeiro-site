import streamlit as st
import json, os, random
from datetime import date, datetime, timedelta

ARQUIVO = "banco_usuarios.json"

FRASES = [
    "🚀 Hoje é um ótimo dia para evoluir 1%!",
    "💪 Consistência vence talento!",
    "📚 Foco no assunto do dia!",
]

# EXPLICAÇÃO DE VERDADE - NÃO GENÉRICA
def explicacao_real(materia, assunto_dia, duvida):
    d = duvida.lower()

    if "multiplic" in d:
        return f"""
**Você perguntou: {duvida}**

### O que é multiplicação em {materia}?

É uma soma repetida. Ex: 3 x 4 = 4 + 4 + 4 = 12

**Como funciona:**
- 3 é quantas vezes vai repetir
- 4 é o número que repete

**Exemplos que caem na prova:**
- 2 x 5 = 10
- 7 x 3 = 21
- Se tem 3 caixas com 4 lápis cada = 3 x 4 = 12 lápis

**Erro comum:** Confundir 3 x 4 com 3 + 4. Multiplicação é sempre maior (menos com zero).

**Dica pra não errar:** Faz a tabuada do 2, 3 e 4 hoje. 15 min cada.
"""

    if "delta" in d or "bhaskara" in d:
        return f"""
**Você disse: {duvida}**

### Por que errou delta em {assunto_dia}?

Delta = b² - 4ac

Quando dá negativo (ex: -16), NÃO tem raiz real. Você tentou calcular √-16.

**Exemplo real da prova:**
x² + 2x + 5 = 0
a=1, b=2, c=5
Δ = 2² - 4*1*5 = 4 - 20 = -16
**Resposta: Sem raízes reais**

**Como tirar 10:** Se ver Δ negativo, já marca "sem raiz real", não calcula raiz.
"""

    if "divis" in d:
        return f"""
**Dúvida: {duvida}**

Divisão é repartir igualmente.

Ex: 12 ÷ 3 = 4 porque 3 grupos de 4 dão 12.

**Truque:** Pensa ao contrário da multiplicação. 12 ÷ 3 =? → 3 x? = 12 → 4
"""

    # RESPOSTA PADRÃO MAS EXPLICATIVA
    return f"""
**Pergunta: {duvida}**

### Explicação de {assunto_dia} em {materia}:

**O que é:** {assunto_dia} é a base para entender o próximo assunto da sua prova.

**Como funciona na prática:**
1. Você pega o conceito principal
2. Aplica a fórmula/exemplo
3. Confere se faz sentido

**Exemplo prático para sua prova:**
Se cair {assunto_dia}, o professor vai pedir para você calcular ou explicar com exemplo do dia a dia.

**Plano para hoje (30 min):**
- 10 min: lê explicação
- 10 min: faz 2 exercícios
- 10 min: me explica o que entendeu

Me diz qual parte ficou confusa que eu explico de outro jeito!
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
    u.setdefault("frase_dia", random.choice(FRASES))
    u.setdefault("dias_estudo", ["Segunda", "Terça", "Quarta", "Quinta", "Sexta", "Sábado"])
    u.setdefault("horas_dia", 2)
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
        u = st.text_input("Usuário", key="login_user")
        s = st.text_input("Senha", type="password", key="login_pass")
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
        nome = st.text_input("Nome", key="cad_nome")
        user = st.text_input("Usuário novo", key="cad_user")
        senha = st.text_input("Senha nova", type="password", key="cad_senha")
        if st.button("Cadastrar"):
            st.session_state.usuarios[user] = {"nome": nome, "senha": senha, "areas": {"Estudos": {"objetivo": "", "materias": {}}}, "cronograma": [], "progresso": {}, "tempo_total_mes": 0, "chat_duvidas": [], "streak": 0, "foco_materia": None, "frase_dia": random.choice(FRASES), "dias_estudo": ["Segunda", "Terça", "Quarta", "Quinta", "Sexta", "Sábado"], "horas_dia": 2}
            salvar()
            st.success("Cadastrado!")
else:
    garantir(st.session_state.usuario_logado)
    USUARIOS = st.session_state.usuarios
    LOGADO = st.session_state.usuario_logado
    usuario = USUARIOS[LOGADO]

    with st.sidebar:
        st.write(f"**{usuario['nome']}** 🔥 {usuario['streak']} dias")
        if usuario.get("foco_materia"):
            st.info(f"🎯 Foco: {usuario['foco_materia']}")
            if st.button("Sair do foco", key="sair_foco"):
                USUARIOS[LOGADO]["foco_materia"] = None
                salvar()
                st.rerun()
        if st.button("🏠 Início", use_container_width=True, key="btn_inicio"):
            st.session_state.pagina = "Início"
            st.rerun()
        if st.button("🎓 Acadêmico", use_container_width=True, key="btn_acad"):
            st.session_state.pagina = "Acadêmico"
            st.rerun()
        if st.button("⚙️ Configuração", use_container_width=True, key="btn_config"):
            st.session_state.pagina = "Config"
            st.rerun()
        if st.button("Sair", key="btn_sair"):
            st.session_state.logado = False
            st.rerun()

    if st.session_state.pagina == "Início":
        st.title(f"Olá, {usuario['nome'].split()[0]}! 👋")
        with st.container(border=True):
            st.write(f"*{usuario.get('frase_dia')}*")
            if st.button("Nova frase 🔄", key="nova_frase"):
                USUARIOS[LOGADO]["frase_dia"] = random.choice(FRASES)
                salvar()
                st.rerun()

        if st.session_state.timer_inicio:
            tempo = datetime.now() - st.session_state.timer_inicio
            with st.container(border=True):
                st.subheader(f"⏱️ ESTUDANDO: {st.session_state.materia_em_estudo}")
                st.title(f"{str(tempo).split('.')[0]}")

        # NOVO - PROGRESSO POR SEMANA 1/6
        st.subheader(f"📅 Sua semana - Estuda {len(usuario.get('dias_estudo', []))} dias")
        st.caption(f"Dias: {', '.join(usuario.get('dias_estudo', []))} | {usuario.get('horas_dia', 2)}h por dia")

        # Calcula quantos dias já estudou essa semana
        hoje = date.today()
        inicio_semana = hoje - timedelta(days=hoje.weekday()) # segunda
        feitos_semana = 0
        for v in usuario["progresso"].values():
            try:
                d = date.fromisoformat(v.get("data", ""))
                if d >= inicio_semana:
                    feitos_semana += 1
            except:
                pass

        total_semana = len(usuario.get("dias_estudo", []))
        # Se hoje é segunda e estudou hoje = 1/6
        # Se hoje é terça e estudou seg e ter = 2/6 etc
        dia_nome = ["Segunda", "Terça", "Quarta", "Quinta", "Sexta", "Sábado", "Domingo"][hoje.weekday()]
        st.write(f"Hoje é **{dia_nome}** ({hoje.strftime('%d/%m')})")
        st.progress(feitos_semana / total_semana if total_semana else 0, text=f"{feitos_semana}/{total_semana} dias essa semana")

        materias_mostrar = usuario["areas"]["Estudos"]["materias"]
        if usuario.get("foco_materia"):
            materias_mostrar = {usuario["foco_materia"]: materias_mostrar.get(usuario["foco_materia"], {})}

        st.divider()
        st.subheader("Seus cartões")
        for mat, dados in materias_mostrar.items():
            tarefas = [t for t in usuario["cronograma"] if t.get("materia") == mat]
            feitos = sum(1 for i, t in enumerate(usuario["cronograma"]) if t.get("materia") == mat and f"tarefa_{i}" in usuario["progresso"])
            with st.container(border=True):
                st.write(f"**{mat}** - 📌 Hoje: {dados.get('assunto_dia', '')}")
                # AGORA MOSTRA TIPO 1/6
                st.write(f"Progresso da matéria: {feitos}/{len(tarefas)} concluídos")
                st.progress(feitos / len(tarefas) if tarefas else 0)

    elif st.session_state.pagina == "Config":
        st.header("⚙️ Configuração")

        st.subheader("📅 Quando você estuda?")
        dias = ["Segunda", "Terça", "Quarta", "Quinta", "Sexta", "Sábado", "Domingo"]
        dias_sel = st.multiselect("Escolha seus dias de estudo", dias, default=usuario.get("dias_estudo", dias[:6]), key="dias_estudo_sel")
        horas = st.number_input("Quantas horas por dia?", 1, 8, usuario.get("horas_dia", 2), key="horas_dia_input")

        obj = st.text_input("Objetivo geral", value=usuario["areas"]["Estudos"].get("objetivo", ""), key="obj_geral")

        if st.button("Salvar tudo", use_container_width=True, key="save_config"):
            USUARIOS[LOGADO]["dias_estudo"] = dias_sel
            USUARIOS[LOGADO]["horas_dia"] = horas
            USUARIOS[LOGADO]["areas"]["Estudos"]["objetivo"] = obj
            salvar()
            st.success(f"Salvo! Você estuda {len(dias_sel)} dias: {', '.join(dias_sel)}, {horas}h por dia")
            st.rerun()

    else:
        st.header("🎓 Acadêmico")
        est = usuario["areas"]["Estudos"]
        tab_mat, tab_estudar, tab_chat, tab_resumo = st.tabs(["📚 Disciplinas", "✏️ Estudar", "💬 Dúvidas", "📈 Resumo"])

        with tab_mat:
            st.subheader("Registrar disciplinas")
            nome_mat = st.text_input("Nome da disciplina", key="nome_mat_add")
            c1, c2 = st.columns(2)
            with c1:
                ag = st.text_input("Assunto geral", key="ass_geral_add")
            with c2:
                ad = st.text_input("Assunto do dia", key="ass_dia_add")
            dp = st.date_input("Prova", value=date.today()+timedelta(days=7), key="prova_add")
            if st.button("Adicionar", type="primary", use_container_width=True, key="btn_add_mat"):
                if nome_mat:
                    USUARIOS[LOGADO]["areas"]["Estudos"]["materias"][nome_mat] = {"assunto_atual": ag, "assunto_dia": ad or ag, "dia_prova": dp.isoformat(), "semestre_passado": 6.0, "semestre_atual": 7.0, "meta_nota": 10.0}
                    for i in range(len(usuario.get("dias_estudo", []))):
                        USUARIOS[LOGADO]["cronograma"].append({"area":"Estudos","materia":nome_mat,"dia":(date.today()+timedelta(days=i)).strftime('%d/%m'),"texto":f"{nome_mat}: {ad or ag}"})
                    salvar()
                    st.rerun()
            for mat, dados in list(est.get("materias", {}).items()):
                with st.container(border=True):
                    st.write(f"**{mat}** - {dados.get('assunto_dia','')}")
                    if st.button("🗑️ Deletar", key=f"del_card_{mat}"):
                        del USUARIOS[LOGADO]["areas"]["Estudos"]["materias"][mat]
                        USUARIOS[LOGADO]["cronograma"] = [t for t in USUARIOS[LOGADO]["cronograma"] if t.get("materia")!=mat]
                        salvar()
                        st.rerun()

        with tab_estudar:
            disp = est.get("materias", {})
            if not disp:
                st.info("Registre disciplina")
            else:
                if st.session_state.timer_inicio:
                    tempo = datetime.now() - st.session_state.timer_inicio
                    with st.container(border=True):
                        st.subheader(f"⏱️ ESTUDANDO: {st.session_state.materia_em_estudo}")
                        st.title(f"{str(tempo).split('.')[0]}")
                mat_sel = st.selectbox("Qual estudar?", list(disp.keys()), key="mat_estudar")
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
                    if st.button("⏹️ Parar e concluir", type="primary", use_container_width=True, key="btn_parar"):
                        if res.strip():
                            tempo = datetime.now() - st.session_state.timer_inicio
                            tm = int(tempo.total_seconds()/60) if tempo.total_seconds()>60 else 1
                            for i,t in enumerate(USUARIOS[LOGADO]["cronograma"]):
                                if t.get("materia")==mat_sel and f"tarefa_{i}" not in USUARIOS[LOGADO]["progresso"]:
                                    USUARIOS[LOGADO]["progresso"][f"tarefa_{i}"] = {"feito": True, "tempo_min": tm, "resumo": res, "data": date.today().isoformat()}
                                    USUARIOS[LOGADO]["tempo_total_mes"] += tm
                                    USUARIOS[LOGADO]["streak"] += 1
                                    break
                            st.session_state.timer_inicio = None
                            st.session_state.materia_em_estudo = None
                            salvar()
                            st.balloons()
                            st.rerun()

        with tab_chat:
            st.subheader("💬 Chat - explicação completa")
            mat_c = st.selectbox("Matéria", list(est.get("materias", {}).keys()) + ["Geral"], key="mat_chat")
            for chat in usuario.get("chat_duvidas", []):
                with st.chat_message(chat["role"]):
                    st.markdown(chat["content"])
            duvida = st.chat_input("Ex: o que é multiplicação")
            if duvida:
                USUARIOS[LOGADO]["chat_duvidas"].append({"role": "user", "content": f"[{mat_c}] {duvida}"})
                assunto = est.get("materias", {}).get(mat_c, {}).get("assunto_dia", mat_c)
                exp = explicacao_real(mat_c, assunto, duvida)
                q = f"{mat_c} {duvida}".replace(" ", "+")
                exp_final = f"{exp}\n\n---\n**📚 Fontes para praticar:**\n- Vídeo: https://www.youtube.com/results?search_query={q}\n- Exercícios: https://www.google.com/search?q={q}+exercicios\n"
                USUARIOS[LOGADO]["chat_duvidas"].append({"role": "assistant", "content": exp_final})
                salvar()
                st.rerun()

        with tab_resumo:
            st.subheader("📈 Resumo Geral")
            if not est.get("materias"):
                st.info("Sem matérias")
            else:
                mat_r = st.selectbox("Escolha a matéria", list(est["materias"].keys()), key="mat_resumo")
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
                    st.progress(feitos/len(tarefas) if tarefas else 0, text=f"{feitos}/{len(tarefas)} dias concluídos")
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
                if st.button("Salvar notas", use_container_width=True, key=f"save_{mat_r}"):
                    USUARIOS[LOGADO]["areas"]["Estudos"]["materias"][mat_r]["semestre_passado"]=np
                    USUARIOS[LOGADO]["areas"]["Estudos"]["materias"][mat_r]["semestre_atual"]=na
                    USUARIOS[LOGADO]["areas"]["Estudos"]["materias"][mat_r]["meta_nota"]=mn
                    salvar()
                    st.success("Salvo!")
