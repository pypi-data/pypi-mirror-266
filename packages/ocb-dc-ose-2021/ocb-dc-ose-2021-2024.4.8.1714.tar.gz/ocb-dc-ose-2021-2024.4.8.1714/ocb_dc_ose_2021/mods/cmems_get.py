import aprl.part
import aprl.utils
import copernicusmarine
import hydra_zen
import pandas as pd

aprl.utils.register_resolvers()


def month_regex_from_date(min_time: str = "2017-01-01", max_time: str = "2017-12-31"):
    """
    Constructs a regex matching any month %Y%m from time period

    Args:
        min_time (str): start of the period
        max_time (str): end of the period

    Returns: Regex string

    """
    dates = list(set(pd.date_range(min_time, max_time).strftime("%Y%m")))
    return "(" + "|".join(dates) + ")"


def duacs_l3(sat: str = "c2"):
    """
    Construct from altimeter id the cmems dataset_id for DUACS L3 reprocessed altimetry tracks:
        "cmems_obs-sl_glo_phy-ssh_my_{sat}-l3-duacs_PT1S"
    Args:
        sat (str): altimeter id

    Returns: dataset_id
    """
    return f"cmems_obs-sl_glo_phy-ssh_my_{sat}-l3-duacs_PT1S"


b = hydra_zen.make_custom_builds_fn(populate_full_signature=True)

run, cfg = aprl.part.register(
    copernicusmarine.get,
    base_args=dict(
        dataset_id=b(duacs_l3),
        regex=b(month_regex_from_date),
        output_directory="${aprl-mkp:data/downloads/ref}",
        force_download=True,
        overwrite_output_data=True,
    ),
    builds_kws=dict(populate_full_signature=False),
    zen_kws=dict(exclude="download_file_list"),
)

if __name__ == "__main__":
    run()
