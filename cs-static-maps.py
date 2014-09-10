#!/usr/bin/python
# -*- coding: UTF-8 -*-

# This script takes the list of administrative areas provided in the meta file
# and produces a static map in PNG format for each of them. 
# It uses Tilemill to generate these images.
#
# Based on the original bounding box in degrees, we calculate a new bounding 
# box for the desired height and width. By default, it scales the polygon and
# centers it. It is also possible to specify offsets.
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
# - add a check if the total offset does not excede height or width
# - China has a bug, not centered
# - India states not being generated. NE's state data for India doesn't have the correct ISO codes.
# - Optimize the PNG's


import subprocess
import shlex
import math
import pandas as pd
from osgeo import ogr

src_meta_aa = 'source/meta/admin_areas.csv'
exp_dir = 'data/assets/images/content/maps/'

# Tilemill installation directory
tm_dir = '/usr/share/tilemill/'
tm_project = 'cs-single-country'

# Approximate desired height and width in pixels
width = 2880
height = 1024


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

def calculate_bbox(lon1,lat1,lon2,lat2,offset_lon1=0,offset_lat1=0,offset_lon2=0,offset_lat2=0):
  "Calculate a new bbox based on the desired height and width in pixels. If no offset is provided, the polygon is simply centered in the new bbox."

  # Get the center coordinates
  center_lon = (lon2 - lon1) / 2 + lon1
  center_lat = (lat2 - lat1) / 2 + lat1

  # Calculate the arc of one degree latitude
  arc_height = distance_on_unit_sphere(lon1, lat1, lon1, lat2) / (lat2 - lat1)
  # Arc of one longitude degree at miny
  arc_lat1 =  distance_on_unit_sphere(lon1, lat1, lon2, lat1) / (lon2 - lon1)
  # Arc of one longitude degree at maxy
  arc_lat2 = distance_on_unit_sphere(lon1, lat2, lon2, lat2) / (lon2 - lon1)
  # Arc of one longitude degree at center latitude
  arc_lat_center = distance_on_unit_sphere(lon1, center_lat, lon2, center_lat) / (lon2 - lon1)
  
  # Check the ratio of the original bounding box, by calculating distance from center
  dist_lat = distance_on_unit_sphere(center_lon, center_lat, center_lon, lat2)
  dist_lon = distance_on_unit_sphere(center_lon, center_lat, lon2, center_lat)
  ratio_original_bbox = dist_lon / dist_lat


  # The desired core bounding box, removing the optional offset.
  total_offset_lon = offset_lon1 + offset_lon2
  total_offset_lat = offset_lat1 + offset_lat2
  core_width = width - total_offset_lon
  core_height = height - total_offset_lat

  # Ratio of the desired core bbox (without offset)
  # Convert to float, otherwise it's an int division, returning an int as well
  ratio_core_bbox = core_width / float(core_height)

  # If the original bbox is wider than the desired core bbox, add space to top and bottom
  if ratio_core_bbox < ratio_original_bbox: 
    # Pixels per lon degree
    pix_width = core_width / (lon2 - lon1)

    # Pixels per degree for the height (we use the width of the center lat)
    pix_height = pix_width * arc_lat_center / arc_height

    # Degrees the longitudes need to be shifted for the offset
    shift_offset_lon1 = offset_lon1 / pix_width
    shift_offset_lon2 = offset_lon2 / pix_width
    # Degrees that the latitudes need to be shifted for the offset
    shift_offset_lat1 = offset_lat1 / pix_height
    shift_offset_lat2 = offset_lat2 / pix_height

    # Calculate how many degrees the lats needs to be shifted from center (without offset)
    shift_core_lat = (core_height / 2 / pix_height)

    # Calculate new lon, lats + bbox
    new_lon1 = lon1 - shift_offset_lon1
    new_lat1 = center_lat - shift_core_lat - shift_offset_lat1
    new_lon2 = lon2 + shift_offset_lon2
    new_lat2 = center_lat + shift_core_lat + shift_offset_lat2

  # ... otherwise add space on the left and right
  else:
    # Pixels per degree for the height
    pix_height = core_height / (lat2 - lat1)
    # Pixels per lon degree at miny
    pix_width_lat1 = pix_height * arc_height / arc_lat1
    # Pixels per lon degree at maxy
    pix_width_lat2 = pix_height * arc_height / arc_lat2
    
    # Degrees the longitudes need to be shifted for the offset
    shift_offset_lon1 = offset_lon1 / pix_width_lat1
    shift_offset_lon2 = offset_lon2 / pix_width_lat2
    # Degrees that the latitudes need to be shifted for the offset
    shift_offset_lat1 = offset_lat1 / pix_height
    shift_offset_lat2 = offset_lat2 / pix_height

    # Calculate how many degrees minx needs to be shifted from center (without offset)
    shift_core_lon1 = core_width / 2 / pix_width_lat1
    # Calculate how many degrees maxx needs to be shifted from center (without offset)
    shift_core_lon2 = core_width / 2 / pix_width_lat2

    # Calculate new lon, lats + bbox
    new_lon1 = center_lon - shift_core_lon1 - shift_offset_lon1
    new_lat1 = lat1 - shift_offset_lat1
    new_lon2 = center_lon + shift_core_lon2 + shift_offset_lon2
    new_lat2 = lat2 + shift_offset_lat2

  new_bbox = '"%s,%s,%s,%s"' % (new_lon1, new_lat1, new_lon2, new_lat2)
  return new_bbox

def generate_cartocss(aa_type,active,full_list,parent=False):
  "Write the stylesheet for the map. Type = country or state, active = the iso of the active area, full_list = the full list of active countries"
  cartocss_template =\
    '''\
    Map { background-color: #f2f2f2; }
    #countries {
      ::outline { line-color: #fff; }
      polygon-fill: #fff;
    '''
  if aa_type == 'c':
    for country in full_list:
      cartocss_template += '[ISO_A2 = "' + country + '"] { polygon-fill: #E5E5E5; }\n'
    # Finish the MSS template by adding the active color
    cartocss_template += '[ISO_A2 = "' + active + '"] { polygon-fill: #C3D500; }\n}'
  elif aa_type == 's':
    cartocss_template += '[ISO_A2 = "' + parent + '"] { polygon-fill: #E5E5E5; }\n}\n#states { ::outline { line-color: #fff; }\n[iso_3166_2 = "' + active + '"] {polygon-fill: #C3D500; }}'

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
        new_bbox = calculate_bbox(lon1,lat1,lon2,lat2,1440,0,200,0)

        if aa == 's':
          # If dealing with a state, also pass the iso of the parent country
          parent = iso[:2]
        else:
          parent = False

        # Make sure we highlight the correct country
        cartocss_template = generate_cartocss(aa,iso,admin_areas,parent)
        
        with open('./tilemill/project/' + tm_project + '/style.mss','w') as mss:
          mss.write(cartocss_template)

        # For the file export, we want the iso code lowercase
        iso_fn = iso.lower()

        # Build the export command
        command = "node %sindex.js export %s %s%s.png --format=png --width=%s --height=%s --bbox=%s --files='tilemill'" % (tm_dir, tm_project, exp_dir, iso_fn, width, height, new_bbox)
        # shlex makes sure that all arguments are correctly passed, most notably the bounding box
        args = shlex.split(command)
        subprocess.call(args)

if __name__ == "__main__":
  main()