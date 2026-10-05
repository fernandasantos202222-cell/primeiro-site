import streamlit as st
import json, os
from datetime import date, timedelta
from PIL import Image, ImageDraw
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
    st.session_state.logado = False
    st.session_state.usuario_logado = ""
if "pagina" not in st.session_state:
    st.session_state.pagina = "Início"

def criar_imagem_cronograma(cronograma, materia, nome):
    img = Image.new('RGB', (800, 600), color=(255,255,255))
    draw = ImageDraw.Draw(img)
    draw.rectangle([(0,0),(800,80)], fill=(108,92,231))
    draw.text((20,20), f"CRONOGRAMA - {materia.upper()}", fill=(255,255,255))
    draw.text((20,50), f"{nome} | {date.today().strftime('%d/%m/%Y')}", fill=(255,255,255))
    y=100
    for i, tarefa in enumerate(cronograma):
        cor = (240,240,255) if i%2==0 else (255,255,255)
        draw.rectangle([(10,y),(790,y+70)], fill=cor, outline=(200,200,200))
        draw.text((20,y+10), f"DIA {i+1}", fill=(108,92,231))
        draw.text((20,y+30), tarefa[:75], fill=(0,0,0))
        y+=80
    caminho="cronograma.png"
    img.save(caminho)
    return caminho

FRASES_IA = [
    "Hoje é o dia que seu futuro vai agradecer. Bora, {nome}!",
    "{nome}, sua meta de {materia} está mais perto do que ontem. Não para agora!",
    "Foco total, {nome}! Cada resumo que você faz é um degrau para sua aprovação.",
    "Você já é melhor que 90% que só planeja e não faz. Continue, {nome}!",
    "Lembre-se do seu porquê. Você quer {materia} para mudar sua vida, {nome}!"
]

AVATARES = ["😀","😎","🤓","👩‍🎓","👨‍🎓","🚀","🔥","🧠","📚","💪","🎯","🦁"]

st.set_page_config(page_title="EvoluiAI", layout="centered")

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
        user=st.text_input("Usuário (sem espaço)",key="c5")
        email=st.text_input("E-mail",key="c4")
        senha=st.text_input("Senha",type="password",key="c6")
        if st.button("Cadastrar"):
            if not nome or not user or not senha: st.warning("Preenche")
            elif user in st.session_state.usuarios: st.warning("Já existe")
            else:
                st.session_state.usuarios[user]={"nome":nome,"email":email,"senha":senha,"avatar":"🚀","perfil":None,"cronograma":[],"progresso":{},"resumos":{},"notas":{"mes_passado":0,"mes_atual":0,"meta_nota":10},"topicos":[],"streak":0}
                salvar()
                st.success("Cadastrado!")
else:
    usuario = st.session_state.usuarios[st.session_state.usuario_logado]
    # Corrige contas antigas
    for k,v in {"progresso":{}, "resumos":{}, "streak":0, "avatar":"🚀", "notas":{"mes_passado":0,"mes_atual":0,"meta_nota":10}, "topicos":[]}.items():
        if k not in usuario: st.session_state.usuarios[st.session_state.usuario_logado][k]=v

    # MENU LATERAL
    with st.sidebar:
        st.write(f"{usuario.get('avatar','🚀')} **{usuario['nome']}**")
        st.write(f"@{st.session_state.usuario_logado}")
        st.divider()
        if st.button("🏠 Início", use_container_width=True): st.session_state.pagina="Início"; st.rerun()
        if st.button("📚 Meu Plano / Estudos", use_container_width=True): st.session_state.pagina="Plano"; st.rerun()
        if st.button("⚙️ Configurações", use_container_width=True): st.session_state.pagina="Config"; st.rerun()
        st.divider()
        if st.button("Sair"): st.session_state.logado=False; st.rerun()

    # ===== PÁGINA INÍCIO =====
    if st.session_state.pagina=="Início":
        st.title(f"Bem-vindo de volta, {usuario['nome']}! {usuario.get('avatar','🚀')}")

        # FRASE MOTIVACIONAL DA IA NO INÍCIO
        if usuario["perfil"]:
            materia = usuario["perfil"].get("materia", usuario["perfil"].get("objetivo","sua meta"))
            frase_ia = random.choice(FRASES_IA).format(nome=usuario["nome"].split()[0], materia=materia)
            st.success(f"💬 **Frase da IA hoje:** {frase_ia}")
            st.info(f"🎯 {usuario['perfil'].get('meta_ia','')}")

            col1,col2,col3 = st.columns(3)
            with col1: st.metric("🔥 Sequência", f"{usuario.get('streak',0)} dias")
            with col2: st.metric("Progresso Semana", f"{len(usuario.get('progresso',{}))}/{len(usuario.get('cronograma',[]))}")
            with col3:
                notas = usuario.get("notas",{})
                evo = notas.get("mes_atual",0) - notas.get("mes_passado",0)
                st.metric("Evolução Nota", f"{notas.get('mes_atual',0)}", delta=f"{evo} pts")

            st.divider()
            if st.button("📚 Ir para Meu Plano", type="primary"): st.session_state.pagina="Plano"; st.rerun()
        else:
            st.info("Você ainda não tem um plano. Vamos criar?")
            frase_boas = f"Olá {usuario['nome']}! Eu sou sua IA. Me diz qual área você quer evoluir e eu crio tudo pra você!"
            st.success(f"💬 {frase_boas}")
            if st.button("Criar meu primeiro plano"): st.session_state.pagina="Plano"; st.rerun()

    # ===== PÁGINA PLANO / ESTUDOS =====
    elif st.session_state.pagina=="Plano":
        st.header("📚 Meu Plano de Estudos")

        if usuario["perfil"] is None:
            st.subheader("Criar novo plano")
            area = st.selectbox("Área?", ["Estudos","Saúde","Financeira"], key="area")
            nivel = st.selectbox("Nível?", ["Ensino Fundamental","Ensino Médio","Ensino Superior","Concurso/ENEM"], key="niv")
            curso = st.text_input("Qual curso superior?", key="cur") if nivel=="Ensino Superior" else ""
            materia = st.text_input("Matéria dessa semana?", key="mat")
            # NOVO: TÓPICOS QUE PRECISA APRENDER
            topicos_txt = st.text_area("O que você PRECISA aprender sobre isso? (separa por vírgula)", placeholder="Ex: Artigo 5º, Remédios constitucionais, Direitos sociais", key="topicos_in")
            quer = st.multiselect("Quer o que?", ["Teoria","Vídeos","Livros","Simulados","Revisão"], default=["Teoria"], key="quer")
            tempo = st.slider("Horas/dia?",1,6,2,key="tmp")
            dias = st.multiselect("Dias?", ["Segunda","Terça","Quarta","Quinta","Sexta","Sábado","Domingo"], default=["Segunda","Terça","Quarta","Quinta","Sexta"], key="ds")

            st.divider()
            st.subheader("📝 Suas notas (para ver evolução)")
            c1,c2,c3 = st.columns(3)
            with c1: nota_passada = st.number_input("Nota mês passado", 0.0, 10.0, 5.0, key="np")
            with c2: nota_atual = st.number_input("Nota mês atual / simulado", 0.0, 10.0, 6.0, key="na")
            with c3: meta_nota = st.number_input("Meta de nota", 0.0, 10.0, 9.0, key="mn")

            if st.button("✨ Gerar plano completo"):
                if not materia: st.warning("Qual matéria?")
                else:
                    hoje=date.today()
                    cron=[f"{dias[i]} {(hoje+timedelta(days=i)).strftime('%d/%m')} - {quer[i%len(quer)] if quer else 'Estudo'}: {materia}" for i in range(len(dias))]
                    topicos = [t.strip() for t in topicos_txt.split(",") if t.strip()]
                    st.session_state.usuarios[st.session_state.usuario_logado]["perfil"]={"area":area,"nivel":nivel,"curso":curso,"materia":materia,"quer":quer,"tempo":tempo,"dias":dias,"meta_ia":f"Meta: Dominar {', '.join(topicos[:3])} e tirar {meta_nota} em {materia}","frase_boas_vindas":f"Bora tirar {meta_nota} em {materia}!","data_inicio":date.today().isoformat()}
                    st.session_state.usuarios[st.session_state.usuario_logado]["cronograma"]=cron
                    st.session_state.usuarios[st.session_state.usuario_logado]["progresso"]={}
                    st.session_state.usuarios[st.session_state.usuario_logado]["resumos"]={}
                    st.session_state.usuarios[st.session_state.usuario_logado]["notas"]={"mes_passado":nota_passada,"mes_atual":nota_atual,"meta_nota":meta_nota}
                    st.session_state.usuarios[st.session_state.usuario_logado]["topicos"]=topicos
                    salvar()
                    st.rerun()
        else:
            p=usuario["perfil"]
            st.subheader(f"Semana: {p.get('materia','')}")

            # MOSTRA EVOLUÇÃO DE NOTA
            notas = usuario.get("notas",{})
            col1,col2,col3 = st.columns(3)
            with col1: st.metric("Mês passado", notas.get("mes_passado",0))
            with col2: st.metric("Mês atual", notas.get("mes_atual",0), delta=notas.get("mes_atual",0)-notas.get("mes_passado",0))
            with col3: st.metric("Meta", notas.get("meta_nota",10))

            # Gráfico evolução
            st.line_chart([notas.get("mes_passado",0), notas.get("mes_atual",0), notas.get("meta_nota",10)])

            # O que precisa aprender
            if usuario.get("topicos"):
                st.write("**📌 O que você deve aprender nessa semana:**")
                for t in usuario.get("topicos",[]):
                    st.checkbox(f"Aprender: {t}", key=f"top_{t}")

            st.divider()
            # Imagem cronograma
            caminho=criar_imagem_cronograma(usuario.get("cronograma",[]), p.get("materia",""), usuario["nome"])
            st.image(caminho)
            with open(caminho,"rb") as file:
                st.download_button("📥 Baixar imagem", file, file_name="cronograma.png", mime="image/png")

            # Tarefas com resumo
            for i, tarefa in enumerate(usuario.get("cronograma",[])):
                chave=f"tarefa_{i}"
                ja=usuario.get("progresso",{}).get(chave,False)
                with st.expander(f"{'✅' if ja else '⏳'} {tarefa}", expanded=not ja):
                    if ja:
                        st.success("Concluído!")
                        if chave in usuario.get("resumos",{}): st.write(f"Resumo: {usuario['resumos'][chave]}")
                        if st.button(f"Refazer", key=f"ref_{i}"):
                            del st.session_state.usuarios[st.session_state.usuario_logado]["progresso"][chave]
                            salvar(); st.rerun()
                    else:
                        resumo=st.text_area("O que aprendeu hoje?", value=usuario.get("resumos",{}).get(chave,""), key=f"res_{i}", height=100)
                        if st.button(f"✅ Concluir Dia {i+1}", key=f"conc_{i}", type="primary"):
                            if not resumo.strip(): st.warning("Escreve o resumo!")
                            else:
                                st.session_state.usuarios[st.session_state.usuario_logado]["resumos"][chave]=resumo
                                st.session_state.usuarios[st.session_state.usuario_logado]["progresso"][chave]=True
                                st.session_state.usuarios[st.session_state.usuario_logado]["streak"]=usuario.get("streak",0)+1
                                # Atualiza nota atual automaticamente um pouco
                                salvar()
                                st.balloons()
                                st.rerun()

            if st.button("🔄 Nova semana / Alterar nota"):
                st.session_state.usuarios[st.session_state.usuario_logado]["perfil"]=None
                salvar(); st.rerun()

    # ===== PÁGINA CONFIG =====
    elif st.session_state.pagina=="Config":
        st.header("⚙️ Configurações")

        st.subheader("Avatar")
        avatar_atual = st.selectbox("Escolha seu avatar", AVATARES, index=AVATARES.index(usuario.get("avatar","🚀")) if usuario.get("avatar","🚀") in AVATARES else 0)
        if avatar_atual!= usuario.get("avatar"):
            st.session_state.usuarios[st.session_state.usuario_logado]["avatar"]=avatar_atual
            salvar()
            st.success("Avatar atualizado!")

        st.divider()
        st.subheader("Seus dados")
        novo_nome = st.text_input("Nome", value=usuario["nome"], key="cfg_nome")
        novo_email = st.text_input("E-mail", value=usuario.get("email",""), key="cfg_email")
        nova_senha = st.text_input("Nova senha (deixa em branco pra não mudar)", type="password", key="cfg_senha")

        if st.button("Salvar alterações"):
            st.session_state.usuarios[st.session_state.usuario_logado]["nome"]=novo_nome
            st.session_state.usuarios[st.session_state.usuario_logado]["email"]=novo_email
            if nova_senha.strip():
                st.session_state.usuarios[st.session_state.usuario_logado]["senha"]=nova_senha
                st.success("Dados e senha atualizados!")
            else:
                st.success("Dados atualizados!")
            salvar()

        st.divider()
        st.subheader("Notas - Atualizar evolução")
        notas = usuario.get("notas",{})
        c1,c2,c3 = st.columns(3)
        with c1: np = st.number_input("Mês passado", 0.0, 10.0, float(notas.get("mes_passado",0)), key="cfg_np")
        with c2: na = st.number_input("Mês atual", 0.0, 10.0, float(notas.get("mes_atual",0)), key="cfg_na")
        with c3: mn = st.number_input("Meta nota", 0.0, 10.0, float(notas.get("meta_nota",10)), key="cfg_mn")
        if st.button("Atualizar notas"):
            st.session_state.usuarios[st.session_state.usuario_logado]["notas"]={"mes_passado":np,"mes_atual":na,"meta_nota":mn}
            salvar()
            st.success("Evolução atualizada! Volta no Início pra ver o gráfico subir!")
