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
    u.setdefault("progresso",{}) # f"tarefa_{i}": {"feito":True, "tempo_min":25, "resumo":""}
    u.setdefault("resumos",{})
    u.setdefault("streak",0)
    u.setdefault("tempo_total_mes",0)

FRASES = [
    "Bora evoluir hoje, {nome}? Seu objetivo é: {obj}",
    "{nome}, cada dia conta. Vamos pra {feitos}?",
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
                garantir(u); salvar()
                st.session_state.logado=True; st.session_state.usuario_logado=u; st.rerun()
            else: st.error("Errado")
    with t2:
        nome=st.text_input("Nome",key="c1")
        user=st.text_input("Usuário",key="c5")
        senha=st.text_input("Senha",type="password",key="c6")
        if st.button("Cadastrar"):
            st.session_state.usuarios[user]={"nome":nome,"senha":senha,"perfil_academico":{"nivel":"Ensino Médio","status":"Em andamento"},"areas":{"Estudos":{"objetivo":"","materias":{}}},"cronograma":[],"progresso":{},"resumos":{},"streak":0,"tempo_total_mes":0}
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

        # LEMBRETE DE PROVA
        for mat, dados in usuario["areas"]["Estudos"]["materias"].items():
            try:
                data_prova = date.fromisoformat(dados.get("dia_prova",""))
                dias_falta = (data_prova - date.today()).days
                if 0 <= dias_falta <= 7:
                    st.warning(f"⚠️ Lembrete: Prova de **{mat}** em **{dias_falta} dias** ({data_prova.strftime('%d/%m')}) - Assunto: {dados.get('assunto_atual','')}")
                elif dias_falta < 0:
                    st.error(f"⏰ Prova de {mat} já passou em {data_prova.strftime('%d/%m')} - atualize a data!")
            except: pass

        # TIMER APARECENDO NO INÍCIO
        if st.session_state.timer_inicio and st.session_state.materia_em_estudo:
            tempo = datetime.now() - st.session_state.timer_inicio
            with st.container(border=True):
                st.write(f"⏱️ Você está estudando **{st.session_state.materia_em_estudo}** agora")
                st.write(f"Tempo: {str(tempo).split('.')[0]}")
                if st.button("Ir para concluir"): st.session_state.pagina="Acadêmico"; st.rerun()

        obj = usuario["areas"]["Estudos"].get("objetivo") or "seus estudos"
        with st.container(border=True):
            st.write(f"📅 Hoje, {date.today().strftime('%d/%m/%Y')}")
            st.subheader(random.choice(FRASES).format(nome=usuario['nome'].split()[0], obj=obj, feitos=f"{len(usuario['progresso'])}/{len(usuario['cronograma'])}"))

        st.subheader("Seus cartões")
        for area_nome, dados_area in usuario["areas"].items():
            objetivo = dados_area.get("objetivo") or "Defina em Perfil"
            with st.container(border=True):
                st.write(f"**{area_nome}**")
                st.write(f'🎯 Objetivo: "{objetivo}"')
                # Mostra por matéria separado
                for mat in dados_area.get("materias",{}).keys():
                    tarefas_mat = [t for t in usuario["cronograma"] if t.get("materia")==mat]
                    feitos_mat = sum(1 for i,t in enumerate(usuario["cronograma"]) if t.get("materia")==mat and f"tarefa_{i}" in usuario["progresso"])
                    st.write(f" 📚 {mat}: **{feitos_mat}/{len(tarefas_mat)} dias** concluídos")
                    st.progress(feitos_mat/len(tarefas_mat) if tarefas_mat else 0)

    elif st.session_state.pagina=="Config":
        st.header("⚙️ Perfil")
        perfil=usuario["perfil_academico"]
        nivel=st.selectbox("Nível",["Ensino Fundamental","Ensino Médio","Ensino Superior","Cursos livres"], index=1)
        objetivo=st.text_input("Objetivo geral", value=usuario["areas"]["Estudos"].get("objetivo",""), placeholder="Ex: Passar no ENEM, Tirar 10 em Matemática")
        if st.button("Salvar"):
            USUARIOS[LOGADO]["perfil_academico"]["nivel"]=nivel
            USUARIOS[LOGADO]["areas"]["Estudos"]["objetivo"]=objetivo
            salvar(); st.success("Salvo!")

    else:
        st.header("🎓 Acadêmico")
        est = usuario["areas"]["Estudos"]
        tab_mat, tab_estudar, tab_resumo = st.tabs(["📚 Minhas Matérias","✏️ Estudar Agora","📈 Resumo Geral"])

        with tab_mat:
            st.subheader("Adicionar nova matéria")
            st.caption("Pode adicionar quantas quiser: Matemática, Python, etc.")
            nome_materia = st.text_input("Nome da matéria", placeholder="Ex: Matemática, Python", key="nova_mat_final")
            col1,col2=st.columns(2)
            with col1: assunto=st.text_input("Assunto atual", placeholder="Ex: Funções, Bhaskara", key="assunto_final")
            with col2: dia_prova=st.date_input("Dia da prova", value=date.today()+timedelta(days=7), key="prova_final")

            if st.button("Adicionar matéria", type="primary"):
                if not nome_materia:
                    st.warning("Digite o nome")
                else:
                    garantir(LOGADO)
                    # NÃO APAGA AS OUTRAS
                    USUARIOS[LOGADO]["areas"]["Estudos"]["materias"][nome_materia]={
                        "assunto_atual": assunto,
                        "dia_prova": dia_prova.isoformat(),
                        "semestre_passado": 6.0,
                        "semestre_atual": 7.0,
                        "meta_nota": 10.0
                    }
                    # Cria 5 dias SÓ para essa matéria
                    for i in range(5):
                        USUARIOS[LOGADO]["cronograma"].append({
                            "area":"Estudos",
                            "materia": nome_materia,
                            "dia": (date.today()+timedelta(days=i)).strftime('%d/%m'),
                            "texto": f"{nome_materia}: {assunto}"
                        })
                    salvar()
                    st.success(f"✅ {nome_materia} adicionada! Agora você tem {len(USUARIOS[LOGADO]['areas']['Estudos']['materias'])} matérias")
                    st.rerun()

            st.divider()
            st.write(f"**Você tem {len(est.get('materias',{}))} matérias:**")
            for mat, dados in est.get("materias",{}).items():
                with st.container(border=True):
                    st.write(f"**{mat}** | Assunto: {dados.get('assunto_atual','')} | Prova: {dados.get('dia_prova','')}")

        with tab_estudar:
            if not est.get("materias"):
                st.info("Adicione uma matéria na aba anterior")
            else:
                materia_sel=st.selectbox("Qual vai estudar?", list(est["materias"].keys()))

                dados_mat=est["materias"][materia_sel]
                st.write(f"📌 **{materia_sel}** - Assunto: {dados_mat.get('assunto_atual','')}")

                # CONTEÚDO DA IA JÁ APARECE AQUI
                st.divider()
                st.subheader(f"📚 IA preparou para {materia_sel}")
                st.info(f"**Resumo da web:** {materia_sel} - {dados_mat.get('assunto_atual','')} precisa de foco. Dica: estude 25min e revise.")
                st.link_button(f"🎥 Vídeos de {materia_sel}", f"https://www.youtube.com/results?search_query={materia_sel}+{dados_mat.get('assunto_atual','')}")
                st.link_button(f"📄 PDF grátis de {materia_sel}", f"https://www.google.com/search?q={materia_sel}+pdf")

                st.divider()
                st.subheader("⏱️ Estudo")

                if st.session_state.timer_inicio is None:
                    if st.button(f"▶️ Começar a estudar {materia_sel} agora", type="primary"):
                        st.session_state.timer_inicio=datetime.now()
                        st.session_state.materia_em_estudo=materia_sel
                        st.rerun()
                else:
                    tempo=datetime.now()-st.session_state.timer_inicio
                    st.write(f"⏱️ Estudando **{st.session_state.materia_em_estudo}** há: **{str(tempo).split('.')[0]}**")

                    resumo=st.text_area("✍️ O que você aprendeu?", placeholder="Ex: Aprendi que função...", key=f"resumo_{materia_sel}", height=120)

                    col1,col2=st.columns(2)
                    with col1:
                        if st.button("⏹️ Parar e concluir", type="primary"):
                            if not resumo.strip():
                                st.warning("Escreve o que aprendeu!")
                            else:
                                tempo_min = int(tempo.total_seconds()/60) if tempo.total_seconds()>60 else 1
                                # Salva tempo
                                for i,t in enumerate(USUARIOS[LOGADO]["cronograma"]):
                                    if t.get("materia")==materia_sel and f"tarefa_{i}" not in USUARIOS[LOGADO]["progresso"]:
                                        USUARIOS[LOGADO]["progresso"][f"tarefa_{i}"]={"feito":True,"tempo_min":tempo_min,"resumo":resumo,"data":date.today().isoformat()}
                                        USUARIOS[LOGADO]["tempo_total_mes"]=USUARIOS[LOGADO].get("tempo_total_mes",0)+tempo_min
                                        break
                                st.session_state.timer_inicio=None
                                st.session_state.materia_em_estudo=None
                                salvar()
                                st.balloons()
                                st.success(f"✅ Concluído! Você estudou {tempo_min} min. Seu progresso de {materia_sel} atualizou!")
                                st.rerun()
                    with col2:
                        if st.button("Cancelar"):
                            st.session_state.timer_inicio=None
                            st.session_state.materia_em_estudo=None
                            st.rerun()

        with tab_resumo:
            st.subheader("📈 Tempo de estudo do mês")
            tempo_total=usuario.get("tempo_total_mes",0)
            st.metric("Tempo total estudado esse mês", f"{tempo_total} min", f"{tempo_total//60}h {tempo_total%60}min")

            # Comparação meses (simulado por enquanto)
            st.write("Comparação: Mês passado vs Atual")
            st.bar_chart({"Mês passado": 120, "Este mês": tempo_total})

            st.divider()
            st.subheader("📝 Notas por disciplina")

            for mat, dados in est.get("materias",{}).items():
                st.write(f"**{mat}** - {dados.get('assunto_atual','')}")
                c1,c2,c3=st.columns(3)
                with c1:
                    np=st.number_input(f"Semestre passado {mat}",0.0,10.0,float(dados.get("semestre_passado",5.0)),key=f"npf_{mat}")
                with c2:
                    na=st.number_input(f"Semestre atual {mat}",0.0,10.0,float(dados.get("semestre_atual",6.0)),key=f"naf_{mat}")
                with c3:
                    mn=st.number_input(f"Meta {mat}",0.0,10.0,float(dados.get("meta_nota",10.0)),key=f"mnf_{mat}")

                evo = na - np
                if na >= mn:
                    st.success(f"🏆 Meta atingida em {mat}! Parabéns!")
                else:
                    # LÓGICA QUE FAZ SENTIDO
                    falta = mn - na
                    if falta <=1:
                        plano = f"Quase lá! Revise {dados.get('assunto_atual','')} 30min por dia"
                    elif falta <=3:
                        plano = f"Meta pra alcançar: Estudar {mat} 1h extra por dia + fazer simulados"
                    else:
                        plano = f"Meta pra alcançar: Foco total em {mat}, 2h/dia + resumo + exercícios"

                    st.warning(f"📉 Evolução: {np} → {na} ( {evo:+.1f} ) | {plano}")

                if st.button(f"Salvar notas {mat}", key=f"saven_{mat}"):
                    USUARIOS[LOGADO]["areas"]["Estudos"]["materias"][mat]["semestre_passado"]=np
                    USUARIOS[LOGADO]["areas"]["Estudos"]["materias"][mat]["semestre_atual"]=na
                    USUARIOS[LOGADO]["areas"]["Estudos"]["materias"][mat]["meta_nota"]=mn
                    salvar()
                    st.success("Salvo!")
                st.divider()
