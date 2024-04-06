import glob
import logging
from functools import partial
from pathlib import Path
from typing import Callable, Sequence

log = logging.getLogger(__name__)
import aprl.part
import aprl.utils
import hydra_zen
import ocn_tools._src.geoprocessing.validation as ocnval
import pandas as pd
import xarray as xr


def preprocess_track(
    ds: xr.Dataset,
    min_lon: float = -66,
    max_lon: float = -54,
    min_lat: float = 32,
    max_lat: float = 44,
    min_time: str = "2016-12-01",
    max_time: str = "2018-02-01",
):
    """
    Check presence of time, lat, lon coordinates
    Set units to longitude, latitude, ssh variable
    Set range of longitude between -180 and 180
    Selecting SSH variable
    Filter values between min_max values for lat, lon and time

    Args:
        ds: Dataset
        min_lon: min longitude value
        max_lon: max longitude value
        min_lat: min latitude value
        max_lat: max latitude value
        min_time: min time value
        max_time: max time value

    Returns: xarray.Dataset

    """

    log.debug(
        f"Processing {ds}, using ssh_var {(min_lon, max_lon, min_lat, max_lat, min_time, max_time)}"
    )
    ds = (
        ds.rename(longitude="lon", latitude="lat")
        .pipe(ocnval.validate_latlon)
        .pipe(ocnval.validate_time)
        .pipe(
            lambda d: d.where(
                (d.lon.load() >= min_lon)
                & (d.lon <= max_lon)
                & (d.lat.load() >= min_lat)
                & (d.lat <= max_lat)
                & (d.time.load() >= pd.to_datetime(min_time))
                & (d.time <= pd.to_datetime(max_time)),
                drop=True,
            )
        )
        .assign(ssh=lambda d: d.sla_filtered + d.mdt - d.lwe)
        .pipe(ocnval.validate_ssh)
        .sortby("time")[["ssh"]]
    )
    log.debug(f"Returning {ds=}")
    return ds


def prepare_track(
    input_paths: str | Sequence[str],
    output_path: str,
    preprocess: Callable[xr.Dataset, xr.Dataset],
):
    """
    Open multifile dataset to be contatenated by time apply processing and write output

    Args:
        input_paths (str | Path | Sequence): path(s) to input netcdf file(s)
        output_path (str): path where to write the output
        preprocess (callable): function to apply to each netcdf
    """
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    log.info(f"Starting")
    log.debug(f"Opening {input_paths=}")
    log.debug(f"Applying preprocessing {preprocess}")
    log.debug(f"{getattr(preprocess, '__doc__', '')}")
    xr.open_mfdataset(
        input_paths,
        preprocess=preprocess,
        combine="nested",
        concat_dim="time",
    ).to_netcdf(output_path)
    log.info("Done")


def sorted_glob(pathname: str):
    """

    Args:
        pathname: file pattern to select

    Returns: Sorted list of files matching pathname

    """
    return sorted(glob.glob(pathname=pathname, recursive=True))


b = hydra_zen.make_custom_builds_fn(populate_full_signature=True)
pb = hydra_zen.make_custom_builds_fn(zen_partial=True, populate_full_signature=True)

run, cfg = aprl.part.register(
    prepare_track,
    base_args=dict(
        input_paths=b(sorted_glob, pathname="data/downloads/ref/**/*.nc"),
        output_path="data/prepared/ref/default.nc",
        preprocess=pb(
            preprocess_track,
            min_lon=-65,
            max_lon=-55,
            min_lat=33,
            max_lat=43,
            min_time="2017-01-01",
            max_time="2017-12-31",
        ),
    ),
)

if __name__ == "__main__":
    run()
