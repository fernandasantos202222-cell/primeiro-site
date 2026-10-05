import streamlit as st
import json, os
from datetime import date, datetime, timedelta

ARQUIVO="banco_usuarios.json"
def carregar():
    if os.path.exists(ARQUIVO):
        try:
            with open(ARQUIVO,"r",encoding="utf-8") as f: return json.load(f)
        except: return {}
    return {}
def salvar():
    with open(ARQUIVO,"w",encoding="utf-8") as f:
        json.dump(st.session_state.usuarios,f,indent=4,ensure_ascii=False)

if "usuarios" not in st.session_state: st.session_state.usuarios=carregar()
if "logado" not in st.session_state:
    st.session_state.logado=False
    st.session_state.usuario_logado=""
    st.session_state.pagina="Início"
    st.session_state.timer_inicio=None
    st.session_state.materia_em_estudo=None
    st.session_state.foco_materia=None

def garantir(uid):
    u=st.session_state.usuarios[uid]
    u.setdefault("nome","")
    u.setdefault("areas",{"Estudos":{"objetivo":"","materias":{}}})
    if "Estudos" not in u["areas"]: u["areas"]["Estudos"]={"objetivo":"","materias":{}}
    u["areas"]["Estudos"].setdefault("materias",{})
    u.setdefault("cronograma",[])
    u.setdefault("progresso",{})
    u.setdefault("tempo_total_mes",0)
    u.setdefault("chat_duvidas",[])
    u.setdefault("streak",0)
    u.setdefault("foco_materia",None)

st.set_page_config(page_title="EvoluiAI", layout="centered")

if not st.session_state.logado:
    st.title("🚀 EvoluiAI")
    t1,t2=st.tabs(["Entrar","Cadastrar"])
    with t1:
        u=st.text_input("Usuário")
        s=st.text_input("Senha",type="password")
        if st.button("Entrar"):
            if u in st.session_state.usuarios and st.session_state.usuarios[u]["senha"]==s:
                garantir(u); salvar()
                st.session_state.logado=True; st.session_state.usuario_logado=u; st.rerun()
    with t2:
        nome=st.text_input("Nome")
        user=st.text_input("Usuário novo")
        senha=st.text_input("Senha nova",type="password")
        if st.button("Cadastrar"):
            st.session_state.usuarios[user]={"nome":nome,"senha":senha,"areas":{"Estudos":{"objetivo":"","materias":{}}},"cronograma":[],"progresso":{},"tempo_total_mes":0,"chat_duvidas":[],"streak":0,"foco_materia":None}
            salvar(); st.success("Cadastrado! Entra.")
else:
    garantir(st.session_state.usuario_logado)
    USUARIOS=st.session_state.usuarios
    usuario=USUARIOS[st.session_state.usuario_logado]
    LOGADO=st.session_state.usuario_logado

    with st.sidebar:
        st.write(f"**{usuario['nome']}** 🔥 {usuario['streak']}")
        if usuario.get("foco_materia"):
            st.info(f"🎯 Foco: {usuario['foco_materia']}")
            if st.button("Sair do foco"):
                USUARIOS[LOGADO]["foco_materia"]=None; salvar(); st.rerun()
        if st.button("🏠 Início",use_container_width=True): st.session_state.pagina="Início"; st.rerun()
        if st.button("🎓 Acadêmico",use_container_width=True): st.session_state.pagina="Acadêmico"; st.rerun()
        if st.button("⚙️ Perfil",use_container_width=True): st.session_state.pagina="Config"; st.rerun()
        if st.button("Sair"): st.session_state.logado=False; st.rerun()

    if st.session_state.pagina=="Início":
        st.title(f"Olá, {usuario['nome'].split()[0]}!")

        # LEMBRETE PROVA
        for mat, dados in usuario["areas"]["Estudos"]["materias"].items():
            try:
                data_prova=date.fromisoformat(dados.get("dia_prova",""))
                dias=(data_prova-date.today()).days
                if 0 <= dias <= 7:
                    st.warning(f"⚠️ Prova {mat} em {dias} dias ({data_prova.strftime('%d/%m')}) - {dados.get('assunto_atual','')}")
            except: pass

        if st.session_state.timer_inicio:
            tempo=datetime.now()-st.session_state.timer_inicio
            with st.container(border=True):
                st.write(f"⏱️ Estudando {st.session_state.materia_em_estudo} - {str(tempo).split('.')[0]}")

        # SE TEM FOCO, MOSTRA SÓ ELE
        materias_para_mostrar = usuario["areas"]["Estudos"]["materias"]
        if usuario.get("foco_materia"):
            materias_para_mostrar = {usuario["foco_materia"]: materias_para_mostrar.get(usuario["foco_materia"],{})}

        st.subheader(f"Cartões {' - FOCO' if usuario.get('foco_materia') else ''}")
        for mat, dados in materias_para_mostrar.items():
            tarefas=[t for t in usuario["cronograma"] if t.get("materia")==mat]
            feitos=sum(1 for i,t in enumerate(usuario["cronograma"]) if t.get("materia")==mat and f"tarefa_{i}" in usuario["progresso"])
            with st.container(border=True):
                c1,c2,c3=st.columns([3,1,1])
                with c1:
                    st.write(f"**{mat}**")
                    st.write(f"📌 Assunto do dia: {dados.get('assunto_dia', dados.get('assunto_atual',''))}")
                    st.progress(feitos/len(tarefas) if tarefas else 0, text=f"{feitos}/{len(tarefas)} dias")
                with c2:
                    if st.button("✏️", key=f"e_{mat}"):
                        st.session_state.pagina="Acadêmico"; st.rerun()
                with c3:
                    if st.button("▶️", key=f"p_{mat}"):
                        st.session_state.pagina="Acadêmico"; st.rerun()

    elif st.session_state.pagina=="Config":
        st.header("⚙️ Perfil")
        obj=st.text_input("Objetivo geral", value=usuario["areas"]["Estudos"].get("objetivo",""))
        if st.button("Salvar"):
            USUARIOS[LOGADO]["areas"]["Estudos"]["objetivo"]=obj; salvar(); st.success("Salvo!")

    else:
        st.header("🎓 Acadêmico")
        est=usuario["areas"]["Estudos"]
        tab_mat, tab_estudar, tab_chat, tab_resumo = st.tabs(["📚 Disciplinas","✏️ Estudar","💬 Dúvidas","📈 Resumo Geral"])

        with tab_mat:
            st.subheader("Registrar disciplinas")

            # MODO FOCO - ESCOLHER 1 DISCIPLINA PRA FOCAR
            if est.get("materias"):
                st.write("**🎯 Quer focar só em uma disciplina?**")
                foco_opcoes = ["Nenhum - ver todas"] + list(est["materias"].keys())
                foco_sel = st.selectbox("Focar em:", foco_opcoes, index=0 if not usuario.get("foco_materia") else foco_opcoes.index(usuario["foco_materia"]) if usuario.get("foco_materia") in foco_opcoes else 0)
                if st.button("Definir foco"):
                    if foco_sel=="Nenhum - ver todas":
                        USUARIOS[LOGADO]["foco_materia"]=None
                    else:
                        USUARIOS[LOGADO]["foco_materia"]=foco_sel
                    salvar(); st.success(f"Foco definido: {foco_sel}"); st.rerun()

            st.divider()
            st.write("**Adicionar nova disciplina**")
            nome_materia=st.text_input("Nome da disciplina", placeholder="Ex: Matemática", key="add_m")
            col1,col2=st.columns(2)
            with col1: assunto=st.text_input("Assunto geral", placeholder="Ex: Bhaskara", key="ass_g")
            with col2: assunto_dia=st.text_input("Assunto do dia (hoje)", placeholder="Ex: Delta negativo", key="ass_dia")
            col3,col4=st.columns(2)
            with col3: dia_prova=st.date_input("Dia da prova", value=date.today()+timedelta(days=7))
            with col4: carga=st.number_input("Meta dias",1,10,5, help="Ex: estudar 5 dias")

            if st.button("Adicionar disciplina", type="primary", use_container_width=True):
                if not nome_materia: st.warning("Nome obrigatório")
                else:
                    USUARIOS[LOGADO]["areas"]["Estudos"]["materias"][nome_materia]={
                        "assunto_atual":assunto,
                        "assunto_dia":assunto_dia or assunto,
                        "dia_prova":dia_prova.isoformat(),
                        "semestre_passado":6.0,
                        "semestre_atual":7.0,
                        "meta_nota":10.0,
                        "meta_dias":carga
                    }
                    for i in range(carga):
                        USUARIOS[LOGADO]["cronograma"].append({"area":"Estudos","materia":nome_materia,"dia":(date.today()+timedelta(days=i)).strftime('%d/%m'),"texto":f"{nome_materia}: {assunto_dia or assunto}"})
                    salvar(); st.success(f"{nome_materia} registrada!"); st.rerun()

            st.divider()
            st.subheader(f"Suas disciplinas ({len(est.get('materias',{}))}) - editar/deletar aqui")

            for mat, dados in list(est.get("materias",{}).items()):
                with st.container(border=True):
                    st.write(f"**{mat}** | Assunto geral: {dados.get('assunto_atual','')} | **Hoje: {dados.get('assunto_dia','')}** | Prova: {dados.get('dia_prova','')}")
                    c1,c2,c3,c4=st.columns(4)
                    with c1:
                        if st.button("🎯 Focar", key=f"focar_{mat}"):
                            USUARIOS[LOGADO]["foco_materia"]=mat; salvar(); st.rerun()
                    with c2:
                        if st.button("✏️ Editar", key=f"edit_{mat}"):
                            st.session_state[f"editando_{mat}"]=True
                    with c3:
                        if st.button("🗑️ Deletar", key=f"del_{mat}"):
                            del USUARIOS[LOGADO]["areas"]["Estudos"]["materias"][mat]
                            USUARIOS[LOGADO]["cronograma"]=[t for t in USUARIOS[LOGADO]["cronograma"] if t.get("materia")!=mat]
                            if USUARIOS[LOGADO].get("foco_materia")==mat: USUARIOS[LOGADO]["foco_materia"]=None
                            salvar(); st.rerun()
                    with c4:
                        if st.button("▶️ Estudar", key=f"est_{mat}"):
                            st.session_state.materia_em_estudo=mat
                            st.session_state.timer_inicio=datetime.now()
                            salvar(); st.rerun()

                    if st.session_state.get(f"editando_{mat}", False):
                        with st.form(f"form_{mat}"):
                            st.write(f"Editando {mat}")
                            novo_nome=st.text_input("Nome", value=mat)
                            novo_assunto=st.text_input("Assunto geral", value=dados.get("assunto_atual",""))
                            novo_assunto_dia=st.text_input("Assunto do dia", value=dados.get("assunto_dia",""))
                            nova_data=st.date_input("Data prova", value=date.fromisoformat(dados.get("dia_prova",date.today().isoformat())))
                            col_s1,col_s2=st.columns(2)
                            with col_s1:
                                if st.form_submit_button("Salvar"):
                                    if novo_nome!=mat:
                                        USUARIOS[LOGADO]["areas"]["Estudos"]["materias"][novo_nome]=USUARIOS[LOGADO]["areas"]["Estudos"]["materias"].pop(mat)
                                        mat=novo_nome
                                    USUARIOS[LOGADO]["areas"]["Estudos"]["materias"][mat]["assunto_atual"]=novo_assunto
                                    USUARIOS[LOGADO]["areas"]["Estudos"]["materias"][mat]["assunto_dia"]=novo_assunto_dia
                                    USUARIOS[LOGADO]["areas"]["Estudos"]["materias"][mat]["dia_prova"]=nova_data.isoformat()
                                    st.session_state[f"editando_{mat}"]=False
                                    salvar(); st.rerun()
                            with col_s2:
                                if st.form_submit_button("Cancelar"):
                                    st.session_state[f"editando_{mat}"]=False
                                    st.rerun()

        with tab_estudar:
            materias_disponiveis = est.get("materias",{})
            if usuario.get("foco_materia"):
                materias_disponiveis = {usuario["foco_materia"]: materias_disponiveis.get(usuario["foco_materia"],{})}

            if not materias_disponiveis: st.info("Registre disciplina primeiro")
            else:
                # TIMER EM CIMA
                if st.session_state.timer_inicio:
                    tempo=datetime.now()-st.session_state.timer_inicio
                    with st.container(border=True):
                        st.subheader(f"⏱️ ESTUDANDO: {st.session_state.materia_em_estudo}")
                        st.title(f"{str(tempo).split('.')[0]}")
                        st.write(f"Assunto do dia: {est['materias'][st.session_state.materia_em_estudo].get('assunto_dia','')}")

                materia_sel=st.selectbox("Qual disciplina estudar?", list(materias_disponiveis.keys()))

                # Campo assunto do dia editável aqui também
                assunto_dia_atual=st.text_input(f"Assunto do dia para {materia_sel}", value=materias_disponiveis[materia_sel].get("assunto_dia",""), key=f"ass_dia_est_{materia_sel}")
                if st.button("Atualizar assunto do dia"):
                    USUARIOS[LOGADO]["areas"]["Estudos"]["materias"][materia_sel]["assunto_dia"]=assunto_dia_atual
                    salvar(); st.success("Assunto do dia atualizado!")

                if st.session_state.timer_inicio is None:
                    if st.button(f"▶️ Começar {materia_sel}", type="primary", use_container_width=True):
                        st.session_state.timer_inicio=datetime.now()
                        st.session_state.materia_em_estudo=materia_sel
                        st.rerun()
                else:
                    resumo=st.text_area("O que aprendeu?", key=f"res_{materia_sel}")
                    if st.button("⏹️ Parar e concluir", type="primary", use_container_width=True):
                        if not resumo.strip(): st.warning("Escreve")
                        else:
                            tempo=datetime.now()-st.session_state.timer_inicio
                            tempo_min=int(tempo.total_seconds()/60) if tempo.total_seconds()>60 else 1
                            for i,t in enumerate(USUARIOS[LOGADO]["cronograma"]):
                                if t.get("materia")==materia_sel and f"tarefa_{i}" not in USUARIOS[LOGADO]["progresso"]:
                                    USUARIOS[LOGADO]["progresso"][f"tarefa_{i}"]={"feito":True,"tempo_min":tempo_min,"resumo":resumo,"data":date.today().isoformat()}
                                    USUARIOS[LOGADO]["tempo_total_mes"]+=tempo_min
                                    break
                            st.session_state.timer_inicio=None; st.session_state.materia_em_estudo=None
                            salvar(); st.balloons(); st.success(f"{tempo_min} min salvos!"); st.rerun()

                st.divider()
                st.info(f"📚 IA preparou para {materia_sel}: {materias_disponiveis[materia_sel].get('assunto_dia','')}")
                st.link_button("🎥 Vídeos", f"https://www.youtube.com/results?search_query={materia_sel}+{assunto_dia_atual}")

        with tab_chat:
            st.subheader("💬 Chat dúvidas com fontes")
            materia_chat=st.selectbox("Matéria da dúvida", list(est.get("materias",{}).keys())+["Geral"], key="mc")

            for chat in usuario.get("chat_duvidas",[]):
                with st.chat_message(chat["role"]):
                    st.markdown(chat["content"])

            duvida=st.chat_input(f"Dúvida de {materia_chat}...")
            if duvida:
                USUARIOS[LOGADO]["chat_duvidas"].append({"role":"user","content":f"[{materia_chat}] {duvida}"})
                query=f"{materia_chat}+{duvida}".replace(" ","+")
                link_g=f"https://www.google.com/search?q={query}"
                link_y=f"https://www.youtube.com/results?search_query={query}"
                resposta=f"""
**Dúvida:** {duvida}

**Explicação clara:**
Em {materia_chat}, sobre {est.get('materias',{}).get(materia_chat,{}).get('assunto_dia','')}, isso acontece porque...

**Passo a passo:**
1. Conceito
2. Exemplo
3. Como não errar mais

---
**🔗 Fontes:**
1. Google: {link_g}
2. YouTube: {link_y}
"""
                USUARIOS[LOGADO]["chat_duvidas"].append({"role":"assistant","content":resposta})
                salvar(); st.rerun()

        with tab_resumo:
            st.subheader("📈 Resumo geral - escolha a matéria")

            if not est.get("materias"):
                st.info("Nenhuma disciplina registrada")
            else:
                # ESCOLHER POR MATÉRIA - NÃO FICA MUITA ABA
                mat_sel_resumo=st.selectbox("Selecione a disciplina para ver resumo", list(est["materias"].keys()), key="resumo_mat_sel")

                dados=est["materias"][mat_sel_resumo]
                tarefas=[t for t in usuario["cronograma"] if t.get("materia")==mat_sel_resumo]
                feitos=sum(1 for i,t in enumerate(usuario["cronograma"]) if t.get("materia")==mat_sel_resumo and f"tarefa_{i}" in usuario["progresso"])

                with st.container(border=True):
                    st.write(f"**{mat_sel_resumo}**")
                    st.write(f"Assunto geral: {dados.get('assunto_atual','')} | Hoje: {dados.get('assunto_dia','')}")
                    st.progress(feitos/len(tarefas) if tarefas else 0, text=f"Progresso: {feitos}/{len(tarefas)} dias concluídos")

                    # Tempo dessa matéria
                    tempo_mat=sum(v.get("tempo_min",0) for i,v in usuario["progresso"].items() if usuario["cronograma"][int(i.split('_')[1])].get("materia")==mat_sel_resumo) if usuario["progresso"] else 0
                    st.metric("Tempo estudado nessa matéria (mês)", f"{tempo_mat} min")

                st.divider()
                st.write(f"**Notas - {mat_sel_resumo}**")
                c1,c2,c3=st.columns(3)
                with c1: np=st.number_input("Semestre passado",0.0,10.0,float(dados.get("semestre_passado",6.0)),key=f"np_{mat_sel_resumo}")
                with c2: na=st.number_input("Semestre atual",0.0,10.0,float(dados.get("semestre_atual",7.0)),key=f"na_{mat_sel_resumo}")
                with c3: mn=st.number_input("Meta",0.0,10.0,float(dados.get("meta_nota",10.0)),key=f"mn_{mat_sel_resumo}")

                evo=na-np
                if na>=mn:
                    st.success(f"🏆 Meta atingida em {mat_sel_resumo}!")
                else:
                    falta=mn-na
                    if falta<=1: plano=f"Revise {dados.get('assunto_dia','')} 30min/dia"
                    elif falta<=3: plano=f"Estude {mat_sel_resumo} 1h extra + exercícios"
                    else: plano=f"Foco total: 2h/dia em {mat_sel_resumo}"
                    st.warning(f"Evolução: {np} → {na} ({evo:+.1f}) | {plano}")

                if st.button(f"Salvar notas {mat_sel_resumo}", use_container_width=True):
                    USUARIOS[LOGADO]["areas"]["Estudos"]["materias"][mat_sel_resumo]["semestre_passado"]=np
                    USUARIOS[LOGADO]["areas"]["Estudos"]["materias"][mat_sel_resumo]["semestre_atual"]=na
                    USUARIOS[LOGADO]["areas"]["Estudos"]["materias"][mat_sel_resumo]["meta_nota"]=mn
                    salvar(); st.success("Notas salvas!")

                st.divider()
                st.subheader("Comparação geral de todas as matérias")
                if len(est["materias"])>1:
                    dados_graf={}
                    for m,d in est["materias"].items():
                        dados_graf[m]=[d.get("semestre_passado",0), d.get("semestre_atual",0)]
                    st.bar_chart(dados_graf)
