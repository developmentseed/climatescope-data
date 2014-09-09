#!/usr/bin/python
# -*- coding: UTF-8 -*-

# Script to process core data of the Climatescope. Given the limited amount of
# times the data will be updated, the script works as a make file: rebuilding
# the full dataset on every run.
#
# INPUT
# One or more .xlsx files with data about the Climatescope. Every file contains
# data on a different year. Check the Readme.md for more information about the
# structure.
#
# OUTPUT
# - a set of JSON files that will serve as the internal API
# - a set of CSV files, mostly used by users to download contextual data
#
# USAGE
#
# Example: python cs-core.py
#
#
#
#
# Preliminary structure:
#
# 0. sanity checks
#   - all sheets in xlsx
#   - correct headers
#   - year specified in filename
# 1. store all years in one CSV
# 2. generate csv's
# 3. generate json
#
# TECH DEBT / TODO
# - build_col_index(): reading in the whole excel sheet to just fetch the header
# - check what's up with CN-65 & CD. Has strange character that needs to be sanitized
# - add metadata about indicators and admin areas to CSV's (incl. i18n)
# - automatically generate all the folders


import sys
import os
import os.path
import shutil
import pandas as pd
import glob

# Directory structure
src_dir = 'source/'
export_dir = 'data/'
tmp_dir = 'tmp/'

# Source - filenames / dirs
src_core = src_dir + 'cs-core/'
src_meta_aa = src_dir + 'meta/admin_areas.csv'
src_meta_index = src_dir + 'meta/index.csv'

# Export - filenames / dirs
exp_core_csv = export_dir + 'cs-core.csv'

# Source structure
core_data_sheets = ['score', 'param', 'ind']
core_data_cols = ['id', 'iso', 'score']

# Languages
langs = ['en','es']


def check_dir(d):
  "Check if a folder exists. If so, ask user to delete it first."
  if os.path.exists(d):
    print 'The directory \'%s\' seems to exist already. Please remove it and run this script again.' % (d)
    return True
  else:
    return False


def list_years():
  "Build a list with the years there is data for."
   # Check which years are available
  years = []
  for fn in os.listdir(src_core):
    years.append(os.path.splitext(fn)[0])
  return years


def build_set(search,search_col,result,csv):
  "Build a set from a CSV file, iterating over rows and storing the value of 'result' column when the 'search' is found in the 'search_col'."
  df = pd.read_csv(csv)
  s = set()
  for index, row in df.iterrows():
    if row[search_col] == search:
      s.add(row[result])
  return s


def clean_tmp(full = False):
  "Clean up the temporary directory. If full == 1, the tmp directory itself will be deleted as well."
  if full:
    shutil.rmtree(tmp_dir)
  else:
    for fn in os.listdir(tmp_dir):
      file_path = os.path.join(tmp_dir, fn)
      try:
        os.unlink(file_path)
      except Exception, e:
        print e
   

def build_col_index(fn,sheet):
  "Build an index for the columns in the Excel sheet that should be parsed."
  df = pd.read_excel(fn,sheet)

  # Store the sheet's original header in list
  cols_src = df.columns.values.tolist()

  # Index the relevant columns
  cols_index = []
  for col in core_data_cols:
    cols_index.append(cols_src.index(col))
  return cols_index


def main():

  # Check if tmp folder exists, otherwise create it
  if check_dir(tmp_dir) == True:
    sys.exit(0)
  else:
    os.makedirs(tmp_dir)

  # Build the different sets with things we have to loop over.
  regions = build_set('region','type','iso',src_meta_aa)
  countries = build_set('country','type','iso',src_meta_aa)
  states = build_set('state','type','iso',src_meta_aa)
  admin_areas = countries | states
  index_score = build_set('score','type','id',src_meta_index)
  index_param = build_set('param','type','id',src_meta_index)
  years = list_years()
  current_yr = max(years)

  # 1. Store the relevant core data for each year in one big CSV
  first_yr = True

  for year in years:
    # All core data files are named after the year of the edition
    fn = src_core + year + '.xlsx'

    df_yr = pd.DataFrame()
    for sheet in core_data_sheets:
      
      # Build an index to parse only the relevant columns
      cols_index = build_col_index(fn,sheet)

      # Read Excel (parsing only relevant cols)
      df_sheet = pd.read_excel(fn,sheet,parse_cols = cols_index)

      # Append each sheet to a dataframe holding the data for that year
      df_yr = df_yr.append(df_sheet, ignore_index=True)

    # Rename the column 'score' to year
    df_yr.rename(columns={'score':year}, inplace=True)

    if first_yr:
      # If it's the first year, we initialize the full DataFrame
      df_full = df_yr
      first_yr = False
    else:
      # Every subsequent year will have to be merged into df_full
      df_full = pd.merge(df_full,df_yr,on=['iso','id'])

  df_full.to_csv(exp_core_csv,encoding='UTF-8',index=0)
  
  # 2.1 Generate the main CSV

  # Filter out only the score and parameters
  df = df_full[df_full['id'].isin(index_param | index_score)]

  # Pivot the dataframe and use only the data of the current edition
  df_main = df.pivot(index='iso',columns='id',values=current_yr)
  for lang in langs:
    fn = export_dir + lang + '/download/climatescope-main.csv'
    df_main.to_csv(fn,encoding='UTF-8')

  # 2.2 Generate the region CSVs
  for region in regions:
    # Build a set with the admin areas for this region
    aa_region = build_set(region,'region','iso',src_meta_aa)

    # Filter the main dataframe of the current edition on region
    df_region = df_main.loc[aa_region]
    for lang in langs:
      fn = export_dir + lang + '/download/regions/climatescope-' + region + '.csv'
      df_region.to_csv(fn,encoding='UTF-8')

  # 2.3 Generate the country + state CSVs
  for aa in admin_areas:
    df_aa = df_full[df_full['iso'] == aa]
    # Drop the ISO column
    df_aa1 = df_aa.drop(['iso'],axis=1)
    for lang in langs:
      fn = export_dir + lang + '/download/admin-areas/climatescope-' + aa + '.csv'
      df_aa1.to_csv(fn,index=0)

  # 2.4 Generate the parameter CSVs
  for param in index_param:
    df_param = df_full[df_full['id'] == param]
    # Drop the id column
    df_param1 = df_param.drop(['id'],axis=1)
    for lang in langs:
      fn = export_dir + lang + '/download/parameters/climatescope-' + str(param) + '.csv'
      df_param.to_csv(fn,encoding='UTF-8',index=0)

  # Fully remove the temp directory
  clean_tmp(True)

if __name__ == "__main__":
  main()