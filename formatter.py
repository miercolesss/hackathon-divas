import pandas as pd



def is_missing(value) -> bool:
    """True для None / NaN / порожнього рядка / порожнього списку."""
    pass


def normalize_authors(authors) -> list[str]:
    """str ('A B, C D' або 'A B; C D') або list -> список рядків 'Ім'я Прізвище'."""
    pass


def split_name(full_name: str) -> tuple[str, list[str]]:
    """'John Ronald Smith' -> ('Smith', ['John', 'Ronald'])."""
    pass


def initials(given_names: list[str]) -> str:
    """['John', 'Ronald'] -> 'J. R.'."""
    pass


def normalize_doi(doi) -> str:
    """'10.1234/abc' або 'https://doi.org/10.1234/abc' -> 'https://doi.org/10.1234/abc'.
    Якщо doi відсутній -> ''."""
    pass



def format_authors_apa(authors: list[str]) -> str:
    """1: 'Smith, J.' | 2: 'Smith, J., & Doe, A.' | 3–20: усі через кому з '&' | 21+: перші 19, '...', останній."""
    pass


def format_authors_dstu(authors: list[str]) -> str:
    """1–3 автори: 'Smith J., Doe A.' | 4+: порожньо (опис під назвою, 'та ін.' у відповідальності)."""
    pass


def format_apa(row: dict) -> str:
    """Author, A. (Year). Title. Journal. https://doi.org/..."""
    pass


def format_dstu(row: dict) -> str:
    """Прізвище І. Назва. Журнал. Рік. URL: ... (дата звернення: дд.мм.рррр)."""
    pass


def add_citations(df: pd.DataFrame, style: str = "APA") -> pd.DataFrame:
    """Повертає копію df з новою колонкою 'citation'. style: 'APA' | 'DSTU'."""
    pass


def add_both_citations(df: pd.DataFrame) -> pd.DataFrame:
    """Колонки 'citation_apa' і 'citation_dstu' одразу (зручно для UI-перемикача)."""
    pass



if __name__ == "__main__":
    sample = pd.DataFrame([
        {"title": "Deep learning for citations", "authors": ["John Smith", "Olena Koval"],
         "publication_year": 2021, "cited_by_count": 15,
         "doi": "10.1234/abcd", "journal": "Journal of Data Science"},
        {"title": "No year, no journal", "authors": "Ivan Petrenko",
         "publication_year": None, "cited_by_count": 0,
         "doi": None, "journal": None},
    ])
    print(add_both_citations(sample)[["citation_apa", "citation_dstu"]].to_string())