import logging
from functools import partial
from pathlib import Path

import aprl.part
import hydra_zen
import ocn_tools._src.geoprocessing.gridding as ocngri
import ocn_tools._src.geoprocessing.validation as ocnval
import xarray as xr

log = logging.getLogger(__name__)


def preprocess_map(ds, ssh_var="ssh"):
    """
    Check presence of time, lat, lon coordinates
    Set units to longitude, latitude, ssh variable
    Set range of longitude between -180 and 180
    Select ssh variable

    Args:
        ds (xarray.Dataset): input dataset
        ssh_var (str): Sea surface height variable

    Returns: validated xarray.Dataset
    """
    log.debug(f"Processing {ds}, using ssh_var {ssh_var}")
    return (
        ds.pipe(ocnval.validate_latlon)
        .pipe(ocnval.validate_time)
        .pipe(partial(ocnval.validate_ssh, variable=ssh_var))[[ssh_var]]
    )


def interp_on_track(
    grid_paths, track_paths, output_path, preprocess_grid=None, preprocess_track=None
):
    """
    Sample a map along an altimeter track

    The input data is read using:
    ```
        xr.open_mfdataset(
            paths, preprocess=preprocess, combine="nested", concat_dim="time"
        )
    ```

    Args:
        grid_paths (str | Path | Sequence): path(s) to netcdf file(s) containing the data to sample
        track_paths (str | Path | Sequence): path(s) to netcdf file(s) containing alongtrack data with a time dimension
        output_path (str): path where to write the output
        preprocess_grid (callable): function to apply to each grid netcdf
        preprocess_track (callable): function to apply to each grid netcdf
    """
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    log.info(f"Starting")
    log.debug(f"Opening {grid_paths=}")
    log.debug(f"Applying preprocessing {preprocess_grid}")
    log.debug(f"{getattr(preprocess_grid, '__doc__', '')}")
    map = xr.open_mfdataset(
        grid_paths, preprocess=preprocess_grid, combine="nested", concat_dim="time"
    )

    log.debug(f"Opening {track_paths=}")
    log.debug(f"Applying preprocessing {preprocess_track}")
    log.debug(f"{getattr(preprocess_track, '__doc__', '')}")
    track = xr.open_mfdataset(
        track_paths, preprocess=preprocess_track, combine="nested", concat_dim="time"
    )

    log.debug(f"Sampling {map} along {track})
    log.debug(f"Writing results to {output_path})
    ocngri.grid_to_coord_based(src_grid_ds=map, tgt_coord_based_ds=track).to_netcdf(
        output_path
    )
    log.info(f"Done")


b = hydra_zen.make_custom_builds_fn(populate_full_signature=True)
pb = hydra_zen.make_custom_builds_fn(zen_partial=True, populate_full_signature=True)
run, cfg = aprl.part.register(
    interp_on_track,
    base_args=dict(
        grid_paths="???",
        track_paths="data/prepared/ref/default.nc",
        output_path="data/prepared/method_output/map_on_track.nc",
        preprocess_grid=pb(preprocess_map, ssh_var="rec_ssh"),
        preprocess_track=None,
    ),
)

if __name__ == "__main__":
    run()
