#!/usr/bin/env python

from pathlib import Path
from pprint import pprint

import geopandas as gpd


aoi = gpd.read_file("../data/gadm/gadm36_MOZ.gpkg", layer="gadm36_MOZ_1")
names = aoi["NAME_1"].to_dict()
names = {k: n.replace(" ", "_") for k, n in names.items()}

root = Path("../data/hrsl/sep_prov/")
files = sorted([f for f in root.iterdir() if f.suffix == ".gpkg"])

gdf = None
for f in files:
    num = int(f.stem.split("_")[1])
    name = names[num]
    if gdf is None:
        gdf = gpd.read_file(f)
        gdf = gdf.assign(province=name)
    else:
        new = gpd.read_file(f)
        new = new.assign(province=name)
        gdf = gdf.append(new)
gdf = gdf.reset_index().drop(columns=["index"])

gdf.to_file("../data/hrsl/clusters.gpkg", driver="GPKG")
