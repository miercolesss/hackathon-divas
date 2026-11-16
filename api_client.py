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
