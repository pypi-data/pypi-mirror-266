import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Union, List

import pandas as pd
import psycopg2
from sqlalchemy.sql import text

from aq_utilities.config.data import CHUNCKSIZE
from aq_utilities.data.remote import download_file
from aq_utilities.data.failures.psql import write_failure_to_postgres


def stations_info_to_postgres(stations_info_fp: str,
                              engine: "sqlalchemy.engine.Engine",
                              chunksize: int = CHUNCKSIZE,
                              verbose: bool = False) -> int:
    """Load station info data to postgres database."""
    # get timestamp from the directory name
    timestamp_component = Path(stations_info_fp).parent.stem
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
        print(f"[{datetime.now()}] loading {stations_info_fp} to postgres")

    try:
        names = download_file(fp=stations_info_fp, timestamp=timestamp)
        if verbose: print(f"[{datetime.now()}] downloaded {stations_info_fp}")
        local_fp, blob_name = names
        if verbose: print(f"[{datetime.now()}] reading {local_fp}")
        df = pd.read_csv(local_fp, sep="|", encoding="latin-1")
    except Exception as e:
        write_failure_to_postgres((timestamp, stations_info_fp),
                                  "stations_info_failures", engine=engine)
        print(e)
        return 1

    if verbose: print(f"[{datetime.now()}] read {local_fp}")
    # merge the "StateAbbrevation" and "StateAbbreviation" columns into a single column called state_abbreviation
    if "StateAbbrevation" in df and "StateAbbreviation" not in df:
        df.rename(columns={"StateAbbrevation": "state_abbreviation"}, inplace=True)
    elif "StateAbbreviation" in df:
        df.rename(columns={"StateAbbreviation": "state_abbreviation"}, inplace=True)
    else:
        df["state_abbreviation"] = df["StateAbbrevation"].combine_first(df["StateAbbreviation"])
        df.drop(columns=["StateAbbrevation", "StateAbbreviation"], inplace=True)
    columns_to_rename = {
        "AQSID": "aqsid",
        "FullAQSID": "full_aqsid",
        "StationID": "station_id",
        "Parameter": "parameter",
        "MonitorType": "monitor_type",
        "SiteCode": "site_code",
        "SiteName": "site_name",
        "Status": "status",
        "AgencyID": "agency_id",
        "AgencyName": "agency_name",
        "EPARegion": "epa_region",
        "Latitude": "latitude",
        "Longitude": "longitude",
        "Elevation": "elevation",
        "GMTOffset": "gmt_offset",
        "CountryFIPS": "country_fips",
        "CBSA_ID": "cbsa_id",
        "CBSA_Name": "cbsa_name",
        "StateAQSCode": "state_aqs_code",
        "CountyAQSCode": "county_aqs_code",
        "CountyName": "county_name"
    }
    df.rename(columns=columns_to_rename,
            inplace=True)
    df.status = df.status.str.upper()
    # add a column with todays date or date of the file
    df["timestamp"] = timestamp

    try:
        df.to_sql(
            "stations_info",
            engine,
            if_exists="append",
            index=False,
            chunksize=chunksize,
            method="multi",
        )
        if verbose:
            print(f"[{datetime.now()}] wrote {stations_info_fp} to postgres")
    except Exception as e:
        if isinstance(e, psycopg2.errors.UniqueViolation): pass
        else:
            if verbose: print(e)
            return 1
    return 0


def load_stations_info(
    engine: "sqlalchemy.engine.base.Engine",
    table_name: str = "stations_info",
    query_date: str = "2022-01-01",
    selected_aqsids: Union[List[str], None] = None,
    verbose: bool = False,
) -> pd.DataFrame:
    # get the station information for these stations from the database
    if selected_aqsids is not None:
        assert len(selected_aqsids) > 0, "selected_aqsids must have at least one aqsid if provided"
        assert isinstance(selected_aqsids, list), "selected_aqsids must be a list"
        aqsid = ",".join(f"'{s}'" for s in selected_aqsids)
        aqsid_override = f"AND d.aqsid IN ({aqsid})"
    else:
        aqsid_override = ""
    query = f"SELECT d.aqsid, d.latitude, d.longitude, d.elevation FROM {table_name} AS d WHERE d.timestamp = '{query_date}' {aqsid_override} GROUP BY d.aqsid, d.latitude, d.longitude, d.elevation ORDER BY d.aqsid;"

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
