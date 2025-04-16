import plotly.graph_objects as go
import streamlit as st


def plot_run_statistics(test_df, selected_run_ids, run_df):
    """Render stacked bar plot of test run statistics."""
    st.subheader("Test Run Statistics")

    test_data = test_df[test_df["run_id"].isin(selected_run_ids)]
    if test_data.empty:
        st.info("No test data available for the selected runs.")
        return

    run_labels = {row["run_id"]: f"{row['run_id']} - {row['start_time'].strftime('%Y-%m-%d %H:%M:%S')}" for _, row in run_df.iterrows()}

    status_counts = test_data.groupby(["run_id", "status"]).size().unstack(fill_value=0)
    status_counts["label"] = status_counts.index.map(run_labels)

    fig = go.Figure()
    color_map = {"FAIL": "#FF4B4B", "SKIP": "#FFD166", "PASS": "#74CF80"}

    for status in ["FAIL", "SKIP", "PASS"]:
        if status in status_counts.columns:
            fig.add_trace(
                go.Bar(
                    x=status_counts["label"],
                    y=status_counts[status],
                    name=status,
                    marker_color=color_map[status],
                )
            )

    fig.update_layout(xaxis_title="Run", yaxis_title="Number of Tests", barmode="stack", legend_title="Test Status")
    st.plotly_chart(fig, use_container_width=True)
