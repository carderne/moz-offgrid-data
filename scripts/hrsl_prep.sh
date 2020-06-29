#!/bin/bash

for f in sep_prov/*; do
    echo $f
    name=$(echo $f | sed -r "s/.+\/(.+)\..+/\1/");
    ~/Code/clusterize/run.py prep --res=0.0008 --min_val=0 $f sep_prov/"$name"_prep.tif
done
