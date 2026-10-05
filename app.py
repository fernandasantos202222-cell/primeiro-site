                st.divider()
                # EVOLUÇÃO - VERSÃO BONITA E LIMPA
                st.subheader(f"Evolução em {mat_res}")

                # Card de evolução - sem gráfico feio
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Semestre passado", f"{np}", delta=None)
                with col2:
                    st.metric("Semestre atual", f"{na}", delta=f"{na-np:+.1f} vs passado", delta_color="normal")
                with col3:
                    falta = mn - na
                    st.metric("Meta", f"{mn}", delta=f"Falta {falta:.1f}" if falta > 0 else "Atingida! 🏆", delta_color="inverse" if falta > 0 else "normal")

                # Barra de progresso da meta - bem mais bonito que gráfico
                progresso_meta = (na / mn * 100) if mn > 0 else 0
                st.write(f"**Progresso até a meta:** {progresso_meta:.0f}%")
                st.progress(min(progresso_meta / 100, 1.0))

                # Tempo total - versão limpa sem linha feia
                st.divider()
                st.subheader("⏱️ Seu tempo de estudo")
                c1, c2 = st.columns(2)
                with c1:
                    st.metric("Essa matéria", f"{tempo_mat} min")
                with c2:
                    st.metric("Total no mês", f"{usuario.get('tempo_total_mes',0)} min", delta=f"{usuario.get('tempo_total_mes',0)//30} min/dia em média")

                # Se quiser gráfico, usa só 1 barra bonita
                if tempo_mat > 0:
                    st.bar_chart({mat_res: tempo_mat}, height=200)
