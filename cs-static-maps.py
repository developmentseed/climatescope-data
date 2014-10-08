#!/usr/bin/python
# -*- coding: UTF-8 -*-

# This script takes the list of administrative areas provided in the meta file
# and produces a static map in PNG format for each of them. 
# It uses Tilemill to generate these images.
#
# Based on the original bounding box in degrees, we calculate a new bounding 
# box for the desired height and width. By default, it scales the polygon and
# centers it. It is also possible to specify paddings.
#
# The bulk of the calculations is done to re-calculate the bounding box 
# properly, taking into account the different distances between the longitudes
# at the min and max latitude.
#
#
# USAGE
#
# Example: python cs-static-maps.py
#
#
# Todo:
# - check if Natural Earth shapefiles exist and if not, download them
# - runs Tilemill in the standard Ubuntu install folder
# - Optimize the PNG's


import subprocess
import shlex
import math
import sys
import pandas as pd
from osgeo import ogr

src_meta_aa = 'source/meta/admin_areas.csv'
exp_dir = 'data/assets/images/content/maps/'

# Tilemill installation directory
tm_dir = '/usr/share/tilemill/'
tm_project = 'cs-single-country'

# Languages to generate images for
langs = ('en','es')

# Approximate desired height and width in pixels
width = 512
height = 512
# Define the padding for each of the 4 sides (top, right, bottom, left)
padding = (48,48,48,48)

#http://www.johndcook.com/python_longitude_latitude.html
def distance_on_unit_sphere(lon1, lat1, lon2, lat2):

  # Convert latitude and longitude to 
  # spherical coordinates in radians.
  degrees_to_radians = math.pi/180.0
      
  # phi = 90 - latitude
  phi1 = (90.0 - lat1)*degrees_to_radians
  phi2 = (90.0 - lat2)*degrees_to_radians
      
  # theta = longitude
  theta1 = lon1*degrees_to_radians
  theta2 = lon2*degrees_to_radians
      
  # Compute spherical distance from spherical coordinates.
      
  # For two locations in spherical coordinates 
  # (1, theta, phi) and (1, theta, phi)
  # cosine( arc length ) = 
  #    sin phi sin phi' cos(theta-theta') + cos phi cos phi'
  # distance = rho * arc length
  
  cos = (math.sin(phi1)*math.sin(phi2)*math.cos(theta1 - theta2) + 
         math.cos(phi1)*math.cos(phi2))
  arc = math.acos( cos )

  # Remember to multiply arc by the radius of the earth 
  # in your favorite set of units to get length.
  return arc

def calculate_bbox(lon1,lat1,lon2,lat2,padding=(0,0,0,0)):
  "Calculate a new bbox based on the desired height and width in pixels. If no padding is provided, the polygon is simply centered in the new bbox."

  # The desired core bounding box, removing the optional padding.
  total_padding_lon = padding[1] + padding[3]
  total_padding_lat = padding[0] + padding[2]
  core_width = width - total_padding_lon
  core_height = height - total_padding_lat

  # Calculate amount of degrees longitude and latitude for the original bbox.
  degrees_lon = lon2 - lon1
  degrees_lat = lat2 - lat1
  # Get the center coordinates
  center_lon = degrees_lon / 2 + lon1
  center_lat = degrees_lat / 2 + lat1

  # By default, no shift
  shift_core_lon = 0
  shift_core_lat = 0

  # Calculate the length of the original bbox. For the longitude, calculate at center lat
  length_lat = distance_on_unit_sphere(lon1, lat1, lon1, lat2)
  length_lon = distance_on_unit_sphere(lon1, center_lat, lon2, center_lat)

  # Calculate the ratio of the original bbox to decide whether dealing with a wide or narrow shape
  ratio_original_bbox = length_lon / length_lat
  
  # Ratio of the desired core bbox (without padding)
  # Convert to float, otherwise it's an int division, returning an int as well
  ratio_core_bbox = core_width / float(core_height)

  # If the original bbox is wider than the desired core bbox, add space to top and bottom
  if ratio_core_bbox < ratio_original_bbox: 
    # In this case, the longitudes fit the core box exactly. Therefore, we can
    # calculate the amount of px per arc, at the center latitude
    px_distance_arc_lon = core_width / length_lon
    # Determine the height in px of the original bbox
    px_distance_lat = px_distance_arc_lon * length_lat

    # Amount of pixels to add to top AND bottom to get the desired core bbox
    px_to_add = (core_height - px_distance_lat) / 2

    # Calculate the amount of pixels per degree longitude
    px_per_degree_lon = core_width / degrees_lon
    # Calculate the amount of pixels per degree latitude
    px_per_degree_lat = px_distance_lat / degrees_lat

    # Degree that the bbox has to be shifted (left and right) to fit the desired core bbox.
    shift_core_lat = px_to_add / px_per_degree_lat

  # ... otherwise add space on the left and right
  else:
    # In this case, the latitudes fit the core box exactly. Therefore, we can
    # calculate the amount of px per arc
    px_distance_arc_lat = core_height / length_lat
    # Determine the width in px of the original bbox
    px_distance_lon = px_distance_arc_lat * length_lon

    # Amount of pixels to add to left AND right to get the desired core bbox
    px_to_add = (core_width - px_distance_lon) / 2

    # Calculate the amount of pixels per degree longitude
    px_per_degree_lon = px_distance_lon / degrees_lon
    # Calculate the amount of pixels per degree latitude
    px_per_degree_lat = core_height / degrees_lat

    # Degree that the bbox has to be shifted (left and right) to fit the desired core bbox.
    shift_core_lon = px_to_add / px_per_degree_lon

  # Degrees the longitudes need to be shifted for the padding
  shift_padding_lon1 = padding[3] / px_per_degree_lon
  shift_padding_lon2 = padding[1] / px_per_degree_lon
  # Degrees that the latitudes need to be shifted for the padding
  shift_padding_lat1 = padding[2] / px_per_degree_lat
  shift_padding_lat2 = padding[0] / px_per_degree_lat

  # Calculate new lon, lats + bbox
  new_lon1 = lon1 - shift_core_lon - shift_padding_lon1
  new_lat1 = center_lat - shift_core_lat - shift_padding_lat1
  new_lon2 = lon2 + shift_core_lon + shift_padding_lon2
  new_lat2 = center_lat + shift_core_lat + shift_padding_lat2

  new_bbox = '"%s,%s,%s,%s"' % (new_lon1, new_lat1, new_lon2, new_lat2)
  return new_bbox

def generate_cartocss(aa_type,active,lang):
  "Write the stylesheet for the map. Type = country or state, active = the iso of the active area, lang = language"
  if aa_type == 'c':
    layer = 'countries'
    iso_id = 'ISO_A2'
  elif aa_type == 's':
    layer = 'states'
    iso_id = 'iso_3166_2'

  cartocss_template =\
  '''\
  Map { background-color: #f2f2f2; }
  #%s [%s = "%s"] {
    ::outline { line-color: #fff; line-width: 2px; }
    polygon-fill: #C3D500;
  }
  #capitals [iso = "%s"] {
    text-name: [capital:%s];
    text-size: 32px;
    text-fill: #333;
    text-halo-fill: #fff;
    text-halo-radius: .75;
    text-face-name: 'Calibri Regular';
    text-dy: -16px;
    marker-width: 12;
    marker-fill: #fff;
    marker-line-color: #333;
    marker-line-width: 2px;
  }
  ''' % (layer,iso_id,active,active,lang)

  return cartocss_template

def build_set(search,search_col,result,csv):
  "Build a set from a CSV file, iterating over rows and storing the value of 'result' column when the 'search' is found in the 'search_col'."
  df = pd.read_csv(csv)
  s = set()
  for index, row in df.iterrows():
    if row[search_col] == search:
      s.add(row[result])
  return s

def main():

  if height < (padding[0] + padding[2]):
    print "ABORT. ABORT.\n"\
          "The combined padding for the top and bottom exceeds the desired height."
    sys.exit(0)
  elif width < (padding[1] + padding[3]):
    print "ABORT. ABORT.\n"\
          "The combined padding for the left and right exceeds the desired width."
    sys.exit(0)

  # Build the lists with countries and states to generate a map for.  
  countries = build_set('country','type','iso',src_meta_aa)
  states = build_set('state','type','iso',src_meta_aa)
  
  # Country are treated slightly different than states and provinces.
  for aa in 'c','s':
    if aa == 'c':
      shp = 'source/shapefiles/ne_10m_admin_0_countries/ne_10m_admin_0_countries.shp'
      # The attribute in the shapefile containing the iso code of the administrative area
      attribute = 'ISO_A2'
      admin_areas = countries
    else:
      shp = 'source/shapefiles/ne_10m_admin_1_states_provinces/ne_10m_admin_1_states_provinces.shp'
      attribute = 'iso_3166_2'
      admin_areas = states
    
    ds = ogr.Open(shp)
    lyr = ds.GetLayer(0)
    lyr.ResetReading()
    count = lyr.GetFeatureCount()

    for i in range(count):
      feature = lyr.GetFeature(i)
      iso = feature.GetField(attribute)
      if iso in admin_areas:

        # Get bbox in minx, maxx, miny, maxy format
        env = feature.GetGeometryRef().GetEnvelope()
        
        # SW = lon1, lat1 (min)
        lon1 = env[0]
        lat1 = env[2]
        # NE = lon2, lat2 (max)
        lon2 = env[1]
        lat2 = env[3]

        # Get the new bbox for the desired size in px.
        new_bbox = calculate_bbox(lon1,lat1,lon2,lat2,padding)

        for lang in langs:
          # Make sure we highlight the correct country
          cartocss_template = generate_cartocss(aa,iso,lang)
          
          with open('./tilemill/project/' + tm_project + '/style.mss','w') as mss:
            mss.write(cartocss_template)

          # For the file export, we want the iso code lowercase
          iso_fn = iso.lower()

          # Build the export command
          command = "node %sindex.js export %s %s%s/%s.png --format=png --width=%s --height=%s --bbox=%s --files='tilemill'" % (tm_dir, tm_project, exp_dir, lang, iso_fn, width, height, new_bbox)
          # shlex makes sure that all arguments are correctly passed, most notably the bounding box
          args = shlex.split(command)
          subprocess.call(args)

if __name__ == "__main__":
  main()