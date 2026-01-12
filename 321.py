import streamlit as st
import pandas as pd
from supabase import create_client, Client

# --- 1. KONFIGURACJA POŁĄCZENIA ---
@st.cache_resource
def init_connection():
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

supabase = init_connection()

# --- 2. POBIERANIE DANYCH ---
def get_data():
    res = supabase.table("produkt").select("id, nazwa, liczba, cena, kategoria_id, kategorie(nazwa)").execute()
    if not res.data:
        return pd.DataFrame()
    
    flat_data = []
    for row in res.data:
        flat_data.append({
            "ID": row["id"],
            "Produkt": row["nazwa"],
            "Ilość": row["liczba"],
            "Cena": row["cena"],
            "Kategoria": row["kategorie"]["nazwa"] if row["kategorie"] else "Brak"
        })
    return pd.DataFrame(flat_data).sort_values(by="Produkt")

# --- 3. INTERFEJS ---
st.set_page_config(page_title="Magazyn Supabase", layout="wide")
st.markdown("# 📦 Inteligentny Magazyn")

df = get_data()

# --- 4. STATYSTYKI ---
if not df.empty:
    m1, m2, m3 = st.columns(3)
    m1.metric("📦 Suma sztuk", int(df["Ilość"].sum()))
    m2.metric("💰 Wartość", f"{(df['Ilość'] * df['Cena']).sum():,.2f} PLN")
    m3.metric("🏷️ Kategorie", len(df["Kategoria"].unique()))
    st.divider()

# --- 5. WYKRESY ---
if not df.empty:
    st.subheader("📊 Stan magazynowy")
    st.bar_chart(data=df, x="Produkt", y="Ilość", color="Kategoria")

# --- 6. PANEL BOCZNY (OPERACJE) ---
with st.sidebar:
    st.header("⚙️ Zarządzanie")

    # A. DODAWANIE NOWEGO PRODUKTU
    with st.expander("➕ Dodaj nowy produkt"):
        kat_res = supabase.table("kategorie").select("id, nazwa").execute()
        opcje_kat = {item['nazwa']: item['id'] for item in kat_res.data}
        
        p_nazwa = st.text_input("Nazwa")
        p_ilosc = st.number_input("Ilość startowa", min_value=1)
        p_cena = st.number_input("Cena", min_value=0.0)
        p_kat = st.selectbox("Kategoria", options=list(opcje_kat.keys()))
        
        if st.button("Dodaj do bazy"):
            supabase.table("produkt").insert({
                "nazwa": p_nazwa, "liczba": p_ilosc, "cena": p_cena, "kategoria_id": opcje_kat[p_kat]
            }).execute()
            st.rerun()

    st.divider()

    # B. USUWANIE KONKRETNEJ ILOŚCI (ZDJĘCIE ZE STANU)
    st.subheader("📉 Zdejmij ze stanu")
    if not df.empty:
        wybrany_prod = st.selectbox("Wybierz produkt", df["Produkt"].tolist())
        # Pobieramy aktualną ilość z DataFrame
        aktualna_ilosc = df[df["Produkt"] == wybrany_prod]["Ilość"].values[0]
        wybrane_id = df[df["Produkt"] == wybrany_prod]["ID"].values[0]
        
        st.caption(f"Aktualnie w magazynie: {aktualna_ilosc}")
        ilosc_do_odjecia = st.number_input("Ile sztuk usunąć?", min_value=1, max_value=int(aktualna_ilosc))

        if st.button("Usuń wskazaną ilość", type="primary"):
            nowa_ilosc = aktualna_ilosc - ilosc_do_odjecia
            
            if nowa_ilosc > 0:
                # Aktualizujemy liczbę
                supabase.table("produkt").update({"liczba": nowa_ilosc}).eq("id", int(wybrane_id)).execute()
                st.toast(f"Usunięto {ilosc_do_odjecia} szt. Pozostało: {nowa_ilosc}")
            else:
                # Jeśli zero, pytamy czy usunąć cały rekord, albo po prostu zerujemy
                supabase.table("produkt").update({"liczba": 0}).eq("id", int(wybrane_id)).execute()
                st.toast("Produkt został wyzerowany w magazynie!")
            
            st.rerun()

    # C. CAŁKOWITE USUNIĘCIE Z BAZY
    with st.expander("🗑️ Usuń produkt całkowicie"):
        prod_del = st.selectbox("Produkt do skasowania", df["Produkt"].tolist(), key="del_total")
        id_del = df[df["Produkt"] == prod_del]["ID"].values[0]
        if st.button("SKASUJ REKORD", type="secondary"):
            supabase.table("produkt").delete().eq("id", int(id_del)).execute()
            st.rerun()

# --- 7. TABELA PODGLĄDU ---
st.subheader("📋 Aktualna lista")
st.dataframe(df[["Produkt", "Ilość", "Cena", "Kategoria"]], use_container_width=True, hide_index=True)
