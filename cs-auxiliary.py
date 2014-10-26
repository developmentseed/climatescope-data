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
import pandas as pd
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
    "name": 'installed-capacity',
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
    "name": 'clean-energy-investments',
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


def build_set(search,search_col,result,csv):
  """Perform a lookup and return the matching results for the row in a set
  
  Parameters
  ----------
  search    : string
              The value to search for
  search_col: string
              The column to perform the search on
  result    : string
              The column with the result
  csv       : string
              The name of the CSV file to be parsed
  """
  df = pd.read_csv(csv)
  s = set()
  for index, row in df.iterrows():
    if row[search_col] == search:
      s.add(row[result])
  return s


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

  # Build the different sets of admin areas with things we have to loop over.
  countries = build_set('country','type','iso',src_meta_aa)
  states = build_set('state','type','iso',src_meta_aa)
  admin_areas = countries | states
  
  for ind in indicators:
    fn_source = src_auxiliary + str(current_edition) + '-' + str(ind["id"]) + '.csv'

    for aa in admin_areas:
      for lang in langs:
        # Initialize the array that will be written to JSON
        json_data = []

        for si in ind["subindicators"]:
          # Initialize the object for the subindicator    
          si_to_append = {"name": si[lang], "values": []}

          # Read in the CSV file
          ifile = csv.DictReader(open(fn_source))
          for row in ifile:
            # The name of the subindicators are always in English
            if aa == row["iso"] and si["en"] == row["sub_indicator"]:
              values_to_append = []
              for yr in ind["years"]:
                yr_to_append = {"year": yr, "value":row[str(yr)]}
                values_to_append.append(yr_to_append)
              si_to_append["values"] = values_to_append

          json_data.append(si_to_append)

        # Write the list to a JSON file
        with open(export_dir + lang + '/api/auxiliary/' + ind["name"] + '/' + aa.lower() + '.json','w') as ofile:
          json.dump(json_data, ofile)

  print "All done. The auxiliary data has been prepared for use on global-climatescope.org."

if __name__ == "__main__":
  main()