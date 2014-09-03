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
# 1. sanity checks
#   - all sheets in xlsx
#   - correct headers
#   - year specified in filename
# 2. store all years in one CSV
# x. convert xlsx to csv
# x. store countries in dict
# x. generate csv's
# x. generate json
#
# TECH DEBT / TODO
# - build_col_index(): reading in the whole excel sheet to just fetch the header
# - merge_csv(): year stored as dtype float64


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

# Export - filenames
fn_core_full_csv = export_dir + 'cs-core.csv'

# Source structure
core_data_sheets = ['score', 'param', 'ind']
core_data_cols = ['id', 'iso', 'score']

# Languages
lang = ['en','es']


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


def build_list(search,result,csv):
  "Build a list from a CSV file, iterating over rows and storing the 'result' column when the 'search' matches."
  df = pd.read_csv(csv)
  l = []
  for index, row in df.iterrows():
    if row['type'] == search:
      l.append(row[result])
  return l


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

  # Build the different lists with things we have to loop over.
  countries = build_list('country','iso',src_meta_aa)
  states = build_list('state','iso',src_meta_aa)
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

  df_full.to_csv(fn_core_full_csv,encoding='UTF-8',index=0)
  
  # Fully remove the temp directory
  clean_tmp(True)

if __name__ == "__main__":
  main()