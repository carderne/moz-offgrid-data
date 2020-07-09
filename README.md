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
| Distance to cities | [JRC Global Accessibility Map](https://forobs.jrc.ec.europa.eu/products/gam/download.php) | Not specified - but most EU data is CC BY 4.0 |
| GDP | [UNEP/DEWA/GRID-Geneva GDP 2010](https://preview.grid.unep.ch/index.php?preview=data&events=socec&evcat=1&lang=eng) | UN license, Free for non-commercial |
| Admin boundaries | [GADM](https://gadm.org/download_country_v3.html) | Free for non-commercial use, noredistribution |
| Admin boundaries | [Natural Earth Admin 0](https://www.naturalearthdata.com/downloads/10m-cultural-vectors/) | Public domain |
| Compilation | [USAID RtM](https://dec.usaid.gov/dec/content/Detail_Presto.aspx?vID=47&ctID=ODVhZjk4NWQtM2YyMi00YjRmLTkxNjktZTcxMjM2NDBmY2Uy&rID=NTU5NDcy) | General USAID DEC license, Creative Commons Attribution-No Derivatives 4.0 International License |
| Night time lights | [NOAA VIIRS](https://developers.google.com/earth-engine/datasets/catalog/NOAA_VIIRS_DNB_MONTHLY_V1_VCMCFG) | No copyright |
| Hydropower resources | [African Small Hydro Potential](https://energydata.info/dataset/small-and-mini-hydropower-potential-in-sub-saharan-africa) | Creative Commons Attribution 4.0 |
| OpenStreetMap | [OpenStreetMap](https://download.geofabrik.de/africa.html) | Open Data Commons Open Database License |
| OpenStreetMap | [HOT Feature Exports](https://data.humdata.org/search?organization=hot&q=mozambique) | Open Database License (ODC-ODbL) |
| Settlements | [UN IOM Mozambique settlements](https://data.humdata.org/dataset/mozambique-settlement-shapefiles) | Non-commercial, no redistribute |
| Settlements | [OCHA Main Cities](https://data.humdata.org/dataset/mozambique-main-cities) |  	Creative Commons Attribution International |
| Health | [OCHA Health Facilities](https://data.humdata.org/dataset/mozambique-health-facilities) | Public domain |
| Energy | [OCHA Energy Facilities](https://data.humdata.org/dataset/mozambique-energy-facilities) | Creative Commons Attribution International |
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
- [x] Province (admin 1)
- [x] District (admin 2)
- [x] Posto (admin 3)
- [x] Village name (or name of containing Posto)
- [x] Latitude and longitude
- [x] Nearest city
- [x] Straight line distance to nearest city [km]
- [x] Travel time to nearest city [hours]
- [x] Population (from HRSL/Worldpop)
- [x] Households (population divided by house size)
- [x] Area [km2]
- [x] Population density [people/km2]
- [x] Urban type
- [ ] Grid distance (to gridfinder/official) [km]
- [ ] Electricity access (how calculated?)
- [ ] Poverty rate
- [ ] Markets
- [ ] Schools
- [ ] Health sites
- [ ] NDVI (vegetation indicator, from Sentinel-2)
- [ ] Road network access
- [ ] Emissions (from Sentinel-5P NO2)
- [x] Night-time lights (from VIIRS)
- [x] GDP (sum of GDP in cluster) [million USD]
- [ ] Telecom towers (don't have a source, RTM says FUNAE)

### Add base features to clusters
Configuration file is in `./clusters/features.yml`.

Then run: `~/Code/clusterize/run.py feat --config ./clusters/features.yml ./clusters/clusters-proc.gpkg ./clusters/clusters-feat.gpkg`

### Add area to clusters
In QGIS:
1. Open attribute table
2. Delete any existing "area" column
3. Use new column calculator to create new column "area", type float, precision 1, with formula: `$area / 1e6`.

### Add admin levels
Using OCHA data admin 3 data. Use QGIS "Join attributes by location". Select intersects and within. Join type: first located. Tick Discard records.

Fields to include:
- ADM1_PT
- ADM2_PT
- ADM3_PT

### Add village names
Using IOM settlements data. In QGIS use "Voronoi polygons" with settlements, 10% buffer.

Then with clusters, "Join attributes by location". Select intersects and within. Join type: first located. Tick Discard records. Choose "Sett_Name" field.

### Urban level
Use QGIS Raster -> Merge to merge/mosaic four tiles covering Mozambique.

Warp/reproject to EPSG:4326 (nearest neighbour, nodata 0).

Use Zonal statistics with clusters layer, calculate majority/mode of raster value.

Urban codes are as follows:
11: Mostly uninhabited
12: Rural, dispersed area
13: Village
21: Suburbs
22: Semi-dense town
23: Dense town
30: City

### Calculate grid distance of each cluster with QGIS
1. Ensure grid data and clusters are in the same CRS (coordinate reference system).
2. Rasterize grid data. Burn value: 1. Size units: georeferenced. Width/height: ??. Output extent: from clusters layer.
3. Raster proximity. Target values: 1. Distance units: georeferenced.
4. Zonal statistics to get values from raster into clusters geometry.

### Add distance to cities
Using [this Wikipedia article](https://en.wikipedia.org/wiki/List_of_cities_in_Mozambique_by_population) with the following list of the 17 largest cities in Mozambique:
- Matola
- Maputo
- Nampula
- Beira
- Chimoio
- Quelimane
- Tete
- Nacala
- Lichinga
- Pemba
- Mocuba
- Gurúè
- Xai-Xai
- Maxixe
- Angoche
- Inhambane
- Cuamba

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

### Number of households and population density
For this we assume average household size is 5. SO number of households is a new column with `population / 5` (and kept as integer).

Population density is `population / area` (also integer).

### Get latitude and longitude
Use Centroids tools to convert clusters to points. Then in Attribute table, create new columns `lat` and `long`, as real numbers, with `$y` and `$x` as the formulae, respectively. Then use Join attributes by location to add the `lat` and `long` fields to the clusters.
