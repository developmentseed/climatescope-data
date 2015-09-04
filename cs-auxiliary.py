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

# Export filename of the json files
export_ind = export_dir + '{lang}/api/auxiliary/{indicator}/{aa}.json'

# Languages
langs = ['en','es']
# Years we have want data for
yrs = [2006,2007,2008,2009,2010,2011,2012,2013]
# The current edition
current_edition = 2014


indicators = [
  {
    "id": 107, # The source file contains an indication of the id
    "custom": True,
    "export": 'installed-capacity', # Folder for the exported data
    "title": { # Title of the chart
      "en": 'Installed capacity',
      "es": 'Capacidad instalada'
    },
    "labelx": { # Label of the x-axis
      "en": 'year',
      "es": 'año'
    },
    "labely": { # Label of the y-axis
      "en": 'MW',
      "es": 'MW'
    },
    "series": [
      {
        "id": 'non-clean-energy', # The id used in the export
        "source-id": 'Non-clean Energy', # The id in the source CSV
        "level": "country", # Data on country level. When 'regional' or 'global' is used, averages are calculated
        "name": {
          "en": 'Non-clean Energy',
          "es": 'Energía no limpia'
        }
      },
      {
        "id": 'clean-energy', # The id used in the export
        "source-id": 'Clean Energy', # The id in the source CSV
        "level": "country",
        "name": {
          "en": 'Clean Energy',
          "es": 'Energía limpia'
        }
      }
    ],
    "years": yrs # List with years to process
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
    "series": [
      {
        "id": 'country',
        "source-id": "Clean energy investments",
        "level": "country",
      }
    ],
    "years": yrs
  },
  {
    "id": 401,
    "export": 'carbon-offset-projects',
    "title": {
      "en": 'Carbon offset projects by sector',
      "es": 'Compensaciones de carbono por sector'
    },
    "labelx": {
      "en": 'category',
      "es": 'categoria'
    },
    "labely": {
      "en": '',
      "es": ''
    },
    "series": [
      {
        "id": 'power-generation',
        "source-id": "Power generation",
        "level": "country",
        "name": {
          "en": 'Power generation',
          "es": 'Generación eléctrica'
        }
      },
      {
        "id": 'methane',
        "source-id": "Methane",
        "level": "country",
        "name": {
          "en": 'Methane',
          "es": 'Metano'
        }
      },
      {
        "id": 'forestry',
        "source-id": "Forestry",
        "level": "country",
        "name": {
          "en": 'Forestry',
          "es": 'Silvicultura'
        }
      },
      {
        "id": 'waste',
        "source-id": "Waste",
        "level": "country",
        "name": {
          "en": 'Waste',
          "es": 'Residuos'
        }
      },
      {
        "id": 'energy-efficiency',
        "source-id": "Energy efficiency",
        "level": "country",
        "name": {
          "en": 'Energy efficiency',
          "es": 'Eficiencia energética'
        }
      },
      {
        "id": 'other',
        "source-id": "Other",
        "name": {
          "en": 'Other',
          "es": 'Otro'
        }
      },
    ],
    "years": [2014]
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
  """  Returns a list of iso codes for the states and countries from the admin_areas.csv
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
    ind_source = src_auxiliary + str(current_edition) + '-' + str(ind["id"]) + '.csv'

    for aa in admin_areas:
      iso = aa.lower()
      for lang in langs:
        # Initialize the array that will be written to JSON
        json_data = {"name": iso, "iso": iso, "meta": {"title": ind["title"][lang], "label-x": ind["labelx"][lang], "label-y": ind["labely"][lang]}, "data": []}

        for serie in ind["series"]:
          if serie["id"] == 'country':
            # If we're dealing with a country, use the country name as label of serie
            serie_name = aa
          else:
            serie_name = serie["name"][lang]

          # Initialize the object for the serie    
          serie_to_append = {"name": serie_name, "id": serie["id"], "values": []}

          # Read in the CSV file
          ind_data = csv.DictReader(open(ind_source))
          for row in ind_data:
            if aa == row["iso"] and serie["source-id"] == row["sub_indicator"]:
              values_to_append = []
              for yr in ind["years"]:
                if row[str(yr)] == '-':
                  yr_to_append = {"year": yr, "value": 0}
                else:
                  yr_to_append = {"year": yr, "value": float(row[str(yr)])}
                values_to_append.append(yr_to_append)
              serie_to_append["values"] = values_to_append

          json_data["data"].append(serie_to_append)

        # Write the list to a JSON file
        file_path = (export_ind).format(lang=lang,indicator=ind["export"],aa=iso)
        with open(file_path,'w') as ofile:
          json.dump(json_data, ofile)

  # Fully remove the temp directory
  clean_tmp(True)

  print "All done. The auxiliary data has been prepared for use on global-climatescope.org."

if __name__ == "__main__":
  main()