from datetime import date
import csv
import errno
import json
import os
import shutil
import urllib

debug = True
# Directory structure
src_dir = 'source/'
export_dir = 'data/'

# Source - filenames / dirs
src_meta_aa = src_dir + 'meta/admin_areas.csv'
# Directory path for final data export.
# Language will be replaced before saving the file.
country_profile_export = export_dir + '{lang}/api/countries-profile/'

langs = ['en', 'es']
indicators = [
              "NY.GDP.PCAP.KD",  # GDP per capita (constant 2005 US$)
              "NY.GDP.PCAP.KD.ZG",  # GDP per capita growth (annual %)
              "SP.POP.TOTL",  # Population, total
              ]

def debug(data):
    """
    Prints a message to the console if debug is enabled.
    
    Parameters
    ----------
    data:      : string
            The data to print
    """
    if debug:
        print data

def get_country_list():
    """
    Returns a list of country iso codes from the admin_areas.csv
    """
    countries = [];
    with open(src_meta_aa, 'rb') as csv_file:
        meta_aa = csv.reader(csv_file)
        for row in meta_aa:
            if row[1] == 'country':
                countries.append(row[0])
    return countries

def get_worldbank_indicator_api_url(lang, country, indicator, yr=None):
    """
    Returns the url to use to interact with the worldbank api
    
    Parameters
    ----------
    lang:      : string
            The language.
    country:      : string
            The country for which to query the data.
    indicator:      : string
            The indicator to request
    yr:      : string
            The year for which to get the data.
            If not provided the current year is used.
    """
    if yr == None:
        yr = date.today().year

    return "http://api.worldbank.org/{lang}/countries/{country}/indicators/{indicator}?date={yr}&format=json".format(lang=lang, country=country, indicator=indicator, yr=yr)

def query_worldbank_indicator_api(lang, country, indicator, yr=None):
    """
    Returns the data for the requested indicator fetched from the api.
    If there's no data available for the specified year None
    is returned.
    
    Parameters
    ----------
    lang:      : string
            The language.
    country:      : string
            The country for which to query the data.
    indicator:      : string
            The indicator to request
    yr:      : string
            The year for which to get the data.
            If not provided the current year is used.
    """
    url = get_worldbank_indicator_api_url(lang, country, indicator, yr)
    # Query the worldbank API.
    response = urllib.urlopen(url);
    data = json.loads(response.read())
    # We only need the actual indicator data.
    # Example response:
    # [
    #    {
    #     Meta information about the page
    #    },
    #    [
    #        {
    #         Indicator object
    #        }
    #    ]
    # ]
    # Check if the year doesn't exist.
    # This happens with queries outside WB range of data.
    if data[1] == None:
        return None
    else:
        return data[1][0]

def query_worldbank_indicator_api_recursive(lang, country, indicator, preferred_yr, max_yr=2000):
    """
    Recursively query the API until valid data is found or the max_yr
    is reached.
    The API may not return data for the pretended year. In that case
    try again with the previous year.

    Returns the data for the requested indicator fetched from the api.
    
    Parameters
    ----------
    lang:      : string
            The language.
    country:      : string
            The country for which to query the data.
    indicator:      : string
            The indicator to request
    preferred_yr:      : string
            The year for which to get the data.
    max_yr:      : string
            How back to search for data.
            Default to year 2000
    """
    if preferred_yr < max_yr:
        # The recursiveness has to come to an end.
        # If no data was found return null.
        debug("  No data until {year} for: {lang} - {country} - {indicator}".format(lang=lang, country=country, indicator=indicator, year=preferred_yr))
        return None
    
    debug("  {lang} - {country} - {indicator} - {year}".format(lang=lang, country=country, indicator=indicator, year=preferred_yr))
    data = query_worldbank_indicator_api(lang, country, indicator, preferred_yr)
    # There might be the case that there isn't data for a specific year.
    # In that case we query again going back one year.
    if data == None or data['value'] == None:
        preferred_yr = preferred_yr - 1
        new_data = query_worldbank_indicator_api_recursive(lang, country, indicator, preferred_yr)
        # There's a difference between a data without value and no data at all.
        # When there's no data return the last one.
        if new_data != None:
            data = new_data
    return data

def clean_dir(path):
    """
    Cleans a directory by deleting it and creating it again.
    
    Parameters
    ----------
    path:      : string
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

def main():
    print "Getting data from Worldbank API"
    # Prepare export directories.
    for lang in langs:
        clean_dir(country_profile_export.format(lang=lang))

    countries = get_country_list()
    for iso in countries:
        iso = iso.lower()
        for lang in langs:
            # Init with defaults.
            country_data = { 'name': None, 'iso': iso, 'indicators': [] }
            for indicator in indicators:
                ## Get data recursively.
                data = query_worldbank_indicator_api_recursive(lang, iso, indicator, 2013)
                indicator_to_append = { 'id': indicator, 'name': None, 'value': None, 'year': None }
                
                if data == None:
                    country_data['indicators'].append(indicator_to_append)
                    continue
                elif data['value'] == None:
                    indicator_to_append['name'] = data['indicator']['value']
                    country_data['indicators'].append(indicator_to_append)
                    continue
                
                # Add country name if it is not present.
                if country_data['name'] == None:
                    country_data['name'] = data['country']['value']
                
                indicator_to_append['name'] = data['indicator']['value']
                indicator_to_append['value'] = data['value']
                indicator_to_append['year'] = int(data['date'])
                country_data['indicators'].append(indicator_to_append)
                
            # Write the list to a JSON file
            file_path = (country_profile_export + '{iso}.json').format(lang=lang, iso=iso)
            with open(file_path, 'w') as ofile:
                json.dump(country_data, ofile)

        remaining = len(countries) - countries.index(iso.upper()) - 1
        debug("Data collected for {country}. Left {count} countries".format(country=iso, count=remaining))


if __name__ == "__main__":
  main()