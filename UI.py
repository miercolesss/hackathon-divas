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