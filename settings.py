# Settings - Climatescope
# -*- coding: latin-1 -*-

# The main settings to process the Climatescope data


# Directory structure
src_dir = 'source/'
export_dir = 'data/'
tmp_dir = 'tmp/'

# Source - filenames / dirs
src_core = src_dir + 'cs-core/'
src_auxiliary = src_dir + 'cs-auxiliary/'

src_meta_aa = src_dir + 'meta/admin_areas.csv'
src_meta_index = src_dir + 'meta/index.csv'

# Export filename of the json files
exp_core_csv = export_dir + 'cs-core.csv'
exp_aux_json = export_dir + '{lang}/api/auxiliary/{indicator}/{aa}.json'

# Source structure
core_data_sheets = ['score', 'param', 'ind']
core_data_cols = ['id', 'iso', 'score', 'data']

# Languages
langs = ['en','es']
# Years we have want data for
yrs = [2006,2007,2008,2009,2010,2011,2012,2013]

# The current edition
current_edition = 2014


indicators = [
  {
    "id": 107, # The source file contains an indication of the id
    "custom": True,
    "export": 'installed-capacity', # Folder for the exported data
    "title": { # Title of the chart
      "en": 'Installed capacity',
      "es": 'Capacidad instalada'
    },
    "labelx": { # Label of the x-axis
      "en": 'year',
      "es": 'año'
    },
    "labely": { # Label of the y-axis
      "en": 'MW',
      "es": 'MW'
    },
    "series": [
      {
        "id": 'non-clean-energy', # The id used in the export
        "source-id": 'Non-clean Energy', # The id in the source CSV
        "level": "country", # Data on country level. When 'regional' or 'global' is used, averages are calculated
        "name": {
          "en": 'Non-clean Energy',
          "es": 'Energía no limpia'
        }
      },
      {
        "id": 'clean-energy', # The id used in the export
        "source-id": 'Clean Energy', # The id in the source CSV
        "level": "country",
        "name": {
          "en": 'Clean Energy',
          "es": 'Energía limpia'
        }
      }
    ],
    "years": yrs # List with years to process
  },
  {
    "id": 201,
    "export": 'clean-energy-investments',
    "title": {
      "en": 'Clean energy investments',
      "es": 'Inversiones en energías limpias'
    },
    "labelx": {
      "en": 'year',
      "es": 'año'
    },
    "labely": {
      "en": 'USDm',
      "es": 'USDm'
    },
    "series": [
      {
        "id": 'country',
        "source-id": "Clean energy investments",
        "level": "country",
      }
    ],
    "years": yrs
  },
  {
    "id": 401,
    "export": 'carbon-offset-projects',
    "title": {
      "en": 'Carbon offset projects by sector',
      "es": 'Compensaciones de carbono por sector'
    },
    "labelx": {
      "en": 'category',
      "es": 'categoria'
    },
    "labely": {
      "en": '',
      "es": ''
    },
    "series": [
      {
        "id": 'power-generation',
        "source-id": "Power generation",
        "level": "country",
        "name": {
          "en": 'Power generation',
          "es": 'Generación eléctrica'
        }
      },
      {
        "id": 'methane',
        "source-id": "Methane",
        "level": "country",
        "name": {
          "en": 'Methane',
          "es": 'Metano'
        }
      },
      {
        "id": 'forestry',
        "source-id": "Forestry",
        "level": "country",
        "name": {
          "en": 'Forestry',
          "es": 'Silvicultura'
        }
      },
      {
        "id": 'waste',
        "source-id": "Waste",
        "level": "country",
        "name": {
          "en": 'Waste',
          "es": 'Residuos'
        }
      },
      {
        "id": 'energy-efficiency',
        "source-id": "Energy efficiency",
        "level": "country",
        "name": {
          "en": 'Energy efficiency',
          "es": 'Eficiencia energética'
        }
      },
      {
        "id": 'other',
        "source-id": "Other",
        "name": {
          "en": 'Other',
          "es": 'Otro'
        }
      },
    ],
    "years": [2014]
  },
]