import argparse
import os

import streamlit as st
from roboscope.database import Database

from components.filters import apply_test_run_filters
from data.db import load_initial_data

st.set_page_config(page_title="RoboScope UI", layout="wide", initial_sidebar_state="expanded")

parser = argparse.ArgumentParser()
parser.add_argument("--db_url", type=str, help="Database URL")
args, _ = parser.parse_known_args()

db_url = args.db_url or st.secrets.get("db_url")

if not db_url:
    st.error("Database URL not provided. Please set the `--db_url=...` argument or use `st.secrets`.")
    st.stop()

if db_url.startswith("sqlite:///"):
    db_path = db_url.replace("sqlite:///", "")
    if not os.path.exists(db_path):
        st.error(f"SQLite database file not found at: `{db_path}`. Please check the path.")
        st.stop()

if "db" not in st.session_state:
    st.session_state["db"] = Database(db_url=db_url)

dashboard_page = st.Page("dashboards/test_run_dashboard.py", title="Test Run", icon=":material/dashboard:", default=True)
numeric_measurements_page = st.Page("measurements/numeric_measurements.py", title="Numeric Measurements", icon=":material/query_stats:")
string_measurements_page = st.Page("measurements/string_measurements.py", title="String Measurements", icon=":material/query_stats:")
boolean_measurements_page = st.Page("measurements/boolean_measurements.py", title="Boolean Measurements", icon=":material/query_stats:")
series_measurements_page = st.Page("measurements/series_measurements.py", title="Series Measurements", icon=":material/query_stats:")

pg = st.navigation(
    {
        "Dashboards": [
            dashboard_page,
        ],
        "Measurements": [
            numeric_measurements_page,
            string_measurements_page,
            boolean_measurements_page,
            series_measurements_page,
        ],
    }
)

min_start_time, max_start_time, initial_runs = load_initial_data(st.session_state["db"])
apply_test_run_filters(min_start_time, max_start_time, initial_runs)

pg.run()
