import time
from datetime import datetime
from pathlib import Path
from typing import Union, List

import pandas as pd
import psycopg2
from sqlalchemy.sql import text

from aq_utilities.config.data import CHUNCKSIZE
from aq_utilities.data.remote import download_file
from aq_utilities.data.failures.psql import write_failure_to_postgres


def hourly_predictions_to_postgres(predictions: pd.DataFrame,
                                   engine: "sqlalchemy.engine.Engine",
                                   chunksize: int = CHUNCKSIZE,
                                   verbose: bool = False) -> int:
    """Load hourly data to postgres database."""
    if verbose:
        print(
            f"[{datetime.now()}] writing {len(predictions)} records to postgres"
        )
    try:
        predictions.to_sql(
            "hourly_predictions",
            engine,
            if_exists="append",
            index=False,
            chunksize=chunksize,
            method="multi",
        )
        if verbose:
            print(
                f"[{datetime.now()}] wrote {len(predictions)} records to postgres"
            )
    except Exception as e:
        if isinstance(e, psycopg2.errors.UniqueViolation): pass
        else:
            if verbose:
                print(
                    f"[{datetime.now()}] failed to write {len(predictions)} records to postgres with error {e}"
                )
            return 1
    return 0


def hourly_features_to_postgres(features: pd.DataFrame,
                                engine: "sqlalchemy.engine.Engine",
                                chunksize: int = CHUNCKSIZE,
                                verbose: bool = False) -> int:
    """Load hourly features to postgres database."""
    if verbose:
        print(
            f"[{datetime.now()}] writing {len(features)} records to postgres")
    try:
        features.to_sql(
            "hourly_features",
            engine,
            if_exists="append",
            index=False,
            chunksize=chunksize,
            method="multi",
        )
        if verbose:
            print(
                f"[{datetime.now()}] wrote {len(features)} records to postgres"
            )
    except Exception as e:
        if isinstance(e, psycopg2.errors.UniqueViolation): pass
        else:
            if verbose:
                print(
                    f"[{datetime.now()}] failed to write {len(features)} records to postgres with error {e}"
                )
            return 1
    return 0


def hourly_data_to_postgres(hourly_data_fp: str,
                            engine: "sqlalchemy.engine.Engine",
                            chunksize: int = CHUNCKSIZE,
                            verbose: bool = False) -> int:
    """Load hourly data to postgres database."""
    # get timestamp from file name
    timestamp = datetime.strptime(
        Path(hourly_data_fp).stem.split("_")[1].split(".")[0], "%Y%m%d%H")
    if verbose:
        print(f"[{datetime.now()}] loading {hourly_data_fp} to postgres")
    if verbose: print(f"[{datetime.now()}] file timestamp is {timestamp}")
    try:
        names = download_file(fp=hourly_data_fp, timestamp=timestamp)
        if verbose: print(f"[{datetime.now()}] downloaded {hourly_data_fp}")
        local_fp, blob_name = names
        df = pd.read_csv(local_fp, sep="|", encoding="latin-1", header=None)
        if verbose: print(f"[{datetime.now()}] read {local_fp}")
    except ValueError as e:
        write_failure_to_postgres((timestamp, hourly_data_fp),
                                  "hourly_data_failures", engine=engine)
        print(e)
        return 1
    df.rename(
        columns={
            0: "date",
            1: "time",
            2: "aqsid",
            3: "name",
            4: "unk",
            5: "measurement",
            6: "units",
            7: "value",
            8: "source"
        }, inplace=True)
    # join date and time columns to make a timestamp column
    df["timestamp"] = pd.to_datetime(df["date"] + " " + df["time"],
                                     format="%m/%d/%y %H:%M")
    df.drop(["date", "time"], axis=1, inplace=True)
    try:
        df.to_sql(
            "hourly_data",
            engine,
            if_exists="append",
            index=False,
            chunksize=chunksize,
            method="multi",
        )
        if verbose: print(f"wrote {hourly_data_fp} to postgres")
    except Exception as e:
        if isinstance(e, psycopg2.errors.UniqueViolation): pass
        else:
            if verbose: print(e)
            return 1
    return 0


def load_hourly_data(
    engine: "sqlalchemy.engine.base.Engine",
    table_name: str = "hourly_data",
    features: List[str] = ["PM2.5"],
    start_time: str = "2020-01-01",
    end_time: str = "2024-01-01",
    aqsids_filter: Union[List[str], None] = None,
    verbose: bool = False,
) -> pd.DataFrame:
    """Load the dataframe from the database."""
    measurements = ",".join(f"'{m}'" for m in features)
    aqsids_filter = ",".join(f"'{a}'" for a in aqsids_filter) if aqsids_filter is not None else None
    aqsid_override = f"AND d.aqsid IN ({aqsids_filter})" if aqsids_filter is not None else ""
    query = f"SELECT d.aqsid, d.timestamp, d.measurement, d.value FROM {table_name} AS d WHERE d.timestamp >= '{start_time}' AND d.timestamp < '{end_time}' AND d.measurement IN ({measurements}) {aqsid_override} GROUP BY d.aqsid, d.timestamp, d.measurement, d.value ORDER BY d.timestamp;"

    if verbose: print(f"[{datetime.now()}] executing query: {query}")

    # execute the query
    with engine.connect() as conn:
        query_start = time.time()
        df = pd.read_sql_query(text(query), conn)
        query_end = time.time()
        if verbose:
            print(
                f"[{datetime.now()}] query executed in {query_end - query_start:.2f} seconds"
            )

    if verbose: print(f"[{datetime.now()}] dataframe shape: {df.shape}")

    return df


def load_hourly_features(
    engine: "sqlalchemy.engine.base.Engine",
    table_name: str = "hourly_features",
    features: List[str] = ["PM2.5"],
    start_time: str = "2020-01-01",
    end_time: str = "2024-01-01",
    h3_indices_filter: Union[List[str], None] = None,
    aqsids_filter: Union[List[str], None] = None,
    verbose: bool = False,
) -> pd.DataFrame:
    """Load the dataframe from the database."""
    # build filter for measurements
    measurement_filter = ",".join(f"'{m}'" for m in features)
    # build filter for aqsid (station ids)
    aqsids_filter = ",".join(f"'{a}'" for a in aqsids_filter) if aqsids_filter is not None else None
    aqsids_filter_override = f" AND d.aqsid IN ({aqsids_filter})" if aqsids_filter is not None else ""
    # build filter for h3 index
    h3_indices_filter = ",".join(f"'{a}'" for a in h3_indices_filter) if h3_indices_filter is not None else None
    h3_indices_filter_override = f" AND d.h3_index IN ({h3_indices_filter})" if h3_indices_filter is not None else ""
    
    # build the query
    query = f"SELECT d.aqsid, d.h3_index, d.timestamp, d.measurement, d.value FROM {table_name} AS d WHERE d.timestamp >= '{start_time}' AND d.timestamp < '{end_time}' AND d.measurement IN ({measurement_filter}){aqsids_filter_override}{h3_indices_filter_override} GROUP BY d.aqsid, d.h3_index, d.timestamp, d.measurement, d.value ORDER BY d.timestamp;"

    if verbose: print(f"[{datetime.now()}] executing query: {query}")

    # execute the query
    with engine.connect() as conn:
        query_start = time.time()
        df = pd.read_sql_query(text(query), conn)
        query_end = time.time()
        if verbose:
            print(
                f"[{datetime.now()}] query executed in {query_end - query_start:.2f} seconds"
            )

    if verbose: print(f"[{datetime.now()}] dataframe shape: {df.shape}")

    return df


def load_hourly_feature(
    engine: "sqlalchemy.engine.base.Engine",
    table_name: str = "hourly_features",
    feature: str = "PM2.5",
    start_time: str = "2020-01-01",
    end_time: str = "2024-01-01",
    h3_indices_filter: Union[List[str], None] = None,
    aqsids_filter: Union[List[str], None] = None,
    verbose: bool = False,
) -> pd.DataFrame:
    """Load the dataframe from the database."""
    # build filter for measurements
    measurement_filter =f"'{feature}'"
    # build filter for aqsid (station ids)
    aqsids_filter = ",".join(f"'{a}'" for a in aqsids_filter) if aqsids_filter is not None else None
    aqsids_filter_override = f" AND d.aqsid IN ({aqsids_filter})" if aqsids_filter is not None else ""
    # build filter for h3 index
    h3_indices_filter = ",".join(f"'{a}'" for a in h3_indices_filter) if h3_indices_filter is not None else None
    h3_indices_filter_override = f" AND d.h3_index IN ({h3_indices_filter})" if h3_indices_filter is not None else ""
    
    # build the query
    query = f"SELECT d.aqsid, d.h3_index, d.timestamp, d.value FROM {table_name} AS d WHERE d.timestamp >= '{start_time}' AND d.timestamp < '{end_time}' AND d.measurement IN ({measurement_filter}){aqsids_filter_override}{h3_indices_filter_override} GROUP BY d.aqsid, d.h3_index, d.timestamp, d.measurement, d.value ORDER BY d.timestamp;"

    if verbose: print(f"[{datetime.now()}] executing query: {query}")

    # execute the query
    with engine.connect() as conn:
        query_start = time.time()
        df = pd.read_sql_query(text(query), conn)
        query_end = time.time()
        if verbose:
            print(
                f"[{datetime.now()}] query executed in {query_end - query_start:.2f} seconds"
            )

    if verbose: print(f"[{datetime.now()}] dataframe shape: {df.shape}")

    return df
