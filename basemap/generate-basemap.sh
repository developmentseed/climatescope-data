# Generate the Climatescope basemap from the meta/admin_areas.csv

# Every time, a country is added or removed from the Climatescope, a new
# basemap needs to be generated and uploaded to Mapbox. To do so, follow
# these steps:
#
# 1. run this script
#       $ bash generate_basemap.sh
# 2. convert the JSON files to mbtiles format using tippecanoe. (-Z 0 -z 6)
# 3. log in to Mapbox and replace the tilesets with the mbtiles files
#


mkdir tmp
wget http://www.naturalearthdata.com/http//www.naturalearthdata.com/download/50m/cultural/ne_50m_admin_0_countries.zip -O ./tmp/ne_50m.zip
wget http://www.naturalearthdata.com/http//www.naturalearthdata.com/download/50m/cultural/ne_50m_admin_0_boundary_lines_land.zip -O ./tmp/ne_50m_lines.zip
wget http://www.naturalearthdata.com/http//www.naturalearthdata.com/download/50m/cultural/ne_50m_populated_places_simple.zip -O ./tmp/ne_50m_places.zip
unzip ./tmp/ne_50m.zip -d ./tmp
unzip ./tmp/ne_50m_lines.zip -d ./tmp
unzip ./tmp/ne_50m_places.zip -d ./tmp
ogr2ogr -f "GeoJSON" ./tmp/ne50.json ./tmp/ne_50m_admin_0_countries.shp
ogr2ogr -f "GeoJSON" ./tmp/ne50_places.json ./tmp/ne_50m_populated_places_simple.shp -sql "SELECT name, featurecla, iso_a2 FROM ne_50m_populated_places_simple WHERE featurecla='Admin-0 capital'"
ogr2ogr -f "GeoJSON" ./climatescope-admin0-lines.json ./tmp/ne_50m_admin_0_boundary_lines_land.shp
node process-boundaries.js
node process-places.js
rm -r tmp