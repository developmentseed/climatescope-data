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
# - automatically generate all the folders


import sys
import os
import os.path
import re
import numpy as np
import pandas as pd
import glob

from utils.utils import check_dir, clean_dir, write_json
import settings


def get_years(current=True):
  """Return a set with the years there is core data for. To determine this, the
  function loops over the contents of the source folder and checks the names of
  the files for properly formatted years.

  Parameters
  ----------
  current   : boolean
              If set to false, only the previous years are returned. Assumes 
              that the current year is the highest year in the range.
  """
   # Check which years are available
  years = list()
  fn_pattern = re.compile('^20[0-9]{2}$')

  for f in os.listdir(settings.src_core):
    fn = os.path.splitext(f)[0]
    ext = os.path.splitext(f)[-1].lower()
    path = os.path.join(settings.src_core, fn)

    if not os.path.isdir(path):
      # Only continue if dealing with file, ignore the folders
      if ext == ".xlsx":
        # Check if dealing with an .xlsx
        if fn_pattern.match(fn):
          # If the file-name is a properly formatted year, add it
          years.append(fn)

  if not current:
    current_yr = max(years)
    years.remove(current_yr)

  years.sort(reverse=True)
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
  for col in settings.core_data_cols:
    cols_index.append(cols_src.index(col))
  return cols_index


def indicator_active(aa,ind):
  """Whether an indicator is used to calculate the overall score, depends on a
  country's grid status. This function checks whether an indicator is used to
  calculate the score for a given country / state.

  Parameters
  ----------
  aa        : string
              The ISO 3166-alpha2 code of the administrative area.
  ind       : float
              The ID of the indicator.
  """

  ind_grid = df_meta_index.loc[ind,'grid']
  aa_grid = df_meta_aa.ix[aa,'grid']
  
  ind_active = False

  if ind_grid == 'both':
    # If indicator is valid for both on and off-grid countries, return True
    ind_active = True
  elif ind_grid == aa_grid:
    ind_active = True

  return ind_active


def rank_dict(df,ind,yr):
  """Returns a dict with type of ranking as key and the rank as value.
  Eg. { 'overall_ranking': 16, 'regional_ranking': 9 }

  Parameters
  ----------
  df        : dataframe
              The dataframe to fetch the rank from
  ind       : float
              The indicator we're building the rank for
  yr        : int
              The year we're interested in
  """

  # Add the rankings
  rankings = { 'gr': 'overall_ranking', 'sr': 'state_ranking' }
  aa_ranks = {}

  # Not every type of admin area has all the rankings
  # Check if it is not null and if so, add it.
  for key, value in rankings.iteritems():
    rank = df.loc[ind,(yr,key)]
    if pd.isnull(rank):
      aa_ranks[value] = None
    else:
      aa_ranks[value] = int(rank)

  return aa_ranks


def get_raw_data(df,ind,lang,yr):
  """Returns a dict with the value and unit of the raw data for an indicator.

  Parameters
  ----------
  df        : dataframe
              The dataframe to fetch the rank from
  ind       : float
              The indicator we're building the rank for
  lang      : string
              The active language
  yr        : int
              The year we're interested in
  """

  # Fetch the raw data that underlies the score of this indicator
  raw_data = {}
  raw_value = df.ix[float(ind),(yr,'data')]

  if pd.isnull(raw_value):
    # By default Pandas returns NaN, for the JSON this needs to be null
    raw_data['value'] = None
    raw_data['unit'] = None
  else:
    # If there is data, fetch the value and the unit in the proper language
    raw_data['value'] = round(raw_value,5)
    raw_data['unit'] = df_meta_index.ix[ind,'unit:' + lang]

  return raw_data


def get_rank(aal,df,name):
  """Build a dataframe that ranks a list of administrative areas on every
  variable available (score, parameter, indicator)

  Parameters
  ----------
  aal       : list
              A list of iso codes (strings) to process
  df        : dataframe
              The dataframe to process, multi-indexed on 'iso' and 'id'. The
              columns also have a hierarchy (year, 'value')
  name      : string
              The name of the rank (eg. 'or').
  """

  # Initialize an empty dataframe
  df_rank = pd.DataFrame()

  for year in years:
    
    # For each year, slice the DF on the list of administrative areas
    df_yr = df.loc[(aal,slice(None)),(year,'value')]
    
    # Substitute all the 0 value for NaN, these will not receive a ranking
    df_yr.replace(to_replace=0,value=np.nan,inplace=True)
    
    # Group by the indicator and build a rank. In case of equal values, the
    # lowest rank will assigned. (1, 2, 2, 2, 5, 6, 7, etc)
    # The rank is stored in the empty DF to ensure no previous values get
    # overridden by NaN.
    df_rank[(year, name)] = df_yr.groupby(level=1).rank(method='min',ascending=False)

  # Overwrite the NaN values in the original DF with values in the df_rank
  df.update(df_rank)
  
  return df


def build_json_aa(aa,df_data,lang,indicators=False,historic=False,single_p=None):
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
  indicators : boolean (optional, default = False)
              When set to True, detailed indicator data will be provided.
  historic  : boolean (optional, default = False)
              When set to True, data of previous years will be included.
  single_p  : int (optional, default = None)
              By default, the function returns data for all parameters. When
              the id of a single parameter is passed, only data for that 
              parameter is returned.
  """

  aa_data = {}

  # Slice the dataframe to only contain the data for the administrative area
  df_aa = df_data.loc[aa]

  # Load metadata for the admin areas
  aa_data['iso'] = aa.lower()
  aa_data['name'] = df_meta_aa.ix[aa,'name:' + lang]
  aa_data['grid'] = df_meta_aa.ix[aa,'grid']

  if historic:
    # Provide the score for all editions
    sl = []
    for yr in years:
      # For each year, we're storing an object with year and the value
      yr_data = {}
      if np.isnan(df_aa.loc[(0),(yr,'value')]):
        yr_data['value'] = None
      else:
        yr_data['value'] = round(df_aa.loc[(0),(yr,'value')],5)
      yr_data['year'] = int(yr)

      # Fetch the scores and update the yr_data dict with them
      aa_ranks = rank_dict(df_aa,0,yr)
      yr_data.update(aa_ranks)

      sl.append(yr_data)

    aa_data['score'] = sl
  else:
    # Add the score for this year
    aa_data['score'] = round(df_aa.loc[(0),(current_yr,'value')],5)

    # Fetch the rankings for the scores and update the aa_data dict with them
    aa_ranks = rank_dict(df_aa,0,current_yr)
    aa_data.update(aa_ranks)


  # In case all parameters are processed (single_p == None), the data is 
  # returned in a parameters list.
  # If single_p is defined, its data is added straight to the aa_data dict

  # Check if all parameters should be processed (default), or one in particular
  if single_p == None:
    params = index_param
  else:
    params = set([single_p])

  param_list = []
  for param in params:
    param_data = {}
    
    if single_p == None:
      # Add data to the param_data dict
      proper_dict = param_data

      # If all parameters are processed, include meta information
      proper_dict['id'] = int(param)
      proper_dict['name'] = df_meta_index.ix[param,'name:' + lang]
      proper_dict['weight'] = round(df_meta_index.ix[param,'weight'],5)
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
        if np.isnan(df_aa.loc[(float(param)),(yr,'value')]):
          yr_data['value'] = None
        else:
          yr_data['value'] = round(df_aa.loc[(float(param)),(yr,'value')],5)
        yr_data['year'] = int(yr)

        # Fetch the rankings for the param and update the yr_dict with them
        aa_ranks = rank_dict(df_aa,param,yr)
        yr_data.update(aa_ranks)

        pl.append(yr_data)
      # Add the list with historic data to the correct dict
      proper_dict['data'] = pl
    else:
      # Otherwise just provide the value for the current year
      proper_dict['value'] = round(df_aa.loc[(float(param)),(current_yr,'value')],5)

      # Fetch the rankings for the param and update the proper dict with them
      aa_ranks = rank_dict(df_aa,param,current_yr)
      proper_dict.update(aa_ranks)


    if indicators:
      # If indicators is True, then provide data on all indicators

      # The indicator_group is a list with dicts for each indicator
      # Fetch the indicator groups for this parameter
      param_groups = build_set(param,'parent','id',settings.src_meta_index)
      gl = []
      for group in param_groups:
        group_data = {}
        group_data['name'] = df_meta_index.ix[group,'name:' + lang]
        gl.append(group_data)

        # Build a set with all the indicators for this group
        group_inds = build_set(group,'parent','id',settings.src_meta_index)
        il = []
        for ind in group_inds:
          # Not every country has data on every indicator. Check if it's in the index.
          if float(ind) in df_aa.index:
            ind_data = {}
            ind_data['id'] = ind
            ind_data['name'] = df_meta_index.ix[ind,'name:' + lang]
            ind_data['description'] = df_meta_index.ix[ind,'description:' + lang]
            ind_data['active'] = indicator_active(aa,ind)
            
            if historic:
              # Provide values for all editions
              ind_yr = []
              for yr in years:
                # For each year, we're storing an object with year and the value
                yr_data = {}
                if np.isnan(df_aa.ix[float(ind),(yr,'value')]):
                  yr_data['value'] = None
                else:
                  yr_data['value'] = round(df_aa.ix[float(ind),(yr,'value')],5)
                yr_data['year'] = int(yr)

                # Fetch the rankings for the indicator and update the yr_dict with them
                aa_ranks = rank_dict(df_aa,ind,yr)
                yr_data.update(aa_ranks)

                # Fetch the raw data that underlies the score of this indicator
                yr_data['raw'] = get_raw_data(df_aa,ind,lang,yr)
                
                ind_yr.append(yr_data)

              ind_data['data'] = ind_yr

            else:
              # Provide the value for the current edition only
              ind_data['value'] = round(df_aa.ix[float(ind),(current_yr,'value')],5)

              # Fetch the rankings for the indicator and update the yr_dict with them
              aa_ranks = rank_dict(df_aa,ind,current_yr)
              ind_data.update(aa_ranks)

              # Fetch the raw data that underlies the score of this indicator
              yr_data['raw'] = get_raw_data(df_aa,ind,lang,current_yr)

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
    country_states = build_set(aa,'country','iso',settings.src_meta_aa)

    # Loop over the country states
    state_list = []
    if country_states:
      for state in country_states:
        # Call this function for all the states. At this point, only interested in
        # non-detailed data for the current version.
        state_data = build_json_aa(state,df_data,lang,indicators=False,historic=True,single_p=single_p)
        state_list.append(state_data)

    # Even when there are no states, an empty list has to be printed
    aa_data['states'] = state_list

  return aa_data


def pivot_df(df,ind,col,val):
  """Pivot a dataframe.

  Parameters
  ----------
  df        : DataFrame
              A DataFrame that is indexed on iso and id
  ind:      : string
              The column to use as index
  col:      : string
              The column use as column headers
  val:      : string
              The column to use for the values
  """
  # Reset the index, so we can pivot the df
  df = df.reset_index()
  # Pivot the dataframe
  df = df.pivot(index=ind,columns=col,values=val)

  return df


def main():

  #############################################################################
  # 0.
  #

  # Check if tmp folder exists, otherwise create it
  if check_dir(settings.tmp_dir) == True:
    sys.exit(0)
  else:
    os.makedirs(settings.tmp_dir)

  # Run some checks on the source folder with core data.
  if not get_years():
    # Is there anything in the source folder to begin with?
    print "We were not able to find a XLSX file with core data in the folder: "\
          "%s. Make sure this folder contains at least one XLSX file named "\
          "after the year (eg. 2014.xlsx). Check the readme for more info "\
          "about the required structure of these files.\n"\
          "Quiting..." % (settings.src_core)
    sys.exit(0)

  # Provide feedback that the script only processes XLSX files with properly
  # formatted filenames. (eg. 2014.xlsx)
  fn_pattern = re.compile('^20[0-9]{2}$')
  for f in os.listdir(settings.src_core):
    fn = os.path.splitext(f)[0]
    ext = os.path.splitext(f)[-1].lower()
    path = os.path.join(settings.src_core, fn)
    
    if not os.path.isdir(path):
      # Only check files
      if ext == ".xlsx":
        if not fn_pattern.match(fn):
          print "The XLSX file %s doesn't have a properly formatted year as "\
                "filename and will be ignored." % (f)
      else:
        print "The script only processes XLSX files. %s will be ignored." % (f)


  print "Loading the core and meta data..."

  # Build the different sets of admin areas with things we have to loop over.
  countries = build_set('country','type','iso',settings.src_meta_aa)
  states = build_set('state','type','iso',settings.src_meta_aa)
  admin_areas = countries | states
  
  # Build sets for the variables we loop over
  global index_param
  index_param = build_set('param','type','id',settings.src_meta_index)
  index_score = build_set('score','type','id',settings.src_meta_index)
  sp = list(index_score | index_param)

  # Build set for the years we're interested in
  global years
  years = get_years()
  global current_yr
  current_yr = max(years)


  # Read in the files with meta-data and set the scope to global
  global df_meta_aa
  df_meta_aa = pd.read_csv(settings.src_meta_aa,index_col='iso')
  global df_meta_index
  df_meta_index = pd.read_csv(settings.src_meta_index,index_col='id')


  #############################################################################
  # 1. Store the relevant core data in one DF (df_full)
  #
  #
  # Output: df_full
  #
  #             2014            2015
  # iso   ind   value   data    value   data
  # AR    0     1.2420  NaN     1.2235  NaN
  #       1.01  0.1802  78.17   0.1795  75.16
  # ...


  first_yr = True

  for yr in years:
    # All core data files are named after the year of the edition
    fn = settings.src_core + yr + '.xlsx'

    df_yr = pd.DataFrame()
    for sheet in settings.core_data_sheets:
      
      # Build an index to parse only the relevant columns
      cols_index = build_col_index(fn,sheet)

      # Read Excel (parsing only relevant cols)
      df_sheet = pd.read_excel(fn,sheet,parse_cols=cols_index)

      # Ensure that the iso codes don't contain strange characters. They can only
      # contain letters, numbers and hyphens. (eg. CN, CN-65 or IN-MP)
      df_sheet['iso'].replace(to_replace='[^a-zA-Z0-9-]', value='',inplace=True,regex=True) 

      # Append each sheet to a dataframe holding the data for that year
      df_yr = df_yr.append(df_sheet)

    # Set the index of the DF to the ISO code and ID of the indicator
    df_yr.set_index(['iso','id'],inplace=True)
    # Make sure the index is sorted so the slicing works well
    df_yr.sortlevel(inplace=True)

    # Rename the column 'score' to value
    df_yr.rename(columns={'score':'value'}, inplace=True)

    
    # Add an extra level in the hierarchy of the columns (Mutli-index)
    # containing an indication of the year

    # Create list that repeats 'value' for the amount of years available
    c = [yr] * len(df_yr.columns)
    # Add a level to the cols
    df_yr.columns = [c, df_yr.columns]

    if first_yr:
      # If it's the first year, we initialize the full DataFrame
      df_full = df_yr
      first_yr = False
    else:
      # Every subsequent year will have to be merged into df_full
      df_full = pd.merge(df_full,df_yr,how='outer',left_index=True,right_index=True)

  df_full.sortlevel(axis=1,inplace=True)

  #############################################################################
  # 2. CSV downloads
  #
  # For all the CSV exports, prepare a dataframe that combines the data with
  # the meta.

  print "Building the CSV files for the download section..."

  # For the CSV, we're only interested in the value column of each year
  df_full_csv = df_full.loc[:,(slice(None),'value')]
  df_full_csv.columns = df_full_csv.columns.get_level_values(0)

  # The full DF is a multi-index. Since the meta-files have a single index,
  # it is necessary to reset the indexes before joining on the column.
  df_full_csv = df_full_csv.reset_index()
  df_meta_aa_csv = df_meta_aa.reset_index()
  df_meta_index_csv = df_meta_index.reset_index()

  # Merge the country meta
  df_full_csv = pd.merge(df_full_csv,df_meta_aa_csv,on='iso')

  # Merge the index meta data
  df_full_csv = pd.merge(df_full_csv,df_meta_index_csv,on='id',suffixes=('_aa','_var'))

  # Re-index the DF on iso & id  and make sure it's sorted
  df_full_csv.set_index(['iso','id'],inplace=True)
  df_full_csv.sortlevel(inplace=True)

  # 2.0 Export the full dataset to CSV

  for lang in settings.langs:
    # Build a list with the meta-data that needs to be included
    columns = ['name:' + lang + '_aa','name:' + lang + '_var','type_var']
    columns = columns + list(years)

    file_path = (settings.exp_full_csv).format(lang=lang)
    df_full_csv.loc[slice(None),columns].to_csv(file_path,encoding='UTF-8',index=False)
  

  # 2.1 Generate the main CSV files

  # Slice the DF to only contain the score and parameters for the current year.
  df_main_csv = df_full_csv.loc[(slice(None),sp),:]

  for lang in settings.langs:
    # Pivot the DF and export it
    file_path = (settings.exp_current_csv).format(lang=lang, yr=current_yr)
    pivot_df(df_main_csv,'name:' + lang + '_aa','name:' + lang + '_var',current_yr).to_csv(file_path,encoding='UTF-8')


  # 2.3 Generate the country + state CSV files
  for aa in admin_areas:
    # Select the data of this admin area
    df_aa_csv = df_full_csv.loc[(aa,slice(None)),:]
    for lang in settings.langs:
      # Include the name of the var, its type and the years
      columns = ['name:' + lang + '_var','type_var'] + list(years)

      # Select the proper columns and generate the CSV
      file_path = (settings.exp_aa_csv).format(lang = lang, aa = aa.lower())
      df_aa_csv.loc[slice(None),columns].to_csv(file_path,encoding='UTF-8',index=False)


  #############################################################################
  # 3. Calculate the rankings
  #
  #
  # Output: df_full
  #
  #             2014                    2015
  #             value   data  gr  sr    value  data  gr  sr
  # iso   id
  # AR    0     1.2420  NaN   13  NaN   1.2235 NaN   12  NaN
  #       1.01  0.1802  73.1  5   NaN   0.1795 75.8  6   NaN
  # ...


  print "Calculating the ranking..."

  # 3.0 Prepare the structure
  # Add placeholder cols with NaN that can be updated later with df.update()
  for year in years:
    for rank in ('gr', 'sr'):
      df_full[(year,rank)] = np.nan
  # Make sure its sorted
  df_full.sortlevel(axis=1,inplace=True)

 
  # 3.1 Global rank
  # The global rank (gr) is a rank of all the COUNTRIES in the project
  df_full = get_rank(countries,df_full,'gr')


  # 3.3 State rank
  # The state rank ('sr') ranks the STATES of a particular country
  for country in countries:
    # Check if there are any states or provinces for this country
    cs = build_set(country,'country','iso',settings.src_meta_aa)
    if cs:
      df_full = get_rank(cs,df_full,'sr')


  #############################################################################
  # 4. JSON api
  #

  print "Building the JSON files for the API..."

  # 4.1 Generate the main JSON file
  for lang in settings.langs:
    # The JSON will contain a list with dicts
    json_data = []
    
    # Loop over the countries list
    for country in countries:
      country_data = build_json_aa(country,df_full,lang, historic=True)
      # Sort the list of states / provinces
      if country_data['states']:
        country_data['states'] = sorted(country_data['states'], key=lambda k: k['name'])
      json_data.append(country_data)

    # Sort the list of countries by name
    sorted_data = sorted(json_data, key=lambda k: k['name'])

    # Write the list to a JSON file
    file_path = (settings.exp_core).format(lang=lang)
    write_json(file_path, sorted_data)


  # 4.3 Generate the country + state JSON files
  for aa in admin_areas:
    for lang in settings.langs:
      # Get the data for this admin area in a dict
      json_data = build_json_aa(aa,df_full,lang,indicators=True,historic=True)

      # Write the dict to a JSON file
      file_path = (settings.exp_aa).format(lang=lang,aa=aa.lower())
      write_json(file_path, json_data)


  # Fully remove the temp directory
  clean_dir(settings.tmp_dir , True)

  print "All done. The data has been prepared for use on global-climatescope.org."

if __name__ == "__main__":
  main()