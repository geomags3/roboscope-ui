import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from components.filters import apply_measurement_filters

from roboscope.models import NumericMeasurement

st.title("Numeric Measurements")

db = st.session_state.db
selected_run_ids = st.session_state.selected_run_ids

if not selected_run_ids:
    st.warning("Please select at least one Test Run to display measurements.")
    st.stop()

numeric_df = db.query(NumericMeasurement).where_in("run_id", selected_run_ids).as_dataframe()

if numeric_df.empty:
    st.info("No numeric data available for the selected runs.")
    st.stop()

st.subheader("Measurement Filters")


numeric_df = apply_measurement_filters(numeric_df)

if numeric_df.empty:
    st.info("No data after filtering. Adjust your filters to see results.")
    st.stop()

with st.expander("Data Table", expanded=False):
    st.dataframe(numeric_df)

col1, col2 = st.columns([1, 1])

with col1:
    x_axis_option = st.segmented_control("X-axis", options=["Run ID", "Timestamp"], default="Run ID")
with col2:
    line_style_option = st.segmented_control(
        "Line Style", options=["Smooth (Spline)", "Straight (Linear)", "Markers Only"], default="Smooth (Spline)"
    )

# Map to plotly line shape
line_shape_map = {
    "Smooth (Spline)": "spline",
    "Straight (Linear)": "linear",
    "Markers Only": None,  # handled separately
}

line_shape = line_shape_map[line_style_option]

fig = go.Figure()

# Prepare grouping label (Name + optional DUT)
meta_df = pd.json_normalize(numeric_df["meta"])
if "dut" in numeric_df.columns:
    numeric_df["label"] = numeric_df["name"] + " / " + numeric_df["dut"].fillna("Unknown")
else:
    numeric_df["label"] = numeric_df["name"]

# Prepare X-axis
if x_axis_option == "Run ID":
    x_data = numeric_df["run_id"]
else:
    numeric_df["timestamp"] = pd.to_datetime(numeric_df["timestamp"])
    x_data = numeric_df["timestamp"]

# Plot measurement traces
for label, group in numeric_df.groupby("label"):
    mode = "markers" if line_style_option == "Markers Only" else "lines+markers"

    fig.add_trace(
        go.Scatter(
            x=group[x_data.name],
            y=group["value"],
            mode=mode,
            name=label,
            line=dict(shape=line_shape) if line_shape else None,
        )
    )

# Plot limit lines
for limit_name, color, column in [("Lower Limit", "red", "lower_limit"), ("Upper Limit", "red", "upper_limit")]:
    limits = numeric_df[column].dropna().unique()
    if limits.size:
        limit_value = limits.flat[0]
        fig.add_trace(
            go.Scatter(
                x=numeric_df[x_data.name],
                y=[limit_value] * len(numeric_df),
                mode="lines",
                name=limit_name,
                line=dict(dash="dash", color=color),
            )
        )

# Update layout
fig.update_layout(
    title="Numeric Measurements",
    xaxis_title=x_axis_option,
    yaxis_title=f"Value ({numeric_df.get('unit', pd.Series([''])).iloc[0]})",
    legend_title="Measurement",
)

st.plotly_chart(fig, use_container_width=True)
