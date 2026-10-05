import streamlit as st
import json, os
from datetime import date, timedelta
from PIL import Image, ImageDraw, ImageFont
import random

ARQUIVO = "banco_usuarios.json"
def carregar():
    if os.path.exists(ARQUIVO):
        try:
            with open(ARQUIVO, "r", encoding="utf-8") as f: return json.load(f)
        except: return {}
    return {}
def salvar():
    with open(ARQUIVO, "w", encoding="utf-8") as f:
        json.dump(st.session_state.usuarios, f, indent=4, ensure_ascii=False)

if "usuarios" not in st.session_state: st.session_state.usuarios = carregar()
if "logado" not in st.session_state:
    st.session_state.logado=False
    st.session_state.usuario_logado=""
    st.session_state.pagina="Início"

def criar_imagem_frase(frase, nome):
    img = Image.new('RGB', (1080, 600), color=(108, 92, 231))
    draw = ImageDraw.Draw(img)
    # Fundo degradê simples
    draw.rectangle([(0,0),(1080,600)], fill=(108,92,231))
    draw.text((50,50), f"EvoluiAI para {nome}", fill=(255,255,255))
    # Quebra frase em linhas
    palavras = frase.split()
    linhas=[]
    linha_atual=""
    for p in palavras:
        if len(linha_atual+p) < 35:
            linha_atual+=p+" "
        else:
            linhas.append(linha_atual)
            linha_atual=p+" "
    linhas.append(linha_atual)
    y=150
    for l in linhas:
        draw.text((50, y), l, fill=(255,255,255))
        y+=50
    draw.text((50, 500), f"{date.today().strftime('%d/%m/%Y')} - Sua meta do dia", fill=(220,220,255))
    caminho="frase_do_dia.png"
    img.save(caminho)
    return caminho

def criar_imagem_cronograma(todas_tarefas, nome):
    qtd = len(todas_tarefas)
    altura = 120 + qtd*80
    img = Image.new('RGB', (800, altura), color=(255,255,255))
    draw = ImageDraw.Draw(img)
    draw.rectangle([(0,0),(800,80)], fill=(108,92,231))
    draw.text((20,20), f"PLANO SEMANAL - {nome}", fill=(255,255,255))
    y=100
    for i, t in enumerate(todas_tarefas):
        cor = (240,240,255) if i%2==0 else (255,255,255)
        draw.rectangle([(10,y),(790,y+70)], fill=cor, outline=(200,200,200))
        draw.text((20,y+5), f"{t['area']} - {t['dia']}", fill=(108,92,231))
        draw.text((20,y+30), t['texto'][:70], fill=(0,0,0))
        y+=80
    caminho="cronograma_multi.png"
    img.save(caminho)
    return caminho

FRASES_IA = {
    "Estudos": ["{nome}, hoje é dia de dominar {detalhe}. Sua nota vai de {nota_atual} para {meta_nota}!",
                "Foco, {nome}! Cada página de {detalhe} te aproxima da sua meta {meta_nota}"],
    "Saúde": ["{nome}, seu corpo é seu templo. Hoje é dia de {detalhe} por você!",
              "Saúde em dia, {nome}! {detalhe} hoje para evoluir!"],
    "Financeira": ["{nome}, hoje você dá um passo para sua liberdade: {detalhe}",
                   "Meta financeira: {detalhe}. Vamos lá, {nome}!"]
}

st.set_page_config(page_title="EvoluiAI Multi", layout="centered")

if not st.session_state.logado:
    st.title("🚀 EvoluiAI")
    a1,a2 = st.tabs(["Entrar","Cadastrar"])
    with a1:
        u=st.text_input("Usuário",key="l1")
        s=st.text_input("Senha",type="password",key="l2")
        if st.button("Entrar"):
            if u in st.session_state.usuarios and st.session_state.usuarios[u]["senha"]==s:
                st.session_state.logado=True
                st.session_state.usuario_logado=u
                st.session_state.pagina="Início"
                st.rerun()
            else: st.error("Errado")
    with a2:
        nome=st.text_input("Nome",key="c1")
        user=st.text_input("Usuário",key="c5")
        email=st.text_input("E-mail",key="c4")
        senha=st.text_input("Senha",type="password",key="c6")
        if st.button("Cadastrar"):
            if not nome or not user or not senha: st.warning("Preenche")
            elif user in st.session_state.usuarios: st.warning("Já existe")
            else:
                st.session_state.usuarios[user]={"nome":nome,"email":email,"senha":senha,"avatar_path":None,"areas":{},"cronograma":[],"progresso":{},"resumos":{},"streak":0}
                salvar()
                st.success("Cadastrado!")
else:
    usuario = st.session_state.usuarios[st.session_state.usuario_logado]

    with st.sidebar:
        # AVATAR COMO FOTO
        if usuario.get("avatar_path") and os.path.exists(usuario.get("avatar_path")):
            st.image(usuario.get("avatar_path"), width=100)
        else:
            st.write("👤 Sem foto")
        st.write(f"**{usuario['nome']}**")
        st.divider()
        if st.button("🏠 Início", use_container_width=True): st.session_state.pagina="Início"; st.rerun()
        if st.button("📚 Meu Plano Multi", use_container_width=True): st.session_state.pagina="Plano"; st.rerun()
        if st.button("⚙️ Config / Avatar", use_container_width=True): st.session_state.pagina="Config"; st.rerun()
        if st.button("Sair"): st.session_state.logado=False; st.rerun()

    # ===== INÍCIO COM FRASE COMO IMAGEM =====
    if st.session_state.pagina=="Início":
        st.title(f"Início - Olá {usuario['nome'].split()[0]}!")

        if not usuario.get("areas"):
            st.info("Você ainda não escolheu suas áreas. Vamos começar?")
            if st.button("Escolher minhas áreas"): st.session_state.pagina="Plano"; st.rerun()
        else:
            # PERGUNTA: QUAL ÁREA QUER MELHORAR MAIS HOJE?
            area_foco = st.selectbox("Hoje, qual área você quer focar mais?", list(usuario["areas"].keys()))

            dados_foco = usuario["areas"][area_foco]
            # IA cria frase baseada na área foco
            if area_foco=="Estudos":
                template = random.choice(FRASES_IA["Estudos"])
                frase = template.format(nome=usuario['nome'].split()[0], detalhe=dados_foco.get('materia','seus estudos'), nota_atual=dados_foco.get('notas',{}).get('mes_atual',0), meta_nota=dados_foco.get('notas',{}).get('meta_nota',10))
            else:
                template = random.choice(FRASES_IA.get(area_foco, ["{nome}, bora evoluir em {detalhe}"]))
                frase = template.format(nome=usuario['nome'].split()[0], detalhe=dados_foco.get('objetivo','sua meta'), nota_atual="", meta_nota="")

            st.subheader("💬 Frase motivacional da IA (como imagem)")
            caminho_frase = criar_imagem_frase(frase, usuario['nome'])
            st.image(caminho_frase, caption="Frase do dia - Baixe e poste!")
            with open(caminho_frase, "rb") as f:
                st.download_button("📥 Baixar frase como imagem", f, file_name="frase_motivacional.png", mime="image/png")

            st.divider()
            st.subheader("📊 Progresso por área - Qual é sua meta do dia?")
            for nome_area, dados in usuario["areas"].items():
                st.write(f"**{nome_area}**")
                # Calcula progresso só dessa área
                tarefas_area = [t for t in usuario.get("cronograma",[]) if t["area"]==nome_area]
                total_area = len(tarefas_area)
                feitos_area = sum(1 for i, t in enumerate(usuario.get("cronograma",[])) if t["area"]==nome_area and f"tarefa_{i}" in usuario.get("progresso",{}))

                if total_area>0:
                    pct = feitos_area/total_area
                    st.progress(pct, text=f"{feitos_area}/{total_area} - Meta dia: {dados.get('meta_dia','Fazer 1 tarefa')}")
                else:
                    st.write(f"Meta: {dados.get('meta_dia','Definir')}")

                # Se for estudo mostra evolução nota
                if nome_area=="Estudos" and "notas" in dados:
                    n = dados["notas"]
                    col1,col2,col3 = st.columns(3)
                    with col1: st.metric("Mês passado", n.get("mes_passado",0))
                    with col2: st.metric("Atual", n.get("mes_atual",0), delta=n.get("mes_atual",0)-n.get("mes_passado",0))
                    with col3: st.metric("Meta", n.get("meta_nota",10), delta="Falta" if n.get("mes_atual",0) < n.get("meta_nota",10) else "Atingida!")

    # ===== PLANO MULTI ÁREA =====
    elif st.session_state.pagina=="Plano":
        st.header("📚 Meu Plano Multi-Área")

        if not usuario.get("areas"):
            st.write("Escolha 1 ou mais áreas que você quer evoluir:")
            areas_escolhidas = st.multiselect("Quais áreas?", ["Estudos","Saúde","Financeira","Espiritual","Carreira"], default=["Estudos"])

            areas_temp = {}
            for area in areas_escolhidas:
                st.divider()
                st.subheader(f"Configurar {area}")
                if area=="Estudos":
                    nivel = st.selectbox(f"Nível escolaridade ({area})", ["Fundamental","Médio","Superior","Concurso"], key=f"niv_{area}")
                    curso = st.text_input(f"Qual curso superior? (se for Superior)", key=f"curso_{area}") if nivel=="Superior" else ""
                    materia = st.text_input(f"Matéria atual de {area}?", key=f"mat_{area}")
                    meta_estudo = st.text_input(f"Meta em {area}? Ex: Aprender Constituição", key=f"meta_{area}")
                    meta_dia = st.text_input(f"Meta do DIA em {area}? Ex: Estudar 2h", value="Estudar 1h", key=f"metadia_{area}")
                    topicos = st.text_area(f"O que deve aprender sobre {materia}?", placeholder="Artigo 5º, Remédios...", key=f"top_{area}")
                    c1,c2,c3 = st.columns(3)
                    with c1: np = st.number_input(f"Nota mês passado ({area})", 0.0, 10.0, 5.0, key=f"np_{area}")
                    with c2: na = st.number_input(f"Nota atual ({area})", 0.0, 10.0, 6.0, key=f"na_{area}")
                    with c3: mn = st.number_input(f"Meta nota ({area})", 0.0, 10.0, 9.0, key=f"mn_{area}")

                    areas_temp[area] = {"nivel":nivel,"curso":curso,"materia":materia,"meta":meta_estudo,"meta_dia":meta_dia,"topicos":topicos,"notas":{"mes_passado":np,"mes_atual":na,"meta_nota":mn},"objetivo":meta_estudo,"plano_acao":f"Plano IA: Teoria {materia} + Revisão + Simulado para sair de {na} para {mn}"}

                else:
                    obj = st.text_input(f"Qual seu objetivo em {area}?", key=f"obj_{area}", placeholder=f"Ex: Perder 5kg em {area}")
                    meta_dia = st.text_input(f"Meta do DIA em {area}?", value="Fazer 30min", key=f"metadia_{area}")
                    plano = st.text_area(f"Plano de ação para {area}?", placeholder="O que a IA deve criar?", key=f"plano_{area}")
                    areas_temp[area] = {"objetivo":obj,"meta_dia":meta_dia,"plano_acao": plano if plano else f"IA: Foco em {obj} com {meta_dia} todo dia", "meta":obj}

            if st.button("✨ IA Criar metas e plano de ação para todas áreas", type="primary"):
                if not areas_temp: st.warning("Escolhe pelo menos 1 área")
                else:
                    # GERA CRONOGRAMA MULTI COMEÇANDO HOJE
                    hoje=date.today()
                    todas_tarefas=[]
                    dia_idx=0
                    for nome_area, dados in areas_temp.items():
                        # 2 tarefas por área na semana
                        for j in range(2):
                            data = hoje + timedelta(days=dia_idx)
                            texto = f"{dados.get('materia', dados.get('objetivo','Meta'))} - {dados.get('meta_dia','Estudar')}"
                            todas_tarefas.append({"area":nome_area,"dia":data.strftime('%d/%m'),"texto":texto,"data":data.isoformat()})
                            dia_idx+=1

                    st.session_state.usuarios[st.session_state.usuario_logado]["areas"]=areas_temp
                    st.session_state.usuarios[st.session_state.usuario_logado]["cronograma"]=todas_tarefas
                    st.session_state.usuarios[st.session_state.usuario_logado]["progresso"]={}
                    st.session_state.usuarios[st.session_state.usuario_logado]["resumos"]={}
                    salvar()
                    st.success("Plano multi-área criado! Vai pro Início ver sua frase como imagem!")
                    st.rerun()
        else:
            st.write("Suas áreas ativas:")
            for nome_area, dados in usuario["areas"].items():
                st.info(f"**{nome_area}**: {dados.get('meta','')} | Plano IA: {dados.get('plano_acao','')}")

            caminho = criar_imagem_cronograma(usuario.get("cronograma",[]), usuario["nome"])
            st.image(caminho)
            with open(caminho,"rb") as f:
                st.download_button("📥 Baixar cronograma semanal em imagem", f, file_name="cronograma_semanal.png")

            st.divider()
            st.subheader(f"📅 Tarefas começando hoje {date.today().strftime('%d/%m')}")

            for i, tarefa in enumerate(usuario.get("cronograma",[])):
                chave=f"tarefa_{i}"
                ja=usuario.get("progresso",{}).get(chave,False)
                with st.expander(f"{'✅' if ja else '⏳'} [{tarefa['area']}] {tarefa['dia']} - {tarefa['texto']}", expanded=not ja):
                    if ja:
                        st.success("Concluído!")
                        if chave in usuario.get("resumos",{}): st.write(f"Resumo: {usuario['resumos'][chave]}")
                        if st.button("Refazer", key=f"ref_{i}"):
                            del st.session_state.usuarios[st.session_state.usuario_logado]["progresso"][chave]
                            salvar(); st.rerun()
                    else:
                        # Se for estudo pede nota e resumo
                        if tarefa['area']=="Estudos":
                            resumo=st.text_area(f"O que aprendeu sobre {usuario['areas']['Estudos'].get('materia','')}?", key=f"res_{i}", height=80)
                            if st.button(f"✅ Concluir dia e salvar resumo", key=f"conc_{i}", type="primary"):
                                if not resumo.strip(): st.warning("Escreve resumo!")
                                else:
                                    st.session_state.usuarios[st.session_state.usuario_logado]["resumos"][chave]=resumo
                                    st.session_state.usuarios[st.session_state.usuario_logado]["progresso"][chave]=True
                                    salvar()
                                    st.balloons(); st.rerun()
                        else:
                            if st.button(f"✅ Concluir {tarefa['area']}", key=f"conc_{i}", type="primary"):
                                st.session_state.usuarios[st.session_state.usuario_logado]["progresso"][chave]=True
                                salvar(); st.rerun()

            if st.button("🔄 Refazer todas áreas"):
                st.session_state.usuarios[st.session_state.usuario_logado]["areas"]={}
                salvar(); st.rerun()

    else: # CONFIG
        st.header("⚙️ Configurações")
        st.subheader("Foto de perfil (Avatar)")
        foto = st.file_uploader("Envie sua foto", type=["jpg","png","jpeg"])
        if foto:
            caminho_foto = f"avatar_{st.session_state.usuario_logado}.png"
            with open(caminho_foto, "wb") as f:
                f.write(foto.getbuffer())
            st.session_state.usuarios[st.session_state.usuario_logado]["avatar_path"]=caminho_foto
            salvar()
            st.success("Foto atualizada!")
            st.image(caminho_foto, width=150)

        st.divider()
        st.subheader("Alterar dados")
        novo_nome = st.text_input("Nome", value=usuario["nome"])
        novo_email = st.text_input("E-mail", value=usuario.get("email",""))
        nova_senha = st.text_input("Nova senha", type="password")

        if st.button("Salvar"):
            st.session_state.usuarios[st.session_state.usuario_logado]["nome"]=novo_nome
            st.session_state.usuarios[st.session_state.usuario_logado]["email"]=novo_email
            if nova_senha.strip(): st.session_state.usuarios[st.session_state.usuario_logado]["senha"]=nova_senha
            salvar()
            st.success("Salvo!")
