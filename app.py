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

# 2. Funkcia na bezpečné načítanie dát bez citlivosti na názvy stĺpcov
def nacitat_data_z_sheets():
    try:
        # Vytiahneme čisté ID tabuľky pre priamy export do CSV
        sheet_id = GOOGLE_SHEET_URL.split("/d/")[1].split("/")[0]
        csv_url_strany = f"https://google.com{sheet_id}/export?format=csv&gid=0"
        
        # Načítanie dát cez Pandas
        df = pd.read_csv(csv_url_strany)
        
        # Automatické premenovanie stĺpcov podľa poradia (1. stĺpec = Strana, 2. stĺpec = Hlasy)
        df.columns = ["Strana", "Hlasy"] + list(df.columns[2:])
        df["Hlasy"] = pd.to_numeric(df["Hlasy"], errors='coerce').fillna(0)
        return df
    except Exception as e:
        st.error(f"Chyba pri načítaní dát z Google Tabuľky: {e}")
        return pd.DataFrame()

# Spustenie načítania dát
df_db = nacitat_data_z_sheets()

if not df_db.empty:
    # 3. Výpočet percent (priamo v aplikácii pre stopercentnú presnosť grafu)
    celkovo_hlasov = df_db["Hlasy"].sum()
    df_db["Percentá (%)"] = df_db["Hlasy"].apply(lambda x: round((x / celkovo_hlasov) * 100, 2) if celkovo_hlasov > 0 else 0)

    # --- ROLA: SLEDOVATEĽ (Zobrazenie grafu pre všetkých) ---
    st.subheader("Aktuálne výsledky popularity strán")
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
        st.info("Ako správca môžete upravovať zoznam strán alebo priamo mazať testovacie hlasy vo vašej Google Tabuľke.")
        
        # Rýchly odkaz pre správcu na úpravu zdrojovej tabuľky
        st.markdown(f"[Otvoriť Google Tabuľku na manuálnu úpravu dát]({GOOGLE_SHEET_URL})")
                
    elif heslo != "":
        st.sidebar.error("Nesprávne heslo!")
else:
    st.warning("Systém čaká na správne prepojenie s databázou. Skontrolujte URL adresu tabuľky a jej práva na zdieľanie.")

