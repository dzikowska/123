import streamlit as st
import pandas as pd
from supabase import create_client, Client

# --- 1. KONFIGURACJA POŁĄCZENIA ---
@st.cache_resource
def init_connection():
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

supabase = init_connection()

# --- 2. RÓŻOWE TŁO (CSS) ---
st.markdown("""
    <style>
    /* Główne tło strony */
    .stApp {
        background-color: #FFF0F5; 
    }
    
    /* Tło panelu bocznego */
    section[data-testid="stSidebar"] {
        background-color: #FFB6C1 !important;
    }

    /* Dopasowanie koloru tekstu w panelu bocznym dla czytelności */
    section[data-testid="stSidebar"] .stMarkdown, 
    section[data-testid="stSidebar"] label {
        color: #31333F !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. POBIERANIE DANYCH ---
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

# --- 4. INTERFEJS UŻYTKOWNIKA ---
st.set_page_config(page_title="System Zarządzania Magazynem", layout="wide")
st.title("Zarządzanie Magazynem")

df = get_data()

# --- 5. STATYSTYKI ---
if not df.empty:
    m1, m2, m3 = st.columns(3)
    m1.metric("Łączna liczba produktów", int(df["Ilość"].sum()))
    m2.metric("Wartość magazynu", f"{(df['Ilość'] * df['Cena']).sum():,.2f} PLN")
    m3.metric("Liczba kategorii", len(df["Kategoria"].unique()))
    st.divider()

# --- 6. WYKRESY ---
if not df.empty:
    st.subheader("Stan asortymentu")
    st.bar_chart(data=df, x="Produkt", y="Ilość", color="Kategoria")

# --- 7. PANEL BOCZNY (OPERACJE) ---
with st.sidebar:
    st.header("Panel sterowania")

    # Dodawanie nowego produktu
    with st.expander("Dodaj nowy produkt"):
        kat_res = supabase.table("kategorie").select("id, nazwa").execute()
        opcje_kat = {item['nazwa']: item['id'] for item in kat_res.data}
        
        p_nazwa = st.text_input("Nazwa artykułu")
        p_ilosc = st.number_input("Ilość początkowa", min_value=1)
        p_cena = st.number_input("Cena jednostkowa", min_value=0.0)
        p_kat = st.selectbox("Wybierz kategorię", options=list(opcje_kat.keys()))
        
        if st.button("Zatwierdź produkt"):
            supabase.table("produkt").insert({
                "nazwa": p_nazwa, "liczba": p_ilosc, "cena": p_cena, "kategoria_id": opcje_kat[p_kat]
            }).execute()
            st.rerun()

    st.divider()

    # Zdejmowanie określonej ilości (Twoja prośba)
    st.subheader("Wydanie z magazynu")
    if not df.empty:
        wybrany_prod = st.selectbox("Produkt do wydania", df["Produkt"].tolist())
        aktualna_ilosc = df[df["Produkt"] == wybrany_prod]["Ilość"].values[0]
        wybrane_id = df[df["Produkt"] == wybrany_prod]["ID"].values[0]
        
        st.write(f"Dostępny stan: **{aktualna_ilosc}**")
        ile_usunac = st.number_input("Ilość do odjęcia", min_value=1, max_value=int(aktualna_ilosc))

        if st.button("Aktualizuj stan", type="primary"):
            nowa_ilosc = aktualna_ilosc - ile_usunac
            supabase.table("produkt").update({"liczba": nowa_ilosc}).eq("id", int(wybrane_id)).execute()
            st.success(f"Zaktualizowano stan produktu: {wybrany_prod}")
            st.rerun()

# --- 8. TABELA PODGLĄDU ---
st.subheader("Aktualny wykaz zapasów")
st.dataframe(df[["Produkt", "Ilość", "Cena", "Kategoria"]], use_container_width=True, hide_index=True)
