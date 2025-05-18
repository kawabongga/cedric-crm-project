import streamlit as st
import pandas as pd
from io import BytesIO

st.title("🧾 Import de contacts avec gestion des doublons")

# Upload des fichiers
fichier_bdd = st.file_uploader("📂 Fichier base de données (ex: Modele-Particuliers.xlsx)", type="xlsx")
fichier_nouveaux = st.file_uploader("📥 Fichier nouveaux contacts", type="xlsx")
fichier_mapping = st.file_uploader("🔗 Fichier de mapping (mapping.xlsx)", type="xlsx")

# Fonction de traitement
def traiter_fichiers(bdd, nouveaux, mapping):
    df_bdd = pd.read_excel(bdd)
    df_nouveaux = pd.read_excel(nouveaux)
    df_map = pd.read_excel(mapping)

    map_dict = dict(zip(df_map["Colonne source"], df_map["Colonne destination"]))
    df_nouveaux_mapped = df_nouveaux[list(map_dict.keys())].rename(columns=map_dict)
    df_nouveaux_mapped['Email contact'] = df_nouveaux_mapped['Email contact'].str.strip().str.lower()

    if df_bdd.empty:
        df_bdd_cleaned = df_bdd.copy()
    else:
        df_bdd_cleaned = df_bdd.copy()
        df_bdd_cleaned['Email contact'] = df_bdd_cleaned['Email contact'].astype(str).str.strip().str.lower()

    emails_bdd = df_bdd_cleaned['Email contact'].dropna().unique()
    df_doublons = df_nouveaux_mapped[df_nouveaux_mapped['Email contact'].isin(emails_bdd)]
    df_uniques = df_nouveaux_mapped[~df_nouveaux_mapped['Email contact'].isin(emails_bdd)]

    df_bdd_maj = pd.concat([df_bdd_cleaned, df_uniques], ignore_index=True)

    return df_doublons, df_bdd_maj

# Lancer le traitement
if st.button("🧮 Lancer le traitement") and fichier_bdd and fichier_nouveaux and fichier_mapping:
    doublons, maj = traiter_fichiers(fichier_bdd, fichier_nouveaux, fichier_mapping)

    st.success("✅ Traitement terminé")

    st.subheader("👥 Doublons détectés")
    st.dataframe(doublons)

    # Exporter les doublons
    buffer_doublons = BytesIO()
    doublons.to_excel(buffer_doublons, index=False, engine='openpyxl')
    buffer_doublons.seek(0)
    st.download_button("📤 Télécharger les doublons", data=buffer_doublons, file_name="doublons.xlsx")

    # Exporter la base mise à jour
    buffer_maj = BytesIO()
    maj.to_excel(buffer_maj, index=False, engine='openpyxl')
    buffer_maj.seek(0)
    st.download_button("📤 Télécharger la base mise à jour", data=buffer_maj, file_name="Modele-Particuliers-MAJ.xlsx")
