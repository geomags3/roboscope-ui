import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from components.filters import apply_measurement_filters

from roboscope.models import SeriesMeasurement

st.title("Series Measurements")

db = st.session_state.db
selected_run_ids = st.session_state.selected_run_ids

if not selected_run_ids:
    st.warning("Please select at least one Test Run to display measurements.")
    st.stop()

series_df = db.query(SeriesMeasurement).where_in("run_id", selected_run_ids).as_dataframe()

if series_df.empty:
    st.info("No series data available for the selected runs.")
    st.stop()

st.subheader("Measurement Filters")

series_df = apply_measurement_filters(series_df)

if series_df.empty:
    st.info("No data after filtering. Adjust your filters to see results.")
    st.stop()

with st.expander("Data Table", expanded=False):
    st.dataframe(series_df)


line_style_option = st.segmented_control(
    "Line Style", options=["Smooth (Spline)", "Straight (Linear)", "Markers Only"], default="Smooth (Spline)"
)

line_shape_map = {
    "Smooth (Spline)": "spline",
    "Straight (Linear)": "linear",
    "Markers Only": None,
}
line_shape = line_shape_map[line_style_option]

fig = go.Figure()

# Grouping label (Name + optional DUT)
meta_df = pd.json_normalize(series_df["meta"])
if "dut" in series_df.columns:
    series_df["label"] = series_df["name"] + " / " + series_df["dut"].fillna("Unknown")
else:
    series_df["label"] = series_df["name"]

# Plot each measurement
for label, group in series_df.groupby("label"):
    for _, row in group.iterrows():
        # Prepare X-axis
        x_data = row["x_data"] if row["x_data"] else list(range(len(row["y_data"])))
        mode = "markers" if line_style_option == "Markers Only" else "lines+markers"

        # Measurement trace
        fig.add_trace(
            go.Scatter(
                x=x_data,
                y=row["y_data"],
                mode=mode,
                name=f"{label} - {row['run_id']}",
                line=dict(shape=line_shape) if line_shape else None,
            )
        )

        # Lower limit (optional)
        if row["lower_limits"]:
            fig.add_trace(
                go.Scatter(
                    x=x_data,
                    y=row["lower_limits"],
                    mode="lines",
                    name=f"Lower Limit - {label} - {row['run_id']}",
                    line=dict(dash="dash", color="red"),
                    showlegend=False,
                )
            )

        # Upper limit (optional)
        if row["upper_limits"]:
            fig.add_trace(
                go.Scatter(
                    x=x_data,
                    y=row["upper_limits"],
                    mode="lines",
                    name=f"Upper Limit - {label} - {row['run_id']}",
                    line=dict(dash="dash", color="red"),
                    showlegend=False,
                )
            )

# Update layout
x_label = series_df.get("x_label", pd.Series(["Index"])).iloc[0]
x_unit = series_df.get("x_unit", pd.Series([""])).iloc[0]
y_label = series_df.get("y_label", pd.Series(["Value"])).iloc[0]
y_unit = series_df.get("y_unit", pd.Series([""])).iloc[0]

fig.update_layout(
    title="Series Measurements",
    xaxis_title=f"{x_label} ({x_unit})" if x_unit else x_label,
    yaxis_title=f"{y_label} ({y_unit})" if y_unit else y_label,
    legend_title="Measurement",
)

st.plotly_chart(fig, use_container_width=True)
