from datetime import datetime

import pandas as pd
from streamlit import cache_data

from roboscope.database import Database
from roboscope.models import Failure, TestCase, TestRun, TestSuite


@cache_data
def load_initial_data(_db: Database) -> tuple[datetime, datetime, list[tuple]]:
    min_start_time = _db.query(TestRun).min("start_time")
    max_start_time = _db.query(TestRun).max("start_time")
    count = _db.query(TestRun).count()
    initial_runs = _db.query(TestRun).limit(min(5, count)).values("run_id", "start_time", "meta")
    return min_start_time, max_start_time, initial_runs


@cache_data
def load_selected_data(_db: Database, run_ids: list[int]) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    if not run_ids:
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

    return (
        _db.query(TestRun).where_in("run_id", run_ids).as_dataframe(),
        _db.query(TestCase).where_in("run_id", run_ids).as_dataframe(),
        _db.query(TestSuite).where_in("run_id", run_ids).as_dataframe(),
        _db.query(Failure).where_in("run_id", run_ids).as_dataframe(),
    )
