#!/usr/bin/env python

"""Make clusters using manual approach."""

from pathlib import Path
import os
import warnings

import geopandas as gpd
import rasterio as rio
from rasterio.features import shapes
from shapely import geometry

root = outfile = Path(__file__).parents[1]
hrsl_in = root / "data/hrsl/hrsl_moz_pop_deflate.tif"
hrsl_prep = root / "data/hrsl/hrsl_prep.tif"
clu_out = root / "clusters/clu-man.gpkg"

print("Resample")
res = 0.001
min_val = 1

command = (
    f"gdal_translate -ot Byte -a_nodata none {hrsl_in} /vsistdout/ | "
    f"gdalwarp -tr {res} {res} -r average /vsistdin/ /vsistdout/ | "
    f"gdal_calc.py -A /vsistdin/ --outfile={hrsl_prep} --calc='A>{min_val}' "
    f"--NoDataValue=0 --overwrite > /dev/null"
)
os.system(command)

print("Polygonize")
with rio.open(hrsl_prep) as ds:
    hrsl = ds.read(1)
    crs = ds.crs
    aff = ds.transform
polys = shapes(source=hrsl, mask=hrsl == 1, connectivity=8, transform=aff)
clu = gpd.GeoDataFrame([{"geometry": geometry.shape(p[0])} for p in polys], crs=crs)

print("Filter on area")
clu.geometry = clu.geometry.buffer(0)
clu["Area"] = clu.to_crs("epsg:5629").geometry.area
clu = clu.loc[clu.Area > 13000]

print("Buffer, dissolve, explode")
with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    clu.geometry = clu.geometry.buffer(0.005)
clu["Same"] = 0
clu = clu.dissolve(by="Same")
clu = clu.explode()

print("Clean and save")
clu = clu[["geometry"]]
clu.to_file(clu_out, driver="GPKG")
