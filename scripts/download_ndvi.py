#!/usr/bin/env python

"""
Download Sentinel-2 NDVI mosaics.


Ref: https://gis.stackexchange.com/a/312566
"""

import ee
from geetools.batch import Export

# ee.Authenticate()
ee.Initialize()

loc = "moz"

# xmin, ymin, xmax, ymax
roi = ee.Geometry.Rectangle([28, -28, 43, -9])  # Mozambique

start = ee.Date.fromYMD(2019, 1, 1)
months = ee.List.sequence(0, 11)
startDates = months.map(lambda d: start.advance(d, "month"))


def get_ndvi(img):
    return img.normalizedDifference(["B8", "B4"]).rename("NDVI")


def monthmap(m):
    start = ee.Date(m)
    end = start.advance(1, "month")
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
