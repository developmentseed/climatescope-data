#!/usr/bin/python
# -*- coding: UTF-8 -*-

# Script to process the auxiliary data of the Climatescope that is presented
# in detailed graphs. Given the limited amount of times the data will be
# updated, the script works as a make file: rebuilding it dataset on every run.
#
# INPUT
# One or more .csv files with auxiliary data for the Climatescope. 
# Check the Readme.md for more information about the structure.
#
# OUTPUT
# - a set of JSON files that will serve as the internal API
#
# USAGE
#
# Example: python cs-auxiliary.py


import sys
import os
import os.path
import csv
import shutil
import json


# Directory structure
src_dir = 'source/'
export_dir = 'data/'
tmp_dir = 'tmp/'

# Source - filenames / dirs
src_auxiliary = src_dir + 'cs-auxiliary/'
src_meta_aa = src_dir + 'meta/admin_areas.csv'

# Languages
langs = ['en','es']
# Years we have want data for
yrs = [2006,2007,2008,2009,2010,2011,2012,2013]
# The current edition
current_edition = 2014


indicators = [
  {
    "id": 107,
    "export": 'installed-capacity',
    "title": {
      "en": 'Installed capacity',
      "es": 'Capacidad instalada'
    },
    "labelx": {
      "en": 'year',
      "es": 'año'
    },
    "labely": {
      "en": 'MW',
      "es": 'MW'
    },
    "subindicators": [
      {
        "en": 'All Energy',
        "es": 'All Energy'
      },
      {
        "en": 'Clean Energy',
        "es": 'Clean Energy'
      }
    ],
    "years": yrs
  },
  {
    "id": 201,
    "export": 'clean-energy-investments',
    "title": {
      "en": 'Clean energy investments',
      "es": 'Inversiones en energías limpias'
    },
    "labelx": {
      "en": 'year',
      "es": 'año'
    },
    "labely": {
      "en": 'USDm',
      "es": 'USDm'
    },
    "subindicators": [
      {
        "en": 'Clean energy investments',
        "es": 'Clean energy investments'
      },
    ],
    "years": yrs
  },
]

def check_dir(d):
  """Check if a folder (d) exists. If so, ask user to delete it first.
  """
  if os.path.exists(d):
    print 'The directory \'%s\' seems to exist already. Please remove it and run this script again.' % (d)
    return True
  else:
    return False


def get_aa_list():
  """
  Returns a list of iso codes for the states and countries from the admin_areas.csv
  """
  aareas = [];
  ifile = csv.DictReader(open(src_meta_aa))
  for row in ifile:
    if row["type"] == 'country' or row["type"] == 'state':
      aareas.append(row["iso"])
  return aareas


def clean_tmp(full = False):
  """Clean up the temporary directory.

  Parameters
  ----------
  full      : boolean
              If full is set to True, the tmp directory itself will be deleted
              as well.
  """
  if full:
    shutil.rmtree(tmp_dir)
  else:
    for fn in os.listdir(tmp_dir):
      file_path = os.path.join(tmp_dir, fn)
      try:
        os.unlink(file_path)
      except Exception, e:
        print e
   

def main():

  #############################################################################
  # 0.
  #

  # Check if tmp folder exists, otherwise create it
  if check_dir(tmp_dir) == True:
    sys.exit(0)
  else:
    os.makedirs(tmp_dir)

  # Build the list with countries and states
  admin_areas = get_aa_list()

  for ind in indicators:
    fn_source = src_auxiliary + str(current_edition) + '-' + str(ind["id"]) + '.csv'

    for aa in admin_areas:
      for lang in langs:
        # Initialize the array that will be written to JSON
        json_data = {"title": ind["title"][lang], "label-x": ind["labelx"][lang], "label-y": ind["labely"][lang], "data": []}

        for si in ind["subindicators"]:
          # Initialize the object for the subindicator    
          si_to_append = {"name": si[lang], "values": []}

          # Read in the CSV file
          ifile = csv.DictReader(open(fn_source))
          for row in ifile:
            # The name of the subindicators in the source file are in English
            if aa == row["iso"] and si["en"] == row["sub_indicator"]:
              values_to_append = []
              for yr in ind["years"]:
                yr_to_append = {"year": yr, "value":row[str(yr)]}
                values_to_append.append(yr_to_append)
              si_to_append["values"] = values_to_append

          json_data["data"].append(si_to_append)

        # Write the list to a JSON file
        with open(export_dir + lang + '/api/auxiliary/' + ind["export"] + '/' + aa.lower() + '.json','w') as ofile:
          json.dump(json_data, ofile)

  # Fully remove the temp directory
  clean_tmp(True)
  
  print "All done. The auxiliary data has been prepared for use on global-climatescope.org."

if __name__ == "__main__":
  main()