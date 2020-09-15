# moz-offgrid-data
Overview of data sources and methods for Mozambique Off-Grid data analysis.

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
```
osmfilter moz.o5m --keep="amenity=school" | \
    ogr2ogr -f GPKG osm-schools.gpkg /vsistdin/ multipolygons points
```

Then use the script to merge the polygons and points into a single later:
```
./scripts/merge_centroids.py data/osm/osm-schools.gpkg data/osm/osm-schools.gpkg
```

[Health facilities](https://wiki.openstreetmap.org/wiki/Key:healthcare)
```
osmfilter moz.o5m --keep="healthcare=*" | \
    ogr2ogr -f GPKG osm-health.gpkg /vsistdin/ multipolygons points
```
Based on examination, the OCHA health site data is much more complete, and includes most of the OSM sites, so the OSM data will not be used for health sites.

Grid lines:
```
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

### Agriculture
A [reference paper](https://www.scielo.br/pdf/pab/v47n9/12.pdf).

Script `download_ndvi.py` will download a timeseries of NDVI data. Notebook `ndvi_analysis.ipynb` used to calculate Fourier transform and identify zones of agricultural productivity.

Currently just using 3rd component (counting from 1) of Fourier transform. Use `Zonal statistics` to get mean value into clusters. Multiply by 100.

### Emissions
Script `download_no2.py` will download a single maximum annual value of NO2 for Mozambique.

Use `Zonal statistics` to get max value into clusters. Multiply by 100,000.

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
| Village                | village   |         | IOM Settlements  | |
| Latitude               | lat       | deg     |                  | |
| Longitude              | lon       | deg     |                  | |
| Area                   | area      | km2     |                  | |
| Population             | pop       |         | HRSL             | |
| Households             | hh        |         | HRSL             | |
| Population density     | popd      | pop/km2 | HRSL             | |
| Urban type             | urban     |         | GHSL SMOD        | |
| Nearest city           | city      |         | OCHA Main Cities | redo, all sorts of names present outside of 17 selected |
| Nearest city distance  | cityd     | km      | OCHA Main Cities | |
| Travel time to city    | travel    | hours   | JRC              | still need to divide by 60 and keep as float |
| Health facilities      | health    |         | OCHA             | |
| Schools                | schools   |         | OSM              | |
| Grid distance          | grid      | km      | gridfinder/OSM   | had to divide by 100 and keep as float |
| Electricity access     | elec      |         | gridfinder/OSM   | |
| Agricultural indicator | agri      |         | NDVI             | |
| Emissions              | emissions |         | NO2              | |
| NTL                    | ntl       |         | VIIRS            | |
| GDP                    | gdp       | USD/cap | UNEP             | not sure about units, seems like clusterize scale factor not working |
| Poverty rate           | poverty   |         |                  | |
| Markets                | markets   |         |                  | |
| Telecom towers         | telecom   |         |                  | no source, RTM says FUNAE |
| Electricity access     | prov_elec |         | USAID            | Only at province level |
| Poverty rate           | prov_pov  |         | OPHI             | Only at province level |


### Add attributes
Run this script:
```bash
./scripts/cluster_attributes.py all
```

Can also run with names of features to add instead of all, e.g.:
```bash
./scripts/cluster_features.py pop,ntl
```

### Add village names
Using IOM settlements data. In QGIS use "Voronoi polygons" with settlements, 10% buffer.

Then with clusters, "Join attributes by location". Select intersects and within. Join type: first located. Tick Discard records. Choose "Sett_Name" field.


### Add distance to cities
Using [this Wikipedia article](https://en.wikipedia.org/wiki/List_of_cities_in_Mozambique_by_population) with the following list of the 17 largest cities in Mozambique:

With the OCHA Main Cities dataset, use the following filter query in QGIS to get the selected cities:
```
"TOPONIMO" IN ('Cidade da Matola', 'Maputo', 'Nampula', 'Beira', 'Chimoio',
    'Quelimane', 'Tete', 'Cidade de Nacala', 'Lichinga', 'Pemba', 'Mocuba',
    'Gurué', 'Xai-Xai', 'Maxixe', 'Angoche', 'Inhambane', 'Cuamba')
```

Then use Voronoi polygons (buffer at least 30%) and Join by location (as for village names) to get nearest city for each cluster.

Then for distance:
1. Re-export filtered 17 cities as separate file.
1. Ensure filtered cities and clusters are in the same CRS (coordinate reference system).
2. Rasterize cities data. Burn value: 1. Size units: georeferenced. Width/height: 0.1 (degrees). Output extent: from clusters layer.
3. Raster proximity. Target values: 1. Distance units: georeferenced.
4. Zonal statistics to get Minimum value from distance raster into clusters geometry.
5. Create new column and multiply by 100 to get from degrees to km and convert to integer.


# TODO
- Add GHI, demand, score for each cluster
- Pre-filter clusters to  pop>100
- Rerun gridfinder
- Try manual clustering approach
- Fix auto-adding features to clusters
- Add pop-density filter to webmap
- Don't round area too much! At least two decimal places. Creates weird pop density artefacts.
- Exclude HV from proximity. Exclude gridfinder? Show separately??
