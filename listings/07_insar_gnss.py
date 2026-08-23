"""Ingest Sentinel-1 InSAR line-of-sight rates and GNSS station velocities
into one GeoDataFrame of surface deformation for the twin's dynamic layer."""
import numpy as np
import pandas as pd
import geopandas as gpd

# InSAR persistent-scatterer LOS velocities (mm/yr) as point samples
ps = pd.DataFrame({
    "lon": np.random.uniform(28.6, 29.4, 500),
    "lat": np.random.uniform(40.9, 41.1, 500),
    "los_mm_yr": np.random.normal(-2.0, 3.0, 500),
    "source": "S1_InSAR",
})
# continuous GNSS station velocities
gnss = pd.DataFrame({
    "lon": [28.98, 29.09, 29.36],
    "lat": [41.10, 40.98, 41.02],
    "los_mm_yr": [-1.4, -2.8, -0.9],
    "source": "GNSS",
})
df = pd.concat([ps, gnss], ignore_index=True)
gdf = gpd.GeoDataFrame(
    df, geometry=gpd.points_from_xy(df.lon, df.lat), crs="EPSG:4326")

# flag anomalous subsidence for prioritised inspection
gdf["subsiding"] = gdf.los_mm_yr < gdf.los_mm_yr.quantile(0.05)
gdf.to_file("deformation.gpkg", driver="GPKG")
print(f"{len(gdf)} points; {gdf.subsiding.sum()} flagged as subsiding")
