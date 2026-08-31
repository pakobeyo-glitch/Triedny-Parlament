import streamlit as st
import pandas as pd

# 1. Nastavenie vzhľadu stránky
st.set_page_config(page_title="Parlamentné hlasovanie", layout="wide")
st.title("Hlasovanie a popularita strán")

# =========================================================================
# TU PREPÍŠTE ODKAZY ZA VAŠE VLASTNÉ
# =========================================================================
# 1. Odkaz na vašu hlavnú Google Tabuľku (zo zložky so šípkou na webe)
GOOGLE_SHEET_URL = "https://docs.google.com/spreadsheets/d/1tnZuvYAq47pbBpfAax0TfjGPSoCplkAXZmPD_GyjOTI/edit?usp=sharing"

# 2. Odkaz na váš zverejnený Google Formulár (zo sekcie Odoslať -> ikona reťaze)
ODKAZ_NA_FORMULAR = "https://docs.google.com/forms/d/e/1FAIpQLSdFRKTTneLhn0KpOZI-TJPyWR-6Qj5FWXjcImFznMErBtgHbg/viewform?usp=header"
# =========================================================================

# 2. Funkcia na bezpečné načítanie dát
def nacitat_data_z_sheets():
    try:
        # Ak odkaz obsahuje koncovku /edit alebo parametre, zmeníme ju priamo na CSV export
        url_cista = GOOGLE_SHEET_URL.split("?")[0].split("#")[0]
        if url_cista.endswith("/edit"):
            csv_url_strany = url_cista.replace("/edit", "/export?format=csv&gid=0")
        elif url_cista.endswith("/"):
            csv_url_strany = url_cista + "export?format=csv&gid=0"
        else:
            csv_url_strany = url_cista + "/export?format=csv&gid=0"
        
        # Načítanie dát cez Pandas
        df = pd.read_csv(csv_url_strany)
        
        # Automatické premenovanie stĺpcov podľa poradia
        df.columns = ["Strana", "Hlasy"] + list(df.columns[2:])
        df["Hlasy"] = pd.to_numeric(df["Hlasy"], errors='coerce').fillna(0)
        return df
    except Exception as e:
        st.error(f"Chyba pri načítaní dát z Google Tabuľky: {e}")
        return pd.DataFrame()# Spustenie načítania dát
        
df_db = nacitat_data_z_sheets()

if not df_db.empty:
    # 3. Výpočet percent (priamo v aplikácii pre stopercentnú presnosť grafu)
    celkovo_hlasov = df_db["Hlasy"].sum()
    df_db["Percentá (%)"] = df_db["Hlasy"].apply(lambda x: round((x / celkovo_hlasov) * 100, 2) if celkovo_hlasov > 0 else 0)

    # --- ROLA: SLEDOVATEĽ (Zobrazenie grafu pre všetkých) ---
    st.subheader("Aktuálne výsledky popularity období")
    st.bar_chart(df_db.set_index("Strana")["Percentá (%)"])
    
    # Prehľadná tabuľka s podrobnosťami pod grafom
    st.dataframe(df_db[["Strana", "Hlasy", "Percentá (%)"]], use_container_width=True, hide_index=True)

    # --- ROLA: VOLIČ (Tlačidlo presmerovania na bezpečné hlasovanie) ---
    st.divider()
    st.subheader("Odovzdanie vášho hlasu")
    st.write("Hlasovanie je zabezpečené cez systém Google. Každý volič môže po prihlásení odovzdať iba jeden hlas.")
    
    # Veľké modré tlačidlo, ktoré otvorí zverejnený formulár
    st.link_button("KLIKNI SEM A ODOVZDAJ SVOJ HLAS", ODKAZ_NA_FORMULAR, type="primary", use_container_width=True)

    # --- ROLA: SPRÁVCA (Zabezpečená sekcia pod heslom) ---
    st.divider()
    st.sidebar.header("Sekcia pre správcu")
    heslo = st.sidebar.text_input("Zadajte administrátorské heslo", type="password")

    if heslo == "admin123":
        st.sidebar.success("Prístup povolený!")
        st.subheader("Administrácia a správa dát")
        
        # 1. Odkaz na manuálnu úpravu tabuľky
        st.markdown(f"[Otvoriť Google Tabuľku na úpravu dát]({GOOGLE_SHEET_URL})")
        
        st.divider()
        st.subheader("Vyresetovanie všetkých hlasov")
        st.warning("Pozor: Ak chcete vymazať doterajšie hlasy a spustiť hlasovanie nanovo, postupujte takto:")
        
        st.write("1. Otvorte editor vášho Google Formulára.")
        st.write("2. Prejdite na kartu **Odpovede** (Responses).")
        st.write("3. Kliknite na **tri bodky** vpravo hore a vyberte **Odstrániť všetky odpovede** (Delete all responses).")
        st.write("4. Tým sa tabuľka vyprázdni a graf sa automaticky vynuluje.")
        
        # Vytiahnutie odkazu na editáciu formulára (z viewform urobíme edit)
        odkaz_na_editaciu_formulara = ODKAZ_NA_FORMULAR.replace("/viewform", "/edit")
        
        # Rýchle tlačidlo pre správcu na prechod do editácie formulára
        st.link_button("PREJSŤ NA VYMAZANIE HLASOV VO FORMULÁRI", odkaz_na_editaciu_formulara, type="secondary", use_container_width=True)
                
    elif heslo != "":
        st.sidebar.error("Nesprávne heslo!")
