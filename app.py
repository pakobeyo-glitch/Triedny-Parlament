import streamlit as st
import pandas as pd
from streamlit_local_storage import StLocalStorage

# 1. Nastavenie vzhľadu stránky
st.set_page_config(page_title="Parlamentné hlasovanie", layout="wide")

# Inicializácia trvalého úložiska v prehliadači
local_storage = StLocalStorage()

# Predvolené (štartovacie) odkazy – SEM VLOŽTE VAŠE AKTUÁLNE
PREDVOLENA_TABULKA = "https://docs.google.com/spreadsheets/d/1tnZuvYAq47pbBpfAax0TfjGPSoCplkAXZmPD_GyjOTI/edit?usp=sharing"
PREDVOLENY_FORMULAR = "https://docs.google.com/forms/d/e/1FAIpQLSdFRKTTneLhn0KpOZI-TJPyWR-6Qj5FWXjcImFznMErBtgHbg/viewform?usp=header"

# Načítanie uložených odkazov z pamäte, inak sa použijú predvolené
GOOGLE_SHEET_URL = local_storage.get("ulozeny_sheet")
if GOOGLE_SHEET_URL is None:
    GOOGLE_SHEET_URL = PREDVOLENA_TABULKA

ODKAZ_NA_FORMULAR = local_storage.get("ulozeny_formular")
if ODKAZ_NA_FORMULAR is None:
    ODKAZ_NA_FORMULAR = PREDVOLENY_FORMULAR

# Inicializácia stavu úvodnej obrazovky
if "klikol_pokracovat" not in st.session_state:
    st.session_state.klikol_pokracovat = False

# Funkcia na načítanie dát
def nacitat_data_z_sheets():
    try:
        base_url = GOOGLE_SHEET_URL.split("/edit")
        csv_url_strany = f"{base_url[0]}/export?format=csv&gid=0"
        df = pd.read_csv(csv_url_strany)
        df.columns = ["Strana", "Hlasy"] + list(df.columns[2:])
        df["Hlasy"] = pd.to_numeric(df["Hlasy"], errors='coerce').fillna(0)
        return df
    except Exception as e:
        st.error(f"Chyba pri načítaní dát z Google Tabuľky: {e}")
        return pd.DataFrame()

# =========================================================================
# SCÉNA 1: ÚVODNÁ OBRAZOVKA
# =========================================================================
if st.session_state.klikol_pokracovat == False:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown("<h1 style='text-align: center;'>Volby</h1>", unsafe_allow_html=True)
        st.markdown("<h3 style='text-align: center;'>Prieskum popularity strán a hlasovanie</h3>", unsafe_allow_html=True)
        st.write("Vítame vás v aplikácii. Tu môžete sledovať priebežné výsledky volieb v reálnom čase.")
        
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("POKRAČOVAŤ", type="primary", use_container_width=True):
            st.session_state.klikol_pokracovat = True
            st.rerun()

# =========================================================================
# SCÉNA 2: HLAVNÁ OBRAZOVKA
# =========================================================================
else:
    st.title("Hlasovanie a popularita strán")
    
    df_db = nacitat_data_z_sheets()
    
    if not df_db.empty:
        celkovo_hlasov = df_db["Hlasy"].sum()
        df_db["Percentá (%)"] = df_db["Hlasy"].apply(lambda x: round((x / celkovo_hlasov) * 100, 2) if celkovo_hlasov > 0 else 0)

        st.subheader("Aktuálne výsledky popularity strán")
        st.bar_chart(df_db.set_index("Strana")["Percentá (%)"])
        st.dataframe(df_db[["Strana", "Hlasy", "Percentá (%)"]], use_container_width=True, hide_index=True)

    st.divider()
    st.subheader("Odovzdanie vášho hlasu")
    st.write("Hlasovanie je zabezpečené cez systém Google Forms.")
    st.link_button("KLIKNI SEM A ODOVZDAJ SVOJ HLAS", ODKAZ_NA_FORMULAR, type="primary", use_container_width=True)

    # Sekcia pre správcu v bočnom paneli
    st.sidebar.header("Sekcia pre správcu")
    heslo = st.sidebar.text_input("Zadajte administrátorské heslo", type="password")

    if heslo == "admin123":
        st.sidebar.success("Prístup povolený!")
        st.subheader("Administrácia a zmena zdrojov")
        
        # --- NOVINKA: Inputy pre správcu na zmenu URL ---
        nova_tabulka = st.text_input("URL novej Google Tabuľky:", value=GOOGLE_SHEET_URL)
        novy_formular = st.text_input("URL nového Google Formulára:", value=ODKAZ_NA_FORMULAR)
        
        if st.button("ULOŽIŤ NOVÉ ODKAZY NATRVALO"):
            local_storage.set("ulozeny_sheet", nova_tabulka)
            local_storage.set("ulozeny_formular", novy_formular)
            st.success("Odkazy boli úspešne uložené a zmenené!")
            st.rerun()
            
        st.divider()
        st.markdown(f"[Otvoriť aktívnu Google Tabuľku]({GOOGLE_SHEET_URL})")
        odkaz_na_editaciu = ODKAZ_NA_FORMULAR.replace("/viewform", "/edit")
        st.link_button("PREJSŤ NA VYMAZANIE HLASOV", odkaz_na_editaciu, type="secondary", use_container_width=True)
        
        if st.sidebar.button("Zobraziť úvodnú obrazovku"):
            st.session_state.klikol_pokracovat = False
            st.rerun()
                
    elif heslo != "":
        st.sidebar.error("Nesprávne heslo!")
