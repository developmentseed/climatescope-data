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
# TECH DEBT / TODO
# - build_col_index(): reading in the whole excel sheet to just fetch the header
# - check what's up with CN-65 & CD. Has strange character that needs to be sanitized
# - automatically generate all the folders


import sys
import os
import os.path
import shutil
import json
import numpy as np
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


def get_years(current=True):
  "Return a set with the years there is core data for. If current is set to false, only the previous years are returned."
   # Check which years are available
  years = set()
  for fn in os.listdir(src_core):
    years.add(os.path.splitext(fn)[0])
  
  if not current:
    current_yr = max(years)
    years.remove(current_yr)

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


def build_main_json_aa(aa, df_data, df_meta_aa, df_meta_index, params,lang):
  "Build the dict for a particular administrative area to be used in the main JSON. 'aa' = iso code, 'df_data' = the dataframe containing the data, 'df_meta_aa' = dataframe with metadata for country, 'df_meta_index' = meta for index, 'params' = the list with parameters to get data for, 'lang' = the language being looped over."
  aa_data = {}

  # Load metadata for the admin areas
  aa_data['iso'] = aa.lower()
  aa_data['name'] = df_meta_aa.ix[aa,'name:' + lang]
  aa_data['grid'] = df_meta_aa.ix[aa,'grid']
  aa_data['score'] = round(df_data.ix[aa,0],2)


  # Not every type of admin area has all the rankings
  if pd.notnull(df_data.ix[aa,'or']):
    aa_data['overall_ranking'] = int(df_data.ix[aa,'or'])
  if pd.notnull(df_data.ix[aa,'rr']):
    aa_data['regional_ranking'] = int(df_data.ix[aa,'rr'])
  if pd.notnull(df_data.ix[aa,'sr']):
    aa_data['state_ranking'] = int(df_data.ix[aa,'sr'])


  # The parameters are stored as a list with dicts
  param_list = []
  for param in params:
    param_data = {}
    param_data['id'] = int(param)
    param_data['value'] = round(df_data.ix[aa,param],2)
    param_data['name'] = df_meta_index.ix[param,'name:' + lang]
    param_data['weight'] = round(df_meta_index.ix[param,'weight'],2)
    param_list.append(param_data)

  aa_data['parameters'] = param_list

  return aa_data


def get_rank(aa,vid,df,name):
  "Build a dataframe that ranks the score of a list of administrative areas for a particular variable. 'aa' = list of iso codes, 'id' = id of variable (score/param/indicator) to rank, 'df' = the dataframe to consume (multi-index on 'iso' and 'id'), 'name' = the name of the rank (eg. 'or')."

  # Slice the DF to only contain the administrative areas and the score/parameter/indicator ranking on. Then calculate the rank.
  df_rank = df.loc[(aa,vid),:].rank(ascending=False)

  # Reset the index, so we can override the parameter ID to the name
  df_rank.reset_index(inplace=True)
  df_rank['id'] = name
  
  # Re-index it again.
  df_rank.set_index(['iso','id'],inplace=True)

  return df_rank


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
  years = get_years()
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
      df_sheet = pd.read_excel(fn,sheet,parse_cols=cols_index)

      # Append each sheet to a dataframe holding the data for that year
      df_yr = df_yr.append(df_sheet)

    # Set the index of the DF to the ISO code and ID of the indicator
    df_yr.set_index(['iso','id'],inplace=True)
    # Make sure the index is sorted so the slicing works well
    df_yr.sortlevel(inplace=True)
    

    # Calculate the Overall Rank (or)

    # To be able to use multi-index slicing, the countries set is converted to a list.
    cl = list(countries)

    # Get the rank for the score
    df_yr_or = get_rank(cl,0,df_yr,'or')

    # Append it to the DF with the yearly data
    df_yr = df_yr.append(df_yr_or)
    df_yr.sortlevel(inplace=True)
  

    # Calculate the Regional Rank (rr)
    for region in regions:
      # Build a set with the admin areas for this region
      aa_region = build_set(region,'region','iso',src_meta_aa)
      # Filter out the states and provinces, leaving only the countries
      c_region = aa_region.difference(states)
      # Turn the set into a list to be able to build the rank
      cl = list(c_region)

      # Build the regional rank
      df_rr = get_rank(cl,0,df_yr,'rr')

      # Append it to the DF with the yearly data
      df_yr = df_yr.append(df_rr)
      df_yr.sortlevel(inplace=True)


    # Add the in-country rank to the states/provinces
    for country in countries:
      # Check if there are any states or provinces for this country
      country_states = build_set(country,'country','iso',src_meta_aa)

      if country_states:
        # Turn the set into a list
        sl = list(country_states)

        # Build the state rank
        df_sr = get_rank(sl,0,df_yr,'sr')

        # Append it to the DF with the yearly data
        df_yr = df_yr.append(df_sr)
        df_yr.sortlevel(inplace=True)


    # Rename the column 'score' to year
    df_yr.rename(columns={'score':year}, inplace=True)

    if first_yr:
      # If it's the first year, we initialize the full DataFrame
      df_full = df_yr
      first_yr = False
    else:
      # Every subsequent year will have to be merged into df_full
      df_full = pd.merge(df_full,df_yr,left_index=True,right_index=True)
      # Make sure the floats are rounded to 2 decimals
      df_full = np.round(df_full,2)

  df_full.to_csv(exp_core_csv,encoding='UTF-8')


  # Read in the files with meta-data
  df_meta_aa = pd.read_csv(src_meta_aa,index_col='iso')
  df_meta_index = pd.read_csv(src_meta_index,index_col='id')


  # 2.1 Generate the main CSV and JSON

  # Only interested in the score, the parameters and the rankings
  rankings = set(['or','rr','sr'])
  spr = list(index_param | index_score | rankings)
  # Slice the DF to only contain the score and parameters for the current year.
  df_main = df_full.loc[(slice(None),spr),current_yr]
  
  # Reset the index, so we can pivot the df
  df_main = df_main.reset_index()
  # Pivot the dataframe
  df_main = df_main.pivot(index='iso',columns='id',values='2015')

  for lang in langs:

    # Generate the main JSON
    # The JSON will contain a list with dicts
    json_data = []

    # Loop over the countries
    for country in countries:
      country_data = build_main_json_aa(country, df_main, df_meta_aa, df_meta_index, index_param,lang)

      # Check if there are any states or provinces for this country
      country_states = build_set(country,'country','iso',src_meta_aa)

      # Loop over the country states
      state_list = []
      if country_states:
        for state in country_states:
          state_data = build_main_json_aa(state, df_main, df_meta_aa, df_meta_index, index_param,lang)
          state_list.append(state_data)

      # Even when there are no states, an empty list has to be printed
      country_data['states'] = state_list

      json_data.append(country_data)

    # Write the list to a JSON file
    with open('data/' + lang + '/api/countries.json','w') as ofile:
      json.dump(json_data, ofile)

    # Generate the CSV
    fn = export_dir + lang + '/download/climatescope-main.csv'
    df_main.to_csv(fn,encoding='UTF-8')
  sys.exit(0)

  # 2.2 Generate the regional CSV and JSON
  for region in regions:
    # Build a set with the admin areas for this region
    aa_region = build_set(region,'region','iso',src_meta_aa)
    aal = list(aa_region)
    
    # Filter the main dataframe of the current edition on region
    df_region = df_main.loc[aal,:]




    for lang in langs:
      fn = export_dir + lang + '/download/regions/climatescope-' + region + '.csv'
      df_region.to_csv(fn,encoding='UTF-8')


  # 2.3 Generate the country + state CSVs
  for aa in admin_areas:
    df_aa = df_full.loc[aa,:]
    for lang in langs:
      fn = export_dir + lang + '/download/admin-areas/climatescope-' + aa + '.csv'
      df_aa.to_csv(fn)


  # 2.4 Generate the parameter CSVs
  for param in index_param:
    df_param = df_full.loc[(slice(None),param),:]
    for lang in langs:
      fn = export_dir + lang + '/download/parameters/climatescope-' + str(param) + '.csv'
      df_param.to_csv(fn,encoding='UTF-8')


  # Fully remove the temp directory
  clean_tmp(True)

if __name__ == "__main__":
  main()