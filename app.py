import streamlit as st
import pandas as pd

# 1. Nastavenie vzhľadu stránky
st.set_page_config(page_title="Hlasovanie", layout="wide")

# =========================================================================
# TU PREPÍŠEM ODKAZY ZA VAŠE VLASTNÉ
# =========================================================================
GOOGLE_SHEET_URL = "https://docs.google.com/spreadsheets/d/1tnZuvYAq47pbBpfAax0TfjGPSoCplkAXZmPD_GyjOTI/edit?usp=sharing"
ODKAZ_NA_FORMULAR = "https://docs.google.com/forms/d/e/1FAIpQLSdFRKTTneLhn0KpOZI-TJPyWR-6Qj5FWXjcImFznMErBtgHbg/viewform?usp=header"
# =========================================================================

# Inicializácia stavu úvodnej obrazovky (aby si web pamätal, kde sa nachádza)
if "klikol_pokracovat" not in st.session_state:
    st.session_state.klikol_pokracovat = False

# Funkcia na načítanie dát – presne tá, ktorá vám doteraz fungovala
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
# SCÉNA 1: ÚVODNÁ OBRAZOVKA (Zobrazí sa hneď po otvorení)
# =========================================================================
if st.session_state.klikol_pokracovat == False:
    # Vytvoríme 3 stĺpce, aby sme text vycentrovali na stred
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown("<h1 style='text-align: center;'>Volby</h1>", unsafe_allow_html=True)
        st.markdown("<h3 style='text-align: center;'>Prieskum popularity období a hlasovanie</h3>", unsafe_allow_html=True)
        st.write("Vítame vás v aplikácii. Tu môžete sledovať priebežné výsledky volieb a bezpečne odovzdať svoj hlas.")
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Tlačidlo na prepnutie do hlavnej scény
        if st.button("POKRAČOVAŤ", type="primary", use_container_width=True):
            st.session_state.klikol_pokracovat = True
            st.rerun()

# =========================================================================
# SCÉNA 2: HLAVNÁ OBRAZOVKA (Graf, hlasovanie, správca - zobrazí sa po kliknutí)
# =========================================================================
else:
    st.title("Hlasovanie a popularita období")
    
    # Načítanie dát z predošlej funkčnej verzie
    df_db = nacitat_data_z_sheets()
    
    if not df_db.empty:
        celkovo_hlasov = df_db["Hlasy"].sum()
        df_db["Percentá (%)"] = df_db["Hlasy"].apply(lambda x: round((x / celkovo_hlasov) * 100, 2) if celkovo_hlasov > 0 else 0)

        # Zobrazenie grafu pre všetkých
        st.subheader("Aktuálne výsledky popularity strán")
        st.bar_chart(df_db.set_index("Strana")["Percentá (%)"])
        st.dataframe(df_db[["Strana", "Hlasy", "Percentá (%)"]], use_container_width=True, hide_index=True)

    # Tlačidlo na odkaz na Google Formulár pre voliča
    st.divider()
    st.subheader("Odovzdanie vášho hlasu")
    st.write("Hlasovanie je zabezpečené cez systém Google Forms. Každý volič môže po prihlásení odovzdať iba jeden hlas.")
    st.link_button("KLIKNI SEM A ODOVZDAJ SVOJ HLAS", ODKAZ_NA_FORMULAR, type="primary", use_container_width=True)

    # Sekcia pre správcu v bočnom paneli
    st.sidebar.header("Sekcia pre správcu")
    heslo = st.sidebar.text_input("Zadajte administrátorské heslo", type="password")

    if heslo == "admin123":
        st.sidebar.success("Prístup povolený!")
        st.subheader("Administrácia a správa dát")
        st.markdown(f"[Otvoriť Google Tabuľku na úpravu dát]({GOOGLE_SHEET_URL})")
        
        odkaz_na_editaciu_formulara = ODKAZ_NA_FORMULAR.replace("/viewform", "/edit")
        st.link_button("PREJSŤ NA VYMAZANIE HLASOV VO FORMULÁRI", odkaz_na_editaciu_formulara, type="secondary", use_container_width=True)
        
        # Možnosť pre správcu vrátiť sa na úvodnú scénu pri testovaní
        if st.sidebar.button("Zobraziť úvodnú obrazovku"):
            st.session_state.klikol_pokracovat = False
            st.rerun()
                
    elif heslo != "":
        st.sidebar.error("Nesprávne heslo!")
