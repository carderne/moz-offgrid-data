#!/usr/bin/env python

"""
Download Sentinel-5P NO2 data


Ref: https://gis.stackexchange.com/a/312566
"""

import ee

# ee.Authenticate()
ee.Initialize()

no2 = "COPERNICUS/S5P/NRTI/L3_NO2"
bands = ["tropospheric_NO2_column_number_density"]

loc = "moz"

# xmin, ymin, xmax, ymax
roi = ee.Geometry.Rectangle([28, -28, 43, -9])  # Mozambique

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
    image=img, description=f"{loc}_no2", scale=1000, region=roi, folder=f"{loc}_no2",
).start()
