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
    # Pobieramy produkty z nazwami kategorii (join)
    res = supabase.table("produkt").select("id, nazwa, liczba, cena, kategoria_id, kategorie(nazwa)").execute()
    if not res.data:
        return pd.DataFrame()
    
    # Mapowanie danych do ładnej tabeli
    flat_data = []
    for row in res.data:
        flat_data.append({
            "ID": row["id"],
            "Produkt": row["nazwa"],
            "Ilość": row["liczba"],
            "Cena": row["cena"],
            "Kategoria": row["kategorie"]["nazwa"] if row["kategorie"] else "Brak"
        })
    return pd.DataFrame(flat_data)

# --- 3. INTERFEJS UŻYTKOWNIKA ---
st.set_page_config(page_title="Magazyn Supabase", layout="wide")

# Nagłówek z kolorem (używamy emoji i markdown)
st.markdown("# 📦 Zarządzanie Magazynem")
st.write("Aplikacja połączona bezpośrednio z Twoją bazą danych.")

# Pobieramy dane
df = get_data()

# --- 4. STATYSTYKI (WIZUALNE BAJERY) ---
if not df.empty:
    m1, m2, m3 = st.columns(3)
    with m1:
        st.metric("Łącznie produktów", df["Ilość"].sum())
    with m2:
        wartosc = (df["Ilość"] * df["Cena"]).sum()
        st.metric("Wartość magazynu", f"{wartosc:.2f} PLN", delta=f"{len(df)} pozycji")
    with m3:
        najdrozszy = df.loc[df['Cena'].idxmax()]['Produkt']
        st.metric("Najdroższy produkt", najdrozszy)

    st.divider()

# --- 5. WYKRESY (NATYWNE DLA STREAMLIT) ---
if not df.empty:
    col_chart1, col_chart2 = st.columns(2)
    
    with col_chart1:
        st.subheader("📊 Stan ilościowy")
        # Wykres słupkowy ilości produktów
        st.bar_chart(data=df, x="Produkt", y="Ilość", color="Kategoria")

    with col_chart2:
        st.subheader("💰 Porównanie cen")
        # Wykres liniowy/obszarowy cen
        st.area_chart(data=df, x="Produkt", y="Cena")

# --- 6. FORMULARZE (SIDEBAR) ---
with st.sidebar:
    st.header("⚙️ Operacje")
    
    # Dodawanie Kategorii
    with st.expander("🆕 Nowa Kategoria"):
        nowa_kat = st.text_input("Nazwa kategorii")
        if st.button("Dodaj kategorię"):
            supabase.table("kategorie").insert({"nazwa": nowa_kat}).execute()
            st.success("Dodano!")
            st.rerun()

    # Dodawanie Produktu
    with st.expander("🆕 Nowy Produkt"):
        kat_res = supabase.table("kategorie").select("id, nazwa").execute()
        opcje_kat = {item['nazwa']: item['id'] for item in kat_res.data}
        
        p_nazwa = st.text_input("Nazwa")
        p_ilosc = st.number_input("Ilość", min_value=0)
        p_cena = st.number_input("Cena", min_value=0.0)
        p_kat = st.selectbox("Kategoria", options=list(opcje_kat.keys()))
        
        if st.button("Dodaj produkt"):
            supabase.table("produkt").insert({
                "nazwa": p_nazwa, "liczba": p_ilosc, "cena": p_cena, "kategoria_id": opcje_kat[p_kat]
            }).execute()
            st.toast("Produkt dodany!")
            st.rerun()

    # Usuwanie Produktu
    st.divider()
    st.subheader("🗑️ Usuwanie")
    if not df.empty:
        prod_do_usuniecia = st.selectbox("Wybierz produkt do usunięcia", df["Produkt"].tolist())
        id_do_usuniecia = df[df["Produkt"] == prod_do_usuniecia]["ID"].values[0]
        if st.button("USUŃ DEFINITYWNIE", type="primary"):
            supabase.table("produkt").delete().eq("id", int(id_do_usuniecia)).execute()
