import pandas as pd
from datetime import date
import re


_DOI_PREFIX = re.compile(r"^(?:https?://(?:dx\.)?doi\.org/|doi:\s*)", re.IGNORECASE)



def is_missing(value) -> bool:
    """True для None / NaN / порожнього рядка / порожнього списку."""
    if value is None:
        return True
    if isinstance(value, str):
        return value.strip() == ""
    if hasattr(value, "__len__"):
        return len(value) == 0
    try:
        return bool(pd.isna(value))
    except (TypeError, ValueError):
        return False


def normalize_authors(authors) -> list[str]:
    """str ('A B, C D' або 'A B; C D') або list -> список рядків 'Ім'я Прізвище'."""
    if is_missing(authors):
        return []
    if isinstance(authors, str):
        text = re.sub(r"\s+(?:and|&)\s+|;", ",", authors)
        items = text.split(",")
    else:
        items = list(authors)

    result = []
    for item in items:
        if is_missing(item):
            continue
        name = " ".join(str(item).split())
        if name:
            result.append(name)
    return result


def split_name(full_name: str) -> tuple[str, list[str]]:
    """'John Ronald Smith' -> ('Smith', ['John', 'Ronald'])."""
    parts = str(full_name).split()
    if not parts:
        return "", []
    return parts[-1], parts[:-1]


def initials(given_names: list[str]) -> str:
    """['John', 'Ronald'] -> 'J. R.'."""
    out = []
    for name in given_names:
        pieces = [p for p in name.split("-") if p]
        if pieces:
            out.append("-".join(f"{p[0].upper()}." for p in pieces))
    return " ".join(out)


def normalize_doi(doi) -> str:
    """'10.1234/abc' або 'https://doi.org/10.1234/abc' -> 'https://doi.org/10.1234/abc'.
    Якщо doi відсутній -> ''."""
    if is_missing(doi):
        return ""
    bare = _DOI_PREFIX.sub("", str(doi).strip())
    return f"https://doi.org/{bare}" if bare else ""



def _text(value) -> str:
    """Безпечно перетворює значення на рядок ('' якщо відсутнє)."""
    return "" if is_missing(value) else " ".join(str(value).split())


def _year(value) -> str:
    """2021 / 2021.0 / '2021' -> '2021'; відсутнє -> ''."""
    if is_missing(value):
        return ""
    try:
        return str(int(float(value)))
    except (TypeError, ValueError):
        return str(value).strip()


def _end(text: str) -> str:
    """Додає крапку, якщо рядок не закінчується на . ? !"""
    if not text:
        return ""
    return text if text[-1] in ".?!" else text + "."



def _apa_name(full_name: str) -> str:
    surname, given = split_name(full_name)
    ini = initials(given)
    return f"{surname}, {ini}" if ini else surname


def _dstu_name(full_name: str) -> str:
    surname, given = split_name(full_name)
    ini = initials(given)
    return f"{surname} {ini}" if ini else surname





def format_authors_apa(authors: list[str]) -> str:
    """1: 'Smith, J.' | 2: 'Smith, J., & Doe, A.' | 3–20: усі через кому з '&' | 21+: перші 19, '...', останній."""
    authors = normalize_authors(authors)
    names = [_apa_name(a) for a in authors]
    if not names:
        return ""
    if len(names) == 1:
        return names[0]
    if len(names) <= 20:
        return ", ".join(names[:-1]) + ", & " + names[-1]
    return ", ".join(names[:19]) + ", ... " + names[-1]


def format_authors_dstu(authors: list[str]) -> str:
    """1–3 автори: 'Smith J., Doe A.' | 4+: порожньо (опис під назвою, 'та ін.' у відповідальності)."""
    authors = normalize_authors(authors)
    if not 1 <= len(authors) <= 3:
        return ""
    return ", ".join(_dstu_name(a) for a in authors)


def format_apa(row: dict) -> str:
    """Author, A. (Year). Title. Journal. https://doi.org/..."""
    authors = normalize_authors(row.get("authors"))
    title = _text(row.get("title")).rstrip(".")
    journal = _text(row.get("journal"))
    year = _year(row.get("year") or row.get("publication_year")) or "n.d."
    doi = normalize_doi(row.get("doi"))

    parts = []
    if authors:
        parts.append(f"{format_authors_apa(authors)} ({year}).")
        parts.append(_end(title))
    else:
        parts.append(_end(title))
        parts.append(f"({year}).")
    parts.append(_end(journal))
    parts.append(doi)
    return " ".join(p for p in parts if p)


def format_dstu(row: dict) -> str:
    """Прізвище І. Назва. Журнал. Рік. URL: ... (дата звернення: дд.мм.рррр)."""
    authors = normalize_authors(row.get("authors"))
    title = _text(row.get("title")).rstrip(".")
    journal = _text(row.get("journal"))
    year = _year(row.get("year") or row.get("publication_year"))
    doi = normalize_doi(row.get("doi"))

    parts = []
    if 1 <= len(authors) <= 3:
        parts.append(format_authors_dstu(authors))
        parts.append(_end(title))
    elif len(authors) > 3:
        surname, given = split_name(authors[0])
        first = f"{initials(given)} {surname}".strip()
        parts.append(f"{title} / {first} та ін.")
    else:
        parts.append(_end(title))
    parts.append(_end(journal))
    parts.append(f"{year}." if year else "[Б. р.]")
    if doi:
        parts.append(f"URL: {doi} (дата звернення: {date.today():%d.%m.%Y}).")
    return " ".join(p for p in parts if p)




_STYLES = {"APA": format_apa, "DSTU": format_dstu, "ДСТУ": format_dstu}




def add_citations(df: pd.DataFrame, style: str = "APA") -> pd.DataFrame:
    """Повертає копію df з новою колонкою 'citation'. style: 'APA' | 'DSTU'."""
    fn = _STYLES.get(style.strip().upper())
    if fn is None:
        raise ValueError(f"Невідомий стиль: {style!r}. Використайте 'APA' або 'DSTU'.")
    out = df.copy()
    out["citation"] = [fn(r) for r in out.to_dict("records")]
    return out


def add_both_citations(df: pd.DataFrame) -> pd.DataFrame:
    """Колонки 'citation_apa' і 'citation_dstu' одразу (зручно для UI-перемикача)."""
    out = df.copy()
    records = out.to_dict("records")
    out["citation_apa"] = [format_apa(r) for r in records]
    out["citation_dstu"] = [format_dstu(r) for r in records]
    return out



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