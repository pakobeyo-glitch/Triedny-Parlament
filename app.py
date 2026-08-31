import streamlit as st
import pandas as pd

# 1. Nastavenie vzhľadu stránky
st.set_page_config(page_title="Parlamentné hlasovanie", layout="wide")

# =========================================================================
# TU PREPÍŠTE ODKAZY ZA VAŠE VLASTNÉ
# =========================================================================
GOOGLE_SHEET_URL = "https://docs.google.com/spreadsheets/d/1tnZuvYAq47pbBpfAax0TfjGPSoCplkAXZmPD_GyjOTI/edit?usp=sharing"
ODKAZ_NA_FORMULAR = "https://docs.google.com/forms/d/e/1FAIpQLSdFRKTTneLhn0KpOZI-TJPyWR-6Qj5FWXjcImFznMErBtgHbg/viewform?usp=header"
# =========================================================================

# Inicializácia stavu – na začiatku sme na úvodnej scéne (False)
if "klikol_pokracovat" not in st.session_state:
    st.session_state.klikol_pokracovat = False

# Funkcia na bezpečné načítanie dát z tabuľky
def nacitat_data_z_sheets():
    try:
        url_cista = GOOGLE_SHEET_URL.split("?").split("#")
        if url_cista.endswith("/edit"):
            csv_url_strany = url_cista.replace("/edit", "/export?format=csv&gid=0")
        elif url_cista.endswith("/"):
            csv_url_strany = url_cista + "export?format=csv&gid=0"
        else:
            csv_url_strany = url_cista + "/export?format=csv&gid=0"
        
        df = pd.read_csv(csv_url_strany)
        df.columns = ["Strana", "Hlasy"] + list(df.columns[2:])
        df["Hlasy"] = pd.to_numeric(df["Hlasy"], errors='coerce').fillna(0)
        return df
    except Exception as e:
        return pd.DataFrame()

# =========================================================================
# SCÉNA 1: ÚVODNÁ OBRAZOVKA
# =========================================================================
if not st.session_state.klikol_pokracovat:
    # Vycentrujeme obsah na stred pomocou stĺpcov
    _, stred, _ = st.columns([1, 2, 1])
    
    with stred:
        st.markdown("<br><br>", unsafe_allow_html=True) # Voľné miesto od vrchu
        st.title("Volíme spolu")
        st.subheader("Vitajte v aplikácii na prieskum popularity období")
        st.write("Táto aplikácia slúži na sledovanie priebežných výsledkov a bezpečné odovzdávanie hlasov voličov.")
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Tlačidlo na presun do druhej scény
        if st.button("POKRAČOVAŤ", type="primary", use_container_width=True):
            st.session_state.klikol_pokracovat = True
            st.rerun()

# =========================================================================
# SCÉNA 2: PÔVODNÁ OBRAZOVKA (Graf, hlasovanie, správca)
# =========================================================================
else:
    st.title("Hlasovanie a popularita období")
    
    # Načítanie a prepočet dát
    df_db = nacitat_data_z_sheets()
    
    if not df_db.empty:
        celkovo_hlasov = df_db["Hlasy"].sum()
        df_db["Percentá (%)"] = df_db["Hlasy"].apply(lambda x: round((x / celkovo_hlasov) * 100, 2) if celkovo_hlasov > 0 else 0)

        # 1. Zobrazenie grafu pre všetkých
        st.subheader("Aktuálne výsledky popularity strán")
        st.bar_chart(df_db.set_index("Strana")["Percentá (%)"])
        st.dataframe(df_db[["Strana", "Hlasy", "Percentá (%)"]], use_container_width=True, hide_index=True)
    else:
        st.warning("Systém čaká na pripojenie k tabuľke.")

    # 2. Tlačidlo pre voliča
    st.divider()
    st.subheader("Odovzdanie vášho hlasu")
    st.write("Hlasovanie je zabezpečené cez systém Google Forms. Každý volič môže po prihlásení odovzdať iba jeden hlas.")
    st.link_button("KLIKNITE SEM A ODOVZDAJ SVOJ HLAS", ODKAZ_NA_FORMULAR, type="primary", use_container_width=True)

    # 3. Sekcia pre správcu (v bočnom paneli)
    st.sidebar.header("Sekcia pre admina")
    heslo = st.sidebar.text_input("Zadajte administrátorské heslo", type="password")

    if heslo == "admin123":
        st.sidebar.success("Prístup povolený!")
        st.subheader("Administrácia a správa dát")
        st.markdown(f"[Otvoriť Google Tabuľku na úpravu dát]({GOOGLE_SHEET_URL})")
        
        odkaz_na_editaciu_formulara = ODKAZ_NA_FORMULAR.replace("/viewform", "/edit")
        st.link_button("PREJSŤ NA VYMAZANIE HLASOV VO FORMULÁRI", odkaz_na_editaciu_formulara, type="secondary", use_container_width=True)
        
        # Možnosť pre správcu vrátiť sa na úvodnú scénu
        if st.sidebar.button("Zobraziť úvodnú obrazovku"):
            st.session_state.klikol_pokracovat = False
            st.rerun()
                
    elif heslo != "":
        st.sidebar.error("Nesprávne heslo!")
