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
import numpy as np
import shutil
import json

import settings
from utils.utils import check_dir, clean_dir, check_create_folder, write_json


def get_aa_list():
  """  Returns a list of iso codes for the states and countries from the admin_areas.csv
  """
  aareas = [];
  ifile = csv.DictReader(open(settings.src_meta_aa))
  for row in ifile:
    if row["type"] == 'country' or row["type"] == 'state':
      aareas.append(row["iso"])
  return aareas


def default_chart(chart, admin_areas):
  """ The default charts
  """

  ind_source = settings.src_auxiliary + str(settings.current_edition) + '-' + str(chart["id"]) + '.csv'

  for aa in admin_areas:
    iso = aa.lower()
    for lang in settings.langs:
      # Initialize the array that will be written to JSON
      json_data = {"name": iso, "iso": iso, "meta": {"title": chart["title"][lang], "label-x": chart["labelx"][lang], "label-y": chart["labely"][lang]}, "data": []}

      for serie in chart["series"]:
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
          if aa == row["iso"] and serie["source-id"].strip() == row["sub_indicator"].strip():
            values_to_append = []
            for yr in chart["years"]:
              try:
                yr_to_append = {"year": yr, "value": float(row[str(yr)])}
              except ValueError:
                yr_to_append = {"year": yr, "value": 0}
              values_to_append.append(yr_to_append)
            serie_to_append["values"] = values_to_append

        json_data["data"].append(serie_to_append)

      # Write the list to a JSON file
      file_path = (settings.exp_aux_json).format(lang=lang,indicator=chart["export"],aa=iso)
      write_json(file_path, json_data)


def main():

  #############################################################################
  # 0.
  #

  # Check if tmp folder exists, otherwise create it
  check_create_folder(settings.tmp_dir)
  
  # Build the list with countries and states
  admin_areas = get_aa_list()

  for chart in settings.charts:
    chart['function'](chart, admin_areas)
  
  # Fully remove the temp directory
  clean_dir(settings.tmp_dir, True)

  print "All done. The auxiliary data has been prepared for use on global-climatescope.org."

if __name__ == "__main__":
  main()