import json
import logging
import operator
from functools import partial
from pathlib import Path
from typing import Callable, Sequence

import aprl.part
import hydra_zen
import numpy as np
import xarray as xr
from ocn_tools._src.metrics.power_spectrum import psd_welch_score
from ocn_tools._src.preprocessing.alongtrack import select_track_segments

log = logging.getLogger(__name__)


def min_intersect(ds, threshold=0.5, dvar="score", dim="wavenumber"):
    """
    Find the first (minimum) coordinates at which a variable passes a threshold

    Args:
        ds (xarray.Dataset): 1 netcdf
        threshold (float): threshold
        dvar (str): 1D dataset variable to pass the threshold
        dim (str): dataset dimension on which to select the intersect

    Returns: dim value linearly interpolated at which dvar is threshold

    """
    max_wnx = ds.isel(**{dim: ds[dvar] <= threshold})[dim].min().item()
    log.debug(
        f"not considering above {max_wnx:.2f}, score: {ds.sel(**{dim: max_wnx})[dvar]:.2f}"
    )
    intersect = (
        ds.isel(**{dim: ds[dim] <= max_wnx})
        .swap_dims(**{dim: dvar})
        .interp({dvar: threshold})[dim]
        .item()
    )
    return intersect


def lambdax(
    study_paths: str | Sequence[str] = "data/prepared/method_output/map_on_track.nc",
    ref_paths: str | Sequence[str] = "data/prepared/ref/default.nc",
    delta_t: float = 0.9434,
    velocity: float = 6.77,
    length_scale: float = 1000,
    segment_overlapping: float = 0.25,
    output_lambdax_path: str = "data/metrics/lambdax.json",
    output_psd_path: str = "data/method_outputs/psd_score.nc",
    preprocess_ref: Callable[xr.Dataset, xr.DataArray] = operator.attrgetter("ssh"),
    preprocess_study: Callable[xr.Dataset, xr.DataArray] = operator.attrgetter("ssh"),
):
    """
    Compute the PSD of the reference signal and the error and calulate the first wavelength $lambda_x$ at which
    $$ 1 - \frac{PSD_{err}(lambda_x)}{PSD_{ref}(lambda_x)} = 0.5 $$

    Args:
        output_lambdax_path (str): Path where to write the json with the score value
        output_psd_path (str): Path where to write the netcdf with the PSD
        preprocess_ref (xr.Dataset -> xr.DataArray): Preprocessing that returns the reference DataArray
        preprocess_study (xr.Dataset -> xr.DataArray): Preprocessing that returns the analysis DataArray
        study_paths (str | Path | Sequence): path(s) to netcdf file(s) containing the analysis dataset
        ref_paths (str | Path | Sequence): path(s) to netcdf file(s) containing the reference dataset
        delta_t (float): Sampling of the reference altimeter
        velocity (float): Speed of the reference altimeter
        length_scale (float): Segment length
        segment_overlapping (float): overlapping proportion between two segments
    """
    log.info("Starting")

    log.debug(f"Opening {study_paths=}")
    log.debug(f"Applying preprocessing {preprocess_study}")
    log.debug(f"{getattr(preprocess_study, '__doc__', '')}")
    study_da = xr.open_mfdataset(
        study_paths, preprocess=preprocess_study, combine="nested", concat_dim="time"
    )

    log.debug(f"Opening {ref_paths=}")
    log.debug(f"Applying preprocessing {preprocess_ref}")
    log.debug(f"{getattr(preprocess_ref, '__doc__', '')}")
    ref_da = xr.open_mfdataset(
        ref_paths, preprocess=preprocess_ref, combine="nested", concat_dim="time"
    )

    eval_ds = xr.Dataset(dict(study=study_da, ref=ref_da)).load()
    eval_ds = eval_ds.where(eval_ds.ref.pipe(np.isfinite), drop=True).interpolate_na(
        dim="time", method="nearest"
    )
    delta_x = velocity * delta_t

    partial_track_fn = partial(
        select_track_segments,
        variable_interp="study",
        variable="ref",
        velocity=velocity,
        delta_t=delta_t,
        length_scale=length_scale,
        segment_overlapping=segment_overlapping,
    )

    partial_score_fn = partial(
        psd_welch_score,
        variable="study",
        variable_ref="ref",
        delta_x=delta_x,
        nperseg=length_scale // delta_x,
    )

    log.debug("Computing track segments")
    segments = eval_ds.pipe(partial_track_fn)
    log.debug(f"{segments=}")
    ds, _ = segments.pipe(partial_score_fn)
    log.debug("Computing the PSD (welch score)")
    log.debug(f"PSD ds {ds}")

    ## Robust lambda_x computation when small wavelength reach score > 0.5
    lambda_x = 1 / min_intersect(ds)
    log.info(f"Effective scale resolved (interpolated at score 0.5) {lambda_x:.2f}")

    Path(output_lambdax_path).parent.mkdir(parents=True, exist_ok=True)
    Path(output_psd_path).parent.mkdir(parents=True, exist_ok=True)
    log.debug(f"Writing PSD ds to {output_psd_path}")
    ds.to_netcdf(output_psd_path)
    log.debug(f"Lambda score to {output_lambdax_path}")
    with open(Path(output_lambdax_path), "w") as f:
        json.dump({"$\lambda_x$": lambda_x}, f)
    log.info("Done")


b = hydra_zen.make_custom_builds_fn()
run, cfg = aprl.part.register(
    lambdax,
    base_args=dict(
        preprocess_ref=b(aprl.utils.kw2a, fn=operator.itemgetter, ssh_var="ssh"),
        preprocess_study=b(aprl.utils.kw2a, fn=operator.itemgetter, ssh_var="rec_ssh"),
    ),
)

if __name__ == "__main__":
    run()
