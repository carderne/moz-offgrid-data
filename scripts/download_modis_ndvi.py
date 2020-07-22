#!/usr/bin/env python

"""
Download MODIS daily NDVI images

https://developers.google.com/earth-engine/datasets/catalog/MODIS_MOD09GA_006_NDVI
"""

import ee
from geetools.batch import Export

# ee.Authenticate()
ee.Initialize()

loc = "moz"
# xmin, ymin, xmax, ymax
roi = ee.Geometry.Rectangle([28, -28, 43, -9])  # Mozambique

modis = 'MODIS/MOD09GA_006_NDVI'
date_sta = "2019-01-01"
date_end = "2020-01-01"
ic = (
    ee.ImageCollection(modis)
    .filterBounds(roi)
    .filterDate(date_sta, date_end)
)

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
