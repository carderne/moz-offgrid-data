#!/usr/bin/env python

"""
Merges polygons and points in an input file
to only points in new output file.
Used for OSM schools data.

Layers in input file must be named
'multipolygons' and 'points' exactly

Arg 1: path to file to merge
Arg 2: path to output file
e.g. ./school_centroids.py schools.gpkg schools-points.gpkg
"""

import sys
from pathlib import Path

import geopandas as gpd

infile = Path(sys.argv[1])
outfile = Path(sys.argv[2])

points = gpd.read_file(infile, layer="points")
polys = gpd.read_file(infile, layer="multipolygons")
polys.geometry = polys.geometry.centroid

merged = points.append(polys)
merged.to_file(outfile, driver="GPKG")
