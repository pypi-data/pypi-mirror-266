# Oceanbench data challenge demo

## Usage:
Requirements:
```
mamba, conda-merge
```

### Usage: Download prepared input data
```
wget -nc https://raw.githubusercontent.com/quentinf00/ocb-dc-ose-2021/envs/dvc-s3.yaml
mamba env create --quiet -n dvc-s3 -f dvc-s3.yaml
dvc get https://github.com/quentinf00/ocb-dc-ose-2021.git datachallenge/data
```

### Usage: Reuse pipelines
```
wget -nc https://raw.githubusercontent.com/quentinf00/ocb-dc-ose-2021/envs/{base,dc}.yaml
conda merge {base,dc}.yaml > env.yaml
mamba env create --quiet -n dc-base -f env.yaml

```

### Usage: Full repro with dvc install
```
git clone https://github.com/quentinf00/ocb-dc-ose-2021.git
conda merge envs/{base,dc,dvc-s3}.yaml > env.yaml
mamba env create --quiet -n dc-dvc -f env.yaml

# login to cmems for data access
copernicusmarine login

cd datachallenge
dvc repro 
```

### Usage: Development (editable)
```
git clone https://github.com/quentinf00/ocb-dc-ose-2021.git
conda merge envs/{base,dc-dev,dvc-s3}.yaml > env.yaml
!mamba env create --quiet -n dc-dev -f env.yaml


# login to cmems for data access
copernicusmarine login

# input data pipeline
ocb-dc_ose_2021-input_data --help
# metrics pipeline
ocb-dc_ose_2021-metrics --help
```

## Modules:

- cmems_get: download data from cmems portal
- prepare_track: filter, merge, compute SSH as sla_filtered + mdt -lwe
- interp_on_track: sample a map on the track geometry
- lambdax: compute effective spatial scale in the track geometry
- mu: compute normalized rmse score

## Pipelines:
- input_data: `ocb-dc_ose_2021-input_data`
- metrics: `ocb-dc_ose_2021-metrics`





