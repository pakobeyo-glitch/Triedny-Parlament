import streamlit as st
import pandas as pd

# 1. Nastavenie vzhľadu stránky
st.set_page_config(page_title="Hlasovanie", layout="wide")

# =========================================================================
# ZÁKLADNÉ PREDVOLENÉ ODKAZY (Sem vložte tie vaše pôvodné)
# =========================================================================
if "google_sheet_url" not in st.session_state:
    st.session_state.google_sheet_url = "https://docs.google.com/spreadsheets/d/1tnZuvYAq47pbBpfAax0TfjGPSoCplkAXZmPD_GyjOTI/edit?usp=sharing"

if "odkaz_na_formular" not in st.session_state:
    st.session_state.odkaz_na_formular = "https://docs.google.com/forms/d/e/1FAIpQLSdFRKTTneLhn0KpOZI-TJPyWR-6Qj5FWXjcImFznMErBtgHbg/viewform?usp=header"
# =========================================================================

# Inicializácia stavu úvodnej obrazovky
if "klikol_pokracovat" not in st.session_state:
    st.session_state.klikol_pokracovat = False

# Funkcia na bezpečné načítanie dát
def nacitat_data_z_sheets():
    try:
        base_url = st.session_state.google_sheet_url.split("/edit")
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
    col1, col2, col3 = st.columns(3)
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
# SCÉNA 2: HLAVNÁ OBRAZOVKA (Graf, hlasovanie, správca)
# =========================================================================
else:
    st.title("Hlasovanie a popularita strán")
    
    df_db = nacitat_data_z_sheets()
    
    if not df_db.empty:
        celkovo_hlasov = df_db["Hlasy"].sum()
        df_db["Percentá (%)"] = df_db["Hlasy"].apply(lambda x: round((x / celkovo_hlasov) * 100, 2) if celkovo_hlasov > 0 else 0)

        # Vykreslenie grafov
        st.subheader("Priebežné výsledky popularity strán")
        
        # 1. Klasický stĺpcový graf
        st.write("Stĺpcový prehľad:")
        st.bar_chart(df_db.set_index("Strana")["Percentá (%)"])
        
        # 2. Koláčový graf
        st.write("Podielový (koláčový) prehľad:")
        import plotly.express as px
        fig = px.pie(df_db, values='Percentá (%)', names='Strana', 
                     color_discrete_sequence=px.colors.sequential.RdBu)
        st.plotly_chart(fig, use_container_width=True)
        
        # Pôvodná tabuľka s podrobnosťami
        st.dataframe(df_db[["Strana", "Hlasy", "Percentá (%)"]], use_container_width=True, hide_index=True)

    st.divider()
    st.subheader("Odovzdanie vášho hlasu")
    st.write("Hlasovanie je zabezpečené cez systém Google Forms.")
    st.link_button("KLIKNI SEM A ODOVZDAJ SVOJ HLAS", st.session_state.odkaz_na_formular, type="primary", use_container_width=True)
    st.divider()
    st.write("Pri komplikáciach sa obráťte na email: chlebus1@mudronka.sk")

    # Sekcia pre správcu v bočnom paneli
    st.sidebar.header("Sekcia pre správcu")
    heslo = st.sidebar.text_input("Zadajte administrátorské heslo", type="password")

    if heslo == "admin123":
        st.sidebar.success("Prístup povolený!")
        st.subheader("Administrácia a zmena zdrojov")
        
        # Vstupné polia pre správcu
        nova_tabulka = st.text_input("URL novej Google Tabuľky:", value=st.session_state.google_sheet_url)
        novy_formular = st.text_input("URL nového Google Formulára:", value=st.session_state.odkaz_na_formular)
        
        if st.button("DOČASNE AKTUALIZOVAŤ ODKAZY"):
            st.session_state.google_sheet_url = nova_tabulka
            st.session_state.odkaz_na_formular = novy_formular
            st.success("Odkazy boli v tejto relácii zmenené!")
            st.rerun()
            
        st.info("Ak chcete zmeny uložiť navždy, skopírujte tieto odkazy a prepíšte ich na riadkoch 11 a 14 na GitHube.")
        
        st.divider()
        st.markdown(f"[Otvoriť aktívnu Google Tabuľku]({st.session_state.google_sheet_url})")
        odkaz_na_editaciu = st.session_state.odkaz_na_formular.replace("/viewform", "/edit")
        st.link_button("PREJSŤ NA VYMAZANIE HLASOV", odkaz_na_editaciu, type="secondary", use_container_width=True)
        
        if st.sidebar.button("Zobraziť úvodnú obrazovku"):
            st.session_state.klikol_pokracovat = False
            st.rerun()
                
    elif heslo != "":
        st.sidebar.error("Nesprávne heslo!")
