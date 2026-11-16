import pandas as pd
import streamlit as st

from api_client import fetch_papers
from formatter import format_authors_apa, format_authors_dstu
from processor import process_works
