import streamlit as st

STATUS_EMOJI_MAP = {
    "PASS": "✅",
    "FAIL": "❌",
    "SKIP": "⏭️",
    "": "❔",
    None: "❔",
}


def show_summary(run_df, selected_run_ids):
    """Show summary table of test runs."""
    st.subheader("Summary")

    summary_df = run_df[run_df["run_id"].isin(selected_run_ids)].copy()
    summary_df["status"] = summary_df["status"].map(STATUS_EMOJI_MAP)

    st.dataframe(
        summary_df,
        column_config={
            "run_id": st.column_config.NumberColumn("Run ID", width="small"),
            "name": st.column_config.TextColumn("Name", width="medium"),
            "meta": st.column_config.JsonColumn("Meta", width="medium"),
            "start_time": st.column_config.DatetimeColumn("Start Time", width="medium"),
            "end_time": st.column_config.DatetimeColumn("End Time", width="medium"),
            "elapsed_time": st.column_config.NumberColumn("Elapsed (s)", width="small"),
            "status": st.column_config.TextColumn("Status", width="small"),
        },
        use_container_width=True,
        hide_index=True,
    )


def show_test_overview(test_df, suite_df, failure_df, selected_run_ids):
    """Show test overview table with optional failure details."""
    st.subheader("Test Overview")

    show_failures = st.toggle("Show Failures", value=False)

    merged_df = test_df[test_df["run_id"].isin(selected_run_ids)].merge(
        suite_df[["run_id", "suite_id", "name"]].rename(columns={"name": "Test Suite"}),
        on=["run_id", "suite_id"],
        how="left",
    )

    merged_df["Status Emoji"] = merged_df["status"].map(STATUS_EMOJI_MAP).fillna("❔")

    failures_map = {}
    if show_failures:
        failures_map = failure_df.groupby(["run_id", "test_id"])["details"].apply(list).to_dict()

    def get_cell_content(row):
        failures = failures_map.get((row["run_id"], row["test_id"]))
        if show_failures and failures:
            return f"{row['Status Emoji']}\n" + "\n".join(failures)
        return row["Status Emoji"]

    merged_df["Cell Content"] = merged_df.apply(get_cell_content, axis=1)

    pivot = merged_df.pivot_table(
        index=["Test Suite", "name"],
        columns="run_id",
        values="Cell Content",
        aggfunc="first",
        fill_value="",
    )
    pivot.columns = [f"Run {col}" for col in pivot.columns]
    pivot.reset_index(inplace=True)
    pivot.rename(columns={"name": "Test Case"}, inplace=True)
    pivot.loc[pivot.duplicated(subset=["Test Suite"]), "Test Suite"] = ""

    run_columns = [col for col in pivot.columns if col.startswith("Run")]
    column_config = {
        "Test Suite": st.column_config.TextColumn("Test Suite", width="medium"),
        "Test Case": st.column_config.TextColumn("Test Case", width="medium"),
    }
    for col in run_columns:
        column_config[col] = st.column_config.TextColumn(col, width="small")

    st.dataframe(
        pivot,
        column_config=column_config,
        use_container_width=True,
        hide_index=True,
    )
