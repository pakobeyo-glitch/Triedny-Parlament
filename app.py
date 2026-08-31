import streamlit as st
import pandas as pd

# 1. Nastavenie vzhľadu stránky
st.set_page_config(page_title="Parlamentné hlasovanie", layout="wide")

# =========================================================================
# TU PRESNE A OPATRNE VLOŽTE VAŠE ODKAZY
# =========================================================================
# POZOR: Do GOOGLE_CSV_URL nevkladajte klasický odkaz, ale presne tento tvar, 
# kde namiesto "KOD_VASEJ_TABULKY" vložíte ten dlhý kód z adresy vašej tabuľky.
# Príklad: https://google.com
GOOGLE_CSV_URL = "https://docs.google.com/spreadsheets/d/1tnZuvYAq47pbBpfAax0TfjGPSoCplkAXZmPD_GyjOTI/edit?usp=sharing"

# Odkaz na váš Google Formulár (klasický odkaz na hlasovanie)
ODKAZ_NA_FORMULAR = "https://docs.google.com/forms/d/e/1FAIpQLSdFRKTTneLhn0KpOZI-TJPyWR-6Qj5FWXjcImFznMErBtgHbg/viewform?usp=header"

# Odkaz na úpravu tabuľky pre správcu (tu môžete dať klasický odkaz z prehliadača)
ODKAZ_PRE_SPRAVCU = "https://docs.google.com/spreadsheets/d/1tnZuvYAq47pbBpfAax0TfjGPSoCplkAXZmPD_GyjOTI/edit?usp=sharing"
# =========================================================================

# Inicializácia stavu úvodnej obrazovky
if "klikol_pokracovat" not in st.session_state:
    st.session_state.klikol_pokracovat = False

# Maximálne zjednodušená funkcia na načítanie dát bez delenia textu
def nacitat_data_z_sheets():
    try:
        # Priame načítanie z vami pripraveného CSV odkazu
        df = pd.read_csv(GOOGLE_CSV_URL)
        df.columns = ["Strana", "Hlasy"] + list(df.columns[2:])
        df["Hlasy"] = pd.to_numeric(df["Hlasy"], errors='coerce').fillna(0)
        return df
    except Exception as e:
        st.error(f"Nepodarilo sa stiahnuť dáta. Dôvod: {e}")
        return pd.DataFrame()

# =========================================================================
# SCÉNA 1: ÚVODNÁ OBRAZOVKA
# =========================================================================
if not st.session_state.klikol_pokracovat:
    _, stred, _ = st.columns([1, 2, 1])
    
    with stred:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.title("Volíme")
        st.subheader("Vitajte na stránke na prieskum popularity období")
        st.write("Táto aplikácia slúži na sledovanie priebežných výsledkov a bezpečné odovzdávanie hlasov voličov.")
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        if st.button("POKRAČOVAŤ", type="primary", use_container_width=True):
            st.session_state.klikol_pokracovat = True
            st.rerun()

# =========================================================================
# SCÉNA 2: PÔVODNÁ OBRAZOVKA (Graf, hlasovanie, správca)
# =========================================================================
else:
    st.title("Hlasovanie a popularita strán")
    
    df_db = nacitat_data_z_sheets()
    
    if not df_db.empty:
        celkovo_hlasov = df_db["Hlasy"].sum()
        df_db["Percentá (%)"] = df_db["Hlasy"].apply(lambda x: round((x / celkovo_hlasov) * 100, 2) if celkovo_hlasov > 0 else 0)

        st.subheader("Priebežné výsledky")
        st.bar_chart(df_db.set_index("Strana")["Percentá (%)"])
        st.dataframe(df_db[["Strana", "Hlasy", "Percentá (%)"]], use_container_width=True, hide_index=True)

    st.divider()
    st.subheader("Odovzdanie vášho hlasu")
    st.write("Hlasovanie je zabezpečené cez systém Google Forms. Každý volič môže po prihlásení odovzdať iba jeden hlas.")
    st.link_button("KLIKNI SEM A ODOVZDAJ SVOJ HLAS", ODKAZ_NA_FORMULAR, type="primary", use_container_width=True)

    # Sekcia pre správcu
    st.sidebar.header("Sekcia pre správcu")
    heslo = st.sidebar.text_input("Zadajte administrátorské heslo", type="password")

    if heslo == "admin123":
        st.sidebar.success("Prístup povolený!")
        st.subheader("Administrácia a správa dát")
        st.markdown(f"[Otvoriť Google Tabuľku na úpravu dát]({ODKAZ_PRE_SPRAVCU})")
        
        odkaz_na_editaciu_formulara = ODKAZ_NA_FORMULAR.replace("/viewform", "/edit")
        st.link_button("PREJSŤ NA VYMAZANIE HLASOV VO FORMULÁRI", odkaz_na_editaciu_formulara, type="secondary", use_container_width=True)
        
        if st.sidebar.button("Zobraziť úvodnú obrazovku"):
            st.session_state.klikol_pokracovat = False
            st.rerun()
                
    elif heslo != "":
        st.sidebar.error("Nesprávne heslo!")
