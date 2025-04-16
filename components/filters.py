from datetime import datetime, timedelta
from functools import reduce

import pandas as pd
import streamlit as st


def setup_filter_defaults(defaults: dict) -> None:
    for key, val in defaults.items():
        st.session_state.setdefault(key, val)


def extract_meta_info(initial_runs: list) -> tuple[list[dict], set]:
    meta_dicts = [meta for _, _, meta in initial_runs if isinstance(meta, dict)]
    meta_keys = set().union(*(meta.keys() for meta in meta_dicts if meta))
    return meta_dicts, meta_keys


def build_meta_filters(meta_keys: set, meta_dicts: list[dict]) -> dict:
    meta_filters = {}
    if meta_keys:
        st.sidebar.header("Meta Filters")
        for key in sorted(meta_keys):
            # Generate a user-friendly name
            display_name = " ".join(word.capitalize() for word in key.split("_"))
            unique_values = sorted({meta[key] for meta in meta_dicts if key in meta})
            # Use a distinct session_state key for meta filters (e.g. meta_key)
            meta_filters[key] = st.sidebar.multiselect(display_name, options=unique_values, key=f"meta_{key}")
    return meta_filters


def filter_runs(initial_runs, start_dt, end_dt, meta_filters):
    # Filter by date and time range.
    filtered_runs = [(run_id, start_time, meta) for run_id, start_time, meta in initial_runs if start_dt <= start_time <= end_dt]
    # Further filter by meta selections (only if a selection is made for the key).
    if meta_filters:
        filtered_runs = [
            (run_id, start_time, meta)
            for run_id, start_time, meta in filtered_runs
            if all(meta.get(key) in selected for key, selected in meta_filters.items() if selected)
        ]
    return filtered_runs


def get_run_options(run_data) -> list[str]:
    return [f"{run_id} - {start_time.strftime('%Y-%m-%d %H:%M:%S')}" for run_id, start_time, _ in run_data]


def apply_test_run_filters(min_start_time: datetime, max_start_time: datetime, initial_runs: list[tuple]) -> list[int]:
    # Determine default values for date/time filters.
    min_date = min_start_time.date()
    max_date = max_start_time.date()
    min_time_of_day = min_start_time.time()
    # Increase max_time slightly (by one minute) to include runs at the very end.
    max_time_of_day = (datetime.combine(datetime.min, max_start_time.time()) + timedelta(minutes=1)).time()

    # Setup default filter state.
    defaults = {
        "from_date": min_date,
        "to_date": max_date,
        "from_time": min_time_of_day,
        "to_time": max_time_of_day,
        "selected_runs": [],
    }
    setup_filter_defaults(defaults)

    # Extract meta information and build meta filter UI.
    meta_dicts, meta_keys = extract_meta_info(initial_runs)
    meta_filters = build_meta_filters(meta_keys, meta_dicts)

    # Combine current session state date and time into datetime objects.
    start_dt = datetime.combine(st.session_state["from_date"], st.session_state["from_time"])
    end_dt = datetime.combine(st.session_state["to_date"], st.session_state["to_time"])

    # Filter runs based on current settings.
    filtered_runs = filter_runs(initial_runs, start_dt, end_dt, meta_filters)

    # Build run options from the filtered runs.
    run_options = get_run_options(filtered_runs)

    # Callback functions for buttons.
    def reset_filters_callback():
        for key, value in defaults.items():
            st.session_state[key] = value
        for key in meta_keys:
            st.session_state[f"meta_{key}"] = []

    def select_all_runs_callback():
        st.session_state["selected_runs"] = get_run_options(filtered_runs)

    # Build the sidebar UI.
    with st.sidebar:
        st.header("Test Run Filters")
        date_col1, date_col2 = st.columns(2)
        date_col1.date_input("From Date", min_value=min_date, max_value=max_date, key="from_date")
        date_col2.date_input("To Date", min_value=min_date, max_value=max_date, key="to_date")

        time_col1, time_col2 = st.columns(2)
        time_col1.time_input("From Time", key="from_time")
        time_col2.time_input("To Time", key="to_time")

        button_col1, button_col2 = st.columns(2)
        button_col1.button("Reset Filters", on_click=reset_filters_callback)
        button_col2.button("All Runs", on_click=select_all_runs_callback)

    # Allow the user to select runs from the generated run options.
    selected_labels = st.sidebar.multiselect("Select Test Runs", options=run_options, key="selected_runs")
    selected_run_ids = [int(label.split(" ")[0]) for label in selected_labels] if selected_labels else []
    st.session_state["selected_run_ids"] = selected_run_ids

    return selected_run_ids


def apply_measurement_filters(df: pd.DataFrame):
    filters = []

    # Name filter
    name_options = sorted(df["name"].dropna().unique())
    selected_names = st.multiselect("Measurement Name", options=name_options, default=[])
    if selected_names:
        filters.append(df["name"].isin(selected_names))

    # Meta filters
    meta_df = pd.json_normalize(df["meta"])
    if not meta_df.empty:
        for col in meta_df.columns:
            options = sorted(meta_df[col].dropna().unique())
            selected = st.multiselect(col.replace("_", " ").title(), options=options, default=[])
            if selected:
                filters.append(meta_df[col].isin(selected))

    # Apply all filters
    if filters:
        combined_filter = reduce(lambda a, b: a & b, filters)  # Combine all filters with AND
        df = df[combined_filter]

    return df
