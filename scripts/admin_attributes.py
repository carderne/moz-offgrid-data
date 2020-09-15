#!/usr/bin/env python

"""Add admin layer attributes."""

from pathlib import Path

import geopandas as gpd

from cluster_attributes import raster_stats, count_sites

root = Path(__file__).resolve().parents[1]
data = root / "data"
layers = {
    "adm1": "admin/moz_admbnda_adm1_ine_20190607_ELECPOV.shp",
    "adm2": "admin/moz_admbnda_adm2_ine_20190607.shp",
    "adm3": "admin/moz_admbnda_adm3_ine_20190607.shp",
}


def pop(adm):
    pop_file = data / "hrsl/hrsl_moz_pop_deflate.tif"
    col = raster_stats(adm, pop_file, "sum")
    col = col.fillna(0).round(0)
    col.loc[col < 0] = 0
    adm["pop"] = col
    adm["hh"] = adm["pop"] / 5
    return adm


def area(adm):
    col = adm.to_crs("epsg:32633").geometry.area / 1e6
    col = col.fillna(0).round(4)
    adm["area"] = col
    return adm


def health_schools(adm):
    health_file = data / "health_facilities/mozambique-healthfacilities.shp"
    schools_file = data / "osm/osm-schools.gpkg"
    adm["health"] = count_sites(adm, health_file)
    adm["schools"] = count_sites(adm, schools_file)
    return adm


def poverty_elec(adm):
    adm1_file = data / layers["adm1"]
    adm1 = gpd.read_file(adm1_file)
    adm1 = adm1[["ADM1_PCODE", "prov_elec", "prov_pov"]]
    adm = adm.merge(adm1, how="left", left_on="adm1_code", right_on="ADM1_PCODE")
    adm = adm.drop(columns=["ADM1_PCODE"], errors="ignore")
    return adm


def do_layer(layer):
    print("Doing layer", layer)
    adm_file = data / layers[layer]
    adm = gpd.read_file(adm_file)
    cols = {
        "geometry": "geometry",
        "ADM1_PT": "adm1",
        "ADM1_PCODE": "adm1_code",
    }
    if layer == "adm1":
        cols["prov_elec"] = "prov_elec"
        cols["prov_pov"] = "prov_pov"
    if layer in ["adm2", "adm3"]:
        cols["ADM2_PT"] = "adm2"
        cols["ADM2_PCODE"] = "adm2_code"
    if layer == "adm3":
        cols["ADM3_PT"] = "adm3"
        cols["ADM3_PCODE"] = "adm3_code"
    adm = adm[cols.keys()]
    adm.columns = cols.values()

    fn_list = [pop, area, health_schools]
    if layer in ["adm2", "adm3"]:
        fn_list.append(poverty_elec)
    for func in fn_list:
        print("Doing", func.__name__)
        adm = func(adm)

    adm.to_file(root / f"admin/{layer}.gpkg", driver="GPKG")


def main():
    for layer in layers:
        do_layer(layer)


if __name__ == "__main__":
    main()
