import pandas as pd

#Перетворює сирий список статей у очищений та відсортований DataFrame.
def process_works(raw_works: list[dict]) -> pd.DataFrame:
  if not raw_works: # Захист від порожнього результату пошуку(щоб програма не впала)
        return pd.DataFrame(
            columns=["title", "authors", "publication_year", "cited_by_count", "doi", "journal"]
        )
    
  df = pd.DataFrame(raw_works)
  
  # 1. Видаляємо рядки без критично важливих даних (назви або DOI)
  df = df.dropna(subset=["title", "doi"]).copy()

  # 2. Видаляємо дублікати за DOI або назвою
  df = df.drop_duplicates(subset=["doi"])
  df = df.drop_duplicates(subset=["title"])

  # 3. Заповнюємо пропуски в другорядних полях, щоб не впав formatter.py
  df["authors"] = df["authors"].fillna("Автор невідомий")
  df["journal"] = df["journal"].fillna("Джерело не вказано")
  
  # Приводимо рік та цитування до чисел (якщо раптом прийшов текст або None)
  df["publication_year"] = pd.to_numeric(df["publication_year"], errors="coerce").fillna(0).astype(int)
  df["cited_by_count"] = pd.to_numeric(df["cited_by_count"], errors="coerce").fillna(0).astype(int)

  # 4. Сортуємо за кількістю цитувань (найавторитетніші- зверху)
  df = df.sort_values(by="cited_by_count", ascending=False).reset_index(drop=True)
  
  return df




#Готує зріз даних для графіка публікацій за роками у Streamlit
def get_yearly_trends(df: pd.DataFrame) -> pd.Series:
    if df.empty:
        return pd.Series(dtype=int)
    # Відкидаємо статті, де рік не розпізнався (0), і рахуємо кількість по роках
    valid_years = df[df["publication_year"] > 1900]
    trends = valid_years["publication_year"].value_counts().sort_index()
    
    return trends
