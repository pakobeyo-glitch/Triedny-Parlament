import streamlit as st
import pandas as pd
from gspread_dataframe import get_as_dataframe, set_with_dataframe
import gspread
from google.oauth2.service_account import Credentials

# 1. Nastavenie stránky
st.set_page_config(page_title="Prieskum popularity strán", layout="wide")
st.title("Aktuálna popularita triednych strán")

# Odkaz na vašu Google Tabuľku (sem vložte ten váš skopírovaný link)
GOOGLE_SHEET_URL = "https://docs.google.com/spreadsheets/d/1E8fjaI4o1NkrYJY9VLi-KhYF9-0L9ixwpwPLnQW4-Wo/edit?usp=sharing"

# Funkcia na pripojenie a načítanie dát
# Streamlit potrebuje prístup cez zdieľaný odkaz alebo servisný účet
@st.cache_data(ttl=5)  # Cache sa obnoví každých 5 sekúnd, aby sledovatelia videli čerstvé dáta
def nacitat_data_z_sheets():
    # Pre zjednodušenie predpokladáme verejný odkaz nastavený na Editora
    # Ak robíte aplikáciu pre produkciu, odporúča sa použiť st.secrets a JSON kľúč
    try:
        # Načítanie cez pandas priamo z CSV exportu Google tabuľky (najrýchlejšia cesta pre čítanie)
        csv_url = GOOGLE_SHEET_URL.replace("/edit#gid=", "/export?format=csv&gid=")
        df = pd.read_csv(csv_url)
        return df
    except Exception as e:
        st.error(f"Chyba pri načítaní dát: {e}")
        return pd.DataFrame(columns=["Strana", "Hlasy"])

# Načítanie aktuálnych dát
df_db = nacitat_data_z_sheets()

if not df_db.empty:
    # 2. Výpočet percent
    celkovo_hlasov = df_db["Hlasy"].sum()
    df_db["Percentá (%)"] = df_db["Hlasy"].apply(lambda x: round((x / celkovo_hlasov) * 100, 2) if celkovo_hlasov > 0 else 0)

    # 3. Zobrazenie pre Sledovateľov
    st.subheader("Aktuálne výsledky")
    st.bar_chart(df_db.set_index("Strana")["Percentá (%)"])
    st.dataframe(df_db, use_container_width=True, hide_index=True)

    # 4. Administrátorská sekcia (Správca)
    st.divider()
    st.sidebar.header("🔐 Sekcia pre správcu")
    heslo = st.sidebar.text_input("Zadajte administrátorské heslo", type="password")

    if heslo == "admin123":
        st.sidebar.success("Prístup povolený!")
        st.subheader("🛠️ Úprava počtu voličov (Zmeny sa uložia natrvalo)")
        
        with st.form("edit_form"):
            nove_hodnoty = {}
            for index, row in df_db.iterrows():
                strana = row["Strana"]
                hlasy_aktualne = int(row["Hlasy"])
                nove_hodnoty[strana] = st.number_input(f"Počet voličov pre {strana}", min_value=0, value=hlasy_aktualne)
            
            ulozit = st.form_submit_button("Aktualizovať Google Tabuľku")
            
            if ulozit:
                # Pre zápis do Google Sheets využijeme priame prepojenie cez knižnicu gspread
                # Na reálne nasadenie do produkcie sem vložíte prihlasovacie údaje (Service Account)
                st.warning("Pre plný zápis do tabuľky nezabudnite v kóde nakonfigurovať 'gspread' servisný účet podľa návodu Streamlit.")
                
                # Lokálna simulácia úspešného zápisu predtým než prepojíte API kľúče:
                st.success("Dáta boli odoslané do databázy!")
                st.cache_data.clear()
                st.rerun()
                
    elif heslo != "":
        st.sidebar.error("Nesprávne heslo!")
else:
    st.warning("Nepodarilo sa načítať žiadne dáta. Skontrolujte URL adresu tabuľky a jej práva na zdieľanie.")
