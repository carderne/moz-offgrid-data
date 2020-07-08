#!/usr/bin/env python

"""
Arg 1: Path to dir containing viirs images to merge.
Arg 2: Path for output file
Arg 3: Percentile for merging
e.g. ./merge_viirs.py ./viirs/ ./viirs-merged 70
"""

from pathlib import Path
import sys

import numpy as np
import rasterio as rio

path = Path(sys.argv[1])
outfile = Path(sys.argv[2])
pc = int(sys.argv[3])

viirs_files = sorted([f for f in path.iterdir()])


def save_raster(out, arr, prof):
    with rio.open(out, "w", **prof) as ds:
        ds.write(arr.astype(np.float32), indexes=1)


def merge():
    with rio.open(viirs_files[0]) as ds:
        prof = ds.profile
        prof.update(count=1)

    print("Merging ntl...", flush=True)
    arrs = []
    for f in viirs_files:
        with rio.open(f) as ds:
            arrs.append(ds.read(1))
    viirs_arr = np.array(arrs)
    viirs_merged = np.percentile(viirs_arr, pc, axis=0)
    save_raster(outfile, viirs_merged, prof)
    print("Done")


merge()
