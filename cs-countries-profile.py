#!/usr/bin/python
# -*- coding: UTF-8 -*-

# This script takes a CSV with profile data for an administrative area and
# produces a JSON to be used on the page of the area.
#
# INPUT
#
# OUTPUT
#
# USAGE
#
# Example: python cs-profile.py

import sys
import os
import os.path
import csv
import shutil
import json
import errno


# Directory structure
src_dir = 'source/'
export_dir = 'data/'

# Source - filenames / dirs
src_meta_aa = src_dir + 'meta/admin_areas.csv'
src_profile_aa = src_dir + 'cs-profiles/profiles.csv'
# Directory path for final data export.
# Language will be replaced before saving the file.
country_profile_export = export_dir + '{lang}/api/countries-profile/'

langs = ['en', 'es']
indicators = [
  {
    "id": "gdp",
    "name": {
      "en": "GDP",
      "es": "PIB"
    },
    "unit": {
      "en": "$bn",
      "es": "$mm"
    }
  },
  {
    "id": "growth_rate",
    "name": {
      "en": "Five-year economic growth rate",
      "es": "Tasa de Crecimiento Anual Compuesto del PIB en 5 Años"
    },
    "unit": {
      "en": "%",
      "es": "%"
    },
    "conversion": "percent|round2"
  },
  {
    "id": "population",
    "name": {
      "en": "Population",
      "es": "Población"
    },
    "unit": {
      "en": "m",
      "es": "m"
    }
  },
  {
    "id": "clean_energy_investments",
    "name": {
      "en": "Total clean energy investments, 2012-2016",
      "es": "Total de Inversiones Acumuladas de Energía Limpia, 2012-2016"
    },
    "unit": {
      "en": "$bn",
      "es": "$mm"
    }
  },
  {
    "id": "installed_power_capacity",
    "name": {
      "en": "Installed power capacity",
      "es": "Potencia Instalada"
    },
    "unit": {
      "en": "GW",
      "es": "GW"
    }
  },
  {
    "id": "renewable_share",
    "name": {
      "en": "Renewable share",
      "es": "Proporción de Renovables"
    },
    "unit": {
      "en": "%",
      "es": "%"
    },
    "conversion": "percent|round2"
  },
  {
    "id": "clean_energy_generation",
    "name": {
      "en": "Total clean energy generation",
      "es": "Generación Total de Energía Limpia"
    },
    "unit": {
      "en": "GWh",
      "es": "GWh"
    }
  }
]


def clean_dir(path):
  """Cleans a directory by deleting it and creating it again.
  
  Parameters
  ----------
  path      : string
              The directory to wipe
  """
  try:
    shutil.rmtree(path)
  except OSError as exception:
    if exception.errno != errno.ENOENT:
      raise
  try:
    os.makedirs(path)
  except OSError as exception:
    if exception.errno != errno.EEXIST:
      raise


def get_aa_list():
  """ Returns a list of iso codes for the states and countries from the admin_areas.csv
  """
  aareas = [];
  ifile = csv.DictReader(open(src_meta_aa))
  for row in ifile:
    if row["type"] == 'country' or row["type"] == 'state':
      aareas.append(row["iso"])
  return aareas


def apply_conversion(conversion_str, value):
  """Applies a series of conversions to a value.
  The value is converted to float so it only makes sense to
  use this on numeric values.

  Parameters
  ----------
  conversion_str: : string
                    The conversions to apply separated by |
  value:          : mixed
                    The value to which the conversions are to be applied
  """

  if conversion_str == '' or conversion_str == None:
    return value

  conversions = conversion_str.split('|');
  for conv in conversions:
    if conv == 'round1':
      value = round(float(value), 1)
    elif conv == 'round2':
      value = round(float(value), 2)
    elif conv == 'round3':
      value = round(float(value), 3)
    elif conv == 'round4':
      value = round(float(value), 4)
    elif conv == 'million':
      value = float(value) / 1000000
    elif conv == 'int':
      value = int(value)
    elif conv == 'percent':
      value = float(value) * 100

  return value


def main():
  # Prepare export directories.
  for lang in langs:
    clean_dir(country_profile_export.format(lang=lang))

  # Build the list with countries and states
  admin_areas = get_aa_list()

  for aa in admin_areas:
    iso = aa.lower()
    for lang in langs:
      # Init with defaults.
      country_data = { 'name': iso, 'iso': iso, 'indicators': [] }

      # Read the profile data
      profile_data = csv.DictReader(open(src_profile_aa))
      for row in profile_data:
        if row["iso"] == aa:
          for indicator in indicators:
            id_ind = indicator['id']

            # Only interested in the indicator if there is data
            if row[id_ind]:
              indicator_to_append = { 'id': id_ind, 'name': indicator['name'][lang], 'unit': indicator['unit'][lang] }
              if 'conversion' in indicator:
                indicator_to_append['value'] = apply_conversion(indicator['conversion'], row[id_ind])
              else:
                indicator_to_append['value'] = float(row[id_ind])
              country_data['indicators'].append(indicator_to_append)

      # Write the list to a JSON file
      file_path = (country_profile_export + '{iso}.json').format(lang=lang, iso=iso)
      with open(file_path, 'w') as ofile:
        json.dump(country_data, ofile)


if __name__ == "__main__":
  main()
