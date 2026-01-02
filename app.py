import streamlit as st
import quant_a
import quant_b

st.set_page_config(page_title="Dashboard Finance Quantitative", layout="wide")

st.sidebar.title("Navigation Projet")
selection = st.sidebar.radio("Choisir le module", ["Quant A - Actif Unique", "Quant B - Portefeuille"])

if selection == "Quant A - Actif Unique":
    quant_a.run()
elif selection == "Quant B - Portefeuille":
    quant_b.run()  