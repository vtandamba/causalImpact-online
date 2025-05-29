import streamlit as st
import pandas as pd
from causalimpact import CausalImpact
import matplotlib.pyplot as plt

st.title("Analyse CausalImpact SEO")
st.markdown("Importez un fichier CSV pour analyser l’impact d’un événement sur la visibilité.")

uploaded_file = st.file_uploader("Téléverser un fichier CSV", type="csv")

if uploaded_file is not None:
    try:
        df = pd.read_csv(uploaded_file, sep=";", encoding="utf-8-sig")
        df["date"] = pd.to_datetime(df["date"], format="%d.%m.%Y", errors="coerce")
        df = df.dropna(subset=["date"])
        df = df.set_index("date").sort_index()

        df["y"] = df["y"].astype(str).str.replace(",", ".").astype(float)
        data = df[["y"]]

        for year in sorted(data.index.year.unique(), reverse=True):
            if year < 2024:
                continue

            st.subheader(f"Analyse pour {year}")
            yearly_data = data[data.index.year == year]
            if len(yearly_data) < 20:
                st.warning("Pas assez de données pour cette année.")
                continue

            try:
                n = len(yearly_data)
                split = int(n * 0.7)
                pre_period = [yearly_data.index[0], yearly_data.index[split - 1]]
                post_period = [yearly_data.index[split], yearly_data.index[-1]]

                ci = CausalImpact(yearly_data, pre_period, post_period)
                st.text(ci.summary("report"))
                st.pyplot(ci.plot())
            except Exception as e:
                st.error(f"Erreur : {str(e)}")
    except Exception as e:
        st.error(f"Fichier invalide ou erreur de traitement : {str(e)}")
