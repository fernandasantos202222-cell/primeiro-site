import streamlit as st
data = st.date_input("Selecione  a data")
st.write("Dia", data.day)
st.write("Mês", data.month)
st.write("Ano", data.year)
data_str = data.strftime("%d/%m/%Y")
st.write(data_str)
datas = st.date_input("Periodo",)
st.write(datas)