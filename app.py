import streamlit as st
import quant_a

st.set_page_config(page_title="Dashboard Finance", layout="wide")

# Menu simple
st.sidebar.title("Navigation")
page = st.sidebar.radio("Choisir un module", ["Analyse Quant A", "Portfolio Quant B"])

if page == "Analyse Quant A":
    quant_a.run()
else:
    st.info("Le module Quant B sera bientot disponible.")