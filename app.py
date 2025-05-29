import streamlit as st
import pandas as pd
from pycausalimpact import CausalImpact


st.title("Analyse d'impact SEO (CausalImpact)")

# 1. Upload CSV
uploaded_file = st.file_uploader("Importer un fichier CSV", type=["csv"])

if uploaded_file:
    # 2. Lire le fichier
    sep = st.selectbox("Séparateur CSV", [";", ","])
    df = pd.read_csv(uploaded_file, sep=sep, encoding="utf-8-sig")

    # 3. Sélection de la colonne date
    date_col = st.selectbox("Choisir la colonne de dates", df.columns)
    try:
        df[date_col] = pd.to_datetime(df[date_col], errors="coerce")
        df = df.dropna(subset=[date_col])
        df = df.set_index(date_col).sort_index()
    except Exception as e:
        st.error(f"Erreur de conversion de la date : {e}")
        st.stop()

    # 4. Sélection de la variable à analyser
    numeric_cols = df.select_dtypes(include='number').columns
    y_col = st.selectbox("Choisir la variable à analyser", numeric_cols)

    if y_col:
        data = df[[y_col]].rename(columns={y_col: "y"})

        # 5. Analyse de l’année choisie
        year = st.selectbox("Année à analyser", sorted(data.index.year.unique(), reverse=True))
        yearly_data = data[data.index.year == year]

        if len(yearly_data) >= 20:
            split = int(len(yearly_data) * 0.7)
            pre_period = [yearly_data.index[0], yearly_data.index[split - 1]]
            post_period = [yearly_data.index[split], yearly_data.index[-1]]

            try:
                ci = CausalImpact(yearly_data, pre_period, post_period)
                st.subheader("Rapport d’analyse")
                st.text(ci.summary("report"))
                st.pyplot(ci.plot())
            except Exception as e:
                st.error(f"Erreur pendant l'analyse : {e}")
        else:
            st.warning("Pas assez de données pour cette année.")
