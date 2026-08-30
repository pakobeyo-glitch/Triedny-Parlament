import streamlit as st
import pandas as pd

# 1. Nastavenie stránky
st.set_page_config(page_title="Prieskum popularity strán", layout="wide")
st.title("📊 Aktuálna popularita parlamentných strán")

# Odkaz na vašu Google Tabuľku (SEM VLOŽTE VÁŠ LINK)
GOOGLE_SHEET_URL = "https://docs.google.com/spreadsheets/d/1tnZuvYAq47pbBpfAax0TfjGPSoCplkAXZmPD_GyjOTI/edit?usp=sharing"

# Funkcia na načítanie dát s vypnutou cache pre okamžité zmeny
def nacitat_data_z_sheets():
    try:
        # Prevod klasickej URL adresy na priamy CSV export
        base_url = GOOGLE_SHEET_URL.split("/edit")[0]
        # Ak tabuľka obsahuje gid v pôvodnom odkaze, vytiahneme ho, inak dáme 0 (prvý list)
        gid = "0"
        if "gid=" in GOOGLE_SHEET_URL:
            gid = GOOGLE_SHEET_URL.split("gid=")[1]
        
        csv_url = f"{base_url}/export?format=csv&gid={gid}"
        df = pd.read_csv(csv_url)
        return df
    except Exception as e:
        st.error(f"Chyba pri načítaní dát z Google Sheets: {e}")
        return pd.DataFrame()

# Načítanie dát
df_raw = nacitat_data_z_sheets()

if not df_raw.empty and len(df_raw.columns) >= 2:
    # Premenujeme stĺpce podľa poradia (1. stĺpec = Strana, 2. stĺpec = Hlasy)
    # Tým pádom nezáleží na tom, čo presne je napísané v prvom riadku tabuľky
    df_db = df_raw.copy()
    df_db.columns = ["Strana", "Hlasy"] + list(df_raw.columns[2:])
    
    # Skonvertujeme stĺpec Hlasy na čísla (ak by tam bol text, nahradí ho nulou)
    df_db["Hlasy"] = pd.to_numeric(df_db["Hlasy"], errors='coerce').fillna(0)

    # 2. Výpočet percent
    celkovo_hlasov = df_db["Hlasy"].sum()
    df_db["Percentá (%)"] = df_db["Hlasy"].apply(lambda x: round((x / celkovo_hlasov) * 100, 2) if celkovo_hlasov > 0 else 0)

    # 3. Zobrazenie pre Sledovateľov
    st.subheader("Aktuálne výsledky")
    st.bar_chart(df_db.set_index("Strana")["Percentá (%)"])
    st.dataframe(df_db[["Strana", "Hlasy", "Percentá (%)"]], use_container_width=True, hide_index=True)

    # 4. Administrátorská sekcia (Správca)
    st.divider()
    st.sidebar.header("🔐 Sekcia pre správcu")
    heslo = st.sidebar.text_input("Zadajte administrátorské heslo", type="password")

    if heslo == "admin123":
        st.sidebar.success("Prístup povolený!")
        st.subheader("🛠️ Úprava počtu voličov")
        st.info("💡 Tip: Keďže zápis z webu vyžaduje zložité nastavovanie Google API kľúčov, najrýchlejšie dáta upravíte tak, že zmeníte čísla priamo vo vašej Google Tabuľke. Zmeny sa tu prejavia hneď po obnovení stránky.")
        
        # Odkaz na rýchly prechod do tabuľky pre správcu
        st.markdown(f"[👉 Otvoriť Google Tabuľku na úpravu dát]({GOOGLE_SHEET_URL})")
                
    elif heslo != "":
        st.sidebar.error("Nesprávne heslo!")
else:
    st.warning("⚠️ Nepodarilo sa správne spracovať dáta. Uistite sa, že Google tabuľka má povolené zdieľanie pre 'Všetkých, ktorí majú odkaz' a obsahuje aspoň dva stĺpce (názvy strán a počty hlasov).")

