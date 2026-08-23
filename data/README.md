# Data sources

All datasets used in this study are open-access. Large grids are **not** bundled in
this repository; download them once and point the `DATA_ROOT` environment variable at
the folder that contains them (the GMT scripts read `"${DATA_ROOT:-$HOME/DATA}"`).

## Open sources and links

| Dataset | Provider | Link |
|---------|----------|------|
| Earthquake catalogues & strong motion | AFAD (TADAS) | https://tadas.afad.gov.tr |
| Waveforms & catalogues | KOERI / Boğaziçi Univ. | http://www.koeri.boun.edu.tr |
| Continuous waveforms (FDSN) | FDSN web services | https://www.fdsn.org |
| Moment tensors (focal mechanisms) | Global CMT Project | https://www.globalcmt.org/CMTsearch.html |
| Bathymetry | GEBCO 2026 | https://www.gebco.net |
| Topography (30 m DEM) | Copernicus GLO-30 | https://dataspace.copernicus.eu — or https://portal.opentopography.org |
| Strong-Motion Database of Türkiye (SMD-TR) | AFAD (PRJ-3950) | https://tadas.afad.gov.tr |

## Bundled files

### `inputs/` — small vector/point inputs (used by the map scripts)
Copied into `figures/` next to the GMT scripts, which read them by name:
`cities.txt`, `cities_L.txt` (settlement labels), `naf.txt` (approximate North
Anatolian Fault trace — replace with Emre et al. 2018 for publication),
`marmara_cmt.txt` (focal-mechanism table for the beachballs), `eq_plot.txt`
(seismicity points: lon, lat, depth, magnitude).

### `derived/SMD_TR_flatfile.csv`
Ground-motion flatfile (15,232 records; columns `record, Mw, Rjb, Vs30, PGA_g`)
produced by `figures/build_smdtr_flatfile.py` from the AFAD SMD-TR database. It is
included so that `fig07_gm_validation.py` runs without re-downloading SMD-TR. To
regenerate it, set `SMDTR_DIR` to your local SMD-TR folder and run the builder.

## Expected local layout under `DATA_ROOT`
The cartography scripts expect (adjust names in the scripts if yours differ):

```
$DATA_ROOT/
├── GEBCO_2026.nc                     # GEBCO bathymetry grid
├── topo15.grd                        # SRTM15+ (sea + fallback land)
└── TURKEY/
    ├── COP30_marmara_ext.tif         # Copernicus GLO-30 land DEM (see download_cop30.sh)
    ├── IEB_Marmara.csv               # instrumental catalogue (fig06)
    └── IEB_3000_Marmara.csv          # catalogue incl. large historical events (fig05)
```

Download the Copernicus GLO-30 tile with `download_cop30.sh` (insert your
OpenTopography API key).
