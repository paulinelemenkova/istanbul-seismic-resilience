"""Scenario ground-motion field (PGA) on a grid over Istanbul from a
ground-motion model (GMM). A compact Boore-Atkinson-style form is used;
replace `gmm_pga` with an OpenQuake GMPE for production."""
import numpy as np

def gmm_pga(mw, r_rup, vs30):
    """Median PGA in g (illustrative coefficients; swap for a calibrated GMM)."""
    ln_pga = (2.30 + 0.55 * (mw - 6.0) - 1.20 * np.log(r_rup + 8.0)
              - 0.40 * np.log(vs30 / 760.0))
    return np.exp(ln_pga)

# grid over the metropolitan region
lon = np.linspace(28.4, 29.95, 160)
lat = np.linspace(40.80, 41.35, 90)
LON, LAT = np.meshgrid(lon, lat)

epi = (40.86, 28.30)                    # central Marmara epicentre
deg2km = 111.0
r = np.hypot((LAT - epi[0]) * deg2km,
             (LON - epi[1]) * deg2km * np.cos(np.radians(epi[0])))
r_rup = np.sqrt(r**2 + 15.0**2)         # add hypocentral depth
vs30 = np.full_like(LON, 400.0)         # replace with a Vs30 raster
pga = gmm_pga(mw=7.4, r_rup=r_rup, vs30=vs30)

np.savez("shakefield.npz", lon=lon, lat=lat, pga=pga)
print(f"PGA field: min={pga.min():.3f} g, max={pga.max():.3f} g")
