# Core listings (Listings 1–10)

Minimal, self-contained building blocks referenced in the paper. Each runs on open
data and is written to be interface-compatible with a production replacement (e.g.
the STA/LTA picker in `02_phase_pick.py` can be swapped for a learned picker, and the
illustrative GMM in `03_gmpe_field.py` for a calibrated OpenQuake model).

Run any listing directly, e.g.:

```bash
python 01_fdsn_ingest.py
```

Dependencies: see `../requirements.txt` / `../environment.yml`.
