#!/usr/bin/env python

"""
Run a basic satellite image classification on Google Earth Engine
Arg 1: resolution (in metres)
e.g.
./scripts/ee_classify.py 100
"""

import sys
from pathlib import Path

import geopandas as gpd
import ee

ee.Initialize()

roi = ee.Geometry.Rectangle([28, -28, 43, -9])  # Mozambique
bands = ["B2", "B3", "B4", "B5", "B6", "B7", "B8"]


def maskS2clouds(image):
    qa = image.select("QA60")
    mask = qa.bitwiseAnd(1024).eq(0) and qa.bitwiseAnd(2048).eq(0)
    return image.updateMask(mask).divide(10000)


def create_img(year):
    img = (
        ee.ImageCollection("COPERNICUS/S2_SR")
        .filterBounds(roi)
        .filterDate(f"{year}-06-01", f"{year}-07-31")
        .filter(ee.Filter.lt("CLOUDY_PIXEL_PERCENTAGE", 20))
        .map(maskS2clouds)
        .mean()
        .select(bands)
    )
    return img


def run(res=1000):
    root = Path(__file__).parents[0]
    labels = gpd.read_file(root / "ml_labels.geojson")
    labels = ee.FeatureCollection(labels.__geo_interface__)

    training = create_img(2020).sampleRegions(
        collection=labels, properties=["landcover"], scale=res
    )
    classifier = ee.Classifier.smileCart().train(
        features=training, classProperty="landcover", inputProperties=bands
    )

    for year in range(2017, 2021):
        print(year)
        classified = create_img(year).classify(classifier).clip(roi)
        ee.batch.Export.image.toDrive(
            image=classified,
            description=f"classified_{year}_{res}",
            scale=res,
            folder="mozam_classified",
            fileNamePrefix=f"classified_{year}_{res}",
            maxPixels=1e11,
        ).start()


if __name__ == "__main__":
    res = int(sys.argv[1])
    run(res)
