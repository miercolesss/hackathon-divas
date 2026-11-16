import pandas as pd
import streamlit as st

from api_client import fetch_papers
from formatter import format_authors_apa, format_authors_dstu
from processor import process_works

st.set_page_config(page_title="ScholarRef", layout="wide")
st.title("🎓 ScholarRef — пошук реальних наукових цитат")
st.markdown("Інструмент для студентів: пошук реальних статей та генерація посилань.")

query = st.text_area(
    "📝 Вставте абзац із вашої наукової роботи:",
    value="",
    height=100,
)

if st.button("Знайти джерела"):
    with st.spinner("Шукаємо в наукових базах та обробляємо через Pandas..."):
        raw_data = fetch_papers(query, limit=10)

df = process_works(raw_data)
if not df.empty:
    df["APA_7"] = df.apply(format_apa, axis=1)
    df["DSTU_8302"] = df.apply(format_dstu, axis=1)

    st.success(f"Знайдено та оброблено {len(df)} перевірених джерел!")
