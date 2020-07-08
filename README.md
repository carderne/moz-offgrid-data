# moz-offgrid-data
Overview of data sources and methods for Mozambique Off-Grid data analysis.

## Data sources
| Type | Source | License |
| ---- | ------ | ------- |
| Population | [Facebook HRSL](https://data.humdata.org/dataset/mozambique-high-resolution-population-density) | Creative Commons Attribution International |
| Population | [Worldpop](https://www.worldpop.org/geodata/summary?id=6404) | Creative Commons Attribution 4.0 International |
| Population | [GHSL](https://ghsl.jrc.ec.europa.eu/download.php) | Creative Commons Attribution 4.0 International |
| Grid | [gridfinder](https://zenodo.org/record/3628142) | Creative Commons Attribution 4.0 International |
| Grid | [Transmission network](https://energydata.info/dataset/mozambique-electricity-transmission-network-2017) | Creative Commons Attribution 4.0 |
| Distance to cities | [JRC Global Accessibility Map](https://forobs.jrc.ec.europa.eu/products/gam/download.php) | Not specified - but most EU data is CC BY 4.0 |
| GDP | [UNEP/DEWA/GRID-Geneva GDP 2010](https://preview.grid.unep.ch/index.php?preview=data&events=socec&evcat=1&lang=eng) | UN license, Free for non-commercial |
| Admin boundaries | [GADM](https://gadm.org/download_country_v3.html) | Free for non-commercial use, noredistribution |
| Admin boundaries | [Natural Earth Admin 0](https://www.naturalearthdata.com/downloads/10m-cultural-vectors/) | Public domain |
| Compilation | [USAID RtM](https://dec.usaid.gov/dec/content/Detail_Presto.aspx?vID=47&ctID=ODVhZjk4NWQtM2YyMi00YjRmLTkxNjktZTcxMjM2NDBmY2Uy&rID=NTU5NDcy) | General USAID DEC license, Creative Commons Attribution-No Derivatives 4.0 International License |
| Night time lights | [NOAA VIIRS](https://developers.google.com/earth-engine/datasets/catalog/NOAA_VIIRS_DNB_MONTHLY_V1_VCMCFG) | No copyright |
| Hydropower resources | [African Small Hydro Potential](https://energydata.info/dataset/small-and-mini-hydropower-potential-in-sub-saharan-africa) | Creative Commons Attribution 4.0 |
| OpenStreetMap | [OpenStreetMap](https://download.geofabrik.de/africa.html) | Open Data Commons Open Database License |
| OpenStreetMap | [HOT Feature Exports](https://data.humdata.org/search?organization=hot&q=mozambique&ext_page_size=25&sort=score%20desc%2C%20if(gt(last_modified%2Creview_date)%2Clast_modified%2Creview_date)%20desc) | Open Database License (ODC-ODbL) |
| Settlements | [UN IOM Mozambique settlements](https://data.humdata.org/dataset/mozambique-settlement-shapefiles) | Non-commercial, no redistribute |
| Health | [OCHA Health Facilities](https://data.humdata.org/dataset/mozambique-health-facilities) | Public domain |
| Energy | [OCHA Energy Facilities](https://data.humdata.org/dataset/mozambique-energy-facilities) | Creative Commons Attribution International |
| Settlements | [OCHA Main Cities](https://data.humdata.org/dataset/mozambique-main-cities) |  	Creative Commons Attribution International |
| Rivers | [OCHA Stream Network](https://data.humdata.org/dataset/mozambique-rivers-and-stream-network) | Creative Commons Attribution International |
| Admin boundaries | [OCHA Admin Boundaries](https://data.humdata.org/dataset/mozambique-administrative-levels-0-3) | humanitarian use only |

## Processing
Scripts are in `/scripts`.

### Preparing clusters
With HRSL, first clip HRSL to separate provinces (this let's us use different parameters for clusters in each area). Use `clip_hrsl_to_provinces.py`.

Then use `hrsl_prep.sh`, followed by `hrsl_make_settlements.sh`. Both of these depend on the [clusterize](https://github.com/carderne/clusterize) library.

Then `merge_clusters.py` to combine the clusters into one national file.

Then in QGIS:
1. Convex hulls
2. Dissolve
3. Multiparts to singleparts
4. Delete all data fields and add area column: $area
5. Filter to only inclea area > 60000
6. Save!

Results in ~29,000 clusters (vs ~7000 for USAID RtM).

### Attributes to add to clusters
- [ ] Village name (or name of containing posto)
- [ ] Province
- [ ] lat/lng
- [ ] posto (and poso ID?)
- [ ] district
- [ ] nearest city
- [ ] km to city
- [ ] population
- [ ] households
- [ ] area (km2)
- [ ] pop density
- [ ] urban type (rural, small village...)
- [ ] elec access (how calculated?)
- [ ] povert rate
- [ ] market?
- [ ] schools
- [ ] health sites
- [ ] grid distance
- [ ] NDVI
- [ ] HRSL (already in pop)
- [ ] road network access
- [ ] emissions (NO2)
- [ ] NTL
- [ ] GDP

### Add features to clusters
Configuration file is in `./clusters/features.yml`.

Then run: `~/Code/clusterize/run.py feat --config ./clusters/features.yml ./clusters/clusters-proc.gpkg ./clusters/clusters-feat.gpkg`

### Calculate grid distance of each cluster with QGIS
1. Ensure grid data and clusters are in the same CRS (coordinate reference system).
2. Rasterize grid data. Burn value: 1. Size units: georeferenced. Width/height: ??. Output extent: from clusters layer.
3. Raster proximity. Target values: 1. Distance units: georeferenced.
4. Zonal statistics to get values from raster into clusters geometry.
