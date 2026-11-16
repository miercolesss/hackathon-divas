import pandas as pd
import streamlit as st

from api_client import fetch_scientific_works
from formatter import format_apa, format_dstu
from processor import process_works, build_search_query

st.set_page_config(page_title="ScholarRef", page_icon="🎓", layout="wide")

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=PT+Serif:ital,wght@0,400;0,700;1,400&display=swap');

    /* Шрифт — лише для текстових елементів, без універсального * */
    html, body, .stApp,
    .stApp p, .stApp label, .stApp li, .stApp input, .stApp textarea,
    .stApp h1, .stApp h2, .stApp h3, .stApp summary,
    .stApp [data-testid="stMarkdownContainer"],
    .stApp [data-testid="stCaptionContainer"] {
        font-family: 'PT Serif', Georgia, serif !important;
        color: #1B283E;
    }

    /* Повертаємо шрифт іконок, щоб не було тексту "arrow_down" */
    .stApp [data-testid="stIconMaterial"],
    .stApp .material-icons,
    .stApp .material-symbols-rounded,
    .stApp span[class*="material"] {
        font-family: "Material Symbols Rounded", "Material Icons" !important;
    }

    .stApp { background-color: #F7F8FA; }

    .block-container {
        max-width: 1200px;
        padding-top: 2.5rem;
    }

    h1, h2, h3 { font-weight: 700 !important; }

    .subtitle {
        font-size: 1.05rem;
        color: #4C5B73 !important;
        margin-top: -0.6rem;
        margin-bottom: 1.5rem;
    }

    /* Кнопки */
    div.stButton > button:first-child,
    div.stDownloadButton > button:first-child {
        background-color: #1B283E !important;
        border: 1px solid #1B283E !important;
        border-radius: 8px;
        padding: 0.55rem 1.6rem;
        font-weight: 700 !important;
        transition: all 0.2s ease;
    }
    div.stButton > button:first-child p,
    div.stDownloadButton > button:first-child p { color: #FFFFFF !important; }
    div.stButton > button:first-child:hover,
    div.stDownloadButton > button:first-child:hover {
        background-color: #2B3E5E !important;
        box-shadow: 0 4px 12px rgba(27, 40, 62, 0.25);
        transform: translateY(-1px);
    }

    /* Картки джерел */
    div[data-testid="stExpander"] {
        background-color: #FFFFFF !important;
        border: 1px solid #D8DEE9 !important;
        border-left: 4px solid #1B283E !important;
        border-radius: 8px;
        margin-bottom: 0.8rem;
        box-shadow: 0 1px 4px rgba(27, 40, 62, 0.06);
    }
    div[data-testid="stExpander"] summary {
        padding: 0.8rem 1rem;
        font-weight: 700;
        line-height: 1.4;
        gap: 0.6rem;
    }
    div[data-testid="stExpander"] summary p { margin: 0; }

    /* Поля з цитатами */
    textarea {
        background-color: #FBFCFD !important;
        border: 1px solid #C5CEDB !important;
        border-radius: 6px !important;
        font-size: 0.95rem !important;
        line-height: 1.5 !important;
    }

    .custom-footer {
        margin-top: 4rem;
        padding: 1.2rem 0 1.5rem;
        border-top: 1px solid #D8DEE9;
        text-align: center;
        color: #4C5B73;
        font-size: 0.95rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def shorten_authors(authors, limit=5):
    """Скорочує довгий список авторів: перші N + 'та ще K'."""
    if isinstance(authors, (list, tuple)):
        items = [str(a).strip() for a in authors if str(a).strip()]
    else:
        items = [a.strip() for a in str(authors).split(",") if a.strip()]
    if len(items) > limit:
        return ", ".join(items[:limit]) + f" та ще {len(items) - limit}"
    return ", ".join(items)


# ---------- Заголовок ----------
st.title("🎓 ScholarRef — пошук реальних наукових цитат")
st.markdown(
    '<p class="subtitle">Інструмент для студентів: пошук реальних статей та генерація посилань.</p>',
    unsafe_allow_html=True,
)

# ---------- Пошук ----------
query = st.text_area(
    "📝 Вставте абзац із вашої наукової роботи:",
    value="",
    height=120,
)

if st.button("Знайти джерела"):
    if not query.strip():
        st.warning("Спочатку введіть текст або ключові слова.")
    else:
        search_query = build_search_query(query)
        with st.spinner("Шукаємо в наукових базах та обробляємо через Pandas..."):
            raw_data = fetch_scientific_works(search_query, limit=10)
            result_df = process_works(raw_data)
            if result_df is not None and not result_df.empty:
                result_df = result_df.copy()
                result_df["APA_7"] = result_df.apply(format_apa, axis=1)
                result_df["DSTU_8302"] = result_df.apply(format_dstu, axis=1)
        # зберігаємо результат, щоб він не зникав при редагуванні полів з цитатами
        st.session_state["df"] = result_df
        st.session_state["search_query"] = search_query

df = st.session_state.get("df")

# ---------- Результати ----------
if df is not None and not df.empty:
    st.caption(f"Пошуковий запит: {st.session_state.get('search_query', '')}")
    st.success(f"Знайдено та оброблено {len(df)} джерел!")

    for pos, (idx, row) in enumerate(df.iterrows()):
        year = "н.д." if pd.isna(row["publication_year"]) else int(row["publication_year"])
        with st.expander(
            f"{row['title']} ({year}) · Цитувань: {row['cited_by_count']}",
            expanded=(pos == 0),  # перша картка розгорнута, решта згорнуті
        ):
            st.markdown(f"**Автори:** {shorten_authors(row['authors'])}")
            st.markdown(f"**Журнал:** {row['journal']}")
            col1, col2 = st.columns(2, gap="large")
            with col1:
                st.text_area("APA 7th Edition", row["APA_7"], height=120, key=f"apa_{idx}")
            with col2:
                st.text_area("ДСТУ 8302:2015", row["DSTU_8302"], height=120, key=f"dstu_{idx}")

    st.subheader("📊 Зведена таблиця")
    st.dataframe(
        df[["title", "authors", "publication_year", "cited_by_count", "doi"]],
        use_container_width=True,
        hide_index=True,
    )

    csv = df.to_csv(index=False).encode("utf-8-sig")  # utf-8-sig — щоб Excel читав кирилицю
    st.download_button("📥 Завантажити бібліографію (CSV)", csv, "references.csv", "text/csv")

elif df is not None and df.empty:
    st.error("Нічого не знайдено. Спробуйте інший запит.")

# ---------- Футер ----------
st.markdown(
    '<div class="custom-footer">Hackathon Divas • 2026</div>',
    unsafe_allow_html=True,
)