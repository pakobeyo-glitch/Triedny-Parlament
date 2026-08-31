import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Nastavenie vzhľadu stránky (MUSÍ BYŤ ÚPLNE PRVÉ)
st.set_page_config(page_title="Hlasovanie", layout="wide")

# =========================================================================
# FUNKCIE NA PREPÍNANIE SCÉN (Definované hore, aby ich Python hneď poznal)
# =========================================================================
def preklop_na_uvod():
    st.session_state.cislo_sceny = 1

def preklop_na_grafy():
    st.session_state.cislo_sceny = 2

def preklop_na_info():
    st.session_state.cislo_sceny = 3

# =========================================================================
# ZÁKLADNÉ PREDVOLENÉ ODKAZY
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
# SCÉNA 1: ÚVODNÁ OBRAZOVKA (Rozcestník)
# =========================================================================
if st.session_state.cislo_sceny == 1:
    col1, col2, col3 = st.columns(3)
    
    with col2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        URL_LOGA = "https://pbs.twimg.com/profile_images/2155836604/logo_mudronka_400x400.jpg"
        
        st.markdown(
            f"""
            <div style="text-align: center;">
                <img src="{URL_LOGA}" width="180" style="margin-bottom: 20px; border-radius: 10px;">
                <h1 style="margin-top: 0px;">Hlasovanie</h1>
                <h3>Prieskum popularity strán a hlasovanie</h3>
                <p style="font-size: 16px; color: #555; margin-bottom: 30px;">
                    Vítame vás v aplikácii. Vyberte si, kam chcete pokračovať:
                </p>
            </div>
            """, 
            unsafe_allow_html=True
        )
        
        # Samostatné riadky s tlačidlami pomocou on_click (BEZ DVOJBODIEK NA KONCI)
        st.button("POKRAČOVAŤ NA STRÁNKU", type="primary", use_container_width=True, on_click=preklop_na_grafy)
        st.markdown("<div style='margin-bottom: 10px;'></div>", unsafe_allow_html=True)
        st.button("PRAVIDLÁ A INFORMÁCIE", type="secondary", use_container_width=True, on_click=preklop_na_info)


# =========================================================================
# SCÉNA 2: HLAVNÁ OBRAZOVKA (Grafy, hlasovanie, správca)
# =========================================================================
elif st.session_state.cislo_sceny == 2:
    # Tlačidlo späť v bočnom menu pre Scénu 2
    st.sidebar.button("Späť na úvod", use_container_width=True, on_click=preklop_na_uvod)
        
    st.title("Hlasovanie a popularita strán")
    
    df_db = nacitat_data_z_sheets()
    
    if not df_db.empty:
        celkovo_hlasov = df_db["Hlasy"].sum()
        df_db["Percentá (%)"] = df_db["Hlasy"].apply(lambda x: round((x / celkovo_hlasov) * 100, 2) if celkovo_hlasov > 0 else 0)

        st.subheader("Priebežné výsledky popularity strán")
        st.write("Stĺpcový prehľad:")
        st.bar_chart(df_db.set_index("Strana")["Percentá (%)"])
        
        st.write("Podielový (koláčový) prehľad:")
        fig = px.pie(df_db, values='Percentá (%)', names='Strana', color_discrete_sequence=px.colors.sequential.RdBu)
        st.plotly_chart(fig, use_container_width=True)
        
        st.dataframe(df_db[["Strana", "Hlasy", "Percentá (%)"]], use_container_width=True, hide_index=True)

    st.divider()
    st.subheader("Odovzdanie vášho hlasu")
    if st.session_state.hlasovanie_povolene:
        st.write("Hlasovanie je zabezpečené cez systém Google Forms.")
        st.link_button("KLIKNI SEM A ODOVZDAJ SVOJ HLAS", st.session_state.odkaz_na_formular, type="primary", use_container_width=True)
    else:
        st.error("Hlasovanie bolo správcom ukončené. Nové hlasy už nie je možné odovzdať.")

    st.divider()
    st.write("V prípade komplikácii sa obráťte na mňa, alebo mi napíšte na email chlebus1@mudronka.sk.")

    # Sekcia pre správcu v bočnom paneli
    st.sidebar.divider()
    st.sidebar.header("Sekcia pre správcu")
    heslo = st.sidebar.text_input("Zadajte administrátorské heslo", type="password")

    if heslo == "admin123":
        st.sidebar.success("Prístup povolený!")
        st.subheader("Administrácia a zmena zdrojov")
        
        nova_tabulka = st.text_input("URL novej Google Tabuľky:", value=st.session_state.google_sheet_url)
        novy_formular = st.text_input("URL nového Google Formulára:", value=st.session_state.odkaz_na_formular)
        
        if st.button("DOČASNE AKTUALIZOVAŤ ODKAZY"):
            st.session_state.google_sheet_url = nova_tabulka
            st.session_state.odkaz_na_formular = novy_formular
            st.success("Odkazy zmenené!")
            st.rerun()
            
        st.divider()
        st.subheader("Ovládanie hlasovania")
        stav = st.radio("Stav volebnej miestnosti:", ("Zapnuté (Otvorené)", "Vypnuté (Zatvorené)"), index=0 if st.session_state.hlasovanie_povolene else 1)
        if st.button("POTVRDIŤ ZMENU STAVU"):
            st.session_state.hlasovanie_povolene = (stav == "Zapnuté (Otvorené)")
            st.success(f"Stav zmenený na: {stav}")
            st.rerun()
            
        st.divider()
        st.markdown(f"[Otvoriť aktívnu Google Tabuľku]({st.session_state.google_sheet_url})")
        odkaz_na_editaciu = st.session_state.odkaz_na_formular.replace("/viewform", "/edit")
        st.link_button("PREJSŤ NA VYMAZANIE HLASOV", odkaz_na_editaciu, type="secondary", use_container_width=True)
                
    elif heslo != "":
        st.sidebar.error("Nesprávne heslo!")


# =========================================================================
# SCÉNA 3: ČISTÁ TEXTOVÁ OBRAZOVKA (Informácie)
# =========================================================================
elif st.session_state.cislo_sceny == 3:
    # Tlačidlo späť v bočnom menu pre Scénu 3
    st.sidebar.button("Späť na úvod", use_container_width=True, on_click=preklop_na_uvod)
        
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
