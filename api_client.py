import json
import requests

try:
    from scholarly import scholarly
except ImportError:
    scholarly = None

OPENALEX_URL = "https://api.openalex.org/works"
HEADERS = {"User-Agent": "mailto:hackathon_team@example.com"}
MAX_PER_PAGE = 200
CACHE_FILE = "papers_cache.json"
GS_LIMIT = 2  # мало, щоб не зловити бан Google Scholar
#-------- основна функція -----------
def _fetch_openalex(query, limit):
    limit = max(1, min(int(limit), MAX_PER_PAGE))
    response = requests.get(
        OPENALEX_URL,
        params={"search": query, "per-page": limit},
        headers=HEADERS,
        timeout=10,
    )
    response.raise_for_status()
    return [_parse_openalex(w) for w in response.json().get("results", [])]


def _fetch_google_scholar(query, limit=GS_LIMIT):
    if scholarly is None:
        return []
    records = []
    try:
        search = scholarly.search_pubs(query)
        for _ in range(limit):
            records.append(_parse_scholar(next(search)))
    except Exception as e:
        print(f"[api_client] Google Scholar недоступний: {e}")
    return records

def fetch_scientific_works(query, limit=20, use_google_scholar=False):
    """Повертає list of dicts за контрактом. Ніколи не кидає виняток.

    OpenAlex -> (+ Google Scholar) -> якщо нічого не отримали, береться кеш.
    """
    records = []
    try:
        records = _fetch_openalex(query, limit)
    except (requests.RequestException, ValueError) as e:
        print(f"[api_client] Помилка OpenAlex: {e}")

    if use_google_scholar:
        records += _fetch_google_scholar(query)

    if records:
        save_to_cache(query, records)
        return records

    cached = load_from_cache(query)
    if cached:
        print("[api_client] Використано дані з кешу.")
    return cached


if __name__ == "__main__":

    import sys

    q = sys.argv[1] if len(sys.argv) > 1 else "AI hallucinations"
    n = int(sys.argv[2]) if len(sys.argv) > 2 else 3
    gs = len(sys.argv) > 3 and sys.argv[3] == "gs"

    works = fetch_scientific_works(q, limit=n, use_google_scholar=gs)
    for w in works:
        print(f"{w['year']} | {w['cited_by_count']} | {w['title']}")
        print(f"    {w['authors'][:80]} | {w['journal']} | {w['doi']}")
    print(f"Отримано: {len(works)}")

def fetch_papers(query, limit=5, use_google_scholar=False):
    import pandas as pd
    return pd.DataFrame(fetch_scientific_works(query, limit, use_google_scholar))
