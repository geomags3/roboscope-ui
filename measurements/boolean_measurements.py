import pandas as pd
import streamlit as st
from components.filters import apply_measurement_filters

from roboscope.models import BooleanMeasurement

st.title("Boolean Measurements")

db = st.session_state.db
selected_run_ids = st.session_state.selected_run_ids

if not selected_run_ids:
    st.warning("Please select at least one Test Run to display measurements.")
    st.stop()

boolean_df = db.query(BooleanMeasurement).where_in("run_id", selected_run_ids).as_dataframe()

if boolean_df.empty:
    st.info("No boolean data available for the selected runs.")
    st.stop()

st.subheader("Measurement Filters")
boolean_df = apply_measurement_filters(boolean_df)

if boolean_df.empty:
    st.info("No data after filtering. Adjust your filters to see results.")
    st.stop()

with st.expander("Data Table", expanded=False):
    st.dataframe(boolean_df)


def determine_boolean_result(row):
    # If expected_value is None → no check, just ✅
    if pd.isna(row["expected_value"]):
        return "✅"
    return "✅" if row["value"] == row["expected_value"] else "❌"


boolean_df["Result"] = boolean_df.apply(determine_boolean_result, axis=1)

# Build display table
display_df = pd.DataFrame(
    {
        "Run ID": boolean_df["run_id"],
        "Measurement Name": boolean_df["name"],
        "Value": boolean_df["value"].apply(lambda x: "True" if x else "False"),
        "Expected": boolean_df["expected_value"].apply(lambda x: "True" if x else "False"),
        "Result": boolean_df["Result"],
    }
)

st.subheader("Measurement Overview")

st.dataframe(display_df, use_container_width=True, hide_index=True)
