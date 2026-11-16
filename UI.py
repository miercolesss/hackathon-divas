import streamlit as st
from api_client import fetch_scientific_works
from formatter import format_apa, format_dstu
from processor import process_works

st.set_page_config(page_title="ScholarRef", layout="wide")

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,500;0,600;0,700;1,400&family=Montserrat:wght@400;500;600&display=swap');

    .stApp, .stApp *, p, span, label, div, input, textarea {
        font-family: 'Montserrat', sans-serif !important;
        color: #1B283E;
    }

    .stApp {
        background-color: #F7F8FA;
    }

    h1, h2, h3, .academic-title {
        font-family: 'Cormorant Garamond', Georgia, serif !important;
        font-weight: 700 !important;
        color: #1B283E !important;
    }

    div.stButton > button:first-child {
        background-color: #1B283E;
        color: #FFFFFF;
        border: 1px solid #1B283E;
        border-radius: 6px;
        padding: 0.55rem 1.4rem;
        font-family: 'Montserrat', sans-serif;
        font-weight: 500;
        transition: all 0.2s ease;
    }
    div.stButton > button:first-child:hover {
        background-color: #2B3E5E;
        border-color: #2B3E5E;
        color: #FFFFFF;
    }

    div[data-testid="stExpander"] {
        background-color: #FFFFFF;
        border: 1px solid #D8DEE9;
        border-left: 4px solid #1B283E;
        border-radius: 6px;
    }

    textarea {
        background-color: #FFFFFF !important;
        border: 1px solid #C5CEDB !important;
        color: #1B283E !important;
        font-family: 'Montserrat', sans-serif !important;
    }

    .custom-footer {
        margin-top: 4rem;
        padding-top: 1.2rem;
        padding-bottom: 1.5rem;
        border-top: 1px solid #D8DEE9;
        text-align: center;
        color: #4C5B73;
        font-size: 0.9rem;
        font-family: 'Montserrat', sans-serif;
    }
    .custom-footer strong {
        color: #1B283E;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("🎓 ScholarRef — пошук реальних наукових цитат")
st.markdown("Інструмент для студентів: пошук реальних статей та генерація посилань")

query = st.text_area(
    "Вставте абзац із вашої наукової роботи:",
    value="",
    height=100,
)

df = None

if st.button("Знайти джерела"):
    if not query.strip():
        st.warning("Спочатку введіть текст або ключові слова.")
    else:
        with st.spinner("Шукаємо в наукових базах та обробляємо через Pandas..."):
            raw_data = fetch_scientific_works(query, limit=10)
            df = process_works(raw_data)

if df is not None and not df.empty:
    df["APA_7"] = df.apply(format_apa, axis=1)
    df["DSTU_8302"] = df.apply(format_dstu, axis=1)

    st.success(f"Знайдено та оброблено {len(df)} перевірених джерел!")

    for idx, row in df.iterrows():
        with st.expander(
                f"{row['title']} ({row['publication_year']}) — Цитувань: {row['cited_by_count']}",
                expanded=True,
        ):
            st.markdown(f"**Автори:** {row['authors']}")
            st.markdown(f"**Журнал:** {row['journal']}")
            col1, col2 = st.columns(2)
            with col1:
                st.text_area("APA 7th Edition", row["APA_7"], height=70, key=f"apa_{idx}")
            with col2:
                st.text_area("ДСТУ 8302:2015", row["DSTU_8302"], height=70, key=f"dstu_{idx}")

    st.subheader("Зведена таблиця")
    st.dataframe(df[["title", "authors", "publication_year", "cited_by_count", "doi"]])

    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button(
        "Завантажити бібліографію (CSV)",
        csv,
        "references.csv",
        "text/csv",
    )
elif df is not None and df.empty:
    st.error("Нічого не знайдено. Спробуйте інший запит.")

st.markdown(
    """
    <div class="custom-footer">
        Hackathon Divas • 2026
    </div>
    """,
    unsafe_allow_html=True,
)