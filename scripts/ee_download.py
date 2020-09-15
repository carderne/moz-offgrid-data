#!/usr/bin/env python

"""
Download satellite imageryvia Google Earth Engine
"""

import sys

import ee
from geetools.batch import Export

# ee.Authenticate()
ee.Initialize()

loc = "moz"
# xmin, ymin, xmax, ymax
roi = ee.Geometry.Rectangle([28, -28, 43, -9])  # Mozambique


def viirs():
    """
    VIIRS NTL imagery
    """

    viirs = "NOAA/VIIRS/DNB/MONTHLY_V1/VCMCFG"
    date_sta = "2019-01-01"
    date_end = "2020-06-04"

    ic = ee.ImageCollection(viirs).filterBounds(roi).filterDate(date_sta, date_end)
    Export.imagecollection.toDrive(
        collection=ic,
        folder=f"ntl_{loc}",
        namePattern=f"{loc}_{{system_date}}",
        region=roi,
        scale=400,
        dataType="float",
        datePattern="yyyyMMdd",
        skipEmptyTiles=True,
        verbose=True,
    )


def no2():
    """
    Sentinel S5P NO2 data
    Ref: https://gis.stackexchange.com/a/312566
    """

    no2 = "COPERNICUS/S5P/NRTI/L3_NO2"
    bands = ["tropospheric_NO2_column_number_density"]

    date_sta = "2019-01-01"
    date_end = "2020-01-01"

    img = (
        ee.ImageCollection(no2)
        .filterBounds(roi)
        .filterDate(date_sta, date_end)
        .select(bands)
        .max()
    )

    ee.batch.Export.image.toDrive(
        image=img,
        description=f"{loc}_no2",
        scale=1000,
        region=roi,
        folder=f"{loc}_no2",
    ).start()


def ndvi():
    """
    Download Sentinel-2 NDVI mosaics.
    Ref: https://gis.stackexchange.com/a/312566
    """

    start = ee.Date.fromYMD(2019, 1, 1)
    weeks = ee.List.sequence(0, 51)
    startDates = weeks.map(lambda d: start.advance(d, "week"))

    def get_ndvi(img):
        return img.normalizedDifference(["B8", "B4"]).rename("NDVI")

    def monthmap(m):
        start = ee.Date(m)
        end = start.advance(1, "week")
        return (
            ee.ImageCollection("COPERNICUS/S2_SR")
            .filterBounds(roi)
            .filterDate(ee.DateRange(start, end))
            .map(get_ndvi)
            .max()
            .set("system_date", start.format("yyyyMMdd"))
        )

    mt = ee.ImageCollection(startDates.map(monthmap))
    Export.imagecollection.toDrive(
        collection=mt,
        folder=f"{loc}_ndvi",
        namePattern=f"{loc}_ndvi_{{system_date}}",
        region=roi,
        scale=300,
        dataType="float",
        datePattern="yyyyMMdd",
        skipEmptyTiles=True,
        verbose=True,
    )


def modis():
    """
    Download MODIS daily NDVI images
    https://developers.google.com/earth-engine/datasets/catalog/MODIS_MOD09GA_006_NDVI
    """

    modis = "MODIS/MOD09GA_006_NDVI"
    date_sta = "2019-01-01"
    date_end = "2020-01-01"
    ic = ee.ImageCollection(modis).filterBounds(roi).filterDate(date_sta, date_end)

    Export.imagecollection.toDrive(
        collection=ic,
        folder=f"{loc}_modisndvi",
        namePattern=f"{loc}_modisndvi_{{system_date}}",
        region=roi,
        scale=1000,
        dataType="float",
        datePattern="yyyyMMdd",
        skipEmptyTiles=True,
        verbose=True,
    )


def main(which):
    globals()[which]()


if __name__ == "__main__":
    which = sys.argv[1]
    main(which)
