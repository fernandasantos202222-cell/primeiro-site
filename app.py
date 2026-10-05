import streamlit as st
import json, os
from datetime import date, datetime
import random, time

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

def garantir(u_id):
    u=st.session_state.usuarios[u_id]
    u.setdefault("nome","")
    u.setdefault("perfil_academico",{"eh_estudante":True,"nivel":"Ensino Médio","status":"Em andamento"})
    u.setdefault("areas",{"Estudos":{"objetivo":"Passar de ano / Tirar 9","materias":{}}})
    u.setdefault("cronograma",[])
    u.setdefault("progresso",{})
    u.setdefault("resumos",{})
    u.setdefault("streak",0)
    if "Estudos" not in u["areas"]:
        u["areas"]["Estudos"]={"objetivo":"Meus estudos","materias":{}}
    u["areas"]["Estudos"].setdefault("materias",{})

FRASES_PT = [
    "Hoje é um ótimo dia para evoluir. Vamos começar, {nome}?",
    "{nome}, foco no seu objetivo: {objetivo}. Um passo de cada vez!",
    "Cada minuto de estudo hoje te aproxima da sua meta, {nome}.",
    "{nome}, você já avançou {progresso}. Continue!",
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
            if not nome or not user or not senha: st.warning("Preenche tudo")
            else:
                st.session_state.usuarios[user]={"nome":nome,"senha":senha,"perfil_academico":{"eh_estudante":True,"nivel":"Ensino Médio","status":"Em andamento"},"areas":{"Estudos":{"objetivo":"","materias":{}}},"cronograma":[],"progresso":{},"resumos":{},"streak":0}
                salvar()
                st.success("Cadastrado! Entra agora.")
else:
    garantir(st.session_state.usuario_logado)
    usuario=st.session_state.usuarios[st.session_state.usuario_logado]

    with st.sidebar:
        st.write(f"**{usuario['nome']}**")
        st.caption(f"🔥 {usuario.get('streak',0)} dias de foco")
        st.divider()
        if st.button("🏠 Início",use_container_width=True): st.session_state.pagina="Início"; st.rerun()
        if st.button("🎓 Acadêmico",use_container_width=True): st.session_state.pagina="Acadêmico"; st.rerun()
        if st.button("⚙️ Configuração / Perfil",use_container_width=True): st.session_state.pagina="Config"; st.rerun()
        if st.button("Sair"): st.session_state.logado=False; st.rerun()

    # INÍCIO - SEM IMAGEM, SÓ FRASE EM PORTUGUÊS
    if st.session_state.pagina=="Início":
        st.title(f"Olá, {usuario['nome'].split()[0]}! 👋")

        # Frase do dia
        total_feitos = len(usuario.get("progresso",{}))
        total_tarefas = len(usuario.get("cronograma",[]))
        if total_tarefas==0: prog_txt = "0/0"
        else: prog_txt = f"{total_feitos}/{total_tarefas}"

        obj_geral = usuario["areas"]["Estudos"]["objetivo"] or "seus estudos"
        frase = random.choice(FRASES_PT).format(nome=usuario['nome'].split()[0], objetivo=obj_geral, progresso=prog_txt)

        with st.container(border=True):
            st.write(f"📅 **Hoje, {date.today().strftime('%d/%m/%Y')}**")
            st.subheader(f"💬 {frase}")

        st.divider()
        st.subheader("Seus cartões por área")
        for nome_area, dados in usuario["areas"].items():
            objetivo = dados.get("objetivo","Defina seu objetivo")
            # Calcula meta do dia: se objetivo é estudar 5 dias, mostra 1/5
            tarefas_area = [t for t in usuario["cronograma"] if t.get("area")==nome_area]
            feitos_area = sum(1 for i,t in enumerate(usuario["cronograma"]) if t.get("area")==nome_area and f"tarefa_{i}" in usuario["progresso"])
            total_area = len(tarefas_area)

            with st.container(border=True):
                st.write(f"**{nome_area}**")
                st.write(f"🎯 Objetivo: **{objetivo}**")
                if total_area>0:
                    st.progress(feitos_area/total_area if total_area else 0, text=f"Meta do dia: {feitos_area}/{total_area} concluídos")
                    if feitos_area>0:
                        st.caption(f"✅ {feitos_area}/{total_area} como concluído - progresso atualizado!")
                else:
                    st.caption("Nenhuma tarefa ainda. Vá em Acadêmico > Minhas Matérias")

                if st.button(f"Estudar {nome_area}", key=f"btn_{nome_area}"):
                    st.session_state.pagina="Acadêmico"
                    st.rerun()

    # CONFIG - PERFIL LIMPO
    elif st.session_state.pagina=="Config":
        st.header("⚙️ Configuração / Perfil Acadêmico")
        st.write("Essas informações deixam seu plano mais inteligente")

        perfil = usuario.get("perfil_academico",{})
        eh_est = st.selectbox("Você é estudante?", ["Sim, sou estudante","Não, faço cursos livres"], index=0 if perfil.get("eh_estudante",True) else 1)
        nivel = st.selectbox("Nível de escolaridade", ["Ensino Fundamental","Ensino Médio","Ensino Superior","Pós / Concurso","Cursos livres"], index=["Ensino Fundamental","Ensino Médio","Ensino Superior","Pós / Concurso","Cursos livres"].index(perfil.get("nivel","Ensino Médio")) if perfil.get("nivel") in ["Ensino Fundamental","Ensino Médio","Ensino Superior","Pós / Concurso","Cursos livres"] else 1)
        status = st.selectbox("Status", ["Em andamento","Concluído","Trancado"], index=0)

        objetivo_geral = st.text_input("Qual seu objetivo geral nos Estudos?", value=usuario["areas"]["Estudos"].get("objetivo",""), placeholder="Ex: Passar no ENEM com 800, ou Tirar 9 em Python")

        if st.button("Salvar perfil"):
            st.session_state.usuarios[st.session_state.usuario_logado]["perfil_academico"]={"eh_estudante": eh_est=="Sim, sou estudante","nivel":nivel,"status":status}
            st.session_state.usuarios[st.session_state.usuario_logado]["areas"]["Estudos"]["objetivo"]=objetivo_geral
            salvar()
            st.success("Perfil salvo! Agora vá em Acadêmico cadastrar suas matérias.")

        st.divider()
        st.write(f"Nível atual: **{nivel}** | Status: **{status}**")

    # ACADÊMICO - AGORA LIMPO E ORGANIZADO
    else:
        st.header("🎓 Área Acadêmica")
        est = usuario["areas"]["Estudos"]

        tab_mat, tab_estudar, tab_resumo = st.tabs(["📚 Minhas Matérias","✏️ Estudar Agora","📈 Resumo Geral e Notas"])

        with tab_mat:
            st.subheader("Cadastrar matéria / curso")
            st.caption("Ex: se você é Ensino Médio, vai ter várias. Se for curso, coloca o nome do curso.")

            nome_materia = st.text_input("Nome da matéria ou curso", placeholder="Ex: python, Matemática, Constitucional", key="nova_mat")
            col1,col2 = st.columns(2)
            with col1:
                assunto_atual = st.text_input("Assunto atual que está estudando", placeholder="Ex: Funções em python", key="assunto")
            with col2:
                dia_prova = st.date_input("Dia da prova / entrega", value=date.today(), key="prova")

            if st.button("Adicionar matéria"):
                if nome_materia:
                    garantir(st.session_state.usuario_logado)
                    # IA já monta cronograma quando coloca nome
                    est["materias"][nome_materia]={
                        "assunto_atual": assunto_atual,
                        "dia_prova": dia_prova.isoformat(),
                        "dia_selecionado": date.today().isoformat(),
                        "mes_passado": 5.0,
                        "mes_atual": 6.0,
                        "meta_nota": 9.0,
                        "resumo_web": f"{nome_materia}: {assunto_atual} é essencial. Principais pontos: conceito, prática e aplicação.",
                        "videos": [f"Melhor aula de {nome_materia} - {assunto_atual}", f"{nome_materia} na prática"],
                        "livros": [f"Apostila grátis de {nome_materia} PDF"]
                    }
                    # Cria cronograma 5 dias para essa matéria - meta 5 dias
                    for i in range(5):
                        usuario["cronograma"].append({"area":"Estudos","materia":nome_materia,"dia":(date.today()+timedelta(days=i)).strftime('%d/%m'),"texto":f"{nome_materia}: {assunto_atual}"})

                    salvar()
                    st.success(f"Matéria {nome_materia} adicionada! IA já montou cronograma 1/5 e conteúdos. Vá em 'Estudar Agora'")
                    st.rerun()

            st.divider()
            st.write("**Suas matérias cadastradas:**")
            for mat, dados in est.get("materias",{}).items():
                with st.container(border=True):
                    st.write(f"**{mat}** - Assunto: {dados.get('assunto_atual','')} | Prova: {dados.get('dia_prova','')}")
                    if st.button(f"Excluir {mat}", key=f"del_{mat}"):
                        del est["materias"][mat]
                        salvar(); st.rerun()

        with tab_estudar:
            if not est.get("materias"):
                st.info("Cadastre uma matéria primeiro na aba Minhas Matérias")
            else:
                materia_sel = st.selectbox("Qual matéria você vai estudar agora?", list(est["materias"].keys()))

                dados_mat = est["materias"][materia_sel]

                st.subheader(f"Estudando: {materia_sel}")
                st.write(f"📌 Assunto atual: **{dados_mat.get('assunto_atual','')}**")
                st.write(f"📅 Prova: {dados_mat.get('dia_prova','')}")

                st.divider()
                st.write("**IA preparou para você:**")
                st.info(f"📄 **Resumo da web:** {dados_mat.get('resumo_web','')}")

                st.write("🎥 **Vídeos sugeridos:**")
                for v in dados_mat.get("videos",[]):
                    st.write(f"- {v}")
                st.link_button(f"Buscar vídeos de {materia_sel} no YouTube", f"https://www.youtube.com/results?search_query={materia_sel}+{dados_mat.get('assunto_atual','')}")

                st.write("📚 **Livros PDF grátis:**")
                for l in dados_mat.get("livros",[]):
                    st.write(f"- {l}")
                st.link_button(f"Buscar PDF de {materia_sel}", f"https://www.google.com/search?q={materia_sel}+apostila+pdf+gratis")

                st.divider()
                st.subheader("⏱️ Timer de estudo + Resumo")

                # TIMER SIMPLES
                if "timer_inicio" not in st.session_state: st.session_state.timer_inicio=None

                col_t1,col_t2 = st.columns(2)
                with col_t1:
                    if st.button("▶️ Começar a estudar agora"):
                        st.session_state.timer_inicio = datetime.now()
                        st.success("Timer iniciado! Foca!")

                with col_t2:
                    if st.session_state.timer_inicio:
                        tempo = datetime.now() - st.session_state.timer_inicio
                        st.write(f"⏱️ Estudando há: {str(tempo).split('.')[0]}")

                resumo_aprendido = st.text_area("O que você aprendeu hoje?", placeholder="Ex: Hoje aprendi que função em python serve para...", key=f"res_{materia_sel}", height=120)

                if st.button(f"✅ Concluir estudo de {materia_sel}", type="primary"):
                    if not resumo_aprendido.strip():
                        st.warning("Escreve um resuminho do que aprendeu para fixar!")
                    else:
                        # Marca como concluído e atualiza 1/5
                        # Acha a próxima tarefa dessa matéria não concluída
                        for i,t in enumerate(usuario["cronograma"]):
                            if t.get("materia")==materia_sel and f"tarefa_{i}" not in usuario["progresso"]:
                                usuario["progresso"][f"tarefa_{i}"]=True
                                usuario["resumos"][f"tarefa_{i}"]=resumo_aprendido
                                usuario["streak"]+=1
                                break

                        salvar()
                        feitos = sum(1 for i,t in enumerate(usuario["cronograma"]) if t.get("materia")==materia_sel and f"tarefa_{i}" in usuario["progresso"])
                        total = sum(1 for t in usuario["cronograma"] if t.get("materia")==materia_sel)
                        st.balloons()
                        st.success(f"✅ {feitos}/{total} como concluído! Progresso atualizado! 🔥")
                        st.rerun()

        with tab_resumo:
            st.subheader("📈 Progresso Geral")

            # Progresso geral por matéria
            for mat in est.get("materias",{}).keys():
                tarefas_mat = [t for t in usuario["cronograma"] if t.get("materia")==mat]
                feitos_mat = sum(1 for i,t in enumerate(usuario["cronograma"]) if t.get("materia")==mat and f"tarefa_{i}" in usuario["progresso"])
                total_mat = len(tarefas_mat)
                st.write(f"**{mat}**")
                st.progress(feitos_mat/total_mat if total_mat else 0, text=f"{feitos_mat}/{total_mat} dias concluídos")

            st.divider()
            st.subheader("📝 Notas por disciplina - Evolução")

            for mat, dados in est.get("materias",{}).items():
                st.write(f"**{mat}** - {dados.get('assunto_atual','')}")
                c1,c2,c3,c4 = st.columns(4)
                with c1:
                    np = st.number_input(f"Mês passado {mat}", 0.0,10.0, float(dados.get("mes_passado",5.0)), key=f"np_{mat}")
                with c2:
                    na = st.number_input(f"Atual {mat}", 0.0,10.0, float(dados.get("mes_atual",6.0)), key=f"na_{mat}")
                with c3:
                    mn = st.number_input(f"Meta {mat}", 0.0,10.0, float(dados.get("meta_nota",9.0)), key=f"mn_{mat}")
                with c4:
                    evo = na - np
                    st.metric("Evolução", f"{na}", delta=f"{evo:.1f}")
                    if na >= mn:
                        st.success("Meta atingida! 🏆")
                    else:
                        st.caption(f"Falta {mn-na:.1f}")

                if st.button(f"Salvar notas {mat}", key=f"save_{mat}"):
                    est["materias"][mat]["mes_passado"]=np
                    est["materias"][mat]["mes_atual"]=na
                    est["materias"][mat]["meta_nota"]=mn
                    salvar()
                    st.success("Notas atualizadas!")

            # Gráfico geral
            if est.get("materias"):
                dados_graf = {mat: [d["mes_passado"], d["mes_atual"], d["meta_nota"]] for mat,d in est["materias"].items()}
                st.line_chart(dados_graf)
