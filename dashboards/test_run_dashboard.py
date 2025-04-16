import streamlit as st
from components.plots import plot_run_statistics
from components.tables import show_summary, show_test_overview
from data.db import load_selected_data

st.title("RoboScope Dashboard")

db = st.session_state.db
selected_run_ids = st.session_state.selected_run_ids

if not selected_run_ids:
    st.warning("Please select at least one Test Run to display statistics.")
    st.stop()

run_df, test_df, suite_df, failure_df = load_selected_data(db, selected_run_ids)

plot_run_statistics(test_df, selected_run_ids, run_df)
show_summary(run_df, selected_run_ids)
show_test_overview(test_df, suite_df, failure_df, selected_run_ids)
