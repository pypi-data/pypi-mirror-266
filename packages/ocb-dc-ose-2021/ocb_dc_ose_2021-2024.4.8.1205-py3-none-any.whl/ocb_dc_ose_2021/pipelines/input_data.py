import aprl.appareil
import aprl.utils

import ocb_dc_ose_2021.mods.cmems_get as cmems_get
import ocb_dc_ose_2021.mods.prepare_track as prepare_track

cmems_get_cfg = aprl.utils.make_partial(cmems_get.cfg)
dataset_id_cfg = cmems_get.cfg.dataset_id
regex_cfg = cmems_get.cfg.regex
_01_dl_track = cmems_get_cfg(
    dataset_id=dataset_id_cfg(sat="${....params.sat}"),
    regex=regex_cfg(
        min_time="${....params.min_time}",
        max_time="${....params.max_time}",
    ),
    output_directory="data/downloads/input/${...params.sat}",
)

prepare_track_cfg = aprl.utils.make_partial(prepare_track.cfg)
input_paths_cfg = prepare_track.cfg.input_paths
preprocess_cfg = prepare_track.cfg.preprocess
_02_prepare_track = prepare_track_cfg(
    input_paths=input_paths_cfg(
        pathname="${..._01_dl_track.output_directory}/**/*.nc",
    ),
    preprocess=preprocess_cfg(
        min_lon="${....params.min_lon}",
        max_lon="${....params.max_lon}",
        min_lat="${....params.min_lat}",
        max_lat="${....params.max_lat}",
        min_time="${....params.min_time}",
        max_time="${....params.max_time}",
    ),
    output_path="data/prepared/input/${...params.sat}.nc",
)
stages = {
    "_01_dl_track": _01_dl_track,
    "_02_prepare_track": _02_prepare_track,
}


params = dict(
    sat="???",
    sat_list=["alg", "h2ag", "j2g", "j2n", "j3", "s3a"],
    min_time="2016-12-01",
    max_time="2018-02-01",
    min_lon=-66.0,
    max_lon=-54.0,
    min_lat=32.0,
    max_lat=44.0,
)


sweep = {
    "params.sat": dict(_target_="builtins.str.join", _args_=[",", "${params.sat_list}"])
}

help_msg = """
Overview:
    Download and prepare data for SSH Mapping (requires CMEMS credentials for download)
    The ssh is computed as "sla_filtered + mdt - lwe"

Basic CLI Usage:
  *  params.sat=<sat_id> to download a prepare a specific satellite

  *  --multirun: Execute the pipeline for each sat in sat_list

  *  params.(min|max)_(lon|lat|time)=<bound> to change the bound

  *  `-cd conf overrides=my_conf` to load config from conf/aprl/overrides/my_conf.yaml

Params:
    sat (str): altimeter id to download (place holder for multirun)
    sat_list (str): list of satellite to download
    min_time: start of the temporal domain
    max_time: end of the temporal domain
    min_lon: lower longitudinal bound
    max_lon: upper longitudinal bound
    min_lat: upper meridional bound
    max_lat: upper meridional bound
"""
pipeline, recipe, params = aprl.appareil.register(
    "dc_ose_2021_inference_data",
    parts=stages,
    params=params,
    default_sweep=sweep,
    help_msg=help_msg,
)
