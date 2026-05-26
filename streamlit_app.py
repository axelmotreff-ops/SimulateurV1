import streamlit as st
import pandas as pd

st.set_page_config(layout="wide")

st.title("📊 Simulateur KNAVE")

# =========================
# SIDEBAR
# =========================

st.sidebar.header("Paramètres")

type_eq = st.sidebar.radio(
    "Type d’équipement",
    ["Mobilité", "Robot / Retail"],
    index=0
)

fees_journalier = 2.5 if type_eq == "Mobilité" else 0.6
fees_mensuels = fees_journalier * 30

# Prix de cession
prix = st.sidebar.slider(
    "Prix de cession (HT €)",
    10000 if type_eq == "Mobilité" else 2000,
    100000,
    20000,
    step=25
)

# Prix achat
prix_achat = st.sidebar.slider(
    "Prix d’achat équipement (HT €)",
    1000,
    prix,
    int(prix * 0.7),
    step=25
)

# VR
vr_pct = st.sidebar.slider("Valeur résiduelle (%)", 10, 80, 50)
vr = prix * vr_pct / 100

# Revente
prix_revente = st.sidebar.slider(
    "Prix de revente (HT €)",
    0,
    prix,
    int(vr * 1.2),
    step=25
)

# Durée
duree = st.sidebar.radio(
    "Durée (mois)",
    [36, 48] if type_eq == "Mobilité" else [36, 48, 60]
)

# Loyer
loyer = st.sidebar.slider(
    "Tarif usage locatif mensuel (HT €)",
    50,
    5000,
    1650,
    step=25
)

# Services annuels
if type_eq == "Mobilité":
    services_label = "Entretien / réparation annuel (HT €)"
    taux_marge = 0.3
else:
    services_label = "Entretien / services annuel (HT €)"
    taux_marge = 0.4

services_annuel = st.sidebar.slider(services_label, 0, 5000, 1000, step=25)

# =========================
# CALCULS
# =========================

services_total = services_annuel * (duree / 12)

amortissement = (prix - vr) / duree
lld = amortissement * 2.8
lld_total = lld * duree

revenu_net = loyer - fees_mensuels
revenu_loc_total = revenu_net * duree

# CA
ca_total = prix + services_total + revenu_loc_total + prix_revente

# Marges
marge_cession = prix - prix_achat
marge_usage = revenu_loc_total
marge_services = services_total * taux_marge
marge_revente = prix_revente - vr

marge_totale = marge_cession + marge_usage + marge_services + marge_revente
gain_annuel = marge_totale / duree * 12

# Break-even
tarif_jour = loyer / 30

be_jours_complet = lld / (tarif_jour - fees_journalier)
be_pct_complet = be_jours_complet / 30

be_jours_sans = amortissement / (tarif_jour - fees_journalier)
be_pct_sans = be_jours_sans / 30

# =========================
# KPI CARDS
# =========================

st.header("Lecture partenaire")

st.markdown("""
<style>
.kpi-card {
    background-color: white;
    padding: 15px;
    border-radius: 10px;
    box-shadow: 0px 1px 3px rgba(0,0,0,0.1);
    text-align: center;
    margin-bottom: 10px;
}
.kpi-label {
    font-size: 14px;
    color: #666;
}
.kpi-value {
    font-size: 26px;
    font-weight: bold;
}
.kpi-sub {
    font-size: 14px;
    color: #888;
}
</style>
""", unsafe_allow_html=True)

# Ligne 1
col1, col2, col3, col4 = st.columns(4)

col1.markdown(f"<div class='kpi-card'><div class='kpi-label'>CA total (HT €)</div><div class='kpi-value'>{ca_total:,.0f}</div></div>", unsafe_allow_html=True)
col2.markdown(f"<div class='kpi-card'><div class='kpi-label'>Engagement total (HT €)</div><div class='kpi-value'>{(lld_total + vr):,.0f}</div></div>", unsafe_allow_html=True)
col3.markdown(f"<div class='kpi-card'><div class='kpi-label'>Marge totale (HT €)</div><div class='kpi-value'>{marge_totale:,.0f}</div></div>", unsafe_allow_html=True)
col4.markdown(f"<div class='kpi-card'><div class='kpi-label'>Marge annuelle (HT €)</div><div class='kpi-value'>{gain_annuel:,.0f}</div></div>", unsafe_allow_html=True)

# Ligne 2
col5, col6, col7 = st.columns(3)

col5.markdown(f"""
<div class='kpi-card'>
    <div class='kpi-label'>Break-even complet</div>
    <div class='kpi-value'>{be_pct_complet:.0%}</div>
    <div class='kpi-sub'>{be_jours_complet:.1f} j/mois</div>
</div>
""", unsafe_allow_html=True)

col6.markdown(f"""
<div class='kpi-card'>
    <div class='kpi-label'>Seuil opérationnel (hors amort.)</div>
    <div class='kpi-value'>{be_pct_sans:.0%}</div>
    <div class='kpi-sub'>{be_jours_sans:.1f} j/mois</div>
</div>
""", unsafe_allow_html=True)

col7.markdown(f"""
<div class='kpi-card'>
    <div class='kpi-label'>Tarif locatif journalier</div>
    <div class='kpi-value'>{tarif_jour:.0f} €</div>
</div>
""", unsafe_allow_html=True)

# =========================
# GRAPH CA
# =========================

st.markdown("---")
st.subheader("Cycle de vie – Chiffre d’affaires")

categories_ca = [
    "1. Cession",
    "2. LLD",
    "3. Services",
    "4. Usage locatif",
    "5. Rachat VR",
    "6. Revente"
]

valeurs_ca = [
    prix,
    -lld_total,
    services_total,
    revenu_loc_total,
    -vr,
    prix_revente
]

df_ca = pd.DataFrame({
    "Catégorie": categories_ca,
    "Montant": valeurs_ca
})

st.bar_chart(df_ca.set_index("Catégorie"))

# =========================
# GRAPH MARGE (NETTOYÉ)
# =========================

st.subheader("Cycle de vie – Marge")

categories_marge = [
    "1. Cession",
    "3. Services",
    "4. Usage locatif",
    "6. Revente"
]

valeurs_marge = [
    marge_cession,
    marge_services,
    marge_usage,
    marge_revente
]

df_marge = pd.DataFrame({
    "Catégorie": categories_marge,
    "Montant": valeurs_marge
})

st.bar_chart(df_marge.set_index("Catégorie"))

# =========================
# LECTURE BUSINESS
# =========================

st.markdown("### Lecture")

st.success(
    f"Le modèle génère environ **{marge_totale:,.0f} € HT** sur {duree} mois.\n\n"
    f"Le break-even complet est atteint à {be_pct_complet:.0%}, soit "
    f"{be_jours_complet:.1f} jours de location par mois.\n\n"
    f"Le seuil opérationnel est de {be_pct_sans:.0%}, soit "
    f"{be_jours_sans:.1f} jours de location par mois.\n\n"
    f"Cela représente environ {gain_annuel:,.0f} € HT par an."
)

# =========================
# DISCLAIMER
# =========================

st.markdown("---")
st.caption("⚠️ Simulation indicative (HT). Validation KNAVE requise.")

# =========================
# MODE EXPERT
# =========================

with st.expander("Mode expert"):
    st.write("Amortissement mensuel :", round(amortissement, 2))
    st.write("LLD mensuel :", round(lld, 2))