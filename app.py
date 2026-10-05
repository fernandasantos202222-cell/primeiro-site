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

def garantir(uid):
    u=st.session_state.usuarios[uid]
    u.setdefault("nome","")
    u.setdefault("perfil_academico",{"eh_estudante":True,"nivel":"Ensino Médio","status":"Em andamento"})
    u.setdefault("areas",{"Estudos":{"objetivo":"","materias":{}}})
    if "Estudos" not in u["areas"]: u["areas"]["Estudos"]={"objetivo":"","materias":{}}
    u["areas"]["Estudos"].setdefault("materias",{})
    u.setdefault("cronograma",[])
    u.setdefault("progresso",{})
    u.setdefault("resumos",{})
    u.setdefault("streak",0)

FRASES_PT = [
    "Hoje é um ótimo dia para evoluir. Vamos começar, {nome}?",
    "{nome}, foco no seu objetivo: {objetivo}. Um passo de cada vez!",
    "Cada minuto de estudo hoje te aproxima da sua meta, {nome}.",
]

st.set_page_config(page_title="EvoluiAI", layout="centered")

if not st.session_state.logado:
    st.title("🚀 EvoluiAI")
    t1,t2=st.tabs(["Entrar","Cadastrar"])
    with t1:
        u=st.text_input("Usuário",key="l1")
        s=st.text_input("Senha",type="password",key="l2")
        if st.button("Entrar"):
            if u in st.session_state.usuarios and st.session_state.usuarios[u]["senha"]==s:
                garantir(u)
                salvar()
                st.session_state.logado=True
                st.session_state.usuario_logado=u
                st.rerun()
            else: st.error("Errado")
    with t2:
        nome=st.text_input("Seu nome",key="c1")
        user=st.text_input("Usuário",key="c5")
        senha=st.text_input("Senha",type="password",key="c6")
        if st.button("Cadastrar"):
            st.session_state.usuarios[user]={"nome":nome,"senha":senha,"perfil_academico":{"eh_estudante":True,"nivel":"Ensino Médio","status":"Em andamento"},"areas":{"Estudos":{"objetivo":"","materias":{}}},"cronograma":[],"progresso":{},"resumos":{},"streak":0}
            salvar()
            st.success("Cadastrado! Faz login.")
else:
    garantir(st.session_state.usuario_logado)
    usuario=st.session_state.usuarios[st.session_state.usuario_logado]

    with st.sidebar:
        st.write(f"**{usuario['nome']}**")
        st.caption(f"🔥 {usuario.get('streak',0)} dias")
        if st.button("🏠 Início",use_container_width=True): st.session_state.pagina="Início"; st.rerun()
        if st.button("🎓 Acadêmico",use_container_width=True): st.session_state.pagina="Acadêmico"; st.rerun()
        if st.button("⚙️ Configuração / Perfil",use_container_width=True): st.session_state.pagina="Config"; st.rerun()
        if st.button("Sair"): st.session_state.logado=False; st.rerun()

    if st.session_state.pagina=="Início":
        st.title(f"Olá, {usuario['nome'].split()[0]}! 👋")
        obj_geral = usuario["areas"]["Estudos"].get("objetivo") or "seus estudos"
        total_feitos=len(usuario.get("progresso",{}))
        total_tarefas=len(usuario.get("cronograma",[]))
        prog_txt = f"{total_feitos}/{total_tarefas}" if total_tarefas else "0/0"
        frase = random.choice(FRASES_PT).format(nome=usuario['nome'].split()[0], objetivo=obj_geral)

        with st.container(border=True):
            st.write(f"📅 **Hoje, {date.today().strftime('%d/%m/%Y')}**")
            st.subheader(f"💬 {frase}")

        st.subheader("Seus cartões por área")
        for nome_area, dados in usuario["areas"].items():
            objetivo = dados.get("objetivo") or "Defina seu objetivo em Configuração"
            tarefas_area=[t for t in usuario["cronograma"] if t.get("area")==nome_area]
            feitos_area=sum(1 for i,t in enumerate(usuario["cronograma"]) if t.get("area")==nome_area and f"tarefa_{i}" in usuario["progresso"])
            total_area=len(tarefas_area)
            with st.container(border=True):
                st.write(f"**{nome_area}**")
                st.write(f'🎯 Objetivo: "{objetivo}"')
                if total_area>0:
                    st.progress(feitos_area/total_area, text=f"Meta: {feitos_area}/{total_area} do dia")
                    st.caption(f"✅ {feitos_area}/{total_area} como concluído")
                else:
                    st.caption("Sem tarefas. Vá em Acadêmico > Minhas Matérias")

    elif st.session_state.pagina=="Config":
        st.header("⚙️ Configuração / Perfil")
        perfil=usuario.get("perfil_academico",{})
        eh_est=st.selectbox("Você é estudante?",["Sim, sou estudante","Não, faço cursos livres"], index=0 if perfil.get("eh_estudante",True) else 1)
        nivel=st.selectbox("Nível de escolaridade",["Ensino Fundamental","Ensino Médio","Ensino Superior","Pós / Concurso","Cursos livres"], index=1)
        status=st.selectbox("Status",["Em andamento","Concluído","Trancado"], index=0)
        objetivo_geral=st.text_input("Qual seu objetivo geral nos Estudos?", value=usuario["areas"]["Estudos"].get("objetivo",""), placeholder="Ex: Tirar 9 em python")

        if st.button("Salvar perfil"):
            st.session_state.usuarios[st.session_state.usuario_logado]["perfil_academico"]={"eh_estudante": eh_est=="Sim, sou estudante","nivel":nivel,"status":status}
            st.session_state.usuarios[st.session_state.usuario_logado]["areas"]["Estudos"]["objetivo"]=objetivo_geral
            salvar()
            st.success("Salvo!")

    else:
        st.header("🎓 Área Acadêmica")
        est=usuario["areas"]["Estudos"]
        tab_mat, tab_estudar, tab_resumo = st.tabs(["📚 Minhas Matérias","✏️ Estudar Agora","📈 Resumo Geral e Notas"])

        with tab_mat:
            st.subheader("Cadastrar matéria / curso")
            nome_materia = st.text_input("Nome da matéria ou curso", placeholder="Ex: python, Matemática", key="nova_mat")
            c1,c2=st.columns(2)
            with c1: assunto_atual=st.text_input("Assunto atual", placeholder="Ex: Funções", key="assunto")
            with c2: dia_prova=st.date_input("Dia da prova", value=date.today(), key="prova")

            if st.button("Adicionar matéria", type="primary"):
                if not nome_materia:
                    st.warning("Escreve o nome da matéria!")
                else:
                    # LINHA 178 CORRIGIDA - USANDO st.session_state DIRETO
                    garantir(st.session_state.usuario_logado)
                    st.session_state.usuarios[st.session_state.usuario_logado]["areas"]["Estudos"]["materias"][nome_materia]={
                        "assunto_atual": assunto_atual,
                        "dia_prova": dia_prova.isoformat(),
                        "mes_passado": 5.0,
                        "mes_atual": 6.0,
                        "meta_nota": 9.0,
                    }
                    # Cria cronograma 5 dias - CORRIGIDO AQUI TAMBÉM
                    for i in range(5):
                        nova_tarefa={"area":"Estudos","materia":nome_materia,"dia":(date.today()+timedelta(days=i)).strftime('%d/%m'),"texto":f"{nome_materia}: {assunto_atual}"}
                        st.session_state.usuarios[st.session_state.usuario_logado]["cronograma"].append(nova_tarefa)

                    salvar()
                    st.success(f"Matéria {nome_materia} adicionada! IA montou 1/5")
                    st.rerun()

            st.divider()
            for mat, dados in est.get("materias",{}).items():
                with st.container(border=True):
                    st.write(f"**{mat}** - {dados.get('assunto_atual','')} | Prova {dados.get('dia_prova','')}")

        with tab_estudar:
            if not est.get("materias"):
                st.info("Cadastre uma matéria primeiro")
            else:
                materia_sel=st.selectbox("Qual matéria vai estudar agora?", list(est["materias"].keys()))
                dados_mat=est["materias"][materia_sel]

                st.write(f"📌 Assunto: **{dados_mat.get('assunto_atual','')}** | Prova: {dados_mat.get('dia_prova','')}")
                st.info(f"📄 Resumo da web (IA): {materia_sel} - {dados_mat.get('assunto_atual','')} é essencial. Estude conceito e prática.")
                st.link_button(f"🎥 Ver vídeos de {materia_sel} no YouTube", f"https://www.youtube.com/results?search_query={materia_sel}+{dados_mat.get('assunto_atual','')}")
                st.link_button(f"📚 Buscar PDF grátis de {materia_sel}", f"https://www.google.com/search?q={materia_sel}+pdf+gratis")

                st.divider()
                if "timer_inicio" not in st.session_state: st.session_state.timer_inicio=None
                if st.button("▶️ Começar a estudar agora"):
                    st.session_state.timer_inicio=datetime.now()
                    st.success("Timer iniciado!")
                if st.session_state.timer_inicio:
                    tempo=datetime.now()-st.session_state.timer_inicio
                    st.write(f"⏱️ Estudando há: {str(tempo).split('.')[0]}")

                resumo=st.text_area("O que você aprendeu hoje?", key=f"res_{materia_sel}", height=100)

                if st.button(f"✅ Concluir estudo de {materia_sel}", type="primary"):
                    if not resumo.strip():
                        st.warning("Escreve um resuminho!")
                    else:
                        # Marca próxima tarefa dessa matéria como feita
                        for i,t in enumerate(st.session_state.usuarios[st.session_state.usuario_logado]["cronograma"]):
                            if t.get("materia")==materia_sel and f"tarefa_{i}" not in st.session_state.usuarios[st.session_state.usuario_logado]["progresso"]:
                                st.session_state.usuarios[st.session_state.usuario_logado]["progresso"][f"tarefa_{i}"]=True
                                st.session_state.usuarios[st.session_state.usuario_logado]["resumos"][f"tarefa_{i}"]=resumo
                                st.session_state.usuarios[st.session_state.usuario_logado]["streak"]+=1
                                break
                        salvar()
                        st.balloons()
                        st.success("Concluído! Progresso atualizado!")
                        st.rerun()

        with tab_resumo:
            st.subheader("📈 Progresso Geral por matéria")
            for mat in est.get("materias",{}).keys():
                tarefas_mat=[t for t in usuario["cronograma"] if t.get("materia")==mat]
                feitos_mat=sum(1 for i,t in enumerate(usuario["cronograma"]) if t.get("materia")==mat and f"tarefa_{i}" in usuario["progresso"])
                total_mat=len(tarefas_mat)
                st.write(f"**{mat}**")
                st.progress(feitos_mat/total_mat if total_mat else 0, text=f"{feitos_mat}/{total_mat} dias")

            st.divider()
            st.subheader("📝 Notas - Evolução e Meta atingida?")
            for mat, dados in est.get("materias",{}).items():
                st.write(f"**{mat}**")
                c1,c2,c3=st.columns(3)
                with c1: np=st.number_input(f"Passado {mat}",0.0,10.0,float(dados.get("mes_passado",5.0)),key=f"np_{mat}")
                with c2: na=st.number_input(f"Atual {mat}",0.0,10.0,float(dados.get("mes_atual",6.0)),key=f"na_{mat}")
                with c3: mn=st.number_input(f"Meta {mat}",0.0,10.0,float(dados.get("meta_nota",9.0)),key=f"mn_{mat}")

                if na >= mn: st.success(f"🏆 Meta atingida em {mat}!")
                else: st.warning(f"Falta {mn-na:.1f} para meta | Evolução: {na-np:+.1f}")

                if st.button(f"Salvar notas {mat}", key=f"save_{mat}"):
                    st.session_state.usuarios[st.session_state.usuario_logado]["areas"]["Estudos"]["materias"][mat]["mes_passado"]=np
                    st.session_state.usuarios[st.session_state.usuario_logado]["areas"]["Estudos"]["materias"][mat]["mes_atual"]=na
                    st.session_state.usuarios[st.session_state.usuario_logado]["areas"]["Estudos"]["materias"][mat]["meta_nota"]=mn
                    salvar()
                    st.success("Salvo!")
