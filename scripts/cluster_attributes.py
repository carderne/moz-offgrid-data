#!/usr/bin/env python

"""Add cluster features."""

from pathlib import Path
import warnings
import sys

import pandas as pd
import geopandas as gpd
import rasterio as rio
from rasterio.features import rasterize
from rasterstats import zonal_stats
from scipy import ndimage

root = Path(__file__).resolve().parents[1]
data = root / "data"
start_file = root / "clusters/clu-man.gpkg"
clu_file = root / "clusters/clu-man-feat.gpkg"


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
        if vector.geometry.type.iloc[0] == "Point":
            # Bufer to convert points to polygons
            # Rasterize doesn't work with points
            vector.geometry = vector.geometry.buffer(0.001)
        elif "String" in vector.geometry.type.iloc[0]:
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
    sites = gpd.read_file(sites)
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
    clu["popd"] = clu.popd.fillna(0).round(0)
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
    clu["travel"] = col.round(2)
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


def cityd(clu):
    raster_like = data / "viirs/viirs70.tif"
    city_file = data / "main_cities/main_cities_filtered.gpkg"
    col = vector_dist(clu, city_file, raster_like)
    col = col.fillna(0) * 100  # deg to km
    col = col.round(0)
    clu["cityd"] = col
    return clu


def admin(clu):
    adm_file = root / "admin" / "adm3.gpkg"
    adm = gpd.read_file(adm_file)
    cols = [
        "adm1",
        "adm1_code",
        "adm2",
        "adm2_code",
        "adm3",
        "adm3_code",
        "prov_elec",
        "prov_pov",
    ]
    adm = adm[cols + ["geometry"]]
    clu = clu.drop(columns=cols, errors="ignore")
    clu = gpd.sjoin(clu, adm, how="left", op="intersects")
    clu["Idx"] = clu.index
    clu = clu.reset_index().drop_duplicates(subset=["Idx"], keep="first")
    clu = clu.drop(columns=["index_right", "Idx"])
    clu = clu.loc[~clu.adm1.isna()]
    return clu


def urban(clu):
    urban_file = data / "ghsl/GHS_SMOD.tif"
    col = raster_stats(clu, urban_file, "majority")
    col = col.fillna(11)
    clu["urban"] = col
    return clu


def lonlat(clu):
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        clu["lon"] = clu.geometry.centroid.x.round(5)
        clu["lat"] = clu.geometry.centroid.y.round(5)
    return clu


def health(clu):
    health_file = data / "health_facilities/mozambique-healthfacilities.shp"
    col = count_sites(clu, health_file)
    clu["health"] = col
    return clu


def schools(clu):
    schools_file = data / "osm/osm-schools.gpkg"
    col = count_sites(clu, schools_file)
    clu["schools"] = col
    return clu


def agri(clu):
    agri_file = data / "ndvi-proc/daily-fft-6bands.tif"
    col = raster_stats(clu, agri_file, "mean")
    col = col.fillna(0).round(0)
    clu["agri"] = col
    return clu


def emissions(clu):
    no2_file = data / "no2/no2_moz.tif"
    col = raster_stats(clu, no2_file, "max")
    col = col.fillna(0).round(3)
    clu["emissions"] = col
    return clu


def clean(clu):
    i32 = "int32"
    f32 = "float32"
    ob = "object"
    clu["fid"] = clu.index
    clu = clu.astype(
        {
            "fid": i32,
            "pop": i32,
            "ntl": f32,
            "travel": f32,
            "gdp": i32,
            "area": f32,
            "lon": f32,
            "lat": f32,
            "grid": f32,
            "adm3": ob,
            "adm2": ob,
            "adm1": ob,
            "adm1_code": ob,
            "adm2_code": ob,
            "adm3_code": ob,
            # "village": ob,
            "urban": i32,
            # "city": ob,
            "cityd": i32,
            "hh": i32,
            "popd": i32,
            "elec": i32,
            "health": i32,
            "schools": i32,
            "prov_elec": i32,
            "prov_pov": i32,
            "agri": i32,
            "emissions": f32,
        }
    )
    return clu


def main(which, scratch=False):
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

    if scratch == "scratch":
        print("Starting from scratch")
        in_file = start_file
    else:
        print("Continuing with -feat file")
        in_file = clu_file

    clu = gpd.read_file(in_file)
    for func in fn_list:
        print("Doing", func.__name__)
        clu = func(clu)

    print("Saving")
    clu.to_file(clu_file)


if __name__ == "__main__":
    which = sys.argv[1]
    scratch = sys.argv[2] if len(sys.argv) > 2 else False
    main(which, scratch)
