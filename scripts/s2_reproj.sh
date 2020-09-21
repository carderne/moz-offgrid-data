#!/bin/bash

for f in $1/*; do
    name=$(echo $f | sed -r "s/.+\/(.+)\..+/\1/")
    if [[ $f == *".tif" ]]; then
        gdal_translate -ot Byte -scale 0 2800 0 255 $f /vsistdout/ |
            gdalwarp -t_srs EPSG:32736 /vsistdin/ $1/../images_proj/$name.tif
    fi
done
