import streamlit as st
from datetime import datetime

if "usuarios" not in st.session_state:
    st.session_state.usuarios = {}
if "logado" not in st.session_state:
    st.session_state.logado = False
    st.session_state.usuario_logado = ""

st.title("🚀 EvoluiAI")

# FUNÇÃO QUE SIMULA A IA CRIANDO A META
def gerar_meta_pela_ia(area, objetivo, tempo, dias):
    # Aqui depois a gente conecta a IA de verdade
    # Por enquanto ela cria a meta baseada na disponibilidade
    qtd_dias = len(dias) if dias else 3
    horas_semana = tempo * qtd_dias

    if area == "Saúde":
        meta = f"Meta IA: Evoluir em '{objetivo}' com {horas_semana}h por semana ({tempo}h em {qtd_dias} dias). Foco em consistência e pequenos hábitos."
    elif area == "Financeira":
        meta = f"Meta IA: Alcançar '{objetivo}' dedicando {horas_semana}h/semana. Meta dividida em: Estudo + Ação Prática + Revisão Financeira."
    elif area == "Espiritual":
        meta = f"Meta IA: Fortalecer '{objetivo}' com {tempo}h diárias de prática consciente durante {qtd_dias} dias na semana."
    else:
        meta = f"Meta IA: Conquistar '{objetivo}' com plano de {horas_semana}h/semana. Dividido em 3 etapas: Aprender, Praticar e Evoluir."

    frase_boas_vindas = f"Bem-vindo à sua jornada de {area.lower()}! Você deu o primeiro passo para '{objetivo}'. Com {horas_semana}h por semana, você vai se surpreender com sua evolução."

    return meta, frase_boas_vindas

if not st.session_state.logado:
    aba1, aba2, aba3 = st.tabs(["Entrar", "Cadastrar", "Trocar Senha"])
    with aba1:
        e1 = st.text_input("Seu E-MAIL", key="e1_login_001")
        s1 = st.text_input("Sua Senha", type="password", key="s1_login_001")
        if st.button("Entrar"):
            if e1 in st.session_state.usuarios and st.session_state.usuarios[e1]["senha"] == s1:
                st.session_state.logado = True
                st.session_state.usuario_logado = e1
                st.rerun()
            else: st.error("E-mail ou senha incorreta.")
    with aba2:
        n = st.text_input("Seu nome", key="n_cad_002")
        e = st.text_input("Seu e-mail", key="e_cad_002")
        s = st.text_input("Crie uma senha", type="password", key="s_cad_002")
        if st.button("Cadastrar agora"):
            if not n or not e or not s: st.warning("Preenche tudo!")
            elif e in st.session_state.usuarios: st.warning("E-mail já existe.")
            else:
                st.session_state.usuarios[e] = {"nome": n, "senha": s, "perfil": None, "cronograma": []}
                st.success(f"Pronto, {n}!")
    with aba3:
        er = st.text_input("Seu e-mail", key="er_003")
        if er in st.session_state.usuarios:
            ns = st.text_input("Nova senha", type="password", key="ns_003")
            if st.button("Salvar nova senha"):
                st.session_state.usuarios[er]["senha"] = ns
                st.success("Trocada!")
        else:
            if er!= "": st.error("E-mail não encontrado")
else:
    usuario = st.session_state.usuarios[st.session_state.usuario_logado]

    if usuario["perfil"] is None:
        st.header(f"🎯 Olá, {usuario['nome']}! Vamos começar?")
        st.write("Me conta um pouco pra eu montar seu plano inteligente.")

        area = st.selectbox("1. Qual ÁREA da sua vida você quer evoluir agora?",
                            ["Saúde", "Financeira", "Espiritual", "Estudos", "Carreira", "Relacionamento", "Outra"], key="area_vida_10")

        objetivo_aberto = st.text_area(f"2. O que você quer alcançar em {area}? (Escreve livre)",
                                       placeholder="Ex: Quero parar de procrastinar e ter mais foco, Quero juntar 10 mil reais, Quero ter mais paz interior", key="obj_aberto_11")

        st.subheader("3. Sua disponibilidade")
        col1, col2 = st.columns(2)
        with col1:
            tempo = st.slider("Quantas horas por dia você tem?", 1, 5, 2, key="tempo_12")
        with col2:
            horario = st.selectbox("Melhor horário?", ["Manhã", "Tarde", "Noite", "Madrugada", "Flexível"], key="hora_13")

        dias = st.multiselect("Quais dias você pode se dedicar?", ["Segunda", "Terça", "Quarta", "Quinta", "Sexta", "Sábado", "Domingo"], default=["Segunda", "Quarta", "Sexta"], key="dias_14")

        if st.button("✨ Criar meu plano com IA"):
            if not objetivo_aberto:
                st.warning("Escreve seu objetivo aberto ali em cima!")
            else:
                meta_ia, frase_ia = gerar_meta_pela_ia(area, objetivo_aberto, tempo, dias)

                st.session_state.usuarios[st.session_state.usuario_logado]["perfil"] = {
                    "area": area,
                    "objetivo_aberto": objetivo_aberto,
                    "tempo": tempo,
                    "horario": horario,
                    "dias": dias,
                    "meta_criada_pela_ia": meta_ia,
                    "frase_boas_vindas": frase_ia,
                    "data": datetime.now().strftime("%d/%m/%Y")
                }
                st.success("Plano criado! Olha sua meta:")
                st.rerun()
    else:
        p = usuario["perfil"]
        # FRASE DE BOAS VINDAS DA IA
        st.success(f"💬 {p['frase_boas_vindas']}")

        st.header(f"Seu Painel de {p['area']}")
        col1, col2, col3 = st.columns(3)
        col1.metric("Área", p['area'])
        col2.metric("Foco", f"{p['tempo']}h/dia")
        col3.metric("Horário", p['horario'])

        st.info(f"🎯 **Sua meta criada pela IA:**\n\n{p['meta_criada_pela_ia']}")
        st.write(f"**Seu objetivo:** {p['objetivo_aberto']}")
        st.write(f"**Disponibilidade:** {', '.join(p['dias'])}")

        st.divider()
        st.subheader("📚 Seu Cronograma Inteligente")
        if not usuario["cronograma"]:
            if st.button("Gerar meu cronograma de estudos/aulas"):
                cronograma = [
                    f"Segunda ({p['horario']}): {p['area']} - Foco em {p['objetivo_aberto'][:30]}...",
                    f"Quarta: Prática + Revisão",
                    f"Sexta: Aprofundamento e evolução"
                ]
                st.session_state.usuarios[st.session_state.usuario_logado]["cronograma"] = cronograma
                st.rerun()
        else:
            for i, aula in enumerate(usuario["cronograma"], 1):
                st.checkbox(aula, key=f"chk_{i}_v2")

        if st.button("Refazer meu plano"):
            st.session_state.usuarios[st.session_state.usuario_logado]["perfil"] = None
            st.session_state.usuarios[st.session_state.usuario_logado]["cronograma"] = []
            st.rerun()

    if st.button("Sair", key="sair_v3"):
        st.session_state.logado = False
        st.rerun()
