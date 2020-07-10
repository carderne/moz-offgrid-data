#!/usr/bin/env python

import ee
from geetools.batch import Export

ee.Authenticate()
ee.Initialize()

viirs = "NOAA/VIIRS/DNB/MONTHLY_V1/VCMCFG"
loc = "moz"
roi = ee.Geometry.Rectangle([28, -28, 43, -9])  # Mozambique

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
