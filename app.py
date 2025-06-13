import streamlit as st
import pandas as pd
from causalimpact import CausalImpact
import matplotlib.pyplot as plt

st.set_page_config(page_title="Analyse Causale avec CausalImpact", layout="centered")
st.title("Analyse Causale d'une série temporelle (CausalImpact)")

# Chargement du fichier CSV
uploaded_file = st.file_uploader("Importer un fichier CSV", type="csv")

if uploaded_file is not None:
    try:
        df = pd.read_csv(uploaded_file, sep=";", encoding="utf-8-sig")
        st.success("Fichier chargé avec succès.")
        st.write("Aperçu des données :", df.head())

        if "date" in df.columns:
            df["date"] = pd.to_datetime(df["date"], format="%d.%m.%Y", errors="coerce")
            df = df.dropna(subset=["date"]).set_index("date").sort_index()
        else:
            st.error("La colonne 'date' est requise.")
            st.stop()

        colonnes_numeriques = df.select_dtypes(include="number").columns.tolist()
        if not colonnes_numeriques:
            st.error("Aucune colonne numérique détectée.")
            st.stop()

        variable = st.selectbox("Sélectionnez la variable à analyser :", colonnes_numeriques)
        data = df[[variable]].copy()
        data.columns = ["y"]
        data = data.dropna()

        if data["y"].nunique() == 1:
            st.warning("La variable sélectionnée est constante. Analyse impossible.")
            st.stop()

        st.markdown("### Évolution de la variable sélectionnée")
        st.line_chart(data['y'])

        st.markdown("### Définir les périodes d'analyse")
        min_date, max_date = data.index.min(), data.index.max()
        st.write(f"Période disponible : **{min_date.date()} → {max_date.date()}**")

        # Calcul de date par défaut (basé sur début d'évolution de y > 0.002)
        seuil = 0.002
        df_significatif = data[data["y"] > seuil]
        default_intervention = df_significatif.index.min() if not df_significatif.empty else min_date

        date_intervention = st.date_input(
            "Date d'intervention",
            min_value=min_date.date(),
            max_value=max_date.date(),
            value=default_intervention.date()
        )
        date_intervention = pd.to_datetime(date_intervention)

        pre_period = [data.index.min(), date_intervention - pd.Timedelta(days=1)]
        post_period = [date_intervention, data.index.max()]

        pre_data = data.loc[pre_period[0]:pre_period[1]]
        post_data = data.loc[post_period[0]:post_period[1]]

        if pre_data.empty or post_data.empty:
            st.warning("Les périodes sélectionnées ne contiennent pas suffisamment de données.")
            st.stop()

        st.write(f"Pré-intervention : **{pre_period[0].date()} → {pre_period[1].date()}**")
        st.write(f"Post-intervention : **{post_period[0].date()} → {post_period[1].date()}**")

        if st.button("Lancer l’analyse causale"):
            if len(data) < 10:
                st.warning("Pas assez de données pour faire une analyse fiable.")
            else:
                try:
                    ci = CausalImpact(data, pre_period, post_period)
                    st.success("Analyse effectuée avec succès")
                    st.text(ci.summary("report"))

                    fig = ci.plot()
                    st.pyplot(fig)

                except Exception as e:
                    st.error(f"Une erreur s’est produite pendant l'analyse : {e}")

    except Exception as e:
        st.error(f"Erreur lors de la lecture du fichier : {e}")
