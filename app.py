import os

import streamlit as st
from components.filters import apply_test_run_filters
from data.db import load_initial_data

from roboscope.database import Database

st.set_page_config(page_title="RoboScope UI", layout="wide", initial_sidebar_state="expanded")

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

if "db" not in st.session_state:
    script_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(script_dir, "../results.db")
    st.session_state["db"] = Database(db_url=f"sqlite:///{db_path}")

min_start_time, max_start_time, initial_runs = load_initial_data(st.session_state["db"])
apply_test_run_filters(min_start_time, max_start_time, initial_runs)

pg.run()
