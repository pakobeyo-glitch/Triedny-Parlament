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

if "hlasovanie_povolene" not in st.session_state:
    st.session_state.hlasovanie_povolene = True

# Pamäť pre číslo scény (1 = Úvod, 2 = Grafy/Hlasovanie, 3 = Informácie)
if "cislo_sceny" not in st.session_state:
    st.session_state.cislo_sceny = 1
    
# =========================================================================

# Inicializácia stavu úvodnej obrazovky
if "klikol_pokracovat" not in st.session_state:
    st.session_state.klikol_pokracovat = False

# Inicializácia stavu hlasovania (Predvolene zapnuté)
if "hlasovanie_povolene" not in st.session_state:
    st.session_state.hlasovanie_povolene = True

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
    # Vytvoríme 3 stĺpce, stredný bude o niečo širší (pomer 1:2:1), aby text dobre vyzeral
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        
        # Odkaz na vaše logo
        URL_LOGA = "https://mudronka.edupage.org/photos/skin/logo/logo_skoly.jpg"
        
        # --- HTML TRIK NA VYCENTROVANIE LOGA A TEXTOV ---
        st.markdown(
            f"""
            <div style="text-align: center;">
                <img src="{URL_LOGA}" width="180" style="margin-bottom: 20px;">
                <h1 style="margin-top: 0px;">Hlasovanie</h1>
                <h3>Prieskum popularity strán a hlasovanie</h3>
                <p style="font-size: 16px; color: #555; margin-bottom: 30px;">
                    Vítame vás v aplikácii. Tu môžete sledovať priebežné výsledky volieb v reálnom čase a bezpečne odovzdať svoj hlas.
                </p>
            </div>
            """, 
            unsafe_allow_html=True
        )
        
        # Grafy a Hlasovanie (Scéna 2)
        if st.button("POKRAČOVAŤ NA HLASOVANIE", type="primary", use_container_width=True):
            st.session_state.cislo_sceny = 2
            st.rerun()
            
        st.markdown("<div style='margin-bottom: 10px;'></div>", unsafe_allow_html=True)
        
        # Nová textová scéna (Scéna 3)
        if st.button("BÁSEŇ", type="secondary", use_container_width=True):
            st.session_state.cislo_sceny = 3
            st.rerun()

# =========================================================================
# SEKCIA 2: HLAVNÁ OBRAZOVKA (Graf, hlasovanie, správca)
# =========================================================================
elif st.session_state.cislo_sceny == 2:
    # Tlačidlo späť v bočnom menu pre Scénu 2
    if st.sidebar.button("Späť na úvod", use_container_width=True):
        st.session_state.cislo_sceny = 1
        st.rerun()

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
        st.write("Koláčový prehľad:")
        import plotly.express as px
        fig = px.pie(df_db, values='Percentá (%)', names='Strana', 
                     color_discrete_sequence=px.colors.sequential.RdBu)
        st.plotly_chart(fig, use_container_width=True)
        
        # Pôvodná tabuľka s podrobnosťami
        st.dataframe(df_db[["Strana", "Hlasy", "Percentá (%)"]], use_container_width=True, hide_index=True)

# =========================================================================
# SEKCIA 3: ROLE
# =========================================================================
    # --- ROLA: VOLIČ ---
    st.divider()
    st.subheader("Odovzdanie vášho hlasu")
    
    # Kód skontroluje, či správca hlasovanie nevypol
    if st.session_state.hlasovanie_povolene:
        st.write("Hlasovanie je zabezpečené cez systém Google Forms.")
        st.link_button("KLIKNI SEM A ODOVZDAJ SVOJ HLAS", st.session_state.odkaz_na_formular, type="primary", use_container_width=True)
    else:
        # Ak je vypnuté, tlačidlo zmizne a ukáže sa toto:
        st.error("Hlasovanie bolo správcom ukončené. Nové hlasy už nie je možné odovzdať.")
        
    st.divider()
    st.write("Pri problémoch sa prosím obráťte na mňa, alebo mi napíšte na email chlebus1@mudronka.sk")
    
    # Sekcia pre správcu v bočnom paneli
    st.sidebar.header("Sekcia pre správcu")
    heslo = st.sidebar.text_input("Zadajte administrátorské heslo", type="password")
    if st.sidebar.button("Zobraziť úvodnú obrazovku"):
            st.session_state.klikol_pokracovat = False
            st.rerun()

    if heslo == "admin123" or "ucitel26":
        st.sidebar.success("Prístup povolený!")
        st.divider()
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
        st.subheader("Ovládanie hlasovania")
        
        # Prepínač, ktorý mení True/False v pamäti
        stav = st.radio("Stav volebnej miestnosti:", ("Zapnuté (Otvorené)", "Vypnuté (Zatvorené)"), 
                        index=0 if st.session_state.hlasovanie_povolene else 1)
        
        if st.button("POTVRDIŤ ZMENU STAVU"):
            st.session_state.hlasovanie_povolene = (stav == "Zapnuté (Otvorené)")
            st.success(f"Stav hlasovania bol zmenený na: {stav}")
            st.rerun()
            
        st.divider()
        st.markdown(f"[Otvoriť aktívnu Google Tabuľku]({st.session_state.google_sheet_url})")
        odkaz_na_editaciu = st.session_state.odkaz_na_formular.replace("/viewform", "/edit")
        st.link_button("PREJSŤ NA VYMAZANIE HLASOV", odkaz_na_editaciu, type="secondary", use_container_width=True)
                
    elif heslo != "":
        st.sidebar.error("Nesprávne heslo!")

# =========================================================================
# SCÉNA 4: ČISTÁ TEXTOVÁ OBRAZOVKA (Informácie)
# =========================================================================
elif st.session_state.cislo_sceny == 3:
    # TLAČIDLO V BOČNOM MENU
    if st.sidebar.button("Späť na úvod", use_container_width=True):
        st.session_state.cislo_sceny = 1
        st.rerun()
        
    col1, col2, col3 = st.columns(3)
    
    with col2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown("<h1 style='text-align: center;'>Pravidlá a informácie</h1>", unsafe_allow_html=True)
        
        # --- SEM SI MÔŽETE NAPÍSAŤ SVOJ ČISTÝ TEXT ---
        st.write("Tu sú základné informácie o našom parlamentnom prieskume:")
        st.write("1. Každý žiak má právo odovzdať **iba jeden platný hlas**.")
        st.write("2. Hlasovanie prebieha anonymne prostredníctvom priloženého Google formulára.")
        st.write("3. Výsledky sa aktualizujú naživo každých pár minút po odoslaní formulára.")
        st.info("Pred hlasovaním si poriadne premyslite svoju voľbu. Hlas nie je možné vziať späť.")
