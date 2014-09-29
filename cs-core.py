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
import shutil
import json
import re
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
  years = set()
  fn_pattern = re.compile('^20[0-9]{2}$')

  for f in os.listdir(src_core):
    fn = os.path.splitext(f)[0]
    ext = os.path.splitext(f)[-1].lower()
    path = os.path.join(src_core, fn)

    if not os.path.isdir(path):
      # Only continue if dealing with file, ignore the folders
      if ext == ".xlsx":
        # Check if dealing with an .xlsx
        if fn_pattern.match(fn):
          # If the file-name is a properly formatted year, add it
          years.add(fn)

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
  rankings = { 'gr': 'overall_ranking', 'rr': 'regional_ranking', 'sr': 'state_ranking' }
  aa_ranks = {}

  # Not every type of admin area has all the rankings
  # Check if it is not null and if so, add it.
  for key, value in rankings.iteritems():
    rank = df.loc[ind,(yr,key)]
    if pd.notnull(rank):
      aa_ranks[value] = int(rank)

  return aa_ranks


def get_basic_stats(aal,df,ind):
  """Returns a list with statistics for a list of administrative areas, for a
  particular score/parameter/indicator. If more than one year is available, it
  will return historic data.
  Eg. [{ 'year': 2014, min': 0.23, 'max': 2.54, 'avg': 1.68 }]

  Parameters
  ----------
  aal       : list
              A list of iso codes (strings) to process
  df        : dataframe
              The dataframe to process, multi-indexed on 'iso' and 'id'. The
              columns also have a hierarchy (year, 'value')
  ind       : float
              The score/param/indicator we're building the rank for
  """

  data = []

  # Slice the full DF so it only contains data for the relevant indicator and
  # countries.
  df_aal = df.loc[(aal,ind),(slice(None),'value')]

  for yr in years:
    # Slice the aal DF so it only contains the year
    df_aal_yr = df_aal.loc[slice(None),yr]

    # For each year, we're storing an object with year and the value
    yr_data = {}
    yr_data['year'] = int(yr)

    # Group the DF by the indicator, calculate the mean and store the value in
    # the dict.
    yr_data['mean'] = round(df_aal_yr.groupby(level=1).mean().iloc[0]['value'],5)
    yr_data['min'] = round(df_aal_yr.groupby(level=1).min().iloc[0]['value'],5)
    yr_data['max'] = round(df_aal_yr.groupby(level=1).max().iloc[0]['value'],5)

    data.append(yr_data)

  return data


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
  years = get_years()

  # Slice the dataframe to only contain the data for the administrative area
  df_aa = df_data.loc[aa]

  # Load metadata for the admin areas
  aa_data['iso'] = aa.lower()
  aa_data['name'] = df_meta_aa.ix[aa,'name:' + lang]
  aa_data['grid'] = df_meta_aa.ix[aa,'grid']
  
  # Add region for the countries
  if df_meta_aa.ix[aa,'type'] == 'country':
    aa_region = {}
    region = df_meta_aa.ix[aa,'region']
    # Add the id of the region
    aa_region['id'] = region
    # Fetch the name of the region from the meta file
    aa_region['name'] = df_meta_aa.ix[region,'name:' + lang]
    aa_data['region'] = aa_region


  if historic:
    # Provide the score for all editions
    sl = []
    for yr in years:
      # For each year, we're storing an object with year and the value
      yr_data = {}
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
            ind_data['description'] = df_meta_index.ix[ind,'description:' + lang]
            ind_data['active'] = indicator_active(aa,ind)
            
            if historic:
              # Provide values for all editions
              ind_yr = []
              for yr in years:
                # For each year, we're storing an object with year and the value
                yr_data = {}
                yr_data['value'] = round(df_aa.ix[float(ind),(yr,'value')],5)
                yr_data['year'] = int(yr)

                # Fetch the rankings for the indicator and update the yr_dict with them
                aa_ranks = rank_dict(df_aa,ind,yr)
                yr_data.update(aa_ranks)
                
                ind_yr.append(yr_data)

              ind_data['data'] = ind_yr
            else:
              # Provide the value for the current edition only
              ind_data['value'] = round(df_aa.ix[float(ind),(current_yr,'value')],5)

              # Fetch the rankings for the indicator and update the yr_dict with them
              aa_ranks = rank_dict(df_aa,ind,current_yr)
              ind_data.update(aa_ranks)

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
        # Call this function for all the states. At this point, only interested in
        # non-detailed data for the current version.
        state_data = build_json_aa(state,df_data,lang,indicators=False,historic=False,single_p=single_p)
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
    # For each year, slice the DF on the list of administrative areas, then
    # group by the indicator and build a rank. In case of equal values, the
    # lowest rank will assigned. (1, 2, 2, 2, 5, 6, 7, etc)
    # The rank is stored in the empty DF to ensure no previous values get
    # overridden by NaN.
    df_rank[(year, name)] = df.loc[(aal,slice(None)),(year,'value')].groupby(level=1).rank(method='min',ascending=False)

  # Overwrite the NaN values in the original DF with values in the df_rank
  df.update(df_rank)
  
  return df


def main():

  #############################################################################
  # 0.
  #

  # Check if tmp folder exists, otherwise create it
  if check_dir(tmp_dir) == True:
    sys.exit(0)
  else:
    os.makedirs(tmp_dir)

  # Run some checks on the source folder with core data.
  if not get_years():
    # Is there anything in the source folder to begin with?
    print "We were not able to find a XLSX file with core data in the folder: "\
          "%s. Make sure this folder contains at least one XLSX file named "\
          "after the year (eg. 2014.xlsx). Check the readme for more info "\
          "about the required structure of these files.\n"\
          "Quiting..." % (src_core)
    sys.exit(0)

  # Provide feedback that the script only processes XLSX files with properly
  # formatted filenames. (eg. 2014.xlsx)
  fn_pattern = re.compile('^20[0-9]{2}$')
  for f in os.listdir(src_core):
    fn = os.path.splitext(f)[0]
    ext = os.path.splitext(f)[-1].lower()
    path = os.path.join(src_core, fn)
    
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
  regions = build_set('region','type','iso',src_meta_aa)
  countries = build_set('country','type','iso',src_meta_aa)
  states = build_set('state','type','iso',src_meta_aa)
  admin_areas = countries | states
  
  # Build sets for the variables we loop over
  global index_param
  index_param = build_set('param','type','id',src_meta_index)
  index_score = build_set('score','type','id',src_meta_index)
  sp = list(index_score | index_param)

  # Build set for the years we're interested in
  global years
  years = get_years()
  global current_yr
  current_yr = max(years)


  # Read in the files with meta-data and set the scope to global
  global df_meta_aa
  df_meta_aa = pd.read_csv(src_meta_aa,index_col='iso')
  global df_meta_index
  df_meta_index = pd.read_csv(src_meta_index,index_col='id')


  #############################################################################
  # 1. Store the relevant core data in one DF (df_full)
  #
  #
  # Output: df_full
  #
  #             2014    2015
  # iso   id
  # AR    0     1.2420  1.2235
  #       1.01  0.1802  0.1795
  # ...


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

      # Ensure that the iso codes don't contain strange characters. They can only
      # contain letters, numbers and hyphens. (eg. CN, CN-65 or IN-MP)
      df_sheet['iso'].replace(to_replace='[^a-zA-Z0-9-]', value='',inplace=True,regex=True) 

      # Append each sheet to a dataframe holding the data for that year
      df_yr = df_yr.append(df_sheet)

    # Set the index of the DF to the ISO code and ID of the indicator
    df_yr.set_index(['iso','id'],inplace=True)
    # Make sure the index is sorted so the slicing works well
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


  #############################################################################
  # 2. CSV downloads
  #
  # For all the CSV exports, prepare a dataframe that combines the data with
  # the meta.

  print "Building the CSV files for the download section..."

  # Make sure the floats are rounded to 5 decimals
  df_full_csv = np.round(df_full,5)

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

  for lang in langs:
    # Build a list with the meta-data that needs to be included
    columns = ['name:' + lang + '_aa','name:' + lang + '_var','type_var']
    columns = columns + list(years)

    df_full_csv.loc[slice(None),columns].to_csv(export_dir + lang + '/download/climatescope-full.csv',encoding='UTF-8',index=False)
  

  # 2.1 Generate the main CSV files

  # Slice the DF to only contain the score and parameters for the current year.
  df_main_csv = df_full_csv.loc[(slice(None),sp),:]

  for lang in langs:
    # Pivot the DF and export it
    pivot_df(df_main_csv,'name:' + lang + '_aa','name:' + lang + '_var',current_yr).to_csv(export_dir + lang + '/download/climatescope-' + current_yr + '.csv',encoding='UTF-8')


  # 2.2 Generate the regional CSV files
  for region in regions:
    # Build a set with the admin areas for this region
    aa_region = build_set(region,'region','iso',src_meta_aa)
    aal = list(aa_region)
    
    # Filter the main csv on region. Used to generate CSV.
    df_region_csv = df_main_csv.loc[aal,:]
    for lang in langs:
      # Pivot the DF and and generate the CSV files
      pivot_df(df_region_csv,'name:' + lang + '_aa','name:' + lang + '_var',current_yr).to_csv(export_dir + lang + '/download/regions/climatescope-' + region + '.csv',encoding='UTF-8')


  # 2.3 Generate the country + state CSV files
  for aa in admin_areas:
    # Select the data of this admin area
    df_aa_csv = df_full_csv.loc[(aa,slice(None)),:]
    for lang in langs:
      # Include the name of the var, its type and the years
      columns = ['name:' + lang + '_var','type_var'] + list(years)

      # Select the proper columns and generate the CSV      
      df_aa_csv.loc[slice(None),columns].to_csv(export_dir + lang + '/download/countries/climatescope-' + aa.lower() + '.csv',encoding='UTF-8',index=False)


  # 2.4 Generate the parameter JSON files
  for p in index_param:
    # Select data of the parameter being dealt with
    df_param = df_full_csv.loc[(slice(None),p),:]
    for lang in langs:
      # Include the name of the country and the years
      columns = ['name:' + lang + '_aa'] + list(years)

      # Select the proper columns and generate the CSV
      df_param.loc[slice(None),columns].to_csv(export_dir + lang + '/download/parameters/climatescope-' + str(int(p)) + '.csv',encoding='UTF-8',index=False)


  #############################################################################
  # 3. Calculate the rankings
  #
  #
  # Output: df_full
  #
  #             2014                  2015
  #             value   gr  rr  sr    value   gr  rr  sr
  # iso   id
  # AR    0     1.2420  13  6   NaN   1.2235  12  8   NaN
  #       1.01  0.1802  5   3   NaN   0.1795  6   3   NaN
  # ...

  print "Calculating the ranking..."

  # 3.0 Prepare the structure
  # Create list that repeats 'value' for the amount of years available
  c = ['value'] * len(df_full.columns)
  # Add a level to the cols, resulting in (2014, 'value'), (2015, 'value') etc
  df_full.columns = [df_full.columns, c]

  # Add placeholder cols with NaN that can be updated later with df.update()
  for year in years:
    for rank in ('gr', 'rr', 'sr'):
      df_full[(year,rank)] = np.nan
  # Make sure its sorted
  df_full.sortlevel(axis=1,inplace=True)

 
  # 3.1 Global rank
  # The global rank (gr) is a rank of all the COUNTRIES in the project
  df_full = get_rank(countries,df_full,'gr')


  # 3.2 Regional rank
  # The regional rank (rr) is a rank of all the COUNTRIES in a region
  for region in regions:
    # Build a set with the admin areas for this region
    aa_region = build_set(region,'region','iso',src_meta_aa)
    # Filter out the states and provinces, leaving only the countries
    cr = aa_region.difference(states)

    df_full = get_rank(cr,df_full,'rr')


  # 3.3 State rank
  # The state rank ('sr') ranks the STATES of a particular country
  for country in countries:
    # Check if there are any states or provinces for this country
    cs = build_set(country,'country','iso',src_meta_aa)
    if cs:
      df_full = get_rank(cs,df_full,'sr')


  #############################################################################
  # 4. JSON api
  #

  print "Building the JSON files for the API..."

  # 4.1 Generate the main JSON file
  for lang in langs:
    # The JSON will contain a list with dicts
    json_data = []
    
    # Loop over the countries list
    for country in countries:
      country_data = build_json_aa(country,df_full,lang)
      json_data.append(country_data)

    # Write the list to a JSON file
    with open('data/' + lang + '/api/countries.json','w') as ofile:
      json.dump(json_data, ofile)


  # 4.2 Generate the regional JSON files
  for region in regions:
    # Build a set with the admin areas for this region
    aa_region = build_set(region,'region','iso',src_meta_aa)
    aal = list(aa_region)

    # Remove states from this set, leaving countries
    c_region = aa_region.difference(states)

    for lang in langs:
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


  # 4.3 Generate the country + state JSON files
  for aa in admin_areas:
    for lang in langs:
      # Get the data for this admin area in a dict
      json_data = build_json_aa(aa,df_full,lang,indicators=True,historic=True)
      
      # Write the dict to a JSON file
      with open('data/' + lang + '/api/countries/' + aa.lower() + '.json','w') as ofile:
        json.dump(json_data, ofile)


  # 4.4 Generate the parameter JSON files
  for p in index_param:
    for lang in langs:
      
      json_data = {}
      json_data['id'] = int(p)
      json_data['name'] = df_meta_index.ix[p,'name:' + lang]
      json_data['weight'] = round(df_meta_index.ix[p,'weight'],2)

      # The JSON will contain a list with dicts
      country_list = []
      # Loop over the countries
      for country in countries:
        country_data = build_json_aa(country,df_full,lang,indicators=False,historic=True,single_p=p)
        country_list.append(country_data)

      json_data['countries'] = country_list

      # Generate the parameter JSONs
      with open('data/' + lang + '/api/parameters/' + str(int(p)) + '.json','w') as ofile:
        json.dump(json_data, ofile)


  # 4.5 Generate the JSON files with derived statistics
  for lang in langs:

    json_data = {}
    
    # Generate regional statistics
    region_list = []
    for region in regions:
      # Build a set with the admin areas for this region
      aa_region = build_set(region,'region','iso',src_meta_aa)

      # Remove states from this set, leaving countries
      c_region = list(aa_region.difference(states))

      # The JSON contains a dict with id, name and a countries list
      region_data = {}
      region_data['id'] = region
      region_data['name'] = df_meta_aa.ix[region,'name:' + lang]

      region_data['score'] = get_basic_stats(c_region,df_full,0)

      param_list = []
      for param in index_param:
        param_data = {}
        param_data['id'] = int(param)
        param_data['name'] = df_meta_index.ix[param,'name:' + lang]
        param_data['data'] = get_basic_stats(c_region,df_full,param)
        param_list.append(param_data)

      region_data['parameters'] = param_list

      region_list.append(region_data)
      
    json_data['regions'] = region_list

    # Write the list to a JSON file
    with open('data/' + lang + '/api/stats.json','w') as ofile:
      json.dump(json_data, ofile)


  # Fully remove the temp directory
  clean_tmp(True)

  print "All done. The data has been prepared for use on globalclimatescope.org."

if __name__ == "__main__":
  main()