import streamlit as st
from api_client import fetch_scientific_works
from formatter import format_apa, format_dstu
from processor import process_works

st.set_page_config(page_title="ScholarRef", layout="wide")
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