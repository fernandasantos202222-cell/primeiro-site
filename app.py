import streamlit as st
import json, os
from datetime import date, datetime, timedelta
import random

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

def garantir(uid):
    u=st.session_state.usuarios[uid]
    u.setdefault("nome","")
    u.setdefault("perfil_academico",{"nivel":"Ensino Médio","status":"Em andamento"})
    u.setdefault("areas",{"Estudos":{"objetivo":"","materias":{}}})
    if "Estudos" not in u["areas"]: u["areas"]["Estudos"]={"objetivo":"","materias":{}}
    u["areas"]["Estudos"].setdefault("materias",{})
    u.setdefault("cronograma",[])
    u.setdefault("progresso",{})
    u.setdefault("resumos",{})
    u.setdefault("streak",0)
    u.setdefault("tempo_total_mes",0)
    u.setdefault("chat_duvidas",[]) # novo

st.set_page_config(page_title="EvoluiAI", layout="centered")

if not st.session_state.logado:
    st.title("🚀 EvoluiAI")
    t1,t2=st.tabs(["Entrar","Cadastrar"])
    with t1:
        u=st.text_input("Usuário",key="l1")
        s=st.text_input("Senha",type="password",key="l2")
        if st.button("Entrar"):
            if u in st.session_state.usuarios and st.session_state.usuarios[u]["senha"]==s:
                garantir(u); salvar()
                st.session_state.logado=True; st.session_state.usuario_logado=u; st.rerun()
            else: st.error("Errado")
    with t2:
        nome=st.text_input("Nome",key="c1")
        user=st.text_input("Usuário",key="c5")
        senha=st.text_input("Senha",type="password",key="c6")
        if st.button("Cadastrar"):
            st.session_state.usuarios[user]={"nome":nome,"senha":senha,"perfil_academico":{"nivel":"Ensino Médio","status":"Em andamento"},"areas":{"Estudos":{"objetivo":"","materias":{}}},"cronograma":[],"progresso":{},"resumos":{},"streak":0,"tempo_total_mes":0,"chat_duvidas":[]}
            salvar(); st.success("Cadastrado!")
else:
    garantir(st.session_state.usuario_logado)
    USUARIOS = st.session_state.usuarios
    usuario = USUARIOS[st.session_state.usuario_logado]
    LOGADO = st.session_state.usuario_logado

    with st.sidebar:
        st.write(f"**{usuario['nome']}** - 🔥 {usuario.get('streak',0)} dias")
        if st.button("🏠 Início",use_container_width=True): st.session_state.pagina="Início"; st.rerun()
        if st.button("🎓 Acadêmico",use_container_width=True): st.session_state.pagina="Acadêmico"; st.rerun()
        if st.button("⚙️ Perfil",use_container_width=True): st.session_state.pagina="Config"; st.rerun()
        if st.button("Sair"): st.session_state.logado=False; st.rerun()

    if st.session_state.pagina=="Início":
        st.title(f"Olá, {usuario['nome'].split()[0]}!")

        # LEMBRETE PROVA
        for mat, dados in usuario["areas"]["Estudos"]["materias"].items():
            try:
                data_prova = date.fromisoformat(dados.get("dia_prova",""))
                dias_falta = (data_prova - date.today()).days
                if 0 <= dias_falta <= 7:
                    st.warning(f"⚠️ Prova de **{mat}** em **{dias_falta} dias** ({data_prova.strftime('%d/%m')})")
            except: pass

        # TIMER NO INÍCIO TAMBÉM
        if st.session_state.timer_inicio and st.session_state.materia_em_estudo:
            tempo = datetime.now() - st.session_state.timer_inicio
            with st.container(border=True):
                st.write(f"⏱️ **Estudando agora:** {st.session_state.materia_em_estudo}")
                st.write(f"⏰ Tempo: {str(tempo).split('.')[0]}")
                if st.button("Ir concluir estudo"): st.session_state.pagina="Acadêmico"; st.rerun()

        obj = usuario["areas"]["Estudos"].get("objetivo") or "seus estudos"
        with st.container(border=True):
            st.write(f"📅 Hoje, {date.today().strftime('%d/%m/%Y')}")
            st.subheader(f"💬 Bora, {usuario['nome'].split()[0]}? Foco em: {obj}")

        st.subheader("Seus cartões")
        for area_nome, dados_area in usuario["areas"].items():
            with st.container(border=True):
                st.write(f"**{area_nome}** - 🎯 Objetivo: \"{dados_area.get('objetivo','')}\"")
                for mat in dados_area.get("materias",{}).keys():
                    tarefas_mat = [t for t in usuario["cronograma"] if t.get("materia")==mat]
                    feitos_mat = sum(1 for i,t in enumerate(usuario["cronograma"]) if t.get("materia")==mat and f"tarefa_{i}" in usuario["progresso"])
                    st.progress(feitos_mat/len(tarefas_mat) if tarefas_mat else 0, text=f"{mat}: {feitos_mat}/{len(tarefas_mat)} dias")

    elif st.session_state.pagina=="Config":
        st.header("⚙️ Perfil")
        objetivo=st.text_input("Objetivo geral", value=usuario["areas"]["Estudos"].get("objetivo",""))
        if st.button("Salvar"):
            USUARIOS[LOGADO]["areas"]["Estudos"]["objetivo"]=objetivo
            salvar(); st.success("Salvo!")

    else:
        st.header("🎓 Acadêmico")
        est = usuario["areas"]["Estudos"]

        # AGORA 4 ABAS - TIMER EM CIMA + CHAT NOVO
        tab_mat, tab_estudar, tab_chat, tab_resumo = st.tabs(["📚 Minhas Matérias","✏️ Estudar Agora","💬 Chat Dúvidas","📈 Resumo Geral"])

        with tab_mat:
            st.subheader("Adicionar matéria")
            nome_materia = st.text_input("Nome da matéria", placeholder="Ex: Matemática", key="nova_mat_final2")
            col1,col2=st.columns(2)
            with col1: assunto=st.text_input("Assunto atual", placeholder="Ex: Bhaskara", key="assunto_final2")
            with col2: dia_prova=st.date_input("Dia da prova", value=date.today()+timedelta(days=7), key="prova_final2")

            if st.button("Adicionar matéria", type="primary"):
                if not nome_materia: st.warning("Digite o nome")
                else:
                    garantir(LOGADO)
                    USUARIOS[LOGADO]["areas"]["Estudos"]["materias"][nome_materia]={
                        "assunto_atual": assunto,
                        "dia_prova": dia_prova.isoformat(),
                        "semestre_passado": 6.0,
                        "semestre_atual": 7.0,
                        "meta_nota": 10.0
                    }
                    for i in range(5):
                        USUARIOS[LOGADO]["cronograma"].append({"area":"Estudos","materia": nome_materia,"dia": (date.today()+timedelta(days=i)).strftime('%d/%m'),"texto": f"{nome_materia}: {assunto}"})
                    salvar(); st.success(f"{nome_materia} adicionada!"); st.rerun()

            for mat, dados in est.get("materias",{}).items():
                with st.container(border=True):
                    st.write(f"**{mat}** - {dados.get('assunto_atual','')} - Prova {dados.get('dia_prova','')}")

        with tab_estudar:
            if not est.get("materias"):
                st.info("Adicione matéria primeiro")
            else:
                # ===== TIMER EM CIMA AGORA =====
                if st.session_state.timer_inicio and st.session_state.materia_em_estudo:
                    tempo = datetime.now() - st.session_state.timer_inicio
                    with st.container(border=True):
                        st.subheader(f"⏱️ ESTUDANDO AGORA: {st.session_state.materia_em_estudo}")
                        st.title(f"{str(tempo).split('.')[0]}")
                        st.caption(f"Assunto: {est['materias'][st.session_state.materia_em_estudo].get('assunto_atual','')}")
                else:
                    st.info("⏱️ Nenhum estudo em andamento. Escolha uma matéria abaixo e clique em Começar")

                st.divider()
                materia_sel=st.selectbox("Qual vai estudar?", list(est["materias"].keys()))

                dados_mat=est["materias"][materia_sel]

                if st.session_state.timer_inicio is None:
                    if st.button(f"▶️ Começar a estudar {materia_sel} agora", type="primary", use_container_width=True):
                        st.session_state.timer_inicio=datetime.now()
                        st.session_state.materia_em_estudo=materia_sel
                        st.rerun()
                else:
                    # Se já tem timer, mostra botão concluir
                    resumo=st.text_area("✍️ O que você aprendeu até agora?", placeholder="Ex: Aprendi Bhaskara...", key=f"resumo_{materia_sel}", height=120)

                    col1,col2=st.columns(2)
                    with col1:
                        if st.button("⏹️ Parar tempo e concluir", type="primary", use_container_width=True):
                            if not resumo.strip(): st.warning("Escreve o que aprendeu!")
                            else:
                                tempo = datetime.now() - st.session_state.timer_inicio
                                tempo_min = int(tempo.total_seconds()/60) if tempo.total_seconds()>60 else 1
                                for i,t in enumerate(USUARIOS[LOGADO]["cronograma"]):
                                    if t.get("materia")==materia_sel and f"tarefa_{i}" not in USUARIOS[LOGADO]["progresso"]:
                                        USUARIOS[LOGADO]["progresso"][f"tarefa_{i}"]={"feito":True,"tempo_min":tempo_min,"resumo":resumo,"data":date.today().isoformat()}
                                        USUARIOS[LOGADO]["tempo_total_mes"]=USUARIOS[LOGADO].get("tempo_total_mes",0)+tempo_min
                                        break
                                st.session_state.timer_inicio=None
                                st.session_state.materia_em_estudo=None
                                salvar()
                                st.balloons()
                                st.success(f"✅ {tempo_min} min salvos! Progresso de {materia_sel} atualizado")
                                st.rerun()
                    with col2:
                        if st.button("Cancelar estudo", use_container_width=True):
                            st.session_state.timer_inicio=None
                            st.session_state.materia_em_estudo=None
                            st.rerun()

                st.divider()
                # IA PREPAROU AGORA FICA EMBAIXO DO TIMER
                st.subheader(f"📚 IA preparou para {materia_sel}")
                st.info(f"Resumo: {materia_sel} - {dados_mat.get('assunto_atual','')} - estude conceito + exercício")
                st.link_button(f"🎥 Vídeos {materia_sel}", f"https://www.youtube.com/results?search_query={materia_sel}+{dados_mat.get('assunto_atual','')}")
                st.link_button(f"📄 PDF {materia_sel}", f"https://www.google.com/search?q={materia_sel}+pdf+gratis")

        with tab_chat:
            st.subheader(f"💬 Chat de dúvidas - {usuario['nome'].split()[0]}")
            st.caption("Ex: Tirei 7 em Matemática, errei questão sobre Bhaskara com delta negativo, explica?")

            materia_chat = st.selectbox("Matéria da dúvida", list(est.get("materias",{}).keys()) + ["Geral"])

            # Mostra histórico
            for chat in usuario.get("chat_duvidas",[]):
                with st.chat_message(chat["role"]):
                    st.write(chat["content"])

            duvida = st.chat_input(f"Digite sua dúvida de {materia_chat}... Ex: errei questão X")

            if duvida:
                # Salva pergunta
                USUARIOS[LOGADO]["chat_duvidas"].append({"role":"user","content": f"[{materia_chat}] {duvida}"})

                # SIMULA PESQUISA NA WEB + RESPOSTA DA IA
                # Aqui depois você pode conectar com API real, por enquanto faz explicação inteligente
                if "tirei" in duvida.lower() or "errei" in duvida.lower() or "7" in duvida:
                    resposta = f"""Entendi! Você mandou: **{duvida}**

Sobre **{materia_chat}**:

🔍 **O que a web diz:**
Pesquisei aqui: Esse erro é comum quando {duvida[:30]}...

✅ **Explicação simples:**
1. O conceito de {est.get('materias',{}).get(materia_chat,{}).get('assunto_atual','essa matéria')} tem um detalhe que muita gente erra
2. Quando delta é negativo, não tem raiz real - por isso você errou
3. Pra tirar 10 na próxima: faça 3 exercícios só desse tipo

🎥 **Recomendo:**
- Vídeo: {materia_chat} - erros comuns
- PDF: exercícios resolvidos de {materia_chat}

Quer que eu monte 3 questões pra você praticar agora sobre isso?
"""
                else:
                    resposta = f"""Boa pergunta sobre **{materia_chat}**!

**{duvida}**

📚 Resposta rápida:
O assunto {est.get('materias',{}).get(materia_chat,{}).get('assunto_atual','')} funciona assim: [explicação da IA aqui]

🔗 **Pesquisei na web pra você:**
- Melhor explicação: https://www.google.com/search?q={materia_chat}+{duvida.replace(' ','+')}+explicação
- Vídeo aula: https://www.youtube.com/results?search_query={materia_chat}+{duvida.replace(' ','+')}

Quer que eu explique de outro jeito?
"""

                USUARIOS[LOGADO]["chat_duvidas"].append({"role":"assistant","content": resposta})
                salvar()
                st.rerun()

            if st.button("Limpar chat"):
                USUARIOS[LOGADO]["chat_duvidas"]=[]
                salvar(); st.rerun()

        with tab_resumo:
            st.subheader("📈 Tempo de estudo")
            st.metric("Total mês", f"{usuario.get('tempo_total_mes',0)} min")
            st.bar_chart({"Passado": 120, "Atual": usuario.get('tempo_total_mes',0)})

            st.divider()
            for mat, dados in est.get("materias",{}).items():
                with st.container(border=True):
                    st.write(f"**{mat}**")
                    c1,c2,c3=st.columns(3)
                    with c1: np=st.number_input(f"Sem passado {mat}",0.0,10.0,float(dados.get("semestre_passado",6.0)),key=f"npf2_{mat}")
                    with c2: na=st.number_input(f"Sem atual {mat}",0.0,10.0,float(dados.get("semestre_atual",7.0)),key=f"naf2_{mat}")
                    with c3: mn=st.number_input(f"Meta {mat}",0.0,10.0,float(dados.get("meta_nota",10.0)),key=f"mnf2_{mat}")

                    if na >= mn: st.success("🏆 Meta atingida!")
                    else:
                        falta=mn-na
                        if falta <=1: plano=f"Revise {dados.get('assunto_atual','')} 30min/dia"
                        elif falta <=3: plano=f"Estude {mat} 1h extra + simulados"
                        else: plano=f"Foco total {mat}: 2h/dia"
                        st.warning(f"{np} → {na} | {plano}")

                    if st.button(f"Salvar {mat}", key=f"saven2_{mat}"):
                        USUARIOS[LOGADO]["areas"]["Estudos"]["materias"][mat]["semestre_passado"]=np
                        USUARIOS[LOGADO]["areas"]["Estudos"]["materias"][mat]["semestre_atual"]=na
                        USUARIOS[LOGADO]["areas"]["Estudos"]["materias"][mat]["meta_nota"]=mn
                        salvar(); st.success("Salvo!")
