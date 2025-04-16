import re

import pandas as pd
import streamlit as st
from components.filters import apply_measurement_filters

from roboscope.models import StringMeasurement

st.title("String Measurements")

db = st.session_state.db
selected_run_ids = st.session_state.selected_run_ids

if not selected_run_ids:
    st.warning("Please select at least one Test Run to display measurements.")
    st.stop()

string_df = db.query(StringMeasurement).where_in("run_id", selected_run_ids).as_dataframe()

if string_df.empty:
    st.info("No string measurements available for the selected runs.")
    st.stop()

st.subheader("Measurement Filters")
string_df = apply_measurement_filters(string_df)

if string_df.empty:
    st.info("No data after filtering. Adjust your filters to see results.")
    st.stop()

with st.expander("Data Table", expanded=False):
    st.dataframe(string_df)


# Add result column
def determine_string_result(row):
    if not row["expected_value"]:
        return "✅"
    value = row["value"] or ""
    expected = row["expected_value"] or ""
    mode = row["mode"]
    ignore_case = row["ignore_case"]

    if ignore_case:
        value = value.lower()
        expected = expected.lower()

    if mode == "equal":
        return "✅" if value == expected else "❌"
    elif mode == "not_equal":
        return "✅" if value != expected else "❌"
    elif mode == "regex":
        flags = re.IGNORECASE if ignore_case else 0
        try:
            return "✅" if re.match(expected, value, flags=flags) else "❌"
        except re.error:
            return "❌"
    elif mode == "log":
        return "✅"
    else:
        return "❌"


string_df["Result"] = string_df.apply(determine_string_result, axis=1)

# Build display table
display_df = pd.DataFrame(
    {
        "Run ID": string_df["run_id"],
        "Measurement Name": string_df["name"],
        "Value": string_df["value"],
        "Expected": string_df["expected_value"],
        "Mode": string_df["mode"],
        "Ignore Case": string_df["ignore_case"].apply(lambda x: "True" if x else "False"),
        "Result": string_df["Result"],
    }
)

st.subheader("Measurement Overview")

st.dataframe(display_df, use_container_width=True, hide_index=True)
