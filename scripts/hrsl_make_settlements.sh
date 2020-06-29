#!/bin/bash

for f in sep_prov/*; do
    if [[ $f == *"_prep"* ]]; then
        echo $f
        name=$(echo $f | sed -r "s/.+\/(.+)\..+/\1/");
        ~/Code/clusterize/run.py make --method=radius --radius=10 --buffer=100 $f sep_prov/$name.gpkg
    fi
done
