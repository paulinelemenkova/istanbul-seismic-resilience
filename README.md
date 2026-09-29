# Reference Architecture and Python-Based Workflow for Istanbul Seismic Resilience

Open, reproducible workflow

This repository contains the runnable building blocks of a six-layer
AI–EEW–Digital-Twin reference architecture and the scripts that generate every
figure in the paper from **open-access** data (earthquake catalogues, strong-motion
records, moment tensors, bathymetry and topography). It is a design-and-workflow
release, not an operational deployment: reproducible code, proposed design, and a
future operational vision are kept distinct.

## Repository structure

```
istanbul-seismic-resilience/
├── listings/          10 core building blocks (Listings 1–10 in the paper)
├── figures/           scripts that produce Figs. 1–7 (+ GMT support files)
├── data/
│   ├── inputs/        small vector/point inputs for the maps
│   ├── derived/       SMD_TR_flatfile.csv (15,232 records; regenerable)
│   ├── download_cop30.sh
│   └── README.md      data sources, links and how to obtain each dataset
├── output/            generated figures are written here
├── requirements.txt   pip dependencies
├── environment.yml    conda environment (includes OpenQuake + GMT)
├── CITATION.cff
└── LICENSE
```

## Listings (`listings/`)

| # | File | Purpose |
|---|------|---------|
| 1 | `01_fdsn_ingest.py` | Open FDSN waveform ingestion (KOERI/AFAD) via ObsPy |
| 2 | `02_phase_pick.py` | Characteristic-function P-wave detection (STA/LTA baseline) |
| 3 | `03_gmpe_field.py` | Scenario ground-motion (PGA) field from a GMM |
| 4 | `04_fragility.py` | Lognormal fragility damage-state exceedance |
| 5 | `05_cascade.py` | Infrastructure-graph cascading-failure analysis |
| 6 | `06_hospital.py` | Hospital-accessibility shortest-path on the road graph |
| 7 | `07_insar_gnss.py` | InSAR/GNSS deformation feature generation |
| 8 | `08_dt_state.py` | Digital-Twin state representation |
| 9 | `09_stream_assim.py` | Streaming data assimilation |
| 10 | `10_forecast.py` | Ensemble occurrence forecast with MC-dropout uncertainty |

## Figures (`figures/`)

| Fig. | Script | Output |
|------|--------|--------|
| 1 | `fig01_architecture.py` | Six-layer reference architecture |
| 2 | `fig02_workflow.py` | AI workflow + EEW latency budget |
| 3 | `fig03_eew_digital_twin.py` | Coupled EEW–digital-twin architecture |
| 4 | `fig04_study_area.sh` | Study-area map (GMT) |
| 5 | `fig05_marmara_seismotectonic.sh` | Seismotectonic map (GMT) |
| 6 | `fig06_seismicity_stats.py` | Gutenberg–Richter catalogue statistics |
| 7 | `fig07_gm_validation.py` | Measured-vs-predicted ground motion (PGA/MMI) |

`build_smdtr_flatfile.py` assembles `data/derived/SMD_TR_flatfile.csv` from the AFAD
SMD-TR database and feeds `fig07_gm_validation.py`.

## Quick start

```bash
# 1. Create the environment (conda-forge ships OpenQuake and GMT as binaries)
conda env create -f environment.yml
conda activate istanbul-seismic

# 2. Point DATA_ROOT at your local copy of the large open grids (see data/README.md)
export DATA_ROOT=$HOME/DATA

# 3. Reproduce a figure
cd figures
python fig06_seismicity_stats.py           # Gutenberg–Richter (needs a catalogue)
python fig07_gm_validation.py              # ground-motion validation (uses derived flatfile)
bash   fig05_marmara_seismotectonic.sh     # seismotectonic map (needs GMT + grids)
```

Figures are written to `../output/`. Python figure scripts need only the
scientific-Python stack; the two `.sh` cartography scripts additionally need
[GMT 6](https://www.generic-mapping-tools.org/). `fig07_gm_validation.py` requires
OpenQuake for the calibrated ground-motion model (see below).

## Ground-motion model (Fig. 7)

`fig07_gm_validation.py` predicts PGA with a published GMM through OpenQuake
(`GMM = "AkkarEtAlRjb2014"` by default; alternatives `KaleEtAl2015Turkey`,
`BooreEtAl2014`). Install OpenQuake from conda-forge (already in `environment.yml`)
rather than pip, to avoid GDAL build issues:

```bash
conda install -c conda-forge openquake.engine
```

## Data

All inputs are open-access; see [`data/README.md`](data/README.md) for sources,
links and the expected local layout under `DATA_ROOT`.

## Citation

If you use this workflow, please cite the paper and this repository (see
`CITATION.cff`). Archived release: **Zenodo DOI 10.5281/zenodo.22070488**.

## License

Code is released under the MIT License (`LICENSE`). Input datasets remain under the
licences of their respective providers (AFAD, KOERI, Global CMT, GEBCO, Copernicus).
