import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Union

import pandas as pd
import numpy as np
from sqlalchemy import text
import psycopg2

from aq_utilities.config import CHUNCKSIZE
from aq_utilities.data.remote import download_file
from aq_utilities.data.failures.psql import write_failure_to_postgres


def daily_stations_to_postgres(daily_stations_fp: str,
                               engine: "sqlalchemy.engine.Engine",
                               chunksize: int = CHUNCKSIZE,
                               verbose: bool = False) -> int:
    """Load daily stations data to postgres database."""
    # get timestamp from the directory name
    timestamp_component = Path(daily_stations_fp).parent.stem
    if verbose:
        print(f"[{datetime.now()}] loading {daily_stations_fp} to postgres")
        print(f"[{datetime.now()}] file timestamp is {timestamp_component}")
    if timestamp_component == "today":
        timestamp = datetime.utcnow()
        timestamp = timestamp.replace(hour=0, minute=0, second=0,
                                      microsecond=0)
    elif timestamp_component == "yesterday":
        timestamp = datetime.utcnow() - timedelta(days=1)
        timestamp = timestamp.replace(hour=0, minute=0, second=0,
                                      microsecond=0)
    else:
        timestamp = datetime.strptime(timestamp_component, "%Y%m%d")
    if verbose:
        print(f"[{datetime.now()}] file timestamp is {timestamp_component}")
    try:
        names = download_file(fp=daily_stations_fp, timestamp=timestamp)
        if verbose: print(f"[{datetime.now()}] downloaded {daily_stations_fp}")
        local_fp, blob_name = names
        df = df = pd.read_csv(local_fp, sep="|", encoding="latin-1",
                              header=None)
        if verbose: print(f"[{datetime.now()}] read {local_fp}")
    except ValueError as e:
        write_failure_to_postgres((timestamp, daily_stations_fp),
                                  "daily_stations_failures", engine=engine)
        print(e)
        return 1
    df = df[[0, 1, 4, 8, 9]]
    # obtain list of unique values for each column based on StationID
    df = df.groupby(0).agg(lambda x: list(sorted(np.unique(x)))
                           if x.name == 1 else x.iloc[0])
    df.rename(
        columns={
            0: "aqsid",
            1: "parameters",
            4: "status",
            8: "latitude",
            9: "longitude"
        }, inplace=True)
    # cast status to upper case
    df.status = df.status.str.upper()
    # add a column with todays date or date of the file
    df["timestamp"] = timestamp
    df = df.rename_axis("aqsid").reset_index()

    try:
        df.to_sql(
            "daily_stations",
            engine,
            if_exists="append",
            index=False,
            chunksize=chunksize,
            method="multi",
        )
        if verbose: print(f"wrote {daily_stations_fp} to postgres")
    except Exception as e:
        if isinstance(e, psycopg2.errors.UniqueViolation): pass
        else:
            print(e)
            return 1
    return 0


def load_daily_stations(
    engine: "sqlalchemy.engine.base.Engine",
    table_name: str = "daily_stations",
    query_date: str = "2022-01-01",
    selected_aqsids: Union[List[str], None] = None,
    measurements: Union[List[str], None] = None,
    verbose: bool = False,
) -> pd.DataFrame:
    # get the station information for these stations from the database
    if selected_aqsids is not None:
        assert len(selected_aqsids) > 0, "selected_aqsids must have at least one aqsid if provided"
        assert isinstance(selected_aqsids, list), "selected_aqsids must be a list"
        aqsid = ",".join(f"'{s}'" for s in selected_aqsids)
        aqsid_override = f" AND d.aqsid IN ({aqsid})"
    else:
        aqsid_override = ""
    # make a measurements filter if measurements are provided
    measurements = ",".join(f"'{m}'" for m in measurements) if measurements is not None else None
    measurements_override = f" AND d.parameters && ARRAY[{measurements}]" if measurements is not None else ""
    
    query = f"SELECT d.aqsid, d.latitude, d.longitude FROM {table_name} AS d WHERE d.timestamp = '{query_date}'{aqsid_override}{measurements_override} GROUP BY d.aqsid, d.latitude, d.longitude ORDER BY d.aqsid;"

    if verbose: print(f"[{datetime.now()}] executing query: {query}")

    with engine.connect() as conn:
        query_start = time.time()
        df_stations = pd.read_sql_query(text(query), conn)
        query_end = time.time()
        if verbose:
            print(
                f"[{datetime.now()}] query executed in {query_end - query_start:.2f} seconds"
            )

    if verbose:
        print(f"[{datetime.now()}] dataframe shape: {df_stations.shape}")

    return df_stations
