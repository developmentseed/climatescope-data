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


def merge_csv(fn):
  "Merge all CSV files in the temporary directory."
  files = glob.glob(tmp_dir + "/*.csv")
  df_merged = pd.DataFrame()  
  for csv in files:
    df = pd.read_csv(csv)
    df_merged = df_merged.append(df, ignore_index=True)
  df_merged.to_csv(fn,index=0)


def main():

  # Check if tmp folder exists, otherwise create it
  if check_dir(tmp_dir) == True:
    sys.exit(0)
  else:
    os.makedirs(tmp_dir)

  # 1. Store the relevant core data for each year in one big CSV

  # Build the different lists with things we have to loop over.
  years = list_years()
  countries = build_list('country','iso',src_meta_aa)
  states = build_list('state','iso',src_meta_aa)

  for year in years:
    fn = src_core + year + '.xlsx'

    for sheet in core_data_sheets:
      
      # Build an index to parse only the relevant columns
      cols_index = build_col_index(fn,sheet)

      # Read Excel (parsing only relevant cols) and store them as temp CSV
      df = pd.read_excel(fn,sheet,parse_cols = cols_index)

      # Add column with year and a column with the type
      df['year'] = year
      df['type'] = sheet

      df.to_csv(tmp_dir + sheet + year + '.csv', encoding='latin-1',index=0)
      
  # Merge the CSV files
  merge_csv(fn_core_full_csv)
  clean_tmp()


  # Fully remove the temp directory
  clean_tmp(True)

if __name__ == "__main__":
  main()