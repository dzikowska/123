import streamlit as st
from supabase import create_client, Client

# Konfiguracja połączenia z Supabase
# Dane te najlepiej przechowywać w Streamlit Secrets
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(url, key)

st.title("Zarządzanie Baza Danych - Sklep")

# --- SEKCJA: DODAWANIE KATEGORII ---
st.header("Dodaj nową kategorię")
with st.form("form_kategoria"):
    nazwa_kat = st.text_input("Nazwa kategorii")
    submit_kat = st.form_submit_button("Zapisz kategorię")

    if submit_kat:
        if nazwa_kat:
            data, count = supabase.table("kategorie").insert({"nazwa": nazwa_kat}).execute()
            st.success(f"Dodano kategorię: {nazwa_kat}")
        else:
            st.error("Wprowadź nazwę kategorii!")

st.divider()

# --- SEKCJA: DODAWANIE PRODUKTU ---
st.header("Dodaj nowy produkt")

# Pobieranie aktualnych kategorii do selectboxa
try:
    response = supabase.table("kategorie").select("id, nazwa").execute()
    kategorie_data = response.data
    kat_options = {item['nazwa']: item['id'] for item in kategorie_data}
except Exception as e:
    st.error("Nie udało się pobrać kategorii.")
    kat_options = {}

with st.form("form_produkt"):
    nazwa_prod = st.text_input("Nazwa produktu")
    liczba = st.number_input("Liczba (sztuki)", min_value=0, step=1)
    cena = st.number_input("Cena", min_value=0.0, step=0.01)
    kategoria_nazwa = st.selectbox("Wybierz kategorię", options=list(kat_options.keys()))
    
    submit_prod = st.form_submit_button("Dodaj produkt")

    if submit_prod:
        if nazwa_prod and kategoria_nazwa:
            nowy_produkt = {
                "nazwa": nazwa_prod,
                "liczba": liczba,
                "cena": cena,
                "kategoria_id": kat_options[kategoria_nazwa] # Klucz obcy
            }
            data, count = supabase.table("produkt").insert(nowy_produkt).execute()
            st.success(f"Produkt '{nazwa_prod}' został dodany!")
        else:
            st.error("Wypełnij wszystkie pola!")
