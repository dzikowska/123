import streamlit as st

# --- Inicjalizacja Magazynu (Użycie st.session_state do przechowywania danych) ---

# Sprawdź, czy stan sesji 'towary' już istnieje. Jeśli nie, utwórz pustą listę.
# To zapewnia, że dane są zachowywane podczas interakcji użytkownika
# (bez zapisywania do pliku).
if 'towary' not in st.session_state:
    st.session_state.towary = []

# --- Funkcje do Zarządzania Magazynem ---

def dodaj_towar(nazwa):
    """Dodaje towar do listy."""
    if nazwa.strip():  # Sprawdź, czy nazwa nie jest pusta
        st.session_state.towary.append(nazwa.strip())
        st.success(f"Dodano: **{nazwa}**")
    else:
        st.warning("Nazwa towaru nie może być pusta.")

def usun_towar(nazwa):
    """Usuwa pierwsze wystąpienie towaru z listy."""
    try:
        st.session_state.towary.remove(nazwa)
        st.info(f"Usunięto: **{nazwa}**")
    except ValueError:
        st.error(f"Błąd: Nie znaleziono towaru o nazwie **{nazwa}**.")

# --- Interfejs Użytkownika Streamlit ---

st.title("📦 Prosty Magazyn (Streamlit + Session State)")
st.caption("Dane przechowywane są tylko w pamięci sesji.")

# --- Sekcja: Dodawanie Towaru ---
st.header("➕ Dodaj Nowy Towar")
with st.form(key='dodaj_form'):
    nowy_towar = st.text_input("Nazwa Towaru", key='nowy_towar_input')
    dodaj_button = st.form_submit_button("Dodaj do Magazynu")

    if dodaj_button:
        dodaj_towar(nowy_towar)
        # Opcjonalne: wyczyść pole wprowadzania po dodaniu
        # st.session_state.nowy_towar_input = "" 
        
# --- Sekcja: Usuwanie Towaru ---
st.header("➖ Usuń Towar")

if st.session_state.towary:
    # Używamy st.selectbox, aby łatwiej wybrać towar do usunięcia
    towar_do_usunięcia = st.selectbox(
        "Wybierz Towar do Usunięcia", 
        st.session_state.towary,
        key='usun_select'
    )
    
    if st.button("Usuń Wybrany Towar"):
        usun_towar(towar_do_usunięcia)
else:
    st.write("Brak towarów do usunięcia.")


# --- Sekcja: Aktualny Stan Magazynu ---
st.header("📊 Aktualny Stan Magazynu")

if st.session_state.towary:
    st.subheader(f"Liczba Towarów: {len(st.session_state.towary)}")
    
    # Wyświetlanie listy towarów
    # Możesz użyć st.dataframe lub st.write z listą, ale st.markdown z listą numerowaną jest czytelniejsze
    
    lista_wyswietlana = "\n".join([f"* {t}" for t in st.session_state.towary])
    st.markdown(lista_wyswietlana)
    
else:
    st.info("Magazyn jest pusty.")

# --- Wymagania: requirements.txt ---
st.sidebar.header("Wymagane Pliki do Wdrożenia")
st.sidebar.code("streamlit")
st.sidebar.markdown("**Uwaga:** Umieść ten plik (`requirements.txt`) w tym samym katalogu co `app.py`.")
