import streamlit as st
import pandas as pd
from causalimpact import CausalImpact
import matplotlib.pyplot as plt

st.set_page_config(page_title="Analyse Causale avec CausalImpact", layout="centered")

st.title(" Analyse Causale d'une série temporelle (CausalImpact)")

# Chargement du fichier CSV
uploaded_file = st.file_uploader("Importer un fichier CSV", type="csv")

if uploaded_file is not None:
    try:
        df = pd.read_csv(uploaded_file, sep=";", encoding="utf-8-sig")
        st.success("Fichier chargé avec succès.")
        st.write("Aperçu des données :", df.head())

        # Sélection de la colonne de date
        if "date" in df.columns:
            df["date"] = pd.to_datetime(df["date"], format="%d.%m.%Y", errors="coerce")
            df = df.dropna(subset=["date"]).set_index("date").sort_index()
        else:
            st.error(" La colonne 'date' est requise.")
            st.stop()

        # Sélection de la colonne à analyser
        colonnes_numeriques = df.select_dtypes(include="number").columns.tolist()
        if not colonnes_numeriques:
            st.error(" Aucune colonne numérique détectée.")
            st.stop()

        variable = st.selectbox("Sélectionnez la variable à analyser :", colonnes_numeriques)
        data = df[[variable]].copy()
        data.columns = ["y"]  # standardiser le nom

        # Choix de la période d'intervention
        st.markdown("### Définir les périodes d'analyse")
        dates_dispo = data.index.to_series().dropna().sort_values()
        min_date, max_date = dates_dispo.min(), dates_dispo.max()
        st.write(f"Plage disponible : {min_date.date()} → {max_date.date()}")

        date_intervention = st.date_input("Date d'intervention", min_value=min_date.date(), max_value=max_date.date(), value=min_date.date())
        date_intervention = pd.to_datetime(date_intervention)

        pre_period = [data.index.min(), date_intervention - pd.Timedelta(days=1)]
        post_period = [date_intervention, data.index.max()]

        st.write(f"Période pré-intervention : {pre_period[0].date()} → {pre_period[1].date()}")
        st.write(f"Période post-intervention : {post_period[0].date()} → {post_period[1].date()}")

        if st.button("Lancer l’analyse causale"):
            if len(data.dropna()) < 10:
                st.warning(" Pas assez de données pour faire une analyse fiable.")
            else:
                try:
                    ci = CausalImpact(data, pre_period, post_period)
                    st.success(" Analyse effectuée avec succès")
                    st.text(ci.summary("report"))

#
                    fig = ci.plot()
                    st.pyplot(fig)

                except Exception as e:
                    st.error(f" Une erreur s’est produite : {e}")

    except Exception as e:
        st.error(f"Erreur lors de la lecture du fichier : {e}")
