#!/usr/bin/env python

"""
Sanitise clusters GeoJSON before uploading to Mapbox.
Will overwrite file.

Arg 1: input file

e.g. ./clean_clusters.py file.geojson
"""

import sys
from pathlib import Path
import json
import geopandas as gpd

path = Path(sys.argv[1])
gdf = gpd.read_file(path)

# Set GeoPandas dtypes
i32 = "int32"
f32 = "float32"
ob = "object"
gdf = gdf.astype(
    {
        "fid": i32,
        "pop": i32,
        "ntl": f32,
        "travel": f32,
        "gdp": i32,
        "area": f32,
        "lat": f32,
        "lng": f32,
        "grid": f32,
        "adm3": ob,
        "adm2": ob,
        "adm1": ob,
        "village": ob,
        "urban": i32,
        "city": ob,
        "cityd": i32,
        "hh": i32,
        "popd": i32,
        "elec": i32,
        "health": i32,
        "school": i32,
    }
)
gdf.to_file(path, driver="GeoJSON")

# Manually round GeoJSON properties
# (Tried with GeoPandas but wasn't properly respected in GeoJSON export)
rounders = {"ntl": 2, "travel": 1, "grid": 1, "area": 1, "lat": 3, "lng": 3}
with open(path) as f:
    gj = json.load(f)
for i, feat in enumerate(gj["features"]):
    for col, dig in rounders.items():
        gj["features"][i]["properties"][col] = round(feat["properties"][col], dig)
with open(path, "w") as f:
    json.dump(gj, f)

# To get it back to one feature per line (json library messes this up
gpd.read_file(path).to_file(path, driver="GeoJSON")
