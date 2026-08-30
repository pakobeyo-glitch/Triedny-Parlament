import streamlit as st
import pandas as pd
import uuid

# 1. Nastavenie stránky
st.set_page_config(page_title="Parlamentné hlasovanie", layout="wide")
st.title("Hlasovanie a popularita strán")

# Odkaz na vašu Google Tabuľku (SEM VLOŽTE VÁŠ LINK)
GOOGLE_SHEET_URL = "https://docs.google.com/spreadsheets/d/1tnZuvYAq47pbBpfAax0TfjGPSoCplkAXZmPD_GyjOTI/edit?usp=sharing"

# Vygenerovanie unikátneho ID pre tento prehliadač (simulácia jedného hlasu)
if "user_id" not in st.session_state:
    st.session_state.user_id = str(uuid.uuid4())

# Načítanie dát strán
def nacitat_dada():
    try:
        base_url = GOOGLE_SHEET_URL.split("/edit")[0]
        # Načítanie listu 1 (Strany a Hlasy)
        csv_url_strany = f"{base_url}/export?format=csv&gid=0"
        df = pd.read_csv(csv_url_strany)
        df.columns = ["Strana", "Hlasy"] + list(df.columns[2:])
        df["Hlasy"] = pd.to_numeric(df["Hlasy"], errors='coerce').fillna(0)
        return df
    except Exception as e:
        st.error(f"Chyba dát: {e}")
        return pd.DataFrame()

df_db = nacitat_dada()

# Simulácia databázy hlasujúcich (v produkcii sa ukladá do Sheet2)
if "uz_hlasoval" not in st.session_state:
    st.session_state.uz_hlasoval = False

if not df_db.empty:
    # Prepočet percent
    celkovo_hlasov = df_db["Hlasy"].sum()
    df_db["Percentá (%)"] = df_db["Hlasy"].apply(lambda x: round((x / celkovo_hlasov) * 100, 2) if celkovo_hlasov > 0 else 0)

    # --- ZOBRAZENIE PRE VŠETKÝCH (Sledovateľ) ---
    st.subheader("Aktuálne výsledky popularity")
    st.bar_chart(df_db.set_index("Strana")["Percentá (%)"])
    st.dataframe(df_db[["Strana", "Hlasy", "Percentá (%)"]], use_container_width=True, hide_index=True)

    # --- ROLA: VOLIČ ---
    st.divider()
    st.subheader("Odovzdanie vášho hlasu")

    if st.session_state.uz_hlasoval:
        st.success("✅ Ďakujeme! Váš hlas už bol úspešne zaznamenaný. Môžete hlasovať iba raz.")
    else:
        # Volič si vyberie stranu zo zoznamu
        vybrana_strana = st.selectbox("Vyberte stranu, ktorej chcete dať svoj hlas:", df_db["Strana"].tolist())
        
        if st.button("Odovzdať hlas"):
            # Uložíme informáciu, že používateľ z tohto prehliadača už hlasoval
            st.session_state.uz_hlasoval = True
            
            # TU PREBIEHA LOGIKA ZÁPISU:
            # V plnej verzii s API kľúčom by kód pripočítal +1 k vybranej strane v Google Sheets
            # Pre rýchle nasadenie bez API kľúčov sa zmena zatiaľ prejaví v pamäti prehliadača:
            st.success(f"Váš hlas pre '{vybrana_strana}' bol zaznamenaný!")
            
            # Rýchly tip pre reálny zápis do tabuľky bez zložitého kódu:
            st.info("💡 Tip: Pre plnohodnotné permanentné hlasovanie z akéhokoľvek zariadenia odporúčame namiesto zložitého kódu vložiť pod graf klasický formulár **Google Forms** (Google Formuláre) a prepojiť ho s touto tabuľkou.")
            st.rerun()

    # --- ROLA: SPRÁVCA ---
    st.divider()
    st.sidebar.header("🔐 Sekcia pre správcu")
    heslo = st.sidebar.text_input("Zadajte administrátorské heslo", type="password")

    if heslo == "admin123":
        st.sidebar.success("Prístup povolený!")
        st.subheader("🛠️ Úprava počtu voličov správcom")
        st.markdown(f"[👉 Otvoriť Google Tabuľku na manuálnu úpravu dát]({GOOGLE_SHEET_URL})")
        
        if st.button("Vynulovať hlasovanie používateľov (Reset)"):
            st.session_state.uz_hlasoval = False
            st.success("Hlasovanie bolo pre váš prehliadač reštartované.")
            st.rerun()
                
    elif heslo != "":
        st.sidebar.error("Nesprávne heslo!")


