#!/usr/bin/env python

"""
Arg 1: Input dir
Arg 2: Output dir
e.g. ./process_ndvi.py data/ndvi-daily data/ndvi-proc
"""

from pathlib import Path
import pickle
import sys

import numpy as np
import rasterio as rio
from sklearn.cluster import KMeans


def fillnan(arr):
    c = 0
    nz = 1
    while nz > 0:
        for i in range(arr.shape[0] - 1):
            mask = np.isnan(arr[i, :, :])
            arr[i, :, :][mask] = arr[i + 1, :, :][mask]
        for i in range(arr.shape[0] - 1):
            ii = 360 - i
            mask = np.isnan(arr[ii, :, :])
            arr[ii, :, :][mask] = arr[ii - 1, :, :][mask]
        nz = np.count_nonzero(np.isnan(arr[:-1, :, :]))
        c += 1
        print(c, nz)
    return arr[:-1, :, :]


def get_stack(dir_in):
    tifs = [f for f in dir_in.iterdir() if f.suffix == ".tif"]
    print("Num files:", len(tifs))

    with rio.open(tifs[0]) as ds:
        prof = ds.profile

    print("Loading rasters")
    arrs = []
    for f in tifs:
        with rio.open(f) as ds:
            arrs.append(ds.read(1))

    print("Stacking")
    st = np.stack(arrs)
    print("Stack shape:", st.shape)

    return st, prof


def calc_fft(st, bands):
    print("Filling nan")
    st = fillnan(st)

    print("Calculate FFT")
    ft = np.abs(np.fft.fft(st, axis=0))
    print("FFT shape:", ft.shape)

    ft = ft[:bands, :, :]
    ft = ft.astype(np.float32)
    return ft


def score(ft):
    c = ft[1, :, :] * ft[2, :, :]
    c = ((c - c.mean()) / c.std()) + 1
    c[c < 0] = 0
    return c


def ml(ft, bands, n_clusters=5):
    ft = np.moveaxis(ft, 0, -1)
    X = ft.reshape((-1, bands))
    X = np.nan_to_num(X, nan=0.0, posinf=0.0, neginf=0.0)

    y = KMeans(n_clusters=n_clusters).fit_predict(X)
    y_out = y.reshape(ft.shape[1:])
    return y_out


def main(dir_in, dir_out):
    st, prof = get_stack(dir_in)
    print("Saving stack pickle in output dir")
    with open(dir_out / "stack.pickle", "wb") as f:
        pickle.dump(st, f, protocol=4)

    bands = 6
    ft = calc_fft(st, bands)

    prof.update(count=bands)
    with rio.open(dir_out / "fft.tif", "w", **prof) as ds:
        ds.write(ft.astype(np.float32))
    print("FFT raster saved in output dir")

    c = score(ft)
    prof.update(count=1)
    with rio.open(dir_out / "scored.tif", "w", **prof) as ds:
        ds.write(c, indexes=1)
    print("Scored raster saved in output dir")

    k = ml(ft, bands)
    prof.update(count=1)
    with rio.open(dir_out / "kmeans.tif", "w", **prof) as ds:
        ds.write(k.astype(np.float32), indexes=1)
    print("KMeans raster saved in output dir")


if __name__ == "__main__":
    dir_in = Path(sys.argv[1])
    dir_out = Path(sys.argv[2])
    main(dir_in, dir_out)
