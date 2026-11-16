import pandas as pd

def process_works(raw_works: list[dict]) -> pd.DataFrame:
      processed_list = []
      for item in raw_data:
            processed_list.append({
                  "title": item.get("title", "No Title"),
                  "authors": item.get("authors", "Unknown"),
                  "publication_year": item.get("year") or item.get("publication_year", 0),
                  "cited_by_count": item.get("cited_by_count", 0),
                  "journal": item.get("journal", "Unknown Journal"),
                  "doi": item.get("doi", "")
            })
    
      df = pd.DataFrame(processed_list)
      return df
    
      df = pd.DataFrame(raw_works)
  
      df = df.dropna(subset=["title", "doi"]).copy()

 
      df = df.drop_duplicates(subset=["doi"])
      df = df.drop_duplicates(subset=["title"])

  
      df["authors"] = df["authors"].fillna("Автор невідомий")
      df["journal"] = df["journal"].fillna("Джерело не вказано")
  
  
      df["publication_year"] = pd.to_numeric(df["year"], errors="coerce").fillna(0).astype(int)
      df["cited_by_count"] = pd.to_numeric(df["cited_by_count"], errors="coerce").fillna(0).astype(int)

  
      df = df.sort_values(by="cited_by_count", ascending=False).reset_index(drop=True)
      return df





def get_yearly_trends(df: pd.DataFrame) -> pd.Series:
      if df.empty:
            return pd.Series(dtype=int)
    
      valid_years = df[df["publication_year"] > 1900]
      trends = valid_years["publication_year"].value_counts().sort_index()
    
      return trends
