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
  """Check if a folder (d) exists. If so, ask user to delete it first.
  """
  if os.path.exists(d):
    print 'The directory \'%s\' seems to exist already. Please remove it and run this script again.' % (d)
    return True
  else:
    return False


def get_years(current=True):
  """Return a set with the years there is core data for.

  Parameters
  ----------
  current   : boolean
              If set to false, only the previous years are returned.
  """
   # Check which years are available
  years = set()
  for fn in os.listdir(src_core):
    years.add(os.path.splitext(fn)[0])
  
  if not current:
    current_yr = max(years)
    years.remove(current_yr)

  return years


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
   

def build_col_index(fn,sheet):
  """Build an index for the columns in the Excel sheet that should be parsed.

  Parameters
  ----------
  fn        : string
              Filename of the Excel to be parsed
  sheet     : string
              The name of the sheet in the Excel file.
  """
  df = pd.read_excel(fn,sheet)

  # Store the sheet's original header in list
  cols_src = df.columns.values.tolist()

  # Index the relevant columns
  cols_index = []
  for col in core_data_cols:
    cols_index.append(cols_src.index(col))
  return cols_index


def build_json_aa(aa,df_data,lang,detailed=False,historic=False,single_p=None):
  """Build the dict with data for a particular administrative area for export
  to JSON.
  
  Parameters
  ----------
  aa        : string
              The ISO 3166-alpha2 code of the administrative area.
  df_data   : dataframe
              The dataframe containing the data.
  lang      : string
              The active language
  detailed  : boolean (optional, default = False)
              When set to True, detailed indicator data will be provided.
  historic  : boolean (optional, default = False)
              When set to True, data of previous years will be included.
  single_p  : int (optional, default = None)
              By default, the function returns data for all parameters. When
              the id of a single parameter is passed, only data for that 
              parameter is returned.
  """

  aa_data = {}
  years = get_years()

  # Slice the dataframe to only contain the data for the administrative area
  df_aa = df_data.loc[aa]
  
  # Load metadata for the admin areas
  aa_data['iso'] = aa.lower()
  aa_data['name'] = df_meta_aa.ix[aa,'name:' + lang]
  aa_data['grid'] = df_meta_aa.ix[aa,'grid']
  
  if detailed:
    # Provide the score for all editions
    sl = []
    for yr in years:
      # For each year, we're storing an object with year and the value
      yr_data = {}
      yr_data['value'] = round(df_aa.loc[(0),yr],2)
      yr_data['year'] = int(yr)
      sl.append(yr_data)
    aa_data['score'] = sl
  else:
    # Add the score for this year
    aa_data['score'] = round(df_aa.loc[(0),current_yr],2)


  # Not every type of admin area has all the rankings
  # Check if it exists in the index
  if 'or' in df_aa.index and pd.notnull(df_aa.ix[('or'),current_yr]):
    aa_data['overall_ranking'] = int(df_aa.loc[('or'),current_yr])
  if 'rr' in df_aa.index and pd.notnull(df_aa.ix[('rr'),current_yr]):
    aa_data['regional_ranking'] = int(df_aa.loc[('rr'),current_yr])
  if 'sr' in df_aa.index and pd.notnull(df_aa.ix[('sr'),current_yr]):
    aa_data['state_ranking'] = int(df_aa.loc[('sr'),current_yr])


  # The parameters are stored as a list with dicts. By default, it returns the
  # value for the current edition.
  # If detailed is set to True, then data for all parameters and indicators 
  # are returned.
  # If a single_p is defined, data about one parameter is returned. If not,
  # then all parameters are processed.

  # Check if all parameters should be processed (default), or one in particular
  if single_p == None:
    params = index_param
  else:
    params = single_p

  param_list = []
  for param in params:
    param_data = {}
    
    if single_p == None:
      # Add data to the param_data dict
      proper_dict = param_data

      # If all parameters are processed, include meta information
      proper_dict['id'] = int(param)
      proper_dict['name'] = df_meta_index.ix[param,'name:' + lang]
      proper_dict['weight'] = round(df_meta_index.ix[param,'weight'],2)
    else:
      # If dealing with a single parameter, add everything straight to the
      # aa_data dict
      proper_dict = aa_data

    
    if historic:
      # Provide the value for all editions
      pl = []
      for yr in years:
        # For each year, we're storing an object with year and the value
        yr_data = {}
        yr_data['value'] = round(df_aa.loc[(float(param)),yr],2)
        yr_data['year'] = int(yr)
        pl.append(yr_data)
      # Add the list with historic data to the correct dict
      proper_dict['data'] = pl
    else:
      # Otherwise just provide the value for the current year
      proper_dict['value'] = round(df_aa.loc[(float(param)),current_yr],2)


    if detailed:
      # If detailed is True, then provide data on all indicators

      # The indicator_group is a list with dicts for each indicator
      # Fetch the indicator groups for this parameter
      param_groups = build_set(param,'parent','id',src_meta_index)
      gl = []
      for group in param_groups:
        group_data = {}
        group_data['name'] = df_meta_index.ix[group,'name:' + lang]
        gl.append(group_data)

        # Build a set with all the indicators for this group
        group_inds = build_set(group,'parent','id',src_meta_index)
        il = []
        for ind in group_inds:
          # Not every country has data on every indicator. Check if it's in the index.
          if float(ind) in df_aa.index:
            ind_data = {}
            ind_data['id'] = ind
            ind_data['name'] = df_meta_index.ix[ind,'name:' + lang]
            
            if historic:
              # Provide values for all editions
              ind_yr = []
              for yr in years:
                # For each year, we're storing an object with year and the value
                yr_data = {}
                yr_data['value'] = round(df_aa.ix[float(ind),yr],2)
                yr_data['year'] = int(yr)
                ind_yr.append(yr_data)
              ind_data['data'] = ind_yr
            else:
              # Provide the value for the current edition only
              ind_data['value'] = round(df_aa.ix[float(ind),current_yr],2)
            il.append(ind_data)
        group_data['indicators'] = il

      proper_dict['indicator_groups'] = gl

    param_list.append(param_data)

  if single_p == None:
    # Only append the parameter list to the country dict if dealing with
    # multiple parameters
    aa_data['parameters'] = param_list


  # When dealing with a country, add data about the states
  if df_meta_aa.ix[aa,'type'] == 'country':
    # Check if there are any states or provinces for this country
    country_states = build_set(aa,'country','iso',src_meta_aa)

    # Loop over the country states
    state_list = []
    if country_states:
      for state in country_states:
        # Call this function for all the states. All optional parameters are 
        # passed on, except for detailed. For the children, we're only
        # interested in high level data.
        state_data = build_json_aa(state,df_data,lang,detailed=False,historic=historic,single_p=single_p)
        state_list.append(state_data)

    # Even when there are no states, an empty list has to be printed
    aa_data['states'] = state_list

  return aa_data


def get_rank(aa,vid,df,name):
  """Build a dataframe that ranks the score of a list of administrative areas
  for a particular variable. 

  Parameters
  ----------
  aa        : list
              A list of iso codes (strings) to process
  id        : float
              The id of the variable (score/param/indicator) to rank
  df        : dataframe
              The dataframe to process, multi-indexed on 'iso' and 'id'
  name      : string
              The name of the rank (eg. 'or').
  """

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
  years = get_years()
  
  # Store the current year
  global current_yr
  current_yr = max(years)

  # Build a set with parameters available in the meta file.
  global index_param
  index_param = build_set('param','type','id',src_meta_index)

  # Read in the files with meta-data and set the scope to global
  global df_meta_aa
  df_meta_aa = pd.read_csv(src_meta_aa,index_col='iso')
  global df_meta_index
  df_meta_index = pd.read_csv(src_meta_index,index_col='id')


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


  # 2.1 Generate the main CSV and JSON
  for lang in langs:

    # Generate the main JSON
    # The JSON will contain a list with dicts
    json_data = []
    
    # Loop over the countries list
    for country in countries:
      country_data = build_json_aa(country,df_full,lang)
      json_data.append(country_data)

    # Write the list to a JSON file
    with open('data/' + lang + '/api/countries.json','w') as ofile:
      json.dump(json_data, ofile)


    # Generate the CSV
    # Only interested in the score, the parameters and the rankings
    rankings = set(['or','rr','sr'])
    spr = list(index_param | index_score | rankings)
    
    # Slice the DF to only contain the score and parameters for the current year.
    df_main_csv = df_full.loc[(slice(None)),current_yr]
    # Reset the index, so we can pivot the df
    df_main_csv = df_main_csv.reset_index()
    # Pivot the dataframe
    df_main_csv = df_main_csv.pivot(index='iso',columns='id',values=current_yr)
    
    fn = export_dir + lang + '/download/climatescope-main.csv'
    df_main_csv.to_csv(fn,encoding='UTF-8')


  # 2.2 Generate the regional CSV and JSON
  for region in regions:
    # Build a set with the admin areas for this region
    aa_region = build_set(region,'region','iso',src_meta_aa)
    aal = list(aa_region)

    # Remove states from this set, leaving countries
    c_region = aa_region.difference(states)
    
    # Filter the main csv on region. Used to generate CSV.
    df_region_csv = df_main_csv.loc[aal,:]

    for lang in langs:
      # Generate the regional JSONs
      # The JSON contains a dict with id, name and a countries list
      json_data = {}
      json_data['id'] = region
      json_data['name'] = df_meta_aa.ix[region,'name:' + lang]

      # The JSON will contain a list with dicts
      country_list = []
      # Loop over the countries list for the region
      for country in c_region:
        country_data = build_json_aa(country,df_full,lang)
        country_list.append(country_data)

      json_data['countries'] = country_list
  
      # Write the list to a JSON file
      with open('data/' + lang + '/api/regions/' + region + '.json','w') as ofile:
        json.dump(json_data, ofile)

      # Generate the CSV files
      fn = export_dir + lang + '/download/regions/climatescope-' + region + '.csv'
      df_region_csv.to_csv(fn,encoding='UTF-8')


  # 2.3 Generate the country + state files
  for aa in admin_areas:

    # Only include data for the administrative area in the dataframe. Used to generate CSV.
    df_aa = df_full.loc[aa,:]

    for lang in langs:
      # Generate the country and state JSON's
      json_data = build_json_aa(aa,df_full,lang,detailed=True,historic=True)
      
      # Write the list to a JSON file
      with open('data/' + lang + '/api/countries/' + aa.lower() + '.json','w') as ofile:
        json.dump(json_data, ofile)
      

      # Generate the CVS files
      # The previous .loc removed the iso code from the index, but we still need it
      # Reset the index
      df_aa = df_aa.reset_index()
      # Add a column with the iso code
      df_aa['iso'] = aa
      # Set the index of the DF to the ISO code and ID of the indicator
      df_aa.set_index(['iso','id'],inplace=True)
      # Make sure the index is sorted so slicing works well
      df_aa.sortlevel(inplace=True)

      fn = export_dir + lang + '/download/admin-areas/climatescope-' + aa.lower() + '.csv'
      df_aa.to_csv(fn)


  # 2.4 Generate the parameter CSVs
  for p in index_param:
    df_param = df_full.loc[(slice(None)),:]
    for lang in langs:
      
      json_data = {}
      json_data['id'] = int(p)
      json_data['name'] = df_meta_index.ix[p,'name:' + lang]
      json_data['weight'] = round(df_meta_index.ix[p,'weight'],2)

      # The JSON will contain a list with dicts
      country_list = []
      # Loop over the countries
      for country in countries:
        country_data = build_json_aa(country,df_full,lang,detailed=False,historic=True,single_p=p)
        country_list.append(country_data)

      json_data['countries'] = country_list

      # Generate the parameter JSONs
      with open('data/' + lang + '/api/topic/' + p + '.json','w') as ofile:
        json.dump(json_data, ofile)

      # Generate the CSV
      fn = export_dir + lang + '/download/parameters/climatescope-' + str(p) + '.csv'
      df_param.to_csv(fn,encoding='UTF-8')


  # Fully remove the temp directory
  clean_tmp(True)

if __name__ == "__main__":
  main()