import streamlit as st
import json, os
from datetime import date, timedelta
from PIL import Image, ImageDraw, ImageFont
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

# IMAGEM DA FRASE CORRIGIDA - MENOR E LETRA GRANDE
def criar_imagem_frase(frase, nome):
    W,H = 700, 400
    img = Image.new('RGB',(W,H), color=(108,92,231))
    draw = ImageDraw.Draw(img)
    # Tenta fonte grande
    try:
        # Se não tiver arial, usa default grande
        font_titulo = ImageFont.load_default()
        font_frase = ImageFont.load_default()
    except:
        font_titulo = None
        font_frase = None

    draw.rectangle([(0,0),(W,90)], fill=(80,60,200))
    draw.text((20,20), f"EvoluiAI • {date.today().strftime('%d/%m/%Y')}", fill=(255,255,255))
    draw.text((20,55), f"Para: {nome}", fill=(230,230,255))

    # Quebra em linhas de 30 chars e letra maior
    y=120
    # Desenha frase com quebra manual
    palavras=frase.split()
    linha=""
    for p in palavras:
        test = linha + " " + p if linha else p
        if len(test) > 28:
            draw.text((20,y), linha, fill=(255,255,255))
            y+=35
            linha=p
        else:
            linha=test
    if linha:
        draw.text((20,y), linha, fill=(255,255,255))

    draw.text((20, H-30), "Sua meta do dia • EvoluiAI 🚀", fill=(200,200,255))
    caminho="frase_dia.png"
    img.save(caminho)
    return caminho

ANIMES = ["😀 Foto Real","🧑‍🎓 Anime Estudiosa","👩‍💻 Anime Dev","🔥 Anime Goku","🌸 Anime Sakura","⚡ Anime Naruto","🎯 Anime Luffy"]

st.set_page_config(page_title="EvoluiAI Acadêmico", layout="wide")

if not st.session_state.logado:
    st.title("🚀 EvoluiAI")
    a1,a2=st.tabs(["Entrar","Cadastrar"])
    with a1:
        u=st.text_input("Usuário",key="l1")
        s=st.text_input("Senha",type="password",key="l2")
        if st.button("Entrar"):
            if u in st.session_state.usuarios and st.session_state.usuarios[u]["senha"]==s:
                st.session_state.logado=True
                st.session_state.usuario_logado=u
                st.rerun()
            else: st.error("Errado")
    with a2:
        nome=st.text_input("Nome",key="c1")
        user=st.text_input("Usuário",key="c5")
        senha=st.text_input("Senha",type="password",key="c6")
        if st.button("Cadastrar"):
            st.session_state.usuarios[user]={"nome":nome,"senha":senha,"avatar_path":None,"avatar_anime":"😀 Foto Real","areas":{"Estudos":{"materias":{},"cursos":[],"certificados":[],"topicos":[],"plano_semana":[]}},"cronograma":[],"progresso":{},"resumos":{},"streak":0}
            salvar()
            st.success("Cadastrado!")
else:
    usuario=st.session_state.usuarios[st.session_state.usuario_logado]

    with st.sidebar:
        if usuario.get("avatar_path") and os.path.exists(usuario.get("avatar_path")):
            st.image(usuario.get("avatar_path"), width=120)
        else:
            st.write(f"# {usuario.get('avatar_anime','😀')}")
        st.write(f"**{usuario['nome']}**")
        st.divider()
        if st.button("🏠 Início", use_container_width=True): st.session_state.pagina="Início"; st.rerun()
        if st.button("🎓 Área Acadêmica", use_container_width=True): st.session_state.pagina="Acadêmico"; st.rerun()
        if st.button("⚙️ Config", use_container_width=True): st.session_state.pagina="Config"; st.rerun()
        if st.button("Sair"): st.session_state.logado=False; st.rerun()

    if st.session_state.pagina=="Início":
        st.title(f"Olá, {usuario['nome'].split()[0]}! 👋")

        # FRASE DO DIA COMO IMAGEM PEQUENA E LEGÍVEL
        frase_hoje = f"Você consegue! Hoje é dia de evoluir em {list(usuario['areas'].keys())[0] if usuario['areas'] else 'seus estudos'}!"
        if usuario['areas'].get('Estudos',{}).get('materias'):
            mat = list(usuario['areas']['Estudos']['materias'].keys())[0]
            frase_hoje = f"{usuario['nome'].split()[0]}, hoje é dia de dominar {mat}. Foco total!"

        st.subheader("💬 Motivação do dia")
        col_img, col_txt = st.columns([1,1])
        with col_img:
            caminho = criar_imagem_frase(frase_hoje, usuario['nome'])
            st.image(caminho, caption=f"{date.today().strftime('%d/%m/%Y')} - Frase do dia")
            with open(caminho,"rb") as f:
                st.download_button("📥 Baixar imagem", f, file_name="frase.png")
        with col_txt:
            st.write(f"**{frase_hoje}**")
            st.write(f"📅 {date.today().strftime('%A, %d/%m/%Y')}")

        st.divider()
        st.subheader("📊 Seus cartões por área - Progresso")
        cols = st.columns(len(usuario['areas']) if usuario['areas'] else 1)
        for idx, (nome_area, dados) in enumerate(usuario['areas'].items()):
            with cols[idx % 3]:
                tarefas_area = [t for t in usuario.get("cronograma",[]) if t.get("area")==nome_area]
                feitos = sum(1 for i,t in enumerate(usuario.get("cronograma",[])) if t.get("area")==nome_area and f"tarefa_{i}" in usuario.get("progresso",{}))
                total = len(tarefas_area)
                pct = feitos/total if total>0 else 0
                with st.container(border=True):
                    st.write(f"**{nome_area}**")
                    st.write(f"🎯 Objetivo: {dados.get('objetivo','Definir') if nome_area!='Estudos' else list(dados.get('materias',{}).keys())[:2]}")
                    st.progress(pct, text=f"{feitos}/{total} do dia")
                    if st.button(f"Ver {nome_area}", key=f"ver_{nome_area}"):
                        st.session_state.pagina="Acadêmico"
                        st.rerun()

    elif st.session_state.pagina=="Acadêmico":
        st.header("🎓 Área Acadêmica - Completa")
        area_estudo = usuario["areas"].get("Estudos", {"materias":{},"cursos":[],"certificados":[],"topicos":[]})

        # Se ainda não tem matéria, cria
        if not area_estudo.get("materias"):
            st.info("Vamos configurar sua vida acadêmica")
            tipo = st.selectbox("Isso é o que?", ["Escola / Faculdade / Matérias","Curso livre / Curso online"])
            if tipo=="Escola / Faculdade / Matérias":
                qtd = st.number_input("Quantas matérias?",1,6,2)
                materias_temp={}
                for i in range(int(qtd)):
                    st.divider()
                    st.write(f"Matéria {i+1}")
                    nome_m = st.text_input(f"Nome matéria {i+1}", key=f"m_{i}", placeholder="Ex: Constitucional")
                    if nome_m:
                        c1,c2,c3 = st.columns(3)
                        with c1: np = st.number_input(f"Nota mês passado {nome_m}",0.0,10.0,5.0,key=f"np_{i}")
                        with c2: na = st.number_input(f"Nota atual {nome_m}",0.0,10.0,6.0,key=f"na_{i}")
                        with c3: mn = st.number_input(f"Meta {nome_m}",0.0,10.0,9.0,key=f"mn_{i}")
                        materias_temp[nome_m]={"mes_passado":np,"mes_atual":na,"meta_nota":mn}
                if st.button("Salvar matérias"):
                    st.session_state.usuarios[st.session_state.usuario_logado]["areas"]["Estudos"]["materias"]=materias_temp
                    salvar(); st.rerun()
            else:
                curso_nome = st.text_input("Nome do curso", placeholder="Ex: Python do Zero")
                if st.button("Adicionar curso"):
                    st.session_state.usuarios[st.session_state.usuario_logado]["areas"]["Estudos"]["cursos"].append(curso_nome)
                    salvar(); st.rerun()
        else:
            # ABAS QUE VOCÊ PEDIU
            tab1, tab2, tab3, tab4 = st.tabs(["📈 Evolução & Notas & Certificados","📚 Desenvolvimento","🗓️ Plano de Ação Semana 1","💬 Chat IA de Melhoria"])

            with tab1:
                st.subheader("Evolução de Notas")
                for mat, notas in area_estudo.get("materias",{}).items():
                    col1,col2,col3,col4 = st.columns(4)
                    with col1: st.metric(f"{mat} - Passado", notas.get("mes_passado",0))
                    with col2: st.metric(f"{mat} - Atual", notas.get("mes_atual",0), delta=notas.get("mes_atual",0)-notas.get("mes_passado",0))
                    with col3: st.metric(f"Meta {mat}", notas.get("meta_nota",10))
                    with col4:
                        if notas.get("mes_atual",0) >= notas.get("meta_nota",10):
                            st.success("Meta atingida! 🏆")
                        else:
                            st.warning(f"Falta {notas.get('meta_nota',10)-notas.get('mes_atual',0)} pts")

                # Gráfico com várias matérias
                if area_estudo.get("materias"):
                    st.line_chart(area_estudo["materias"])

                st.divider()
                st.subheader("🏆 Certificados - Conquistas de Cursos")
                curso_up = st.file_uploader("Envie seu certificado (PDF ou imagem)", type=["pdf","png","jpg"])
                nome_cert = st.text_input("Nome do certificado", placeholder="Ex: Curso Python - Concluído 2026")
                if st.button("Adicionar como conquista"):
                    if nome_cert:
                        area_estudo["certificados"].append(nome_cert)
                        st.session_state.usuarios[st.session_state.usuario_logado]["areas"]["Estudos"]["certificados"]=area_estudo["certificados"]
                        salvar()
                        st.success(f"Conquista adicionada: {nome_cert}!")
                for cert in area_estudo.get("certificados",[]):
                    st.write(f"🏅 {cert}")

            with tab2:
                st.subheader("Desenvolva sua disciplina")
                materia_selec = st.selectbox("Escolha a matéria/curso para estudar", list(area_estudo.get("materias",{}).keys()) + area_estudo.get("cursos",[]))

                st.write(f"**Você está estudando:** {materia_selec}")
                st.write(f"**Tópicos que deve aprender:** {area_estudo.get('topicos', 'Defina seus tópicos')}")

                st.divider()
                st.write("🎥 **Vídeos YouTube recomendados (IA)**")
                st.write(f"- Melhor vídeo de {materia_selec} para iniciantes - Canal Professor X")
                st.write(f"- {materia_selec} - Resumo em 20min que cai na prova")
                st.link_button(f"Buscar {materia_selec} no YouTube", f"https://www.youtube.com/results?search_query={materia_selec}")

                st.divider()
                st.write("📄 **Resumo do assunto da web (IA)**")
                st.info(f"Resumo IA: {materia_selec} é fundamental porque... Principais pontos: 1) Conceito, 2) Aplicação, 3) Exemplo prático. (Aqui depois conectamos com IA real)")

                st.divider()
                st.write("📚 **Livros PDF gratuitos**")
                st.write(f"- Apostila gratuita de {materia_selec} - PDF")
                st.link_button("Buscar livros gratuitos", f"https://www.google.com/search?q={materia_selec}+pdf+gratis")

                st.divider()
                st.write("✍️ **Seu resumo do que aprendeu**")
                resumo = st.text_area(f"Faça seu resumo de {materia_selec}", height=150, key=f"resumo_{materia_selec}", placeholder="O que você aprendeu hoje?")
                if st.button("Salvar resumo"):
                    chave = f"resumo_{materia_selec}_{date.today()}"
                    st.session_state.usuarios[st.session_state.usuario_logado]["resumos"][chave]=resumo
                    salvar()
                    st.success("Resumo salvo!")

            with tab3:
                st.subheader("Plano de Ação - Semana 1 criada pela IA")
                if not usuario.get("cronograma"):
                    if st.button("✨ IA Gerar cronograma Semana 1"):
                        # IA cria: segunda estudo, terça simulado...
                        cronograma_ia=[]
                        dias = ["Segunda","Terça","Quarta","Quinta","Sexta"]
                        acoes = ["Teoria + Anotações","Simulado gerado pela IA","Vídeo-aula + Resumo","Exercícios práticos","Revisão geral + Chat IA"]
                        for i, dia in enumerate(dias):
                            for mat in area_estudo.get("materias",{}).keys():
                                cronograma_ia.append({"area":"Estudos","dia":f"{dia} {(date.today()+timedelta(days=i)).strftime('%d/%m')}","texto":f"{acoes[i]} de {mat}","data":(date.today()+timedelta(days=i)).isoformat()})
                        st.session_state.usuarios[st.session_state.usuario_logado]["cronograma"]=cronograma_ia
                        salvar()
                        st.rerun()
                else:
                    for i, tarefa in enumerate(usuario.get("cronograma",[])):
                        chave=f"tarefa_{i}"
                        ja=usuario.get("progresso",{}).get(chave,False)
                        with st.container(border=True):
                            col1,col2 = st.columns([3,1])
                            with col1: st.write(f"{'✅' if ja else '⏳'} **{tarefa['dia']}** - {tarefa['texto']}")
                            with col2:
                                if not ja:
                                    if st.button("Concluir", key=f"c_{i}"):
                                        st.session_state.usuarios[st.session_state.usuario_logado]["progresso"][chave]=True
                                        salvar(); st.rerun()
                                else:
                                    st.write("Feito!")

            with tab4:
                st.subheader("💬 Chat IA - Como está seu desempenho?")
                st.write("Escreva como está indo e a IA monta um plano de melhoria")

                desempenho = st.text_area("Como está seu desempenho nos estudos?", placeholder="Ex: Estou com dificuldade em Constitucional, minha nota foi 6 e quero 9, não consigo focar...")

                if st.button("IA Analisar e criar plano de melhoria"):
                    if desempenho:
                        # Simulação IA
                        st.success("🤖 IA analisou seu desempenho:")
                        st.write(f"**Análise:** Você mencionou: '{desempenho}'")
                        st.write("**Plano de melhoria IA:**")
                        st.write("1. **Foco:** Dedique 2h extras na matéria com menor nota")
                        st.write("2. **Técnica:** Use Pomodoro 25min estudo / 5min pausa")
                        st.write("3. **Próxima semana:** Segunda - Revisão, Terça - Simulado focado nos erros")
                        st.write("4. **Meta ajustada:** Subir 1 ponto por mês")

                        # Cria novo plano baseado no chat
                        if st.button("Aplicar esse plano no meu cronograma"):
                            st.session_state.usuarios[st.session_state.usuario_logado]["cronograma"].append({"area":"Estudos","dia":f"Extra {date.today().strftime('%d/%m')}","texto":f"Plano melhoria: {desempenho[:30]}...","data":date.today().isoformat()})
                            salvar()
                            st.success("Plano aplicado!")

    else: # CONFIG
        st.header("⚙️ Config - Avatar")
        col1,col2 = st.columns(2)
        with col1:
            st.subheader("Foto real")
            foto = st.file_uploader("Envie sua foto", type=["jpg","png","jpeg"])
            if foto:
                caminho=f"avatar_{st.session_state.usuario_logado}.png"
                with open(caminho,"wb") as f: f.write(foto.getbuffer())
                st.session_state.usuarios[st.session_state.usuario_logado]["avatar_path"]=caminho
                salvar()
                st.success("Foto atualizada!")
                st.image(caminho, width=150)
        with col2:
            st.subheader("Ou avatar anime")
            anime = st.selectbox("Escolha seu anime", ANIMES)
            if st.button("Usar avatar anime"):
                st.session_state.usuarios[st.session_state.usuario_logado]["avatar_anime"]=anime
                st.session_state.usuarios[st.session_state.usuario_logado]["avatar_path"]=None
                salvar()
                st.success(f"Avatar {anime} selecionado!")
