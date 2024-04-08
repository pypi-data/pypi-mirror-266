import numpy as np
import pandas as pd
import xarray as xr

from whiffle_client.analysis.utils import mean_angle

WINDOGRAPHER_COLUMN_MAP = {
    "AvgWs": "wind-speed [m/s]",
    "AvgWd": "wind-direction [deg]",
}


def _parse_turbine_column_name(col_name: str) -> tuple[str, str, str]:
    turbine_name = "_".join(col_name.split("_")[:-1])
    variable = col_name.split("_")[-1].split("[")[0]
    units = col_name.split("[")[-1].split("]")[0]
    units = f"[{units}]"
    return turbine_name, variable, units


def _parse_metmast_column_name(col_name: str) -> tuple[str, float, str, str]:
    metmast_name = "_".join(col_name.split("_")[:-2])
    height = float(col_name.split("_")[-2][1:])
    variable = col_name.split("_")[-1].split("[")[0]
    units = col_name.split("[")[-1].split("]")[0]
    units = f"[{units}]"
    return metmast_name, height, variable, units


def _read_whiffle_wind_csv(csv_path):
    df = pd.read_csv(csv_path, sep=";")
    df["time[UTC]"] = pd.to_datetime(df["time[UTC]"], utc=True)
    df = df.set_index("time[UTC]").rename_axis("time [UTC]")
    return df


def _parse_windographer_column_name_to_tuple(col_name):
    var, height, boom_angle = col_name.split()[1:4]
    height = np.floor(float(height.split("m")[0]))
    return var, height, boom_angle


def whiffle_wind_turbines_csv_to_dataframe(csv_path: str) -> pd.DataFrame:
    """Load a whiffle wind csv with turbine data into a pandas dataframe.

    Parameters
    ----------
    csv_path : str
        Path to the whiffle wind csv file with turbine data.

    Returns
    -------
    pd.DataFrame
        Dataframe with simulated wind turbine data.
    """
    df = _read_whiffle_wind_csv(csv_path)
    midx = df.columns.map(_parse_turbine_column_name)
    midx = [(x[0], f"{x[1]} {x[2]}") for x in midx]
    midx = pd.MultiIndex.from_tuples(midx, names=("turbine", None))
    df.columns = midx
    df = df.stack(level=0, future_stack=True).sort_index()
    return df


def whiffle_wind_turbines_csv_to_dataset(csv_path: str) -> xr.Dataset:
    """Load a whiffle wind csv with turbine data into a xarray dataset.

    Parameters
    ----------
    csv_path : str
        Path to the whiffle wind csv file with turbine data.

    Returns
    -------
    xr.Dataset
        Dataset with simulated wind turbine data.
    """
    df = whiffle_wind_turbines_csv_to_dataframe(csv_path)
    ds = turbine_dataframe_to_dataset(df)
    return ds


def turbine_dataframe_to_dataset(df: pd.DataFrame) -> xr.Dataset:
    """Convert a dataframe with turbine data into an xarray dataset.

    Parameters
    ----------
    df : pd.DataFrame
        Dataframe with simulated wind turbine data.

    Returns
    -------
    xr.Dataset
        Dataset with simulated wind turbine data.
    """
    df = df.rename_axis(("time", "turbine"))
    parsed_columns = [tuple(x.split(" ")) for x in df.columns]
    parsed_variables = parsed_columns + [("time", "[UTC]")]
    df.columns = [x[0] for x in parsed_columns]
    ds = df.to_xarray()
    for var, unit in parsed_variables:
        ds[var].attrs["units"] = unit[1:-1]
    return ds


def whiffle_wind_metmast_csv_to_dataframe(csv_path: str) -> pd.DataFrame:
    """Load a whiffle wind csv with metmast data into a pandas dataframe.

    Parameters
    ----------
    csv_path : str
        Path to the whiffle wind csv file with simulated metmast data.

    Returns
    -------
    pd.DataFrame
        Dataframe with simulated metmast data.
    """
    df = _read_whiffle_wind_csv(csv_path)
    midx = df.columns.map(_parse_metmast_column_name)
    midx = [(x[0], x[1], f"{x[2]} {x[3]}") for x in midx]
    midx = pd.MultiIndex.from_tuples(midx, names=("metmast", "height [m]", None))
    df.columns = midx
    df = df.stack(level=[0, 1], future_stack=True).sort_index()
    return df


def whiffle_wind_metmast_csv_to_dataset(csv_path: str) -> xr.Dataset:
    """Load a whiffle wind csv with metmast data into a xarray dataset.

    Parameters
    ----------
    csv_path : str
        Path to the whiffle wind csv file with simulated metmast data.

    Returns
    -------
    xr.Dataset
        Dataset with simulated metmast data.
    """
    df = whiffle_wind_metmast_csv_to_dataframe(csv_path)
    ds = metmast_dataframe_to_dataset(df)
    return ds


def metmast_dataframe_to_dataset(df: pd.DataFrame) -> xr.Dataset:
    """Convert a dataframe with metmast data into an xarray dataset.

    Parameters
    ----------
    df : pd.DataFrame
        Dataframe with simulated metmast data.

    Returns
    -------
    xr.Dataset
        Dataset with simulated metmast data.
    """
    df = df.rename_axis(("time", "metmast", "height"))
    parsed_columns = [tuple(x.split(" ")) for x in df.columns]
    parsed_variables = parsed_columns + [("time", "[UTC]"), ("height", "[m]")]
    df.columns = [x[0] for x in parsed_columns]
    ds = df.to_xarray()
    for var, unit in parsed_variables:
        ds[var].attrs["units"] = unit[1:-1]
    return ds


def windographer_csv_to_dataframe(
    csv_path: str,
    metmast_name: str = None,
    utc_time_diff: int = 0,
) -> pd.DataFrame:
    """Load a windographer csv containing metmast data into a pandas dataframe.

    Parameters
    ----------
    csv_path : str
        Path to the windographer csv file with measured metmast data.
    metmast_name : str, optional
        Name of the metmast.
    utc_time_diff : int, optional
        Difference in hours between UTC and local time.

    Returns
    -------
    pd.DataFrame
        Dataframe with measured metmast data.
    """
    df = pd.read_csv(csv_path, header=8, sep="\t", encoding="ISO-8859-1")
    df.index = pd.to_datetime(df["Date/Time"], dayfirst=True)
    df = df.drop("Date/Time", axis=1)
    df = pd.concat(
        [
            df.filter(like="AvgWd"),
            df.filter(like="AvgWs").filter(like="m/s"),
        ],
        axis=1,
    )
    df.columns = df.columns.map(_parse_windographer_column_name_to_tuple)
    df = df.sort_index(axis=1).replace(-999, np.nan)
    df = pd.concat(
        [
            df[["AvgWd"]]
            .T.groupby(level=[0, 1], group_keys=False)
            .apply(lambda x: mean_angle(x) if x.shape[0] > 1 else x.droplevel(2))
            .T,
            df[["AvgWs"]]
            .T.groupby(level=[0, 1], group_keys=False)
            .apply(lambda x: x.mean())
            .T,
        ],
        axis=1,
    )
    df = df.rename(columns=WINDOGRAPHER_COLUMN_MAP)
    df.index = (df.index - pd.Timedelta(utc_time_diff, unit="hour")).tz_localize("utc")
    df = df.stack(future_stack=True)
    df = pd.concat({metmast_name: df}, names=["metmast", "time [UTC]", "height [m]"])
    df = df.reorder_levels([1, 0, 2]).sort_index()
    return df
