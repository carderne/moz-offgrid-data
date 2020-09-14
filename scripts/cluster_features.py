#!/usr/bin/env python

"""Add cluster features."""

from pathlib import Path
import warnings

import pandas as pd
import geopandas as gpd
import rasterio as rio
from rasterio.features import rasterize
from rasterstats import zonal_stats
from scipy import ndimage
import click

root = Path(__file__).resolve().parents[1]
data = root / "data"


def raster_stats(clu, raster, op):
    crs = rio.open(raster).crs
    proj = clu.to_crs(crs)
    nodata = rio.open(raster).nodata
    nodata = nodata if nodata else -999
    stats = zonal_stats(proj, raster, stats=op, nodata=nodata)
    return pd.Series([x[op] for x in stats])


def vector_dist(clu, vector, raster_like):
    with rio.open(raster_like) as ds:
        crs = ds.crs
        aff = ds.transform
        shape = ds.shape
    clu = clu.to_crs(crs=crs)
    vector = gpd.read_file(vector)
    vector = vector.to_crs(crs=crs)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        vector = vector.loc[vector["geometry"].length > 0]
    grid_raster = rasterize(
        vector.geometry,
        out_shape=shape,
        fill=1,
        default_value=0,
        all_touched=True,
        transform=aff,
    )
    dist_raster = ndimage.distance_transform_edt(grid_raster) * aff[0]
    dists = zonal_stats(
        vectors=clu, raster=dist_raster, affine=aff, stats="min", nodata=-999
    )
    return pd.Series([x["min"] for x in dists])


def count_sites(clu, sites):
    col = []
    for i, poly in clu.iterrows():
        num_sites = 0
        for j, pt in sites.iterrows():
            if poly.geometry.contains(pt.geometry):
                num_sites += 1
                sites = sites.drop([j])
        col.append(num_sites)
    return pd.Series(col)


def pop(clu):
    pop_file = data / "hrsl/hrsl_moz_pop_deflate.tif"
    col = raster_stats(clu, pop_file, op="sum")
    col = col.fillna(0).round(0)
    col.loc[col < 0] = 0
    clu["pop"] = col
    clu["hh"] = clu["pop"] / 5
    return clu


def area(clu):
    col = clu.to_crs("epsg:32633").geometry.area / 1e6
    col = col.fillna(0).round(3)
    clu["area"] = col
    clu["popd"] = clu["pop"] / clu["area"]
    return clu


def ntl(clu):
    ntl_file = data / "viirs/viirs70.tif"
    col = raster_stats(clu, ntl_file, op="max")
    col = col.fillna(0).round(2)
    col.loc[col < 0] = 0
    clu["ntl"] = col
    return clu


def travel(clu):
    travel_file = data / "accessibility/acc_50k.tif"
    col = raster_stats(clu, travel_file, op="median")
    col = col.fillna(col.median()).round(0) / 60
    clu["travel"] = col
    return clu


def gdp(clu):
    gdp_file = data / "gdp/GDP.tif"
    col = raster_stats(clu, gdp_file, op="sum")
    col = col.fillna(col.median()).round(0) / 1000
    clu["gdp"] = col
    max_gdp = clu.sort_values(by="pop", ascending=False).iloc[0]["gdp"]
    col.loc[col > max_gdp] = max_gdp
    clu["gdp"] = col
    clu["gdp"] = clu["gdp"] / clu["pop"]
    clu["gdp"] = clu["gdp"].round(3)
    return clu


def grid(clu):
    raster_like = data / "viirs/viirs70.tif"
    grid_file = data / "grid/gridfinder_moz.gpkg"
    col = vector_dist(clu, grid_file, raster_like)
    col = col.fillna(0) * 100  # deg to km
    col = col.round(2)
    clu["grid"] = col
    clu["elec"] = 0
    clu.loc[clu["grid"] <= 1, "elec"] = 1
    return clu


def admin(clu):
    adm_file = data / "moz_adm/moz_admbnda_adm3_ine_20190607.shp"
    adm = gpd.read_file(adm_file)
    adm = adm[["ADM1_PT", "ADM2_PT", "ADM3_PT", "geometry"]]
    adm.columns = ["adm1", "adm2", "adm3", "geometry"]
    clu = gpd.sjoin(clu, adm, how="left", op="intersects")
    clu = clu.drop(columns=["index_right"])
    return clu


def urban(clu):
    urban_file = data / "ghsl/GHS_SMOD.tif"
    col = raster_stats(clu, urban_file, "majority")
    col.fillna(11)
    clu["urban"] = col
    return clu


def lonlat(clu):
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        clu["lon"] = clu.geometry.centroid.x
        clu["lat"] = clu.geometry.centroid.y
    return clu


def health(clu):
    health_file = data / "health_facilities/mozambique-healthfacilities.shp"
    health = gpd.read_file(health_file)
    col = count_sites(clu, health)
    clu["health"] = col
    return clu


def schools(clu):
    schools_file = data / "osm/osm-schools.gpkg"
    schools = gpd.read_file(schools_file)
    col = count_sites(clu, schools)
    clu["schools"] = col
    return clu


def agri(clu):
    agri_file = data / "ndvi-proc/daily-fft-6bands.tif"
    col = raster_stats(clu, agri_file, "mean")
    col = col.fillna(0)
    clu["agri"] = col
    return clu


def emissions(clu):
    no2_file = data / "no2/no2_moz.tif"
    col = raster_stats(clu, no2_file, "max")
    col = col.fillna(0)
    clu["emissions"] = col
    return clu


@click.command()
@click.argument("which")
def main(which):
    clu_file = root / "clusters/clu-man-feat.gpkg"
    clu = gpd.read_file(clu_file)

    if which == "all":
        fn_list = [
            pop,
            area,
            ntl,
            travel,
            gdp,
            grid,
            admin,
            urban,
            lonlat,
            health,
            schools,
            agri,
            emissions,
        ]
    else:
        which = which.split(",")
        fn_list = [globals()[w] for w in which]

    for func in fn_list:
        print("Doing", func.__name__)
        clu = func(clu)
    clu.to_file(clu_file)


if __name__ == "__main__":
    main()
