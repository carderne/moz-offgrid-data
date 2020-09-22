# moz-offgrid-data
Overview of data sources and methods for Mozambique Off-Grid Energy project.

The frontend for this project is in a separate repository: [moz-offgrid-viz](https://github.com/carderne/moz-offgrid-viz).

The documentation below describes all steps necessary to replicate the data outputs used in the Mozambique Off-Grid visualization tool.

## Requirements for reproduction
The data was processed using a machine with 8 GB of physical memory and at least 100 GB of free hard drive space.

All processing was done using the following software stack:
```
Ubuntu 20.04
Python 3.7.3
GDAL 3.0.4
QGIS 3.10.4
```

The required Python libraries are listed in `requirements.txt` and can be installed with:
```
pip install -r requirements.txt
```

## Data sources
| Type | Source | License |
| ---- | ------ | ------- |
| Population | [Facebook HRSL](https://data.humdata.org/dataset/mozambique-high-resolution-population-density) | Creative Commons Attribution International |
| Population | [Worldpop](https://www.worldpop.org/geodata/summary?id=6404) | Creative Commons Attribution 4.0 International |
| Population | [GHS-POP](https://ghsl.jrc.ec.europa.eu/download.php?ds=pop) | Creative Commons Attribution 4.0 International |
| Urban degree | [GHS-SMOD](https://ghsl.jrc.ec.europa.eu/download.php?ds=smod) | Creative Commons Attribution 4.0 International |
| Grid | [gridfinder](https://zenodo.org/record/3628142) | Creative Commons Attribution 4.0 International |
| Grid | [Transmission network](https://energydata.info/dataset/mozambique-electricity-transmission-network-2017) | Creative Commons Attribution 4.0 |
| Spatial electricity access | [GDESSA](https://data.mendeley.com/datasets/kn4636mtvg/4) | CC BY 4.0 |
| Electricity statistics | [EDM Master Plan 2018](https://portal.edm.co.mz/sites/default/files/documents/Reports/INTEGRATED%20MASTER%20PLAN%202018-2043.pdf#pdfjs.action=download) | |
| Distance to cities | [JRC Global Accessibility Map](https://forobs.jrc.ec.europa.eu/products/gam/download.php) | Not specified - but most EU data is CC BY 4.0 |
| GDP | [UNEP/DEWA/GRID-Geneva GDP 2010](https://preview.grid.unep.ch/index.php?preview=data&events=socec&evcat=1&lang=eng) | UN license, Free for non-commercial |
| Admin boundaries | [GADM](https://gadm.org/download_country_v3.html) | Free for non-commercial use, noredistribution |
| Admin boundaries | [Natural Earth Admin 0](https://www.naturalearthdata.com/downloads/10m-cultural-vectors/) | Public domain |
| Compilation | [USAID RtM](https://dec.usaid.gov/dec/content/Detail_Presto.aspx?vID=47&ctID=ODVhZjk4NWQtM2YyMi00YjRmLTkxNjktZTcxMjM2NDBmY2Uy&rID=NTU5NDcy) | General USAID DEC license, Creative Commons Attribution-No Derivatives 4.0 International License |
| Night time lights | [NOAA VIIRS](https://developers.google.com/earth-engine/datasets/catalog/NOAA_VIIRS_DNB_MONTHLY_V1_VCMCFG) | No copyright |
| NDVI | [Sentinel-2](https://developers.google.com/earth-engine/datasets/catalog/COPERNICUS_S2_SR) | Copernicus Sentinel Data Terms and Conditions (attribution) |
| NO2 emissions | [Sentinel-5P](https://developers.google.com/earth-engine/datasets/catalog/COPERNICUS_S5P_NRTI_L3_NO2) | Copernicus Sentinel Data Terms and Conditions (attribution) |
| Hydropower resources | [African Small Hydro Potential](https://energydata.info/dataset/small-and-mini-hydropower-potential-in-sub-saharan-africa) | Creative Commons Attribution 4.0 |
| OpenStreetMap | [OpenStreetMap](https://download.geofabrik.de/africa.html) | Open Data Commons Open Database License |
| OpenStreetMap | [HOT Feature Exports](https://data.humdata.org/search?organization=hot&q=mozambique) | Open Database License (ODC-ODbL) |
| Settlements | [UN IOM Mozambique settlements](https://data.humdata.org/dataset/mozambique-settlement-shapefiles) | Non-commercial, no redistribute |
| Settlements | [OCHA Main Cities](https://data.humdata.org/dataset/mozambique-main-cities) |  	Creative Commons Attribution International |
| Health | [OCHA Health Facilities](https://data.humdata.org/dataset/mozambique-health-facilities) | Public domain |
| Energy | [OCHA Energy Facilities](https://data.humdata.org/dataset/mozambique-energy-facilities) | Creative Commons Attribution International |
| Rivers | [OCHA Stream Network](https://data.humdata.org/dataset/mozambique-rivers-and-stream-network) | Creative Commons Attribution International |
| Poverty | [OPHI Poverty Rate](https://data.humdata.org/dataset/mozambique-poverty-rate) |  	Creative Commons Attribution International |
| Affordability | [USAID Power Africa surveys]() | |
| Admin boundaries | [OCHA Admin Boundaries](https://data.humdata.org/dataset/mozambique-administrative-levels-0-3) | humanitarian use only |

## Pre-processing data
Scripts are in `/scripts`.

Google Earth Engine scripts are in [this EE repo](https://code.earthengine.google.com/?accept_repo=users/carderne/giz) (not currently publicly accessible).

### Extracting OSM features

[Schools](https://wiki.openstreetmap.org/wiki/Education_features)
```bash
osmfilter moz.o5m --keep="amenity=school" | \
    ogr2ogr -f GPKG osm-schools.gpkg /vsistdin/ multipolygons points
```

Then use the script to merge the polygons and points into a single later:
```bash
./scripts/merge_centroids.py data/osm/osm-schools.gpkg data/osm/osm-schools.gpkg
```

[Health facilities](https://wiki.openstreetmap.org/wiki/Key:healthcare)
```
osmfilter moz.o5m --keep="healthcare=*" | \
    ogr2ogr -f GPKG osm-health.gpkg /vsistdin/ multipolygons points
```
Based on examination, the OCHA health site data is much more complete, and includes most of the OSM sites, so the OSM data will not be used for health sites.

Grid lines:
```bash
osmfilter moz.o5m --keep="power=line" | ogr2ogr -f GPKG osm-grid.gpkg /vsistdin/ lines
```

### Urban level
GHSL SMOD

Use QGIS Raster -> Merge to merge/mosaic four tiles covering Mozambique.

Warp/reproject to EPSG:4326 (nearest neighbour, nodata 0).

Urban codes are as follows:
11: Mostly uninhabited
12: Rural, dispersed area
13: Village
21: Suburbs
22: Semi-dense town
23: Dense town
30: City

### Emissions
Script `./scripts/ee_download.py no2` will download a single maximum annual value of NO2 for Mozambique.

### Add distance to cities
Using [this Wikipedia article](https://en.wikipedia.org/wiki/List_of_cities_in_Mozambique_by_population) with the following list of the 17 largest cities in Mozambique:

With the OCHA Main Cities dataset, use the following filter query in QGIS to get the selected cities:
```
"TOPONIMO" IN ('Cidade da Matola', 'Maputo', 'Nampula', 'Beira', 'Chimoio',
    'Quelimane', 'Tete', 'Cidade de Nacala', 'Lichinga', 'Pemba', 'Mocuba',
    'Gurué', 'Xai-Xai', 'Maxixe', 'Angoche', 'Inhambane', 'Cuamba')
```

## Advanced analysis
### Copernicus satellite imagery
Download recent Copernicus Sentinel-2 images for each cluster:
```bash
./scripts/s2_imagery.py
```

The files will download to Google Drive.

Mosaic into single tif:
```bash
./scripts/s2_reproj.sh ./data/s2/images/
gdal_merge.py -co COMPRESS=LZW -co BIGTIFF=YES -a_nodata 0 -o s2_mosaic.tif images/*.tif

# Then because the output from gdal_merge is for some reason unnecessary large
gdal_translate -co COMPRESS=LZW -ot Byte s2_mosaic.tif s2_mosaic_byte.tif
```

### Detecting agriculture
Use the script to download daily MODIS NDVI data:
```
./scripts/ee_download.py modis
```

Can also download Sentinel-2 NDVI data, which is a much higher spatial resolution, but much lower (weekly) temporal resolution:
```
./scripts/ee_download.py ndvi
```

Then use the script to process this using the Fourier Transform to get the relative amount of change within different seasons as an indication of agricultural activity. This analysis follows the paper `Cropland area estimates using Modis NDVI time series  in the state of Mato Grosso, Brazil` by Daniel de Castro Victoria et al., [available here](https://www.scielo.br/pdf/pab/v47n9/12.pdf).
```
./scripts/process_ndvi.py data/ndvi-daily/ data/ndvi-proc/
```

Currently this uses the NDVI values *within* the cluster, which of course limits its usefulness, as most agriculture will happen outside the cluster boundaries.

### Detecting urban growth
Use the script to run a simple machine learning classification of different land-cover types and download the results to Google Drive. Results are classified into the following classes: `undeveloped`, `farm`, `developed`, `water`. This is done using the labels I created at `scripts/ml_labels.geojson` which has around 70 labels for each of these land types. The script below uses these labels to train a machine learning model, and then uses that model to classify land cover types over the course of several years. As this is just a demonstration, these labels are neither very good quality, nor very many. Additionally, a smaller sample than possible of each year's imagery is used. Finally, this is only done over the few years of available S2 imagery, instead of using a longer time-series including other imagery sources.
```
# The argument 1000 is the spatial resolution in metres
# Doing at 1000m (instead of native 10m) as this is simply a demonstration
./scripts/ml_classify.py 1000
```

It may be necessary to clip the results to make them easier to work with:
```
gdal_translate -projwin 28 -9 43 -28 -ot Byte data/ml/cls_2019.tif data/ml/cls_2019_clip.tif
```

The chance is calculated along with the other attributes in the `scripts/cluster_attributes.py` script.

### Gridfinder
Please see the [gridfinder](https://github.com/carderne/gridfinder/) and [website](https://gridfinder.org) for details on using gridfinder.

## Administrative layers
### Attributes to add

| Attribute              | Name      | Unit    | Source           | Comments |
| ---------              | ----      | ----    | ------           | -------- |
| Province               | adm1      |         | OCHA             | |
| Province code          | adm1_code |         | OCHA             | |
| District               | adm2      |         | OCHA             | |
| District code          | adm2_code |         | OCHA             | |
| Posto                  | adm3      |         | OCHA             | |
| Posto code             | adm3_code |         | OCHA             | |
| Population             | pop       |         | HRSL             | |
| Area                   | area      | km2     |                  | |
| Electricity access     | prov_elec |         | USAID            | Only at province level |
| Poverty rate           | prov_pov  |         | OPHI             | Only at province level |
| Health facilities      | health    |         | OCHA             | |
| Schools                | schools   |         | OSM              | |

### Add attributes
The OCHA data is used as a base.
First need to manually enter the electricity access figures from USAID, and OPHI's MPI (Multidimensional Poverty Index) into the Province (adm1) layer.
Add these as fields `prov_elec` and `prov_pov` and save the file.

Then use the script:
```bash
./scripts/admin_attributes.py
```

## Clusters
### Creating clusters
The command below runs a script that does the following steps, which can also be run in QGIS:
1. Resample to 0.001 degrees and drop pixels below a threshold
2. Polygonize then fix geometries
3. Add area column $area, and filter area > 13000
4. Buffer 0.005, then fix geometries
5. Dissolve
6. Multipart to singlepart

```bash
./scripts/make_clusters.py
```

### Attributes to add to clusters
| Attribute              | Name      | Unit    | Source           | Comments |
| ---------              | ----      | ----    | ------           | -------- |
| Province               | adm1      |         | OCHA             | |
| Province code          | adm1_code |         | OCHA             | |
| District               | adm2      |         | OCHA             | |
| District code          | adm2_code |         | OCHA             | |
| Posto                  | adm3      |         | OCHA             | |
| Posto code             | adm3_code |         | OCHA             | |
| Settlement             | name      |         | IOM Settlements  | |
| Latitude               | lat       | deg     |                  | |
| Longitude              | lon       | deg     |                  | |
| Area                   | area      | km2     |                  | |
| Population             | pop       |         | HRSL             | |
| Households             | hh        |         | HRSL             | |
| Population density     | popd      | pop/km2 | HRSL             | |
| Urban type             | urban     |         | GHSL SMOD        | |
| Nearest city           | city      |         | OCHA Main Cities | |
| Nearest city distance  | cityd     | km      | OCHA Main Cities | |
| Travel time to city    | travel    | hours   | JRC              | |
| Health facilities      | health    |         | OCHA             | |
| Schools                | schools   |         | OSM              | |
| Grid distance          | grid      | km      | gridfinder/OSM   | |
| Electricity access     | elec      |         | gridfinder/OSM   | |
| Agricultural indicator | agri      |         | NDVI             | |
| Growth                 | growth    |         | ML with S2 image | |
| Emissions              | emissions |         | NO2              | |
| NTL                    | ntl       |         | VIIRS            | |
| GDP                    | gdp       | USD/cap | UNEP             | |
| Poverty rate           | poverty   |         |                  | |
| Markets                | markets   |         |                  | |
| Telecom towers         | telecom   |         |                  | no source, RTM says FUNAE |
| Electricity access     | prov_elec |         | USAID            | Only at province level |
| Poverty rate           | prov_pov  |         | OPHI             | Only at province level |
| Demand                 | demand    | kW      |                  | |

Demand is calculated according to the following formula:
```
demand_pp   = 0.0852   # kW/person
intercept   = -12.44   # kW
health_mult = 20       # multiple of per person demand
school_mult = 20       # multiple of per person demand

demand = (
    pop * demand_pp
    + health * health_mult * demand_pp
    + schools * school_mult * demand_pp
    + intercept
)
```

The cluster score is calculated using a z-score and weighting for each of the following attributes:
| Attributes | Weighting |
| ---------- | --------- |
| pop        | 0.4       |
| popd       | 0.1       |
| grid       | 0.3       |
| health     | 0.1       |
| schools    | 0.1       |

### Add attributes
Run this script:
```bash
./scripts/cluster_attributes.py all scratch
```

Can also run with names of features to add instead of all. If `scratch` is included, it starts from the base clusters with no attributes, otherwise it reads in the file with attributes already added, and will overwrite attributes as needed.
```bash
./scripts/cluster_features.py pop,ntl
```

### Manually add settlement names
1. Using IOM settlements data for settlements.
2. In QGIS use `Voronoi polygons` with settlements, 30% buffer.
3. Then use `Join attributes by location`. Input layer: clusters; join layer: voronoi; predicate: intersects; fields to add: "Sett_Name"; join type: first located; discard records: yes.
4. Rename new field to `name`.

### Manually add nearest city name
1. Use filtered cities file.
2. Use `Voronoi polygons` with cities, 30% buffer.
3. Then use `Join attributes by location`. Input layer: clusters; join layer: voronoi; predicate: intersects; fields to add: "TOPONIMO"; join type: first located; discard records: yes. Rename new field to `name`.
4. Rename new field to `city`.

