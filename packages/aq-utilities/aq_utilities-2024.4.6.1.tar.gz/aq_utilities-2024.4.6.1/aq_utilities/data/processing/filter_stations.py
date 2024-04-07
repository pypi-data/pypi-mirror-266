from datetime import datetime
from typing import Union, Callable, List, Tuple

import pandas as pd


def filter_aqsids(
        stations_info: pd.DataFrame,
        remove_aqsid: Union[List[str], None] = ["000000000"],
        aqsid_col_name: str = "aqsid",
        verbose: bool = False,
    ) -> pd.DataFrame:
    """Filter stations based on aqsid."""
    if verbose:
        print(f"[{datetime.now()}] Filtering from {len(stations_info)} stations.")

    if remove_aqsid is not None:
        if verbose:
            print(f"[{datetime.now()}] Removing stations with aqsid in {remove_aqsid}.")
        stations_info = stations_info[~stations_info[aqsid_col_name].isin(remove_aqsid)]

    if verbose:
        print(f"[{datetime.now()}] Returning {len(stations_info)} stations.")  

    return stations_info


def filter_lat_lon(
        stations_info: pd.DataFrame,
        remove_lat_lon: Union[List[Tuple[float, float]], None] = (0, 0),
        lat_col_name: str = "latitude",
        lon_col_name: str = "longitude",
        verbose: bool = False,
    ) -> pd.DataFrame:
    """Filter stations based on lat-lon locations."""
    if verbose:
        print(f"[{datetime.now()}] Filtering from {len(stations_info)} stations.")

    if remove_lat_lon is not None:
        if verbose:
            print(f"[{datetime.now()}] Removing stations with lat-long paris in {remove_lat_lon}.")
        stations_info = stations_info[
            ~stations_info[[lat_col_name, lon_col_name]].apply(
                lambda x: tuple(x) in remove_lat_lon, axis=1
            )
        ]
    
    if verbose:
        print(f"[{datetime.now()}] Returning {len(stations_info)} stations.")  

    return stations_info


def filter_lat_lon_in_bounding_box(
        stations_info: pd.DataFrame,
        lat_min: float = 24.9493,
        lat_max: float = 49.5904,
        lon_min: float = -125.0011,
        lon_max: float = 	-66.9326,
        lat_col_name: str = "latitude",
        lon_col_name: str = "longitude",
        verbose: bool = False,
    ) -> pd.DataFrame:
    """Filter stations based on lat-lon locations."""
    if verbose:
        print(f"[{datetime.now()}] Filtering from {len(stations_info)} stations.")

    # apply the lat-lon bounding box filter
    if verbose:
        print(f"[{datetime.now()}] Removing stations outside of the bounding box.")
    stations_info = stations_info[
        (stations_info[lat_col_name] >= lat_min) &
        (stations_info[lat_col_name] <= lat_max) &
        (stations_info[lon_col_name] >= lon_min) &
        (stations_info[lon_col_name] <= lon_max)
    ]
    
    if verbose:
        print(f"[{datetime.now()}] Returning {len(stations_info)} stations.")  

    return stations_info


def round_station_lat_lon(
        stations_info: pd.DataFrame,
        round_lat_lon: Union[int, None] = 2,
        lat_col_name: str = "latitude",
        lon_col_name: str = "longitude",
        verbose: bool = False,
    ) -> pd.DataFrame:
    """Filter stations based on aqsid."""
    if verbose:
        print(f"[{datetime.now()}] Filtering from {len(stations_info)} stations.")

    if round_lat_lon is not None:
        if verbose:
            print(f"[{datetime.now()}] Rounding lat and lon to {round_lat_lon} decimal places.")
        stations_info = stations_info.round({lat_col_name: round_lat_lon, lon_col_name: round_lat_lon})
    
    if verbose:
        print(f"[{datetime.now()}] Returning {len(stations_info)} stations.")  

    return stations_info


def remove_duplicate_lat_lon(
        df: pd.DataFrame,
        lat_col_name: str = "latitude",
        lon_col_name: str = "longitude",
        verbose: bool = False,
    ) -> pd.DataFrame:
    """Remove duplicate lat-lon pairs."""
    if verbose:
        print(f"[{datetime.now()}] Removing duplicates from {len(df)} rows.")

    df = df.drop_duplicates(subset=[lat_col_name, lon_col_name])

    if verbose:
        print(f"[{datetime.now()}] Returning {len(df)} rows.")

    return df


def remove_duplicate_aqsid(
        df: pd.DataFrame,
        aqsid_col_name: str = "aqsid",
        verbose: bool = False,
    ) -> pd.DataFrame:
    """Remove duplicate aqsid pairs."""
    if verbose:
        print(f"[{datetime.now()}] Removing duplicates from {len(df)} rows.")

    df = df.drop_duplicates(subset=[aqsid_col_name])

    if verbose:
        print(f"[{datetime.now()}] Returning {len(df)} rows.")

    return df


def apply_filters(
        df: pd.DataFrame,
        filters: List[Callable],
        verbose: bool = False,
    ) -> pd.DataFrame:
    """Apply a list of filters to a dataframe."""
    for f in filters:
        if verbose:
            print(f"[{datetime.now()}] Applying filter {f.__name__}.")
        df = f(df, verbose=verbose)
    return df
