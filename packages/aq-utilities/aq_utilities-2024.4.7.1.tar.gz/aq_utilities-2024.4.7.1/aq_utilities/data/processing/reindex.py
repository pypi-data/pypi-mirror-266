from datetime import datetime
from typing import Union, Callable, List, Tuple

import h3
import numpy as np
import pandas as pd


def measurements_to_aqsid(
    df: pd.DataFrame,
    stations_info: pd.DataFrame,
    start_time: str = "2020-01-01",
    end_time: str = "2024-01-01",
    time_step: str = "1H",
    aggregation_method: Union[Callable, str] = lambda x: np.mean(x[x>0]) if len(x[x>0]) > 0 else np.nan,
    nan_value: Union[float, int] = np.nan,
    time_closed_interval: bool = False,
    verbose: bool = False,
) -> pd.DataFrame:
    """Take the raw DataFrame from the database and process it into a fixed-station, fixed-index format."""
    # make a datetime index for the full range
    date_range = pd.date_range(
        start=start_time, end=end_time, freq=time_step,
        inclusive="left" if time_closed_interval else "both")

    if verbose: print(f"[{datetime.now()}] processing dataframe")

    # we would like df to be indexed on time and have columns for each station
    df = df[["aqsid", "timestamp",
             "value"]].groupby(["timestamp", "aqsid"]).aggregate({
                 "value":
                 aggregation_method
             }).reset_index().pivot(index="timestamp", columns="aqsid",
                                    values="value").resample(time_step).agg(aggregation_method).reindex(date_range)
    # undo the pivot so that we have a column for timestamp, a column for aqsid, and a column for value
    df = df.unstack().reset_index().rename(columns={
        "level_1": "timestamp",
        0: "value"
    })
    # join the lat, lon, elevation information to the main dataframe
    stations_info = stations_info.groupby("aqsid").first()
    df = df.join(stations_info, on="aqsid", how="inner")

    if verbose: print(f"[{datetime.now()}] dataframe shape: {df.shape}")

    # fill missing values with negative 1
    df = df.fillna(nan_value)

    return df


def measurements_to_h3(
    df: pd.DataFrame,
    start_time: str,
    end_time: str,
    aggregation_method: Union[Callable, str],
    min_h3_resolution: int,
    leaf_h3_resolution: int,
    include_root_node: bool = True,
    time_closed_interval: bool = False,
    verbose: bool = False,
) -> np.ndarray:
    """Compute h3 indexed measurements from aqsid index measurements."""
    # ensure that the columns exist
    assert "timestamp" in df.columns
    assert "latitude" in df.columns
    assert "longitude" in df.columns
    assert "aqsid" in df.columns
    assert "value" in df.columns

    # get the features from start time to end time
    if time_closed_interval:
        df = df[(df.timestamp >= start_time)
                & (df.timestamp <= end_time)].copy(deep=True)
    else:
        df = df[(df.timestamp >= start_time)
                & (df.timestamp < end_time)].copy(deep=True)
    df.reset_index(inplace=True)

    if verbose: print(f"[{datetime.now()}] processing feature")

    # we have one station that is at the exact same location as another station, so we need to drop one of them
    df = df.groupby(["timestamp", "latitude", "longitude"]).aggregate({
        "aqsid":
        "first",
        "value":
        aggregation_method
    }).reset_index()
    if verbose: print(f"[{datetime.now()}] dataframe shape: {df.shape}")

    # map the h3 index at the leaf resolution to the station
    # pivot the dataframe so that we have a column for each timestamp and a row for each h3 index
    df = df.pivot(index=["latitude", "longitude"], columns="timestamp",
                  values="value").reset_index()
    if verbose:
        print(f"[{datetime.now()}] pivoted dataframe shape: {df.shape}")

    if verbose:
        print(f"[{datetime.now()}] processing resolution {leaf_h3_resolution}")
    df["h3_index"] = df.apply(
        lambda x: h3.geo_to_h3(x.latitude, x.longitude, leaf_h3_resolution),
        axis=1)
    df.drop(columns=["latitude", "longitude"], inplace=True)

    h3_indexed_features = [
    ]  # tuples of (h3_index, value_t1, ..., value_tn), when concatenated will be shape (num_nodes, num_timestamps)

    # iterate through the h3 indices between the leaf resolution and the coarsest resolution
    for next_h3_resolution in range(leaf_h3_resolution - 1,
                                    min_h3_resolution - 2, -1):
        # ensure that the h3_index is the first column
        col_names = df.columns.tolist()
        col_names.remove("h3_index")
        # sort the columns by timestamp
        col_names.sort()
        col_names.insert(0, "h3_index")
        df = df[col_names]
        # add values for the current resolution
        h3_indexed_features.extend(df.to_numpy())

        if next_h3_resolution < min_h3_resolution: break
        if verbose:
            print(
                f"[{datetime.now()}] processing resolution {next_h3_resolution}"
            )
        # get the h3 index for each station at the next_resolution
        df["next_h3_index"] = df.apply(
            lambda x: h3.h3_to_parent(x.h3_index, next_h3_resolution), axis=1)
        # group by the next h3 index
        df.drop(columns=["h3_index"], inplace=True)
        df = df.groupby("next_h3_index").aggregate(
            aggregation_method).reset_index()
        # rename the h3 index to the current h3 index
        df = df.rename(columns={"next_h3_index": "h3_index"})

    # add another parent node for the entire graph
    if include_root_node:
        if verbose: print(f"[{datetime.now()}] adding root node")
        root_node_id = "root"
        df.drop(columns=["h3_index"], inplace=True)
        h3_indexed_features.append(
            np.concatenate((np.array([root_node_id]),
                            df.apply(aggregation_method).values.T)))

    return h3_indexed_features


def determine_leaf_h3_resolution(
    df: pd.DataFrame,
    min_h3_resolution: int = 0,
    max_h3_resolution: int = 12,
    verbose: bool = False,
) -> int:
    """Determine the leaf resolution that will give us unique hexagons for each station."""
    # we have one station that is at the exact same location as another station, so we need to drop one of them
    assert "latitude" in df.columns and "longitude" in df.columns, "df must have latitude and longitude columns"
    assert "aqsid" in df.columns, "df must have aqsid column"

    df = df.groupby(["latitude", "longitude"]).aggregate({
        "aqsid": "first"
    }).reset_index()

    # find the MAX_H3_RESOLUTION that will give us unique hexagons for each station
    leaf_h3_resolution: int = min_h3_resolution
    if verbose: print(f"[{datetime.now()}] determining leaf resolution")
    for i in range(min_h3_resolution, max_h3_resolution):
        if verbose: print(f"[{datetime.now()}] trying resolution {i}")
        if len(df["aqsid"].values) == len(
                df.apply(lambda x: h3.geo_to_h3(x.latitude, x.longitude, i),
                         axis=1).unique()):
            leaf_h3_resolution = i
            if verbose: print(f"[{datetime.now()}] found resolution {i}")
            break

    return leaf_h3_resolution


def aqsid_to_h3(
    df: pd.DataFrame,
    min_h3_resolution: int = 0,
    leaf_h3_resolution: int = 9,
    include_root_node: bool = True,
    as_df: bool = True,
    verbose: bool = False,
) -> List[Tuple[Union[str, None], str, int]]:
    """Process the edges and edge features for the graph."""
    assert "latitude" in df.columns and "longitude" in df.columns, "df must have latitude and longitude columns"
    if verbose:
        print(f"[{datetime.now()}] processing resolution {leaf_h3_resolution}")
        print(
            f"[{datetime.now()}] after resolution {leaf_h3_resolution}, we have {len(df)} nodes"
        )
    # map the h3 index at the leaf resolution to the station
    df["h3_index"] = df.apply(
        lambda x: h3.geo_to_h3(x.latitude, x.longitude, leaf_h3_resolution),
        axis=1)
    # store as a dataframe, adding new rows for each resolution
    node_df = df[["aqsid", "h3_index"]].copy(deep=True)

    # the aqsid is not meaningful except at the leaf resolution
    df["aqsid"] = None

    # iterate through the h3 indices between the leaf resolution and the coarsest resolution
    for next_h3_resolution in range(leaf_h3_resolution - 1,
                                    min_h3_resolution - 2, -1):
        if next_h3_resolution < min_h3_resolution: break
        if verbose:
            print(
                f"[{datetime.now()}] processing resolution {next_h3_resolution}"
            )
        # get the h3 index for each station at the next_resolution
        df["next_h3_index"] = df.apply(
            lambda x: h3.h3_to_parent(x.h3_index, next_h3_resolution), axis=1)
        # group by the next h3 index
        df = df.groupby("next_h3_index").aggregate({
            "aqsid": "first"
        }).reset_index()  # we don't need to aggregate the values
        # rename the h3 index to the current h3 index
        df = df.rename(columns={"next_h3_index": "h3_index"})
        # add these new rows to the node_df
        node_df = pd.concat([node_df, df[["aqsid", "h3_index"]]])
        if verbose:
            print(
                f"[{datetime.now()}] after resolution {next_h3_resolution}, we have {len(node_df)} nodes"
            )

    # add another parent node for the entire graph if needed
    if include_root_node:
        if verbose: print(f"[{datetime.now()}] adding root node")
        root_node_id = "root"
        node_df = pd.concat([
            node_df,
            pd.DataFrame({
                "aqsid": [None],
                "h3_index": [root_node_id]
            })
        ])

    # the node id is the index
    node_df["node_id"] = range(len(node_df))
    if verbose: print(f"[{datetime.now()}] processed {len(node_df)} nodes")

    # return as a dataframe
    if as_df:
        return node_df
    # return as a list of tuples
    return node_df.to_numpy()


def ensure_feature_axis(
        df: pd.DataFrame,
        h3_indices: List[str],
        timestamps: Union[List[Union[str, datetime]], pd.DatetimeIndex],
        timestamp_col_name: str = "timestamp",
        h3_index_col_name: str = "h3_index",
        values_col_name: str = "value",
        verbose: bool = False,
) -> pd.DataFrame:
    """Ensure the return from remote has the correct columns and rows."""
    # ensure that the columns are the correct type
    df[timestamp_col_name] = pd.to_datetime(df[timestamp_col_name])
    
    if verbose: print(f"[{datetime.now()}] initial dataframe shape: {df.shape}")
    
    df = df.pivot(index=timestamp_col_name, columns=h3_index_col_name, values=values_col_name).reindex(index=timestamps, columns=h3_indices)
    df = df.reset_index()
    df = df.rename(columns={"index": timestamp_col_name})
    df = df.melt(id_vars=timestamp_col_name, value_vars=h3_indices, var_name=h3_index_col_name, value_name=values_col_name)
    
    if verbose: print(f"[{datetime.now()}] final dataframe shape: {df.shape}")
    
    return df
